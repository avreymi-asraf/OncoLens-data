# Research Purpose & Evaluation Philosophy (`purpose.md`)

## 1. Mission
OncoLens develops a **small language model that extracts structured clinical variables from oncology records** (radiology reports, pathology notes, clinical summaries) of cancer patients treated at **Hadassah Ein Kerem**. Hebrew University of Jerusalem, supervised by Prof. Tom Hope (HUJI) and Dr. Shai Rosenberg (Hadassah). The work is research toward a master's and later PhD thesis: rigor, reproducibility, and explaining *why* a result holds matter as much as the metric.

**This repo's job:** get the data the research needs (find it, generate it, or convert existing data into another format) and make it accessible to models in one uniform way — one JSON object per patient, documents grouped, answers optional (`AGENT.md` §1, loaders in `oncolens/`). This wiki is that work's memory: for each dataset, what it is, how it is reached, how it is shaped and labeled, and how a model reads it today. Synthetic data stands in where real data cannot go. Every dataset page should end in the answer to: *can a model read this now, and if not, what is missing?*

## 2. Target variables
1. **RECIST 1.1 treatment response** (longitudinal) — classify each follow-up point as Complete Response (CR), Partial Response (PR), Stable Disease (SD) or Progressive Disease (PD). Clinicians rarely write the code, so it must be inferred from free text (new lesions, shrinkage) and dimensional comparisons across the patient's timeline.
2. **Overall cancer stage, 0–IV with sub-stages** (e.g. IA, IIIB, IVB) — at a point in time (diagnosis, restaging). Mentions in Roman numerals, Arabic numerals and abbreviated text must be normalized to one standard format.
3. **Third variable — not yet specified.**

> Still open (do not invent): the third variable, cohort inclusion, and evaluation metrics. See `G1` in [[gap_map]].

## 3. Data handling rules (inherit on every page)
- Hadassah patient records are PHI, governed by hospital and Helsinki-committee approvals. They are **never** committed, copied into code, notebooks, logs, fixtures, docs, or chat.
- Use aggregate statistics, synthetic data, or de-identified examples only.
- Never send any patient data or excerpts to external services or APIs. (A 2026 MoH directive banning patient data in public generative-AI tools is reported in the press — confirm the circular with the supervisors; see [[datasets/israel-moh-timna]].)
- If a task seems to need raw patient-level output, stop and ask.
- Public/credentialed datasets below carry their own licenses and DUAs (e.g. PhysioNet DUA, CC BY-NC-ND). Check the dataset page before any use.

## 4. Evaluation rules
1. **Leak-free splits:** split by patient; no document dated after the time point being labeled may be used as input.
2. **Simplicity criterion:** with comparable results, prefer the simpler model and the simpler data pipeline.
3. **Explain the mechanism:** record *why* a result holds in `findings/`.
4. **Honest negatives:** refuted ideas go to the banlist in `JOURNAL.md` (experiments repo).
5. **External validity:** prefer designs that can be checked on a second, independent cohort (see [[findings/data-source-landscape]] §5).
