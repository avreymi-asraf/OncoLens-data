---
type: dataset
node_id: ds:israel-national-cancer-registry
title: "Israel National Cancer Registry (INCR)"
maintainer: "Israel Ministry of Health (ICDC)"
url: "https://ghdx.healthdata.org/organizations/israel-national-cancer-registry"
access: application
license: "MoH approval; individual-level access requires ethics + MoH approvals (procedure not found online)"
n_patients: "Entire Israeli population; cancer cases since 1960"
time_span: "1960–present; mandatory reporting since 1982"
modalities: [registry]
oncology_coverage: "all reportable cancers"
language: "he / coded"
data_model: "registry (ICD-O-3 topography/morphology, stage)"
supports_targets: [overall-survival]
resemblance_to_hadassah: medium
credibility: A (peer-reviewed completeness study) / B (registry profiles)
primary_doc_read: "no — abstracts and profiles only"
updated: 2026-10-31
---
# Israel National Cancer Registry (INCR)

## What it is
National population-based registry, established 1960, reporting mandatory since 1982. Holds demographics, diagnosis, diagnosis date, stage, and supports **linkage to national population databases via the national ID** (so vital status / death date is available). A 2021 validation estimated completeness at **93.7%** overall, **96.8%** for invasive solid tumours, **88.0%** for haematopoietic tumours.

## Why it matters
- **Ground truth for survival outcomes.** Hospital EMRs miss deaths that happen outside the hospital. If Hadassah's death dates are incomplete, INCR / population-registry linkage is the standard fix for an overall-survival target.
- **Cohort definition:** registry ICD-O-3 codes are a cleaner definition of "cancer patient" than EMR diagnosis codes.
- **Aggregate benchmarks:** published incidence tables let us check that Hadassah cohort statistics are plausible.

## Caveats
- No online data-request procedure was found (EN or HE searches). Ask the supervisors / MoH ICDC.
- Haematological malignancies are less complete (88%).

## Sources
- [Completeness & timeliness assessment (Univ. Haifa CRIS)](https://cris.haifa.ac.il/en/publications/an-assessment-of-the-completeness-and-timeliness-of-the-israel-na/) — A
- [IMAJ article using INCR](https://ima.org.il/MedicineIMAJ/Article.aspx?aId=4812) — A
- [GHDx registry entry](https://ghdx.healthdata.org/organizations/israel-national-cancer-registry) — B
