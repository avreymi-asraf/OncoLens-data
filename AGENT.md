# AGENT.md — OncoLens Project Description

This file describes the OncoLens project for AI agents working in this repository. Read it before making changes.

> **What this repo is for:** `OncoLens-data` finds or generates — and makes accessible — the data and information the OncoLens research needs (datasets, access paths, label standards, synthetic data, literature). It does not hold patient data or model code; experiments live in the sibling repo `OncoLens-lab`.

## 1. What the project is

OncoLens is a master's lab project that is intended to grow into a PhD-level thesis. It is conducted at the **Hebrew University of Jerusalem** under the supervision of:

- **Prof. Tom Hope** — Hebrew University
- **Dr. Shai Rosenberg** — Hadassah Medical Center (Ein Kerem)

The research develops a **small language model that extracts structured clinical information from oncology records** (radiology reports, pathology notes, clinical summaries) of cancer patients treated at **Hadassah Ein Kerem**. It targets core variables that capture disease progression and severity:

1. **RECIST 1.1 treatment response** — longitudinal; each follow-up is classified as CR, PR, SD or PD. Clinicians rarely write the code, so the model must infer it from free text (new lesions, shrinkage) and dimensional comparisons across the patient's timeline.
2. **Overall cancer stage (0–IV, with sub-stages such as IA, IIIB, IVB)** — at a point in time (diagnosis, restaging). The model must normalize Roman numerals, Arabic numerals and abbreviations into one standard format.
3. *A third variable is planned but not yet specified.*

The work is expected to be **innovative and of high academic standard**. Treat it as research, not as a product prototype: methodological rigor, reproducibility, and clear reasoning about why things work matter as much as the metrics.

## 2. Data

- **Source:** medical records of cancer patients from Hadassah Ein Kerem.
- **Nature:** clinical, longitudinal, and sensitive. Patient records are protected health information (PHI) and are governed by hospital and ethics approvals.
- **Location:** the data is not in this repository and must never be committed to it. Do not copy patient data into code, notebooks, logs, fixtures, test data, or documentation.
- **Handling rules for agents:**
  - Never print, paste, or summarize individual patient records in chat or in files.
  - Use aggregate statistics, synthetic data, or de-identified examples only.
  - Do not send any data, or excerpts of it, to external services or APIs.
  - If a task seems to require raw patient-level output, stop and ask the user first.

## 3. Task

Build and evaluate the extraction model for the variables in §1. The target variables are set; cohort definitions, the third variable, and the evaluation protocol are still being defined — check `wiki-llm/purpose.md` and `wiki-llm/gap_map.md` (`G1`) before assuming them.

This repo's part of the task: find, assess, and document (or generate) the data the model needs — annotated or annotatable oncology text, RECIST/stage label sources, external validation sets, and synthetic records — and keep that knowledge accessible in `wiki-llm/`.

## 4. Repository structure

This repository is the **data and knowledge side** of OncoLens. Its layout:

| Path | Purpose |
|---|---|
| `AGENT.md` | This file: project context for agents |
| `wiki-llm/` | Knowledge base: `purpose.md`, `gap_map.md`, `index.md`, `datasets/` (one page per source), `literature/`, `findings/`, `systems/` |
| `skills-lock.json` | Installed agent skills |

The experiment loop (`JOURNAL.md`, `experiments/`, `scripts/lab.py`, Python environment) lives in the sibling repo `OncoLens-lab`.

## 5. Working conventions

Follow `CODE-STANDARDS.md` for tooling. In brief:

- **Python environment:** `uv` only (`uv sync`, `uv add`, `uv run`). Do not use `pip install`, ad-hoc venvs, or `requirements.txt`.
- **Python version:** as pinned in `.python-version` (≥ 3.11).
- **Lint and format:** `uv run ruff check --fix` and `uv run ruff format`.
- **Type checking:** `uv run pyright`.
- **Tests:** `uv run pytest -q`. Tests must not hit the network by default and must not require real patient data.
- **Experiment tracking:** `wandb` is the intended tool.

Research conventions:

- Every experiment gets its own folder under `experiments/` with a hypothesis, the planned change, and the evaluation outcome. Keep finished experiment folders immutable.
- Record findings in `wiki-llm/findings/` and log open questions in `wiki-llm/gap_map.md`.
- Prefer the simpler method when results are comparable. Explain *why* a change helped or failed.
- Report negative results honestly; add refuted ideas to the banlist in `JOURNAL.md` so they are not retried unchanged.
- Keep evaluation leak-free: splits must respect patient identity (no patient in both train and test), and no document dated after the time point being labeled may be used as input.

## 6. Collaboration and approvals

- Ask before any action that touches real clinical data, shares outputs outside the lab, or publishes results.
- Ask before adding dependencies, changing the evaluation protocol, or altering cohort definitions, since those affect the thesis claims.
- Supervisors are the final authority on methodology and on what may leave the hospital environment.

## 7. Open items for agents

- The third target variable, cohort inclusion criteria, and evaluation metrics are not yet recorded. Ask the user rather than inventing them, and record them in `wiki-llm/purpose.md`.
- No OncoLens-specific system page exists yet under `wiki-llm/systems/`.
