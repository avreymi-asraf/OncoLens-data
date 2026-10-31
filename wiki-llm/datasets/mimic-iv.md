---
type: dataset
node_id: ds:mimic-iv
title: "MIMIC-IV (+ MIMIC-IV-Note)"
maintainer: "MIT LCP / Beth Israel Deaconess Medical Center"
url: "https://physionet.org/content/mimic-iv-note/"
access: credentialed-DUA
license: "PhysioNet Credentialed Health Data License 1.5.0; CITI training; DUA"
n_patients: "Notes: 331,794 discharge summaries (145,915 pts); 2,321,355 radiology reports (237,427 pts)"
time_span: "unknown (PhysioNet note page gives no year range)"
modalities: [structured, notes]
oncology_coverage: "incidental — cancer patients among hospital/ED admissions; no staging, no genomics"
language: "en"
data_model: "MIMIC relational; community OMOP and MEDS conversions"
supports_targets: [short-term-mortality, ed-visit-admission, toxicity]
resemblance_to_hadassah: medium (tertiary hospital EMR, but no oncology structure)
credibility: A (PhysioNet official)
primary_doc_read: "yes — PhysioNet MIMIC-IV-Note page"
updated: 2026-10-31
---
# MIMIC-IV / MIMIC-IV-Note

## What it is
De-identified hospital + ICU EHR from BIDMC; `hosp`, `icu` modules; notes in the separate MIMIC-IV-Note (v2.2), linked via `subject_id` / `hadm_id`.

## Why it matters
- Best openly-credentialed **general hospital EHR** for building the pipeline (feature extraction, patient-level splits, time-zero logic) before Hadassah access.
- Oncology sub-cohorts have been built: **CliCARE** (arXiv 2507.22533) made a "Processed MIMIC-Cancer" set of 2,000 cancer patients (top diagnoses: DLBCL, multiple myeloma, AML) — selection criteria not verified.
- Note: when predicting outcomes, some groups **exclude discharge summaries** because they state the outcome — a leakage pattern to remember for Hadassah notes too.

## Caveats
No staging, treatment lines or genomics. DUA terms on sending data to external LLM APIs must be checked (PhysioNet has published guidance on responsible LLM use; not verified here).

## Sources
- [PhysioNet MIMIC-IV-Note](https://physionet.org/content/mimic-iv-note/) — A
- [MIMIC-IV paper (Sci Data)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9810617/) — A
- [CliCARE](https://arxiv.org/pdf/2507.22533) — A (preprint)
