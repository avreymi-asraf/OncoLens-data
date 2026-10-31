---
type: literature
node_id: lit:jee-2024-msk-chord
title: "Automated real-world data integration improves cancer outcome prediction (MSK-CHORD)"
year: 2024
tags: ["oncology", "real-world-data", "nlp", "survival", "clinicogenomics"]
updated: 2026-10-31
---
# Jee et al., Nature 636:728–736 (2024) — MSK-CHORD

## One-Line Thesis
Adding NLP-derived features (sites of disease, progression, receptor status) to structured + genomic data improves overall-survival prediction over stage or genomics alone across 5 cancers (c-index up to 0.83), and generalizes to an external multi-institution cohort.

## Details read in full text
- NLP: RoBERTa (progression), ClinicalBERT (tumour sites), BERT (cancer presence), Clinical-Longformer (prior treatment, HER2/HR); rule-based for smoking, PD-L1, Gleason, MMR. All AUC > 0.9; precision/recall > 0.78. Labels from GENIE BPC PRISSMM curation (MSK-BPC: 3,202 pts, 38,719 radiology reports); clinicians found many original curation labels wrong in discrepant cases.
- Outcome: OS from cohort entry (= sequencing report date), right-censored, **left truncation** for immortal-time bias.
- Models: random survival forest (1,000 trees); OncoCast (elastic-net Cox + RF residual correction). radLongformer (6-month mortality from CT reports) added nothing.
- External validation: non-MSK GENIE BPC. Consistent except tumour markers in CRC/pancreas/breast.
- Code: GitHub org `clinical-data-mining`. Data: cBioPortal, CC BY-NC-ND 4.0.

## Reusable Ingredients for Our Lab
* **Mechanism:** time zero + left truncation; NLP-derived disease sites as features; RSF baseline; external validation design.
* **Target match:** `G1` (target definition — OS is the proven target), `G3` (external validation), `G5` (Hebrew NLP for sites/progression).

## Limitations & Failure Modes
Sequencing-based cohort entry (selection bias); no comorbidities/symptoms; single catchment.

## Linked Experiments
* none yet
