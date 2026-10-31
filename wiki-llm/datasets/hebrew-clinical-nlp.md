---
type: dataset
node_id: ds:hebrew-clinical-nlp
title: "Hebrew clinical NLP resources (models, de-identification)"
maintainer: "various (Sourasky, Technion, Microsoft, Dicta)"
url: "https://arxiv.org/abs/2512.11502v1"
access: application
license: "HeMed: research use, formal medical institutions under IRB-approved protocols"
n_patients: "n/a"
time_span: "n/a"
modalities: [notes]
oncology_coverage: "general clinical; irAE work is oncology"
language: "he"
data_model: "n/a"
supports_targets: [toxicity, progression, metastasis, treatment-response]
resemblance_to_hadassah: high
credibility: A (arXiv / ACL papers) / C (practitioner blog)
primary_doc_read: "partial — arXiv abstract pages and summaries"
updated: 2026-10-31
---
# Hebrew clinical NLP resources

There is **no public Hebrew clinical corpus**. What exists:

| Resource | What | Access |
|---|---|---|
| **HeMed** (arXiv 2512.11502, Dec 2025) | DictaBERT 2.0 + continued pre-training on ~5M de-identified Sourasky records; vocabulary adaptation; clinical timeline (temporal relation) extraction; de-identification did not hurt performance | Restricted to formal medical institutions with IRB-approved protocols |
| **HSMP-BERT** (arXiv 2509.04519) | HeRo (Hebrew RoBERTa) + MLM on 9,683 Crohn's radiology reports | paper |
| **SMP-BERT** (ClinicalNLP workshop) | prompt learning for Hebrew radiology reports; strong on rare findings | paper |
| **irAE pipeline** (arXiv 2403.09708) | Sourasky ICI notes, see [[datasets/sourasky-imedata]] | paper |
| **Safe Harbor** | open-source Hebrew medical de-identification (NER + rules); shipped in a cloud text-analytics service (GA in Hebrew, 2022) | open source / cloud |
| **NimbleMiner on Sheba notes** (MEDINFO 2019) | Hebrew clinical text mining | paper |
| General Hebrew LMs | AlephBERT, HeRo, DictaBERT | open |

## Why it matters
Hadassah notes are presumably Hebrew (verify). NLP-derived features (sites of disease, progression) were the biggest gain in MSK-CHORD ([[literature/jee-2024-msk-chord]]). Reproducing that at Hadassah needs a Hebrew clinical encoder (HeMed is the best candidate; Hadassah as an IRB-approved institution may qualify) and a Hebrew de-identification step.

## Sources
- [HeMed](https://arxiv.org/abs/2512.11502v1), [HSMP-BERT](https://arxiv.org/html/2509.04519v1), [irAE](https://arxiv.org/abs/2403.09708) — A
- [Safe Harbor background (practitioner write-up)](https://hadasbitran.substack.com/p/ai-and-de-identification-of-healthcare) — C
- [NimbleMiner Hebrew, MEDINFO 2019](https://ebooks.iospress.nl/pdf/doi/10.3233/SHTI190250) — A
