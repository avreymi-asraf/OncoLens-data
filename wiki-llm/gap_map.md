# System Bottlenecks & Knowledge Gaps (`gap_map.md`)

> Each gap has a stable ID (`G1`, `G2`, ...) referenced by experiments (`plan.md`) and findings (`wiki-llm/findings/`).

## Open Gaps

### `G1` — Prediction target, cohort and evaluation are undefined
* **System:** [[systems/hadassah-emr]]
* **Status:** `OPEN` (Priority: Critical — blocks everything)
* **Observation:** AGENT.md: target, cohort inclusion, time zero, horizon and metrics are not recorded. [[purpose]] has a TBD block.
* **Candidate Directions:** Overall survival and progression have the strongest external support (MSK-CHORD, GENIE BPC, SEER). Decide whether cohort entry requires a genomic test (selection bias). See [[findings/data-source-landscape]] §2.

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
