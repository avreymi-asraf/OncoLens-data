---
type: literature
node_id: lit:theodorou-2023-halo
title: "HALO: Synthesize high-dimensional longitudinal EHR via hierarchical autoregressive language model"
year: 2023
tags: ["synthetic-data", "longitudinal-ehr", "generative"]
updated: 2026-10-31
---
# Theodorou, Xiao, Sun — Nat Commun 14:5305 (2023)

## One-Line Thesis
A visit-level + code-level autoregressive transformer generates full longitudinal code sequences (d > 10K codes) with R² > 0.9 to real statistics; models trained on HALO data reach AUROC 0.938 vs 0.943 on real data.

## Reusable Ingredients
* Generator for **coded visit sequences** (diagnoses, procedures, meds) — fits a structured Hadassah extract. Trained on MIMIC-III and outpatient claims.
* Target match: `G4`.

## Limitations
Codes only (no continuous labs, no time gaps between visits, no text). Authors' own numbers; no independent replication found. Privacy risk must be audited separately.
