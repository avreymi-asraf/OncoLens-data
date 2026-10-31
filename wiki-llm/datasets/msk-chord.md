---
type: dataset
node_id: ds:msk-chord
title: "MSK-CHORD (Memorial Sloan Kettering clinicogenomic, NLP-annotated)"
maintainer: "Memorial Sloan Kettering Cancer Center"
url: "https://www.cbioportal.org/study/summary?id=msk_chord_2024"
access: open
license: "CC BY-NC-ND 4.0 (commercial: datarequests@mskcc.org)"
n_patients: "24,950 patients / 25,040 tumours (public); >90,000 internal"
time_span: "MSK-IMPACT era (years unsourced — verify)"
modalities: [structured, genomic, registry, notes-derived]
oncology_coverage: "NSCLC 7,809; breast 5,368; colorectal 5,543; prostate 3,211; pancreatic 3,109"
language: "en"
data_model: "cBioPortal clinical + timeline files; labels follow PRISSMM"
supports_targets: [overall-survival, progression, metastasis, treatment-response]
resemblance_to_hadassah: medium-high (tertiary cancer center, notes-derived features, panel genomics)
credibility: A (Nature 2024, full text read)
primary_doc_read: "yes — Jee et al., Nature 2024 (PMC11655358)"
updated: 2026-10-31
---
# MSK-CHORD

## What it is
Jee et al., *Nature* 636:728 (2024). Structured medications, demographics, tumour registry and MSK-IMPACT genomics, plus **NLP-derived** features: sites of disease, progression, cancer presence, prior outside treatment, HER2/HR status, smoking, Gleason, PD-L1, MMR. 705,241 radiology reports annotated longitudinally for metastatic sites. Published on cBioPortal (`msk_chord_2024`), with timelines.

Survival models: random survival forests; c-index from 0.58 (stage IV pancreatic) to 0.83 (stage I–III breast). Multimodal > stage-only in every cancer type. External validation on the non-MSK part of GENIE BPC. Details: [[literature/jee-2024-msk-chord]].

## Why it matters for OncoLens
- **The closest public analogue of the OncoLens task**: survival / progression prediction from real-world oncology EMR plus genomics plus note-derived features. It is the natural **method-development** and **benchmark** dataset before Hadassah access, and a published baseline to compare against.
- Same building blocks as the Hadassah DataMart (EMR + genomic panel).

## Caveats
- **ND (no-derivatives) license.** Redistributing a modified dataset — including possibly a synthetic dataset trained on it — may breach CC BY-NC-ND. Check before publishing derived data.
- Cohort entry is the **sequencing date** → selection bias towards advanced disease (authors' own limitation).
- No comorbidities or symptoms. New York / New Jersey catchment.
- NLP labels trained on curator labels that were often wrong in discrepant cases — label noise.

## Sources
- [Nature paper, PMC11655358](https://pmc.ncbi.nlm.nih.gov/articles/PMC11655358/) — A
- [Behind the paper](https://communities.springernature.com/posts/msk-chord-an-ai-enabled-24-950-patient-clinicogenomic-dataset-for-cancer-research) — B
- [MSK data catalog](https://datacatalog.mskcc.org/dataset/11458) — B
- [chordR community package](https://github.com/caravagnalab/chordR) — C
