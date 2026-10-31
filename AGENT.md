# AGENT.md — OncoLens Project Description

This file describes the OncoLens project for AI agents working in this repository. Read it before making changes.

## 1. What the project is

OncoLens is a master's lab project that is intended to grow into a PhD-level thesis. It is conducted at the **Hebrew University of Jerusalem** under the supervision of:

- **Prof. Tom Hope** — Hebrew University
- **Dr. Shai Rosenberg** — Hadassah Medical Center (Ein Kerem)

The goal is to build a **predictive model that generates predictions from real clinical data**: electronic medical records (EMR) of cancer patients treated at **Hadassah Ein Kerem**.

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

Build and evaluate a model that produces predictions from the cancer patients' records. Exact prediction targets, cohort definitions, and evaluation protocol are still being defined; check `wiki-llm/` and `JOURNAL.md` for the current state before assuming them.

## 4. Repository structure

This repository is currently a **research-lab control repo** from which the OncoLens work is organized. Its layout:

| Path | Purpose |
|---|---|
| `AGENT.md` | This file: project context for agents |
| `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` | Agent-specific instructions and the experiment loop |
| `CODE-STANDARDS.md` | Rules for how code is written, run, and tested |
| `JOURNAL.md` | Lab journal: current baselines, queued hypotheses, experiment index, banlist of refuted ideas |
| `wiki-llm/` | Compiled knowledge base: `purpose.md`, `gap_map.md`, `systems/`, `findings/`, `literature/` |
| `experiments/` | Immutable evidence folders, one per experiment (`EXP-XXX-…`), plus `_TEMPLATE` |
| `scripts/lab.py` | Lab helper script |
| `pyproject.toml`, `uv.lock`, `.python-version` | Python environment (managed with `uv`) |

**Note:** the current contents are largely a generic template with example entries (e.g., `EXP-000-baseline-example`, `example-agent-repo`). Those examples are placeholders and do not describe OncoLens. Do not treat them as project facts.

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
- Keep evaluation leak-free: splits must respect patient identity (no patient in both train and test), and no information from after the prediction time may be used as a feature.

## 6. Collaboration and approvals

- Ask before any action that touches real clinical data, shares outputs outside the lab, or publishes results.
- Ask before adding dependencies, changing the evaluation protocol, or altering cohort definitions, since those affect the thesis claims.
- Supervisors are the final authority on methodology and on what may leave the hospital environment.

## 7. Open items for agents

- The exact prediction task, cohort inclusion criteria, and evaluation metrics are not yet recorded in this repo. Ask the user rather than inventing them, and suggest recording them in `wiki-llm/purpose.md`.
- No OncoLens-specific system page exists yet under `wiki-llm/systems/`.
