# Wiki-LLM Master Content Catalog (`index.md`)

> **Navigation Rule:** Update this catalog on every wiki write. Read it first, then drill into pages.
> **Repo goal:** get the data the OncoLens research needs (find, generate, or convert it) and make it accessible to models in one uniform way (one JSON object per patient; loaders in `oncolens/`). This wiki is the memory of that work. The research it serves: a small language model extracting RECIST response and overall stage from oncology records ([[purpose]]).
> **Data rule:** no patient data anywhere in this wiki — see [[purpose]] §3.

## Core Steering & Maps
* [[purpose]] — Mission (extraction SLM), target variables (RECIST, stage, third TBD), data-handling and evaluation rules (`Updated: 2026-11-14`)
* [[gap_map]] — Open gaps G1–G7 (third variable/cohort/metrics, EMR schema, external validation, synthetic, Hebrew NLP, governance, outcome completeness) (`Updated: 2026-11-14`)
* [[log]] — Append-only audit trail (`Updated: 2026-10-31`)

## Target Systems (`systems/`)
* [[systems/hadassah-emr]] — Hadassah oncology EMR: what is known, TODO questions for supervisors/IT (`Status: Placeholder`)

## Findings (`findings/`)
* [[findings/data-source-landscape]] — Three-tier data plan, sources × targets matrix, 10 subsurface insights, next steps (`Confidence: Initial`)
* [[findings/synthetic-data-strategy]] — Three jobs for synthetic data, generator per job, validation protocol (`Confidence: Initial`)

## Datasets (`datasets/`) — one page per source, template in `datasets/_TEMPLATE.md`
### Primary (Hadassah)
* [[datasets/hadassah-oncology-datamart]] — ≈260K records + genomics, Rosenberg team (in-hospital; credibility C)
### Israeli sources
* [[datasets/israel-national-cancer-registry]] — national registry since 1960; 93.7% complete; death/stage ground truth
* [[datasets/israel-moh-timna]] — MoH big-data research rooms + regulatory context (2018 circulars, 2026 genAI ban)
* [[datasets/clalit-research]] — Clalit / Samueli cancer data lake; best Israeli validation candidate
* [[datasets/maccabi-ksm]] — 2.7M members, 30 years; community outcomes
* [[datasets/sourasky-imedata]] — Ichilov data lake; HeMed; 108K-note irAE NLP
* [[datasets/mdclone-israel]] — synthetic derivatives at Rambam/Sheba/Sourasky/Maccabi; not confirmed at Hadassah
* [[datasets/hebrew-clinical-nlp]] — HeMed, HSMP-BERT, Safe Harbor de-identification
* [[datasets/trinetx]] — Hadassah member since 2018; implies a standard-terminology mapping
### International real-world oncology / EHR
* [[datasets/msk-chord]] — 24,950 pts, NLP + genomics + survival; open (CC BY-NC-ND); best proxy
* [[datasets/aacr-genie-bpc]] — PRISSMM-curated NSCLC/CRC/breast; external validation; Synapse
* [[datasets/mimic-iv]] — BIDMC hospital EHR + 2.6M notes; credentialed
* [[datasets/ehrshot]] — Stanford longitudinal benchmark in MEDS/OMOP; CLMBR, MOTOR
* [[datasets/tcga-reports]] — 9,523 pathology reports + GDC clinical
* [[datasets/coral-oncology-notes]] — 40 annotated oncology notes (eval only)
* [[datasets/project-data-sphere]] — oncology trial comparator arms
* [[datasets/seer]] — US registry; open to any email since June 2025
* [[datasets/ncdb]] — US hospital registry; not accessible (CoC institutions only)
* [[datasets/flatiron]] — commercial RWD; endpoint definitions worth copying
### Synthetic data
* [[datasets/synthea]] — rule-based; breast/CRC/lung/AML/prostate modules; plumbing only
* [[datasets/synthetic-ehr-generators]] — HALO, CEHR-GPT, TabDDPM, CTGAN, MDClone compared
* [[datasets/synthetic-clinical-notes]] — Asclepius, longitudinal LLM notes, de-id-vs-synthetic
* [[datasets/cancerguide-synthetic]] — GPT-4.1 synthetic NSCLC notes with treatment labels
* [[datasets/mmai-synthetic]] — DFCI MatchMiner-AI: 63,865 synthetic patients × ~13 dated notes (clinical/imaging/path/NGS) + generator timelines; streamed by `oncolens.mmai` (`Updated: 2026-11-14`)

## Literature (`literature/`) — template in `literature/_TEMPLATE.md`
* [[literature/jee-2024-msk-chord]] — MSK-CHORD, Nature 2024 (full text read)
* [[literature/theodorou-2023-halo]] — HALO longitudinal EHR generator
* [[literature/pang-2024-cehr-gpt]] — CEHR-GPT synthetic OMOP timelines
* [[literature/reiner-benaim-2020-mdclone-rambam]] — Rambam MDClone validation
* [[literature/chen-2019-synthea-validity]] — Synthea vs quality measures
* [[literature/damico-2023-synthetic-hematology]] — synthetic MDS/AML with survival validation
* [[literature/synthetic-ehr-privacy-audits]] — membership inference, per-record audits
* [[literature/tabular-synth-benchmarks]] — SynMeter, TabDDPM, health evaluation framework
* [[literature/standards-oncology-data-models]] — OMOP oncology, mCODE, MEDS, PRISSMM
