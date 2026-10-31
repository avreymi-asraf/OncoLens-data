---
type: dataset
node_id: ds:sourasky-imedata
title: "Tel Aviv Sourasky (Ichilov) I-Medata data lake + Hebrew clinical corpora"
maintainer: "Tel Aviv Sourasky Medical Center — I-Medata AI Center"
url: "https://www.tasmc.org.il/sites/en/IMedata/Pages/R-and-D-Sandbox.aspx"
access: in-hospital-only
license: "Hospital-internal; collaborations"
n_patients: "data lake since 2007; HeMed trained on ~5M de-identified records"
time_span: "2007–present"
modalities: [structured, notes]
oncology_coverage: "all; published oncology NLP on ICI patients"
language: "he (+ en)"
data_model: "unknown (Chameleon EMR on AWS, per press)"
supports_targets: [toxicity, overall-survival]
resemblance_to_hadassah: high
credibility: A (arXiv papers) / C (press)
primary_doc_read: "yes — arXiv 2403.09708 abstract page; HeMed arXiv summary"
updated: 2026-10-31
---
# Tel Aviv Sourasky (Ichilov) — I-Medata

## What it is
Ichilov's I-Medata AI Center runs a medical data lake collected digitally since 2007 and an R&D sandbox. Ichilov moved its **Chameleon** EMR (Elad Health) to AWS.

Two oncology-relevant Hebrew NLP results come from this data:
- **irAE monitoring** (Shapiro, Dor, Gurevich-Shapiro, Etan, Wolf — arXiv 2403.09708): **108,280 clinical notes from 1,635 patients on immune-checkpoint inhibitors**; NLP pipeline detects 7 immune-related adverse events; AUC 0.89 per note; patient-level F1 ≥ 0.87 for 5/7 irAEs. A direct template for a **toxicity** target on Hebrew notes.
- **HeMed** (arXiv 2512.11502): DictaBERT 2.0 further pre-trained on ~5M de-identified Sourasky records, for clinical timeline extraction. See [[datasets/hebrew-clinical-nlp]].

## Why it matters
Closest published analogue of Hadassah's data (Israeli tertiary hospital, Hebrew notes, probably the same EMR vendor). Methods from here should transfer; a collaboration could give an Israeli external validation set.

## Sources
- [arXiv 2403.09708 — irAE NLP pipeline](https://arxiv.org/abs/2403.09708) — A
- [arXiv 2512.11502 — HeMed](https://arxiv.org/abs/2512.11502v1) — A
- [TASMC R&D sandbox page](https://www.tasmc.org.il/sites/en/IMedata/Pages/R-and-D-Sandbox.aspx) — B (page content not retrievable)
- [Elad Health profile (Chameleon >80% of Israeli hospitals)](https://startupim.com/company/elad-healthcare-solutions) — C
