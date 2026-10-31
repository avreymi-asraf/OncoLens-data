---
type: dataset
node_id: ds:ehrshot
title: "EHRSHOT (Stanford) + CLMBR / MOTOR foundation models"
maintainer: "Stanford Shah lab (som-shahlab)"
url: "https://github.com/som-shahlab/ehrshot-benchmark"
access: credentialed-DUA
license: "Non-commercial research usage agreement (Redivis); code Apache-2.0"
n_patients: "6,739 patients; 41.6M events; 921,499 visits"
time_span: "Stanford Medicine longitudinal"
modalities: [structured]
oncology_coverage: "one oncology task (new diagnosis: pancreatic cancer)"
language: "en (codes)"
data_model: "Original, MEDS, and OMOP versions"
supports_targets: [ed-visit-admission, short-term-mortality]
resemblance_to_hadassah: medium (full longitudinal EHR, not ICU-only)
credibility: A (NeurIPS D&B 2023; repo)
primary_doc_read: "yes — GitHub README"
updated: 2026-10-31
---
# EHRSHOT

## What it is
15 few-shot tasks over longitudinal structured EHR: operational (long LOS, 30-day readmission, ICU transfer), 5 lab-value forecasts, 6 new diagnoses (incl. **pancreatic cancer**), chest X-ray findings. Released in **MEDS** and **OMOP** formats. Pretrained **CLMBR-T-base** (141M params, 2.57M patients). Related: **MOTOR** — a time-to-event foundation model (143M params, pretrained on up to 55M patient records) — the right family for survival targets.

## Why it matters
A methods sandbox for **foundation-model / few-shot** approaches over structured EHR, in the same MEDS format OncoLens could adopt. MOTOR's time-to-event pretraining is directly relevant to survival prediction.

## Sources
- [ehrshot-benchmark repo](https://github.com/som-shahlab/ehrshot-benchmark) — A
- [EHRSHOT paper, arXiv 2307.02028](https://arxiv.org/html/2307.02028v3) — A
- [MOTOR, arXiv 2301.03150](https://arxiv.org/pdf/2301.03150) — A
