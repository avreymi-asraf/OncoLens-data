---
type: dataset
node_id: ds:synthetic-ehr-generators
title: "Synthetic EHR generators (tabular + longitudinal) — tools, not datasets"
maintainer: "various"
url: "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10471716/"
access: method/tool
license: "per tool (SDV BSL / synthcity Apache-2.0 / research code)"
n_patients: "trained on your data"
time_span: "n/a"
modalities: [structured]
oncology_coverage: "D'Amico 2023: MDS/AML; others general"
language: "n/a"
data_model: "tabular / code sequences / OMOP (CEHR-GPT) / MEDS"
supports_targets: [overall-survival, ed-visit-admission, short-term-mortality]
resemblance_to_hadassah: high (once trained on Hadassah data, in-hospital)
credibility: A (peer-reviewed)
primary_doc_read: "partial — abstracts and summaries"
updated: 2026-10-31
---
# Synthetic EHR generators

Families, ordered by how well they fit a **multi-table, longitudinal** oncology EMR:

| Family | Examples | Longitudinal? | Notes |
|---|---|---|---|
| Rule-based simulators | Synthea | yes (simulated) | guideline-only, see [[datasets/synthea]] |
| Tabular (one row per patient) | SDV (CTGAN, TVAE, GaussianCopula), synthcity, **TabDDPM** | no | TabDDPM wins fidelity/utility but leaks more (SynMeter; Ceritli 2023). Good for a baseline-features table |
| Conditional tabular GAN, oncology | **D'Amico et al. 2023** (MDS/AML, CTGAN-WGAN-GP + SAFE validation) | partial (survival) | Only oncology-specific validated study found; survival estimates replicated; 300% augmentation. [[literature/damico-2023-synthetic-hematology]] |
| Code-sequence LMs | **HALO** (Nat Commun 2023), PromptEHR | yes | >10K-dim code distributions, R² > 0.9; AUROC 0.938 synthetic vs 0.943 real. [[literature/theodorou-2023-halo]] |
| Timeline LMs → OMOP | **CEHR-GPT** (2024; pip `cehrgpt`, MEDS support) | yes, with time gaps | Converts back to OMOP with almost no temporal loss. [[literature/pang-2024-cehr-gpt]] |
| Platform derivatives | **MDClone** | yes (event model) | Validated for observational analyses only. [[datasets/mdclone-israel]] |
| LLM note generators | CancerGUIDE, Asclepius | text | [[datasets/synthetic-clinical-notes]] |

Evaluation must cover **fidelity, utility (train-synthetic-test-real), and privacy** — and privacy needs per-record audits, not only aggregate scores. [[literature/synthetic-ehr-privacy-audits]], [[literature/tabular-synth-benchmarks]].

## Sources
- [HALO](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10471716/), [CEHR-GPT](https://arxiv.org/html/2402.04400v2), [SynMeter](https://arxiv.org/pdf/2402.06806), [TabDDPM-EHR](https://arxiv.org/pdf/2302.14679), [health evaluation framework PMC12058740](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12058740/), [D'Amico 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10569771)
