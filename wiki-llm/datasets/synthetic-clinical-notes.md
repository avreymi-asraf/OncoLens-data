---
type: dataset
node_id: ds:synthetic-clinical-notes
title: "Synthetic clinical-note corpora (Asclepius, longitudinal LLM notes, keyphrase-based)"
maintainer: "various"
url: "https://arxiv.org/html/2309.00237v4"
access: open
license: "per release"
n_patients: "Asclepius 158K notes; longitudinal pipeline 70 patients × 20–50 notes"
time_span: "n/a"
modalities: [notes]
oncology_coverage: "general (not oncology-specific)"
language: "en (SPARCLING: de)"
data_model: "free text (+ instruction/answer pairs)"
supports_targets: []
resemblance_to_hadassah: low
credibility: A (ACL Findings 2024; Sci Rep 2024) / B (arXiv preprints)
primary_doc_read: "no — abstracts and summaries"
updated: 2026-10-31
---
# Synthetic clinical-note corpora

| Corpus | What | Take-away |
|---|---|---|
| **Asclepius** (Kweon et al., ACL Findings 2024) | 158K synthetic notes generated from PMC-Patients case reports + instruction/answer pairs; 7B/13B models | Models trained on synthetic notes ≈ models trained on real notes for many clinical tasks |
| **Longitudinal synthetic notes** (arXiv 2606.26879) | 70 synthetic patients, 20–50 notes each, whole hospital journey, multi-level validation | Shows how to keep a patient's notes consistent over time — the hard part for oncology timelines |
| **Sarkar et al., Sci Rep 2024** — "De-identification is not enough" | Keyphrase → GPT-3.5 synthetic notes; shows membership inference against de-identified notes | Argument for synthetic over de-identified text when notes must leave the hospital |
| **SPARCLING** (NeurIPS 2026 listing) | Synthetic German discharge letters with exact PHI spans | Template for building a **Hebrew** de-identification training set |
| **Vakili et al. 2025** (arXiv 2502.14677) | Domain-adapted LLM generates notes, machine-annotated PHI, train NER | Small drop vs. real data |

No Hebrew synthetic clinical corpus was found.

## Sources
- [Asclepius](https://arxiv.org/html/2309.00237v4), [longitudinal notes](https://arxiv.org/abs/2606.26879), [Sarkar 2024](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11607336/), [SPARCLING](https://neurips.cc/virtual/2026/177229), [Vakili 2025](https://papers.cool/arxiv/2502.14677)
