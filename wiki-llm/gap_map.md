# System Bottlenecks & Knowledge Gaps (`gap_map.md`)

> Each gap has a stable ID (`G1`, `G2`, ...) referenced by experiments (`plan.md`) and findings (`wiki-llm/findings/`).

## Open Gaps

### `G1` — Third target variable, cohort and evaluation are undefined
* **System:** [[systems/hadassah-emr]]
* **Status:** `OPEN` — narrowed 2026-11-14 (Priority: Critical)
* **Observation:** Targets set in [[purpose]] §2: RECIST 1.1 response (CR/PR/SD/PD) and overall stage (0–IV + sub-stages). Still undefined: the third variable, cohort inclusion, evaluation metrics.
* **Candidate Directions:** Identify sources of oncology text with RECIST/stage labels (or labelable). Decide whether cohort entry requires a genomic test (selection bias). The data survey predates the target choice — see [[findings/data-source-landscape]].

### `G2` — Hadassah EMR structure and data model unknown
* **Status:** `OPEN` (Priority: High)
* **Observation:** EMR vendor (Chameleon?), tables, languages, existing mappings (TriNetX 2018, YonaLink) unknown.
* **Candidate Directions:** Questions list in [[systems/hadassah-emr]]; target MEDS + OMOP-oncology episodes + PRISSMM labels ([[literature/standards-oncology-data-models]]).

### `G3` — No external validation cohort secured
* **Status:** `OPEN` (Priority: High)
* **Candidate Directions:** International: GENIE BPC (Synapse), MSK-CHORD. Israeli: Clalit, Sourasky, Maccabi KSM, INCR linkage for survival.

### `G4` — Synthetic data: generator choice and synthetic→real transfer for prediction
* **Status:** `OPEN` (Priority: Medium)
* **Observation:** MDClone/Rambam validations cover descriptive statistics only; D'Amico 2023 is the only oncology survival validation (haematology, one row per patient). No study found tests longitudinal oncology prediction trained on synthetic data.
* **Candidate Directions:** [[findings/synthetic-data-strategy]] jobs A/B/C; TSTR experiment.

### `G5` — Hebrew clinical NLP
* **Status:** `OPEN` (Priority: Medium-High)
* **Observation:** No public Hebrew clinical corpus. HeMed (Sourasky) is IRB-restricted. NLP-derived features drove MSK-CHORD's gains.
* **Candidate Directions:** Request HeMed; Safe Harbor for de-identification; small PRISSMM-style gold set at Hadassah.

### `G6` — Governance: what may leave the hospital
* **Status:** `OPEN` (Priority: High)
* **Observation:** MoH 2018 secondary-use circulars, 2023 bill memo, 2026 genAI directive; no synthetic-data guidance found.
* **Candidate Directions:** Agree with supervisors + Helsinki committee on release rules for aggregates, models, and synthetic data.

### `G7` — Outcome completeness (deaths outside hospital)
* **Status:** `OPEN` (Priority: Medium)
* **Observation:** Hospital EMRs miss out-of-hospital deaths; INCR links to national population data.
* **Candidate Directions:** Ask whether Hadassah death dates are linked to the population registry; otherwise INCR/TIMNA linkage.

## Resolved Gaps
* *(none yet)*
