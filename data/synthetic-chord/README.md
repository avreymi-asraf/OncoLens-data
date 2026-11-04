# synthetic-chord

300 synthetic patients (240 `train`, 60 `test`) in the record shape of `data/README.md`,
with `source: synthetic-chord` and ids `S-000001...`. They are a stand-in for MSK-CHORD for pipelines, prompts and baselines.

## What it is
A schema faker ("job A" of `wiki-llm/findings/synthetic-data-strategy.md`). Every patient is sampled from the
aggregate counts and rates in `profile.json` (computed from the full MSK-CHORD cohort of 24,857 patients),
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
`uv run scripts/synthesize.py --seed 2024` rewrites the records. Same profile and seed give byte-identical files.
