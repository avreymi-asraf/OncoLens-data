"""Connection check: proves, on the real files, that the benchmark's seams hold. Exit 1 on failure.

Not a unit-test suite: each seam below runs the real code on the real data and the real wiki
(`guard_cmd` calls `uv run python -m oncolens.check`). Seams: data contract, patient ids, prompt
leakage, wiki-to-tasks, split disjointness, and the whole bench pipeline with a fixed-answer model.
"""

import argparse
import math
import re
import sys
from collections import Counter
from collections.abc import Callable, Sequence
from pathlib import Path

from oncolens.bench import PRIMARY_METRIC, run
from oncolens.models import Fixed
from oncolens.records import ContractError, Outcomes, Record, load_corpora
from oncolens.tasks import TASKS, select_tasks
from oncolens.wiki import supported_targets

Corpora = dict[str, list[Record]]

# Hand-written gold for "always answer A", deliberately NOT derived through Task.label.
FIRST_OPTION_IS_CORRECT: dict[str, Callable[[Outcomes], bool]] = {
    "overall-survival": lambda o: o.os_status == "LIVING",
    "metastasis": lambda o: "Liver" not in o.metastatic_sites,
}


class SeamFailure(Exception):
    """A seam does not hold; the message says how."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SeamFailure(message)


def check_ids_unique(corpora: Corpora) -> str:
    ids = Counter(r.patient_id for records in corpora.values() for r in records)
    duplicated = sorted(i for i, count in ids.items() if count > 1)
    _require(not duplicated, f"duplicate patient ids: {duplicated[:5]}")
    return f"{len(ids)} unique patient ids across {len(corpora)} corpora"


def check_no_leak(corpora: Corpora) -> str:
    """No outcome value in any body; every rendered prompt is body + a record-independent suffix."""
    suffix_of_task: dict[str, str] = {}
    prompts = 0
    for records in corpora.values():
        for record in records:
            for pattern in _outcome_patterns(record):
                found = re.search(rf"(?<![\w.]){pattern}(?![\w.])", record.prompt_text, re.IGNORECASE)
                _require(found is None, f"{record.patient_id}: body matches outcome pattern {pattern!r}")
            for task in TASKS.values():
                prompt = task.prompt(record)
                _require(
                    prompt.startswith(record.prompt_text),
                    f"{task.id}: prompt does not start with the body",
                )
                suffix = prompt.removeprefix(record.prompt_text)
                expected = suffix_of_task.setdefault(task.id, suffix)
                _require(suffix == expected, f"{task.id}: {record.patient_id} adds record-specific text")
                prompts += 1
    return f"{prompts} rendered prompts hold only body + fixed task text, no outcome value"


def _outcome_patterns(record: Record) -> list[str]:
    """Regex patterns that must not match a body.

    os_months only in its '14.2' form (bare integers would collide with ages and counts). Site names
    are legitimate body words ('Lung Cancer'), so sites are checked as a listed sequence and through
    the word 'metasta...', which no body may use.
    """
    outcomes = record.outcomes
    literals = [outcomes.os_status, str(outcomes.os_months), "os_status", "os_months"]
    if len(outcomes.metastatic_sites) > 1:
        literals.append(", ".join(outcomes.metastatic_sites))
    return [re.escape(literal) for literal in literals] + ["metasta[a-z]*"]


def check_wiki(wiki_dir: Path) -> str:
    targets = supported_targets(wiki_dir)
    tasks, unsupported = select_tasks(targets)
    _require(bool(tasks), f"no wiki target {targets} is implemented")
    return f"wiki targets {targets} -> tasks {[t.id for t in tasks]}, unsupported {unsupported}"


def check_split_disjoint(corpora: Corpora) -> str:
    for source, records in corpora.items():
        by_split = {s: {r.patient_id for r in records if r.split == s} for s in ("train", "test")}
        _require(bool(by_split["test"]), f"{source} has no test records")
        _require(not by_split["train"] & by_split["test"], f"{source}: patients in both train and test")
    return "; ".join(
        f"{source} {Counter(r.split for r in records).most_common()}" for source, records in corpora.items()
    )


def check_pipeline(corpora: Corpora, wiki_dir: Path) -> str:
    """Run the real bench with an always-A model; accuracies must match gold computed by hand."""
    tasks, unsupported = select_tasks(supported_targets(wiki_dir))
    report = run(Fixed("A"), corpora, tasks, unsupported_targets=unsupported)
    _require(len(report.cells) == len(corpora) * len(tasks), "missing (source, task) cells")
    for cell in report.cells:
        test = [r for r in corpora[cell.source] if r.split == "test"]
        correct = [FIRST_OPTION_IS_CORRECT[cell.task](r.outcomes) for r in test]
        accuracy = sum(correct) / len(test)
        balanced = 1 / len(set(correct)) if any(correct) else 0.0
        where = f"{cell.source}/{cell.task}"
        _require(cell.n == len(test), f"{where}: n={cell.n}, expected {len(test)}")
        _require(cell.parse_rate == 1.0, f"{where}: parse_rate={cell.parse_rate}")
        _require(
            math.isclose(cell.accuracy, accuracy),
            f"{where}: accuracy {cell.accuracy} != {accuracy}",
        )
        _require(
            math.isclose(cell.balanced_accuracy, balanced),
            f"{where}: balanced accuracy {cell.balanced_accuracy} != {balanced}",
        )
        _require(
            math.isclose(cell.majority_baseline, max(accuracy, 1 - accuracy)),
            f"{where}: majority baseline",
        )
    numbers = [v for v in report.metrics().values() if isinstance(v, float)]
    _require(
        all(math.isfinite(v) for v in numbers) and PRIMARY_METRIC in report.metrics(),
        "non-finite metrics",
    )
    return f"{len(report.cells)} cells scored, always-A accuracy matches hand-computed gold"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Check the OncoLens benchmark's connections.")
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--wiki", type=Path, default=Path("wiki-llm"))
    args = parser.parse_args(argv)

    failed = False

    def seam(name: str, check: Callable[[], str]) -> None:
        nonlocal failed
        try:
            print(f"PASS {name}: {check()}")
        except (SeamFailure, ContractError, OSError, ValueError) as error:
            failed = True
            print(f"FAIL {name}: {error}")

    corpora: Corpora = {}

    def load() -> str:
        corpora.update(load_corpora(args.data))
        return ", ".join(f"{source} {len(records)} records" for source, records in corpora.items())

    seam("data contract", load)
    if corpora:
        seam("patient ids", lambda: check_ids_unique(corpora))
        seam("no leakage", lambda: check_no_leak(corpora))
        seam("split disjoint", lambda: check_split_disjoint(corpora))
    seam("wiki -> tasks", lambda: check_wiki(args.wiki))
    if corpora:
        seam("bench pipeline", lambda: check_pipeline(corpora, args.wiki))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
