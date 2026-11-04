---
type: dataset
node_id: ds:synthetic-chord
title: "synthetic-chord (schema-faithful synthetic twin of MSK-CHORD)"
maintainer: "OncoLens"
url: "data/synthetic-chord/ (this repository)"
access: method/tool
license: "unresolved: derived from CC BY-NC-ND 4.0 aggregates; keep private"
n_patients: "300 (240 train, 60 test)"
time_span: "not modelled"
modalities: [structured]
oncology_coverage: "NSCLC, breast, colorectal, prostate, pancreatic, in real cohort proportions"
language: "en"
data_model: "custom Markdown record, data/README.md"
supports_targets: [overall-survival, metastasis]
resemblance_to_hadassah: low (a pipeline fixture with real conditional rates, not a clinical twin)
credibility: C (generated; validated only against its own profile)
primary_doc_read: "no — generated data"
updated: 2026-11-04
---
# synthetic-chord

## What it is
"Job A" of [[findings/synthetic-data-strategy]]: a schema faker. `scripts/synthesize.py` reads only `data/synthetic-chord/profile.json` (counts and rates over the full [[datasets/msk-chord]] cohort, computed by `scripts/extract_chord.py`) and samples 240 `train` plus 60 `test` patients, seeded and byte-for-byte reproducible, in the same record shape as [[datasets/msk-chord-mini]].

Sampling is top-down: cancer type, then demographics, stage and biomarkers, then the number and identity of metastatic sites given (type, stage), then LIVING/DECEASED given (type, stage, site-count band), then `os_months` from the real (type, stage, status) distribution, then a first-line regimen. Metastatic burden, stage and cancer type therefore drive the outcomes as they do in the real cohort (deceased rate 0.24 for stage 1-3 colorectal up to 0.80 for stage 4 pancreatic; far higher with 3+ sites). Age, sex, smoking, biomarkers and prior medication are independent of the outcomes: in the real data age shifts the deceased rate by only a few points within a type and stage.

## Access path
`uv run scripts/synthesize.py` (after `extract_chord.py` has refreshed the profile). 30,000 synthetic patients reproduce the profile's deceased rate per (type, stage) to within about 0.02.

## Why it matters for OncoLens
- Gives the pipeline, prompts and baselines a `train` split with learnable signal before any Hadassah data is available, and a `test` split to rehearse evaluation.
- The learnable signal is exactly the profile's: a model can at best rediscover stage, cancer type and site count. Do not read its scores as evidence about real clinical prediction; compare against [[datasets/msk-chord-mini]].

## Caveats
- **Not a privacy-preserving release** and not a fitted generative model; the profile omits extremes and groups under 20 patients but carries no formal guarantee.
- **ND license**: whether aggregates-derived records count as a derivative of MSK-CHORD is undecided; keep inside the private repository (see [[datasets/msk-chord]], Caveats).
- Treatment is the first-line regimen only; `os_months` spans the 5th to 95th percentile of the real distribution; registry entries are capped at 4; the 0-site stage-4 groups are small (about 20 to 50 patients), so their rates are noisy.

## Sources
- [[findings/synthetic-data-strategy]] — B
- [[datasets/msk-chord]] — A
