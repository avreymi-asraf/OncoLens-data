---
type: dataset
node_id: ds:aacr-genie-bpc
title: "AACR Project GENIE — Biopharma Collaborative (BPC)"
maintainer: "AACR; curation at MSK, DFCI, Vanderbilt, UHN (+UCSF in some releases)"
url: "https://www.aacr.org/professionals/research/aacr-project-genie/bpc/"
access: credentialed-DUA
license: "Synapse account + per-release terms; consortium releases restricted"
n_patients: "NSCLC 1,846; CRC 1,485 (public 2.0); Breast 1.0-public listed; more cohorts in consortium releases"
time_span: "unknown"
modalities: [structured, genomic, curated-notes]
oncology_coverage: "NSCLC, CRC, breast (public); other cohorts in consortium releases unverified"
language: "en"
data_model: "PRISSMM curation model"
supports_targets: [overall-survival, progression, treatment-response, metastasis]
resemblance_to_hadassah: medium
credibility: A (AACR, peer-reviewed QA paper)
primary_doc_read: "partial — AACR/MSK pages, genieBPC vignette summaries, QA paper abstract"
updated: 2026-10-31
---
# AACR GENIE BPC

## What it is
Multi-institution, **manually curated** real-world clinicogenomic cohorts. Curation follows **PRISSMM** (Pathology, Radiology/Imaging, Signs/Symptoms, Medical oncologist assessment): one record per pathology report, per imaging report, per oncologist assessment, from the first BPC cancer diagnosis on. <10% of variables come from tumour registries; the rest are abstracted from the EHR. QA by double curation showed reliable inter-curator agreement. R package `genieBPC::pull_data_synapse()`.

## Why it matters
- **Curation schema to copy.** PRISSMM is the de facto label schema for real-world progression / response. MSK-CHORD's NLP models were trained on these labels. If Hadassah builds a small gold-standard label set using PRISSMM definitions, results become directly comparable with MSK-CHORD and BPC.
- **External validation cohort** used by MSK-CHORD itself.

## Sources
- [AACR BPC page](https://www.aacr.org/professionals/research/aacr-project-genie/bpc/) — A
- [MSK BPC page](https://www.mskcc.org/departments/epidemiology-biostatistics/biostatistics/project-genie-bpc-genomics-evidence-neoplasia-information-exchange-biopharma-collaborative) — B
- [Scalable QA process paper (PMC8863125)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8863125/) — A
- [genieBPC data-structure vignette](https://genie-bpc.r-universe.dev/genieBPC/doc/clinical_data_structure_vignette.html) — B
