"""Load patient-record corpora (data/README.md contract) into typed, validated `Record`s.

This is the benchmark's only door to the data. Every file is validated against the contract at load
time, so downstream code (tasks, bench) can trust the shape. `Record.prompt_text` is the only part of
a record a prompt may use: `outcomes` is ground truth and stays on the record solely for labelling.
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from oncolens.frontmatter import split_frontmatter

SOURCES = ("msk-chord", "synthetic-chord")
SPLITS = ("train", "test")
OS_STATUSES = ("LIVING", "DECEASED")
SITE_VOCABULARY = frozenset(
    {
        "Adrenal Glands",
        "Bone",
        "CNS/Brain",
        "Intra Abdominal",
        "Liver",
        "Lung",
        "Lymph Node",
        "Other",
        "Pleura",
        "Reproductive Organs",
    }
)
SECTIONS = ("Demographics", "Disease", "Treatment")
FRONTMATTER_KEYS = {"patient_id", "source", "split", "cancer_type", "outcomes"}
OUTCOME_KEYS = {"os_status", "os_months", "metastatic_sites"}


class ContractError(ValueError):
    """A record file violates the data contract in data/README.md."""


@dataclass(frozen=True)
class Outcomes:
    """Ground truth. Used for labels and scoring, never for prompts."""

    os_status: str
    os_months: float
    metastatic_sites: tuple[str, ...]


@dataclass(frozen=True)
class Record:
    patient_id: str
    source: str
    split: str
    cancer_type: str
    outcomes: Outcomes
    body: str

    @property
    def prompt_text(self) -> str:
        """The leak-safe view: the Markdown body only, without frontmatter."""
        return self.body.strip()


def parse_record(text: str, filename_stem: str) -> Record:
    """Parse and validate one record file; raises ContractError naming the broken rule."""
    try:
        meta, body = split_frontmatter(text)
    except ValueError as error:
        raise ContractError(str(error)) from error
    _require(
        set(meta) == FRONTMATTER_KEYS,
        f"frontmatter keys {sorted(meta)} != {sorted(FRONTMATTER_KEYS)}",
    )
    raw_outcomes = meta["outcomes"]
    _require(
        isinstance(raw_outcomes, dict) and set(raw_outcomes) == OUTCOME_KEYS,
        f"outcomes keys must be exactly {sorted(OUTCOME_KEYS)}",
    )
    outcomes = _parse_outcomes(raw_outcomes)
    patient_id = str(meta["patient_id"])
    _require(patient_id == filename_stem, f"patient_id {patient_id} != file name {filename_stem}")
    _require(meta["source"] in SOURCES, f"unknown source {meta['source']!r}")
    _require(meta["split"] in SPLITS, f"unknown split {meta['split']!r}")
    _require(f"# Patient {patient_id}" in body, "body lacks the '# Patient <id>' title")
    for section in SECTIONS:
        _require(f"\n## {section}\n" in body, f"body lacks the '## {section}' section")
    return Record(patient_id, meta["source"], meta["split"], str(meta["cancer_type"]), outcomes, body)


def load_corpus(directory: Path) -> list[Record]:
    """Load every `<patient_id>.md` of one corpus folder (its README.md is skipped), sorted by id.

    A corpus is a single source: mixed sources in one folder is a contract violation.
    """
    records = []
    for path in sorted(directory.glob("*.md")):
        if path.name == "README.md":
            continue
        try:
            records.append(parse_record(path.read_text(encoding="utf-8"), path.stem))
        except ContractError as error:
            raise ContractError(f"{path}: {error}") from error
    _require(bool(records), f"{directory} holds no records")
    _require(len({r.source for r in records}) == 1, f"{directory} mixes several sources")
    return records


def load_corpora(data_dir: Path) -> dict[str, list[Record]]:
    """Load every corpus folder under `data_dir`, keyed by `source`."""
    corpora: dict[str, list[Record]] = {}
    for directory in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        records = load_corpus(directory)
        source = records[0].source
        _require(source not in corpora, f"source {source} appears in more than one folder")
        corpora[source] = records
    _require(bool(corpora), f"{data_dir} holds no corpus folders")
    return corpora


def content_hash(data_dir: Path) -> str:
    """Short SHA-256 over all files' relative paths and bytes: pins exactly which data a score used."""
    digest = hashlib.sha256()
    for path in sorted(p for p in data_dir.rglob("*") if p.is_file()):
        digest.update(path.relative_to(data_dir).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


def _parse_outcomes(raw: dict[str, Any]) -> Outcomes:
    _require(raw["os_status"] in OS_STATUSES, f"unknown os_status {raw['os_status']!r}")
    months = raw["os_months"]
    _require(
        isinstance(months, int | float) and not isinstance(months, bool) and months >= 0,
        f"os_months must be a non-negative number, got {months!r}",
    )
    sites = raw["metastatic_sites"]
    _require(isinstance(sites, list), "metastatic_sites must be a list")
    _require(
        set(sites) <= SITE_VOCABULARY,
        f"sites outside the vocabulary: {sorted(set(sites) - SITE_VOCABULARY)}",
    )
    _require(sites == sorted(sites), "metastatic_sites must be sorted")
    return Outcomes(raw["os_status"], float(months), tuple(sites))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)
