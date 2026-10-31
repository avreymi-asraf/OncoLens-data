---
type: literature
node_id: lit:synthetic-ehr-privacy-audits
title: "Privacy of synthetic EHR: membership inference and per-record audits"
year: 2026
tags: ["synthetic-data", "privacy", "membership-inference"]
updated: 2026-10-31
---
# Privacy of synthetic EHR (cluster note)

## One-Line Thesis
Aggregate privacy scores can hide patient-level memorization; synthetic EHR should be audited per record, like LLMs.

## Evidence
- LOGAN (Hayes et al.) — membership inference (MI) against generative models.
- Fidelity & Privacy of Synthetic Medical Data (arXiv 2101.08658) — MI reveals a diagnosis even when that field is absent (HIV example); precision-based risk score.
- Data-holder-side MI audit with contrastive representations (PMC8766950).
- **NeurIPS 2026 position paper**: "Synthetic data generation for EHR should be audited like LLMs" — similarity heuristics hide memorization; inconsistent attacks across four autoregressive EHR generators.
- arXiv 2512.06062 — black-box clustering attack finds leakage via neighbourhood overlap for GANs, VAEs, diffusion and LLM generators, even without memorization.

## Reusable Ingredients
* Before any synthetic Hadassah data leaves the hospital: run MI + attribute-inference + nearest-neighbour (DCR/NNDR) audits per record, on a held-out real set. Target match: `G4`, `G6`.
