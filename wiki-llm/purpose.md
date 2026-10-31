# Research Purpose & Evaluation Philosophy (`purpose.md`)

## 1. Mission
OncoLens builds and evaluates a **predictive model over real clinical data**: the electronic medical records (EMR) of cancer patients treated at **Hadassah Ein Kerem**. Hebrew University of Jerusalem, supervised by Prof. Tom Hope (HUJI) and Dr. Shai Rosenberg (Hadassah). The work is research toward a master's and later PhD thesis: rigor, reproducibility, and explaining *why* a result holds matter as much as the metric.

This repo (`OncoLens-data`) is the **data side** of the lab: which data exists, what can be accessed, how it is shaped, and how synthetic data can stand in for real data where real data cannot go.

## 2. Prediction target — TBD
> **TARGET: TBD — fill in with the supervisors.**
> Prediction target(s), cohort inclusion criteria, prediction time (time zero), horizon, and evaluation metrics are **not yet defined**. Do not invent them. See `G1` in [[gap_map]].
>
> Candidate targets that the data survey covers (for planning only, not a decision): overall survival, progression / progression-free survival, treatment response, treatment toxicity (e.g. immune-related adverse events), unplanned ED visit / admission, short-term mortality (e.g. 6-month), metastatic spread by site. The sources × targets matrix is in [[findings/data-source-landscape]].

## 3. Data handling rules (inherit on every page)
- Hadassah patient records are PHI, governed by hospital and Helsinki-committee approvals. They are **never** committed, copied into code, notebooks, logs, fixtures, docs, or chat.
- Use aggregate statistics, synthetic data, or de-identified examples only.
- Never send any patient data or excerpts to external services or APIs. (A 2026 MoH directive banning patient data in public generative-AI tools is reported in the press — confirm the circular with the supervisors; see [[datasets/israel-moh-timna]].)
- If a task seems to need raw patient-level output, stop and ask.
- Public/credentialed datasets below carry their own licenses and DUAs (e.g. PhysioNet DUA, CC BY-NC-ND). Check the dataset page before any use.

## 4. Evaluation rules
1. **Leak-free splits:** split by patient; no feature may use information after the prediction time.
2. **Simplicity criterion:** with comparable results, prefer the simpler model and the simpler data pipeline.
3. **Explain the mechanism:** record *why* a result holds in `findings/`.
4. **Honest negatives:** refuted ideas go to the banlist in `JOURNAL.md` (experiments repo).
5. **External validity:** prefer designs that can be checked on a second, independent cohort (see [[findings/data-source-landscape]] §5).
