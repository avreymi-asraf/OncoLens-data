#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Write the synthetic twin of MSK-CHORD: schema-faithful patient records sampled from aggregate statistics.

Where it fits: this is "job A" of wiki-llm/findings/synthetic-data-strategy.md, a schema faker.
It reads ONLY data/synthetic-chord/profile.json (written by scripts/extract_chord.py from the full cohort)
and never sees patient records or the raw release. Records are rendered with `render_record` from
extract_chord.py, so real and synthetic files share one shape (data/README.md).

Each patient is drawn top-down, so the outcomes carry the real conditional signal:
  cancer type -> sex, age, smoking, stage, registry entries, prior medication, biomarkers
  (cancer type, stage) -> number of metastatic sites -> which sites
  (cancer type, stage, site-count band) -> LIVING or DECEASED -> os_months from that (type, stage, status) distribution
  (cancer type, stage) -> first-line regimen
It is NOT a privacy-preserving release of the real data and not a fitted generative model.

Usage:
    uv run scripts/synthesize.py
    uv run scripts/synthesize.py --seed 7 --n-train 240 --n-test 60
"""

import argparse
import bisect
import json
import random
from pathlib import Path

from extract_chord import DATA_DIR, Patient, find_band, render_record

SYNTHETIC_PREFIX = "S"


def draw(rng: random.Random, shares: dict[str, float]) -> str:
    """One key of `shares`, chosen with probability proportional to its value."""
    return rng.choices(list(shares), weights=list(shares.values()))[0]


def draw_age(rng: random.Random, age: dict[str, float], limits: list[int]) -> int:
    """Normal age with the cancer type's mean and sd, clipped to the release's age range."""
    return round(min(max(rng.gauss(age["mean"], age["sd"]), limits[0]), limits[1]))


def draw_sites(rng: random.Random, site_rate: dict[str, float], count: int) -> list[str]:
    """`count` distinct sites, each pick weighted by how often the site is involved in this (type, stage)."""
    remaining = dict(site_rate)
    sites = []
    for _ in range(count):
        site = rng.choices(list(remaining), weights=list(remaining.values()))[0]
        sites.append(site)
        del remaining[site]
    return sorted(sites)


def draw_os_months(rng: random.Random, quantiles: list[float], levels: list[float]) -> float:
    """Inverse-CDF draw: a uniform level between the lowest and highest published quantile, interpolated linearly."""
    level = rng.uniform(levels[0], levels[-1])
    upper = min(bisect.bisect_left(levels, level), len(levels) - 1)
    lower = max(upper - 1, 0)
    if upper == lower:
        return quantiles[lower]
    fraction = (level - levels[lower]) / (levels[upper] - levels[lower])
    return quantiles[lower] + fraction * (quantiles[upper] - quantiles[lower])


def sample_patient(rng: random.Random, profile: dict, patient_id: str, split: str) -> Patient:
    cancer_type = draw(rng, {name: described["frequency"] for name, described in profile["cancer_types"].items()})
    described = profile["cancer_types"][cancer_type]
    stage = draw(rng, described["stage"])
    stratum = described["by_stage"][stage]

    biomarkers = {
        label: draw(rng, biomarker["values"])
        for label, biomarker in described["biomarkers"].items()
        if rng.random() < biomarker["reported_rate"]
    }
    sites = draw_sites(rng, stratum["site_rate"], count=int(draw(rng, stratum["site_count"])))
    site_band = find_band(len(sites), {label: tuple(limits) for label, limits in profile["site_count_bands"].items()})
    os_status = "DECEASED" if rng.random() < stratum["deceased_rate"][site_band]["rate"] else "LIVING"
    regimens = stratum["first_line_regimens"]
    first_line = rng.choices(regimens, weights=[regimen["n"] for regimen in regimens])[0]["agents"]

    return Patient(
        patient_id=patient_id,
        source="synthetic-chord",
        split=split,
        cancer_type=cancer_type,
        sex=draw(rng, described["sex"]),
        age=draw_age(rng, described["age"], profile["age_limits"]),
        smoking=draw(rng, described["smoking"]),
        stage=stage,
        registry_entries=int(draw(rng, described["registry_entries"])),
        biomarkers=biomarkers,
        prior_medication=draw(rng, described["prior_medication"]),
        agents=first_line,
        first_line_size=len(first_line),
        os_status=os_status,
        os_months=draw_os_months(rng, stratum["os_months_quantiles"][os_status], profile["os_quantile_levels"]),
        metastatic_sites=sites,
    )


def write_corpus(patients: list[Patient], out_dir: Path, seed: int, profile: dict) -> None:
    for stale in out_dir.glob(f"{SYNTHETIC_PREFIX}-*.md"):
        stale.unlink()
    for patient in patients:
        (out_dir / f"{patient.patient_id}.md").write_text(render_record(patient))

    n_train = sum(p.split == "train" for p in patients)
    (out_dir / "README.md").write_text(
        f"""# synthetic-chord

{len(patients)} synthetic patients ({n_train} `train`, {len(patients) - n_train} `test`) in the record shape of `data/README.md`,
with `source: synthetic-chord` and ids `S-000001...`. They are a stand-in for MSK-CHORD for pipelines, prompts and baselines.

## What it is
A schema faker ("job A" of `wiki-llm/findings/synthetic-data-strategy.md`). Every patient is sampled from the
aggregate counts and rates in `profile.json` (computed from the full MSK-CHORD cohort of {profile['cohort_size']:,} patients),
top-down: cancer type, demographics and stage, then metastatic sites, then survival status given
(cancer type, stage, number of sites), then `os_months` from the matching distribution, then a first-line regimen.
Outcomes therefore carry the real conditional signal of those variables, and only of those variables:
age, sex, smoking, biomarkers and prior medication are independent of the outcomes here.

## What it is not
- Not a model fitted on patient records, and **not a privacy-preserving release**. `profile.json` holds only counts and
  rates (no row-level data, no extremes, groups under 20 patients are not listed), but no formal privacy guarantee is made.
- Not clinically faithful beyond the stated conditionals: treatment is the first-line regimen only,
  `os_months` is drawn between the 5th and 95th percentile of the real distribution, registry entries are capped at 4.
- Not releasable. The profile derives from MSK-CHORD (**CC BY-NC-ND 4.0**); whether sampling from its aggregates
  counts as a derivative is undecided. Keep this folder inside the private repository until the supervisors decide.

## Regenerate
`uv run scripts/extract_chord.py <raw msk_chord_2024 dir>` refreshes `profile.json`;
`uv run scripts/synthesize.py --seed {seed}` rewrites the records. Same profile and seed give byte-identical files.
"""
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR, help="OncoLens data/ directory (default: repository data/)")
    parser.add_argument("--seed", type=int, default=2024)
    parser.add_argument("--n-train", type=int, default=240)
    parser.add_argument("--n-test", type=int, default=60)
    args = parser.parse_args()

    out_dir = args.data_dir / "synthetic-chord"
    profile = json.loads((out_dir / "profile.json").read_text())
    rng = random.Random(args.seed)
    splits = ["train"] * args.n_train + ["test"] * args.n_test
    patients = [sample_patient(rng, profile, f"{SYNTHETIC_PREFIX}-{number:06d}", split) for number, split in enumerate(splits, start=1)]
    write_corpus(patients, out_dir, args.seed, profile)
    print(f"{len(patients)} synthetic patients written to {out_dir}")


if __name__ == "__main__":
    main()
