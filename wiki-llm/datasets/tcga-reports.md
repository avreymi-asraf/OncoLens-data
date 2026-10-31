---
type: dataset
node_id: ds:tcga-reports
title: "TCGA-Reports (pathology report text) + TCGA/GDC clinical data"
maintainer: "Kefeli & Tatonetti (Columbia); NCI GDC"
url: "https://data.mendeley.com/datasets/hyg5xkznpx/1"
access: open
license: "Open (Mendeley Data); HF mirror gated"
n_patients: "9,523 reports (from 11,010 patients before filtering)"
time_span: "TCGA collection era (years unsourced — verify)"
modalities: [notes, genomic, structured]
oncology_coverage: "TCGA cancer types (count unsourced — verify)"
language: "en"
data_model: "OCR text; GDC clinical model"
supports_targets: [overall-survival]
resemblance_to_hadassah: low
credibility: A (Patterns 2024)
primary_doc_read: "no — PMC summary"
updated: 2026-10-31
---
# TCGA-Reports

OCR-processed pathology reports from TCGA (11,108 downloaded → 9,523 after removing discrepancy forms). Known noise: heterogeneous formats, duplicates, admin text. 6,940 reports have T/N/M ground truth (used in stage-classification studies). With GDC clinical + survival data it supports **text→stage** and **text+genomics→survival** experiments. Low resemblance to a live EMR (one report per patient, no longitudinal course).

## Sources
- [Kefeli et al., Patterns 2024 (PMC10935496)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10935496/) — A
- [Mendeley Data](https://data.mendeley.com/datasets/hyg5xkznpx/1) — A
