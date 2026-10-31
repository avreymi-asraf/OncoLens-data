---
type: literature
node_id: lit:damico-2023-synthetic-hematology
title: "Synthetic Data Generation by AI to Accelerate Research and Precision Medicine in Hematology"
year: 2023
tags: ["synthetic-data", "oncology", "gan", "survival"]
updated: 2026-10-31
---
# D'Amico et al., JCO Clin Cancer Inform 7 (2023) — Humanitas

## One-Line Thesis
A conditional tabular WGAN-GP generates synthetic MDS (2,043 pts) and AML (1,002 pts) patients with clinical + genomic + treatment + outcome data; SAFE validation (clinical fitness 92%, genomic fitness 89%, NNDR privacy) shows survival estimates replicate; 300% augmentation of a 944-patient cohort.

## Reusable Ingredients
* The **only oncology-specific, survival-validated synthetic-data study found**. Its validation (statistical fidelity + clinical relevance incl. survival curves + NNDR privacy) is a ready template for validating a Hadassah synthetic cohort. Follow-ups: TVAE/GPT variants (ASH 2024: c-index 0.85 real vs 0.84 synthetic), federated version (4,427 MDS pts).
* Target match: `G4`.

## Limitations
One row per patient (not a visit timeline); haematology only; full text not read.
