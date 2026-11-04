#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Turn the public MSK-CHORD release (cBioPortal format) into OncoLens patient records and an aggregate profile.

Where it fits: this is the only script that reads real patient data. It produces
  data/msk-chord-mini/      60 real, de-identified patient records (the `test` corpus)
  data/synthetic-chord/profile.json   counts and rates over the FULL cohort, no patient-level data
`scripts/synthesize.py` reads only that profile and re-uses `Patient` and `render_record` from this file,
so the record shape defined in `data/README.md` lives in exactly one place.

Usage:
    uv run scripts/extract_chord.py /path/to/msk_chord_2024
    uv run scripts/extract_chord.py /path/to/msk_chord_2024 --seed 7 --per-group 6
"""

import argparse
import csv
import json
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# Frontmatter / body vocabulary fixed by data/README.md.
SITE_COLUMNS = {
    "Adrenal Glands": "ADRENAL_GLANDS",
    "Bone": "BONE",
    "CNS/Brain": "CNS_BRAIN",
    "Intra Abdominal": "INTRA_ABDOMINAL",
    "Liver": "LIVER",
    "Lung": "LUNG",
    "Lymph Node": "LYMPH_NODES",
    "Other": "OTHER",
    "Pleura": "PLEURA",
    "Reproductive Organs": "REPRODUCTIVE_ORGANS",
}
BIOMARKER_COLUMNS = {
    "PD-L1 history": "HISTORY_OF_PDL1",
    "HR": "HR",
    "HER2": "HER2",
    "Gleason score, highest reported": "GLEASON_HIGHEST_REPORTED",
}
# Anti-cancer drugs only: bone-protecting agents (zoledronic acid...) and the 12 "Other" rows are left out.
SYSTEMIC_SUBTYPES = {"Chemo", "Hormone", "Targeted", "Biologic", "Immuno", "Investigational"}

# Metastatic burden strata: used to describe survival in profile.json and to look it up in synthesize.py.
# (Age bands were tried: within a cancer type and stage, age moves the deceased rate by only a few points.)
SITE_COUNT_BANDS = {"0 sites": (0, 0), "1-2 sites": (1, 2), "3+ sites": (3, 10)}
AGE_LIMITS = (10, 89)  # range of the release; ages are capped at 89 for de-identification

OS_QUANTILE_GROUPS = (
    20  # 19 cut points: 5%, 10%, ... 95%. Extremes (individual patients) are never published.
)
MIN_GROUP_PATIENTS = (
    20  # a regimen or biomarker is listed only if at least this many patients have it
)
REGISTRY_ENTRIES_CAP = (
    4  # profile.json reports "4 or more" as 4, so no group is a handful of patients
)
MAX_REGIMENS_PER_STRATUM = 8


@dataclass
class Patient:
    """One record in the shape of data/README.md. `outcomes` fields are never rendered into the body."""

    patient_id: str
    source: str
    split: str
    cancer_type: str
    sex: str
    age: int
    smoking: str
    stage: str
    registry_entries: int
    biomarkers: dict[str, str]  # label -> value, only the reported ones
    prior_medication: str
    agents: list[str]  # systemic agents in order of first start
    first_line_size: int  # the first `first_line_size` agents started together (not rendered)
    os_status: str  # LIVING | DECEASED
    os_months: float
    metastatic_sites: list[str] = field(default_factory=list)


def find_band(value: int, bands: dict[str, tuple[int, int]]) -> str:
    """Label of the band whose inclusive (low, high) range contains `value`."""
    return next(label for label, (low, high) in bands.items() if low <= value <= high)


def render_record(patient: Patient) -> str:
    """Markdown text of one patient file. The only place that knows the record shape."""
    biomarkers = "; ".join(f"{label}: {value}" for label, value in patient.biomarkers.items())
    lines = [
        "---",
        f"patient_id: {patient.patient_id}",
        f"source: {patient.source}",
        f"split: {patient.split}",
        f"cancer_type: {patient.cancer_type}",
        "outcomes:",
        f"  os_status: {patient.os_status}",
        f"  os_months: {patient.os_months:.1f}",
        f"  metastatic_sites: [{', '.join(sorted(patient.metastatic_sites))}]",
        "---",
        f"# Patient {patient.patient_id}",
        "",
        "## Demographics",
        f"- Sex: {patient.sex}",
        f"- Age: {patient.age}",
        f"- Smoking: {patient.smoking}",
        "",
        "## Disease",
        f"- Cancer type: {patient.cancer_type}",
        f"- Highest recorded stage: {patient.stage}",
        f"- Tumor registry entries: {patient.registry_entries}",
    ]
    if biomarkers:
        lines.append(f"- Biomarkers: {biomarkers}")
    lines += [
        "",
        "## Treatment",
        f"- Prior medication before MSK: {patient.prior_medication}",
        f"- Systemic agents, in order: {', '.join(patient.agents) or 'None recorded'}",
        "",
    ]
    return "\n".join(lines)


def read_cbioportal_table(path: Path) -> list[dict[str, str]]:
    """Rows of a cBioPortal tab-separated file; '#' lines are descriptions, not data."""
    with path.open() as file:
        return list(
            csv.DictReader((line for line in file if not line.startswith("#")), delimiter="\t")
        )


def load_agents_by_patient(raw_dir: Path) -> dict[str, tuple[list[str], int]]:
    """patient_id -> (systemic agents ordered by first start, size of the first-line group).

    The first-line group is every agent that starts on the patient's earliest start day.
    """
    starts_by_patient: dict[str, dict[str, int]] = defaultdict(dict)
    for row in read_cbioportal_table(raw_dir / "data_timeline_treatment.txt"):
        if row["SUBTYPE"] not in SYSTEMIC_SUBTYPES:
            continue
        starts = starts_by_patient[row["PATIENT_ID"]]
        start_day = int(row["START_DATE"])
        starts[row["AGENT"]] = min(start_day, starts.get(row["AGENT"], start_day))

    agents_by_patient = {}
    for patient_id, starts in starts_by_patient.items():
        ordered = sorted(starts, key=lambda agent: (starts[agent], agent))
        first_day = starts[ordered[0]]
        first_line_size = sum(starts[agent] == first_day for agent in ordered)
        agents_by_patient[patient_id] = (ordered, first_line_size)
    return agents_by_patient


def load_cohort(raw_dir: Path) -> list[Patient]:
    """The analysable MSK-CHORD cohort as Patient records (split left as 'test').

    Keeps patients with exactly one cancer type (90 have two, which the one-type record cannot express)
    and with known sex, age and stage. Sites flagged 'Unknown' are treated as absent.
    """
    cancer_types_by_patient = defaultdict(set)
    for row in read_cbioportal_table(raw_dir / "data_clinical_sample.txt"):
        cancer_types_by_patient[row["PATIENT_ID"]].add(row["CANCER_TYPE"])
    agents_by_patient = load_agents_by_patient(raw_dir)

    cohort = []
    for row in read_cbioportal_table(raw_dir / "data_clinical_patient.txt"):
        cancer_types = cancer_types_by_patient[row["PATIENT_ID"]]
        if (
            len(cancer_types) != 1
            or "Unknown" in (row["GENDER"], row["STAGE_HIGHEST_RECORDED"])
            or not row["CURRENT_AGE_DEID"]
        ):
            continue
        agents, first_line_size = agents_by_patient.get(row["PATIENT_ID"], ([], 0))
        cohort.append(
            Patient(
                patient_id=row["PATIENT_ID"],
                source="msk-chord",
                split="test",
                cancer_type=next(iter(cancer_types)),
                sex=row["GENDER"],
                age=int(row["CURRENT_AGE_DEID"]),
                smoking=row["SMOKING_PREDICTIONS_3_CLASSES"],
                stage=row["STAGE_HIGHEST_RECORDED"],
                registry_entries=int(row["NUM_ICDO_DX"]),
                biomarkers={
                    label: row[column] for label, column in BIOMARKER_COLUMNS.items() if row[column]
                },
                prior_medication=row["PRIOR_MED_TO_MSK"],
                agents=agents,
                first_line_size=first_line_size,
                os_status=row["OS_STATUS"].split(":")[1],
                os_months=float(row["OS_MONTHS"]),
                metastatic_sites=sorted(
                    site for site, column in SITE_COLUMNS.items() if row[column] == "Yes"
                ),
            )
        )
    return cohort


def group_by(items, key) -> dict:
    groups = defaultdict(list)
    for item in items:
        groups[key(item)].append(item)
    return dict(sorted(groups.items()))


def select_subset(cohort: list[Patient], seed: int, per_group: int) -> list[Patient]:
    """`per_group` random patients for every (cancer type, os_status): balanced LIVING/DECEASED, equal per type.

    Uses the most frequent cancer types, as many as the cohort has up to five.
    """
    rng = random.Random(seed)
    frequent_types = [t for t, _ in Counter(p.cancer_type for p in cohort).most_common(5)]
    groups = group_by(cohort, key=lambda p: (p.cancer_type, p.os_status))
    subset = [
        p
        for (cancer_type, _), members in groups.items()
        if cancer_type in frequent_types
        for p in rng.sample(members, per_group)
    ]
    return sorted(subset, key=lambda p: p.patient_id)


def shares(values) -> dict[str, float]:
    """Relative frequency of each distinct value, rounded to four decimals."""
    counts = Counter(values)
    return {str(value): round(count / len(values), 4) for value, count in sorted(counts.items())}


def describe_stratum(patients: list[Patient]) -> dict:
    """Everything the synthesizer needs about one (cancer type, stage) group."""
    site_counts = [len(p.metastatic_sites) for p in patients]
    regimens = Counter(tuple(p.agents[: p.first_line_size]) for p in patients)
    listed_regimens = [
        (agents, n)
        for agents, n in regimens.most_common(MAX_REGIMENS_PER_STRATUM)
        if n >= MIN_GROUP_PATIENTS
    ]

    os_months = {}
    for status, members in group_by(patients, key=lambda p: p.os_status).items():
        cut_points = statistics.quantiles(
            [p.os_months for p in members], n=OS_QUANTILE_GROUPS, method="inclusive"
        )
        os_months[status] = [round(cut_point, 1) for cut_point in cut_points]

    deceased_rate = {}
    for site_band, members in group_by(
        patients, key=lambda p: find_band(len(p.metastatic_sites), SITE_COUNT_BANDS)
    ).items():
        deceased_rate[site_band] = {
            "n": len(members),
            "rate": round(sum(p.os_status == "DECEASED" for p in members) / len(members), 4),
        }

    return {
        "n": len(patients),
        "site_count": shares(site_counts),
        "site_rate": {
            site: round(sum(site in p.metastatic_sites for p in patients) / len(patients), 4)
            for site in SITE_COLUMNS
        },
        "first_line_regimens": [{"agents": list(agents), "n": n} for agents, n in listed_regimens],
        "deceased_rate": deceased_rate,
        "os_months_quantiles": os_months,
    }


def describe_cancer_type(patients: list[Patient]) -> dict:
    ages = [p.age for p in patients]
    biomarkers = {}
    for label in BIOMARKER_COLUMNS:
        reported = [p.biomarkers[label] for p in patients if label in p.biomarkers]
        if len(reported) < MIN_GROUP_PATIENTS:
            reported = []
        biomarkers[label] = {
            "reported_rate": round(len(reported) / len(patients), 4),
            "values": shares(reported) if reported else {},
        }
    return {
        "n": len(patients),
        "sex": shares([p.sex for p in patients]),
        "age": {"mean": round(statistics.mean(ages), 1), "sd": round(statistics.stdev(ages), 1)},
        "smoking": shares([p.smoking for p in patients]),
        "stage": shares([p.stage for p in patients]),
        "registry_entries": shares(
            [min(p.registry_entries, REGISTRY_ENTRIES_CAP) for p in patients]
        ),
        "prior_medication": shares([p.prior_medication for p in patients]),
        "biomarkers": biomarkers,
        "by_stage": {
            stage: describe_stratum(members)
            for stage, members in group_by(patients, key=lambda p: p.stage).items()
        },
    }


def build_profile(cohort: list[Patient]) -> dict:
    """Aggregate statistics of the full cohort. Counts and rates only: no patient-level rows."""
    return {
        "about": "Aggregate profile of the MSK-CHORD public release; input of scripts/synthesize.py. No patient-level data.",
        "cohort_size": len(cohort),
        "age_limits": list(AGE_LIMITS),
        "site_count_bands": {label: list(limits) for label, limits in SITE_COUNT_BANDS.items()},
        "os_quantile_levels": [
            round(i / OS_QUANTILE_GROUPS, 2) for i in range(1, OS_QUANTILE_GROUPS)
        ],
        "cancer_types": {
            cancer_type: describe_cancer_type(members)
            | {"frequency": round(len(members) / len(cohort), 4)}
            for cancer_type, members in group_by(cohort, key=lambda p: p.cancer_type).items()
        },
    }


def write_subset(subset: list[Patient], out_dir: Path, seed: int, per_group: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("P-*.md"):
        stale.unlink()
    for patient in subset:
        (out_dir / f"{patient.patient_id}.md").write_text(render_record(patient))

    by_type = group_by(subset, key=lambda p: p.cancer_type)
    type_lines = "\n".join(
        f"| {cancer_type} | {sum(p.os_status == 'LIVING' for p in members)} | {sum(p.os_status == 'DECEASED' for p in members)} |"
        for cancer_type, members in by_type.items()
    )
    (out_dir / "README.md").write_text(
        f"""# msk-chord-mini

{len(subset)} real, de-identified patients from the public MSK-CHORD release (Jee et al., *Nature* 2024,
cBioPortal study `msk_chord_2024`), one Markdown file each, all `split: test`.
The record shape is defined in `data/README.md`.

| Cancer type | LIVING | DECEASED |
|---|---|---|
{type_lines}

## Provenance and license
- Source: https://www.cbioportal.org/study/summary?id=msk_chord_2024, Memorial Sloan Kettering Cancer Center.
- License: **CC BY-NC-ND 4.0**. Non-commercial research only, no redistribution, and no derivative may be published.
  This folder stays inside the private OncoLens repository.
- Values are verbatim from the release; only the layout changed (`os_months` is printed to 0.1 month).

## How it was built
Eligible patients have exactly one cancer type and known sex, age and stage. For every cancer type,
{per_group} LIVING and {per_group} DECEASED patients were drawn at random with seed `{seed}`.
- `metastatic_sites`: the NLP tumour-site flags that are `Yes` (`Unknown` counts as absent).
- `Systemic agents, in order`: anti-cancer agents (chemo, hormone, targeted, biologic, immuno, investigational)
  by first start day. These come from the full follow-up, so they can reflect later disease course.
- `Biomarkers`: PD-L1 history, HR, HER2 and Gleason score, only where reported.

## Regenerate
`uv run scripts/extract_chord.py <raw msk_chord_2024 dir> --seed {seed} --per-group {per_group}`
"""
    )


def write_profile(profile: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(profile, indent=1) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "raw_dir", type=Path, help="extracted msk_chord_2024 directory (cBioPortal format)"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="OncoLens data/ directory (default: repository data/)",
    )
    parser.add_argument("--seed", type=int, default=2024, help="seed of the stratified draw")
    parser.add_argument(
        "--per-group", type=int, default=6, help="patients per (cancer type, LIVING|DECEASED)"
    )
    args = parser.parse_args()

    cohort = load_cohort(args.raw_dir)
    subset = select_subset(cohort, args.seed, args.per_group)
    write_subset(subset, args.data_dir / "msk-chord-mini", args.seed, args.per_group)
    write_profile(build_profile(cohort), args.data_dir / "synthetic-chord" / "profile.json")
    print(
        f"cohort {len(cohort)} patients -> {len(subset)} written to msk-chord-mini, profile.json updated"
    )


if __name__ == "__main__":
    main()
