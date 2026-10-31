---
type: dataset
node_id: ds:coral-oncology-notes
title: "CORAL — expert-curated oncology reports (PhysioNet)"
maintainer: "UCSF (Sushil et al.)"
url: "https://physionet.org/content/curated-oncology-reports/1.0/"
access: credentialed-DUA
license: "PhysioNet credentialed; DOI 10.13026/v69y-xa45"
n_patients: "40 notes (20 breast, 20 pancreatic)"
time_span: "n/a"
modalities: [notes]
oncology_coverage: "breast, pancreatic"
language: "en"
data_model: "entity/modifier/relation annotations"
supports_targets: [progression, treatment-response, metastasis]
resemblance_to_hadassah: low (tiny, English)
credibility: A (PhysioNet; arXiv 2308.03853)
primary_doc_read: "no — PhysioNet listing summary"
updated: 2026-10-31
---
# CORAL

40 UCSF oncology progress notes with 9,028 entities, 9,986 modifiers, 5,312 relations. Benchmarks GPT-4 zero-shot extraction (BLEU 0.73; 68% accuracy on expert review). **Use:** evaluation set for an oncology information-extraction step (sites, response, progression) — not for training a predictor.

## Sources
- [PhysioNet CORAL](https://physionet.org/content/curated-oncology-reports/1.0/) — A
- [arXiv 2308.03853](https://arxiv.org/abs/2308.03853v3) — A
