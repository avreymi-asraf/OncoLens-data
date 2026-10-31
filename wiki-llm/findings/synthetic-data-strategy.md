---
type: finding
topic: synthetic-data-strategy
status: active
confidence: initial
supporting_experiments: []
updated: 2026-10-31
---
# Finding: Synthetic data strategy for OncoLens

> Raw: [[datasets/synthea]], [[datasets/synthetic-ehr-generators]], [[datasets/synthetic-clinical-notes]], [[datasets/mdclone-israel]], [[literature/synthetic-ehr-privacy-audits]], [[literature/damico-2023-synthetic-hematology]]

## Summary Thesis
Synthetic data serves **three different jobs**, and each needs a different generator. Mixing them up is the main risk.

| Job | What it needs | Generator | Where it runs | Leaves hospital? |
|---|---|---|---|---|
| **A. Code & CI fixtures** (zero PHI, schema-correct) | Right schema, plausible values; no clinical signal needed | Synthea (FHIR → MEDS/OMOP) or a hand-written schema faker shaped like Hadassah tables | anywhere | yes |
| **B. Shareable research twin** (collaborators, reviewers, students outside the hospital) | Fidelity + utility + audited privacy | CEHR-GPT / HALO (timelines), TabDDPM / CTGAN (baseline table), MDClone if available; on-prem LLM for Hebrew notes | **inside Hadassah only** | only after per-record privacy audit and approval |
| **C. Augmentation** (rare subgroups, class imbalance) | Conditional generation that preserves outcome relationships | Conditional tabular GAN/VAE (D'Amico-style), conditional CEHR-GPT | inside Hadassah | no |

## Why Synthea alone is not enough
It generates guideline-concordant care and does not model care deviations (Chen 2019); its lung module has no biomarker-driven therapy. Any model trained on it learns Synthea's rules, not oncology. It is the right tool for job A only.

## Validation protocol (proposed, to agree with supervisors)
1. **Fidelity:** marginals, pairwise correlations, code co-occurrence, Kaplan–Meier curves by stage (D'Amico SAFE-style "clinical fitness").
2. **Utility:** train-on-synthetic / test-on-real (TSTR) vs train-on-real for the chosen `G1` target; report the gap.
3. **Privacy:** per-record membership-inference and attribute-inference audits, distance-to-closest-record / NNDR, against a held-out real set (not only aggregate scores).
4. **Text:** for Hebrew notes, check that no real spans are copied (n-gram overlap with source) before release.

## Constraints
- MoH 2026 (reported in press, credibility C — confirm the circular): no patient data into public generative-AI interfaces → note generation uses on-prem models either way, per AGENT.md.
- No Israeli guidance specific to synthetic data was found; release decisions go to the supervisors and the Helsinki committee.
- MSK-CHORD is CC BY-NC-ND — do not publish synthetic derivatives of it.

## Open Hypotheses
- `G4`: does a survival model trained on an in-hospital synthetic twin keep its c-index on real Hadassah data? (No prior oncology study tests prediction on MDClone-type derivatives.)
