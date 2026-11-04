---
type: dataset
node_id: ds:msk-chord-mini
title: "msk-chord-mini (60 real MSK-CHORD patients as Markdown records)"
maintainer: "OncoLens (subset of Memorial Sloan Kettering Cancer Center data)"
url: "data/msk-chord-mini/ (this repository); source https://www.cbioportal.org/study/summary?id=msk_chord_2024"
access: open
license: "CC BY-NC-ND 4.0 (inherited from MSK-CHORD; private repository only)"
n_patients: "60"
time_span: "MSK-IMPACT era (see msk-chord)"
modalities: [structured, registry, notes-derived]
oncology_coverage: "NSCLC, breast, colorectal, prostate, pancreatic: 12 patients each (6 LIVING, 6 DECEASED)"
language: "en"
data_model: "custom Markdown record, data/README.md"
supports_targets: [overall-survival, metastasis]
resemblance_to_hadassah: medium-high (same as msk-chord)
credibility: A (values verbatim from the Nature 2024 public release)
primary_doc_read: "yes — cBioPortal files and codebook; paper via [[datasets/msk-chord]]"
updated: 2026-11-04
---
# msk-chord-mini

## What it is
A seeded, stratified subset of [[datasets/msk-chord]]: 60 de-identified patients, 6 LIVING and 6 DECEASED per cancer type, all `split: test`. One Markdown file per patient in the record shape of `data/README.md`; outcomes (`os_status`, `os_months`, `metastatic_sites`) sit in the frontmatter and never in the body. Built by `scripts/extract_chord.py` from the cBioPortal files (seed 2024), which also writes the aggregate `data/synthetic-chord/profile.json` used by [[datasets/synthetic-chord]].

## Access path
Regenerate with `uv run scripts/extract_chord.py <raw msk_chord_2024 dir>`; the raw release is a public download from cBioPortal. The folder README states provenance and the seed.

## Why it matters for OncoLens
- A real-data **test set** in the final record format, so a pipeline built on [[datasets/synthetic-chord]] can be scored on real patients before Hadassah access.
- Small by design: 60 patients give coarse estimates (a 95% interval on AUC is wide). Use it as a smoke test and sanity check, not for model selection.

## Caveats
- **ND license**: no redistribution, no published derivatives; the repository must stay private.
- Eligibility: exactly one cancer type (90 two-type patients are dropped) and known sex, age, stage. Sites flagged `Unknown` count as absent.
- `Systemic agents, in order` comes from the full follow-up (all anti-cancer agents by first start day), so it can reflect later disease course: do not treat it as baseline information in a prediction-at-diagnosis task.
- `os_months` is printed to 0.1 month; cohort entry is the sequencing date (selection bias towards advanced disease, see [[datasets/msk-chord]]).

## Sources
- [MSK-CHORD on cBioPortal](https://www.cbioportal.org/study/summary?id=msk_chord_2024) — A
- [[datasets/msk-chord]] — A
