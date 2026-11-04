"""Run a model over every (source, task) cell and score it: the benchmark's entry point.

Composes the other modules: records supply the test split, tasks render prompts and labels, wiki
decides which tasks run, models generate. `run` is the reusable tool (notebook/REPL friendly);
`main` is a thin CLI over it. Only `split: test` is scored; `train` is reserved for later training.
"""

import argparse
import json
import math
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from oncolens.models import Model, load_model
from oncolens.records import Record, content_hash, load_corpora
from oncolens.tasks import LETTERS, Task, select_tasks
from oncolens.wiki import supported_targets

PRIMARY_METRIC = "mean_balanced_accuracy"


@dataclass(frozen=True)
class Cell:
    """Scores of one model on one task in one source."""

    source: str
    task: str
    n: int
    accuracy: float
    balanced_accuracy: float  # mean per-class recall over the classes present in the labels
    parse_rate: float  # fraction of generations containing a valid option; unparsed count as wrong
    majority_baseline: float  # accuracy of always predicting the most common label


@dataclass(frozen=True)
class Report:
    model: str
    data_hash: str
    unsupported_targets: tuple[str, ...]
    cells: tuple[Cell, ...]

    @property
    def n(self) -> int:
        return sum(cell.n for cell in self.cells)

    def metrics(self) -> dict[str, Any]:
        """Flat dict for the lab harness: per-cell scores, cell means, and run provenance."""
        flat: dict[str, Any] = {}
        for cell in self.cells:
            prefix = f"{cell.source}/{cell.task}"
            flat[f"{prefix}/accuracy"] = cell.accuracy
            flat[f"{prefix}/balanced_accuracy"] = cell.balanced_accuracy
            flat[f"{prefix}/parse_rate"] = cell.parse_rate
            flat[f"{prefix}/majority_baseline"] = cell.majority_baseline
            flat[f"{prefix}/n"] = cell.n
        for name in ("accuracy", "balanced_accuracy", "parse_rate", "majority_baseline"):
            flat[f"mean_{name}"] = sum(getattr(c, name) for c in self.cells) / len(self.cells)
        return flat | {
            "model": self.model,
            "n": self.n,
            "unsupported_targets": list(self.unsupported_targets),
            "data_hash": self.data_hash,
        }

    def table(self) -> str:
        header = f"{'source':<16}{'task':<18}{'n':>5}{'acc':>8}{'bal_acc':>9}{'parse':>8}{'majority':>10}"
        rows = [
            f"{c.source:<16}{c.task:<18}{c.n:>5}{c.accuracy:>8.3f}{c.balanced_accuracy:>9.3f}"
            f"{c.parse_rate:>8.3f}{c.majority_baseline:>10.3f}"
            for c in self.cells
        ]
        footer = [
            f"model={self.model}  data={self.data_hash}  "
            f"{PRIMARY_METRIC}={self.metrics()[PRIMARY_METRIC]:.3f}",
            f"unsupported targets (in wiki, not implemented): {list(self.unsupported_targets) or 'none'}",
        ]
        return "\n".join([header, *rows, *footer])


def parse_choice(completion: str) -> str | None:
    """First standalone capital A or B in the completion, else None.

    Case-sensitive so that the article 'a' is not read as an answer (a sentence-initial 'A' still
    is; the prompt demands a bare letter).
    """
    match = re.search(rf"\b([{''.join(LETTERS)}])\b", completion)
    return match.group(1) if match else None


def score(labels: Sequence[str], predictions: Sequence[str | None], source: str, task: str) -> Cell:
    """Score predictions (None = unparsed, counted wrong) against gold letters."""
    n = len(labels)
    correct = [label == prediction for label, prediction in zip(labels, predictions, strict=True)]
    class_counts = Counter(labels)
    recalls = [
        sum(ok for ok, label in zip(correct, labels, strict=True) if label == cls) / count
        for cls, count in class_counts.items()
    ]
    return Cell(
        source=source,
        task=task,
        n=n,
        accuracy=sum(correct) / n,
        balanced_accuracy=sum(recalls) / len(recalls),
        parse_rate=sum(p is not None for p in predictions) / n,
        majority_baseline=max(class_counts.values()) / n,
    )


def run(
    model: Model,
    corpora: Mapping[str, Sequence[Record]],
    tasks: Sequence[Task],
    *,
    limit: int | None = None,
    unsupported_targets: Sequence[str] = (),
    data_hash: str = "",
) -> Report:
    """Score `model` on the test split of every corpus for every task.

    `limit` keeps the first N test patients (by id) per source, for quick runs; it makes cells
    smaller and noisier, so never compare limited runs with full ones.
    """
    cells = []
    for source, records in corpora.items():
        test = sorted((r for r in records if r.split == "test"), key=lambda r: r.patient_id)[:limit]
        if not test:
            raise ValueError(f"source {source} has no test records")
        for task in tasks:
            completions = model.generate([task.prompt(r) for r in test])
            cells.append(
                score(
                    [task.label(r) for r in test],
                    [parse_choice(c) for c in completions],
                    source,
                    task.id,
                )
            )
    return Report(model.name, data_hash, tuple(unsupported_targets), tuple(cells))


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the OncoLens benchmark.")
    parser.add_argument("--model", required=True, help="Hugging Face model id, or 'fixed:A' / 'fixed:B'")
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--wiki", type=Path, default=Path("wiki-llm"))
    parser.add_argument("--limit", type=int, default=None, help="test patients per source")
    args = parser.parse_args(argv)

    tasks, unsupported = select_tasks(supported_targets(args.wiki))
    report = run(
        load_model(args.model),
        load_corpora(args.data),
        tasks,
        limit=args.limit,
        unsupported_targets=unsupported,
        data_hash=content_hash(args.data),
    )
    print(report.table(), file=sys.stderr)
    assert all(math.isfinite(v) for v in report.metrics().values() if isinstance(v, float))
    print(json.dumps(report.metrics()))  # the lab harness reads this last stdout line


if __name__ == "__main__":
    main()
