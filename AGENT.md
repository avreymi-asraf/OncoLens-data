# AGENT.md — OncoLens-data

This file describes the OncoLens-data repository for AI agents working in it. Read it before making changes.

## 1. What this repo is for

OncoLens-data gets the data the OncoLens research needs, and **makes it accessible in one uniform way**: a model's training or evaluation code asks for a dataset and receives, one patient at a time, a JSON object holding that patient's documents (and the answers, `y`, when the dataset has them). The code that does this is in `oncolens/`.

Requests come in two kinds:
- **Get new data about something** (a cancer type, a variable, a kind of document): find data that exists, or generate it.
- **Change data into a different format**: usually the patient shape below, or another format the training code needs.

Both end the same way, in data a model can read. Finding is therefore part of the job, and its result is data, or a named candidate plus what stands between it and a model; a report on the landscape is not the result.

A dataset is **accessible** when training or evaluation code can iterate over it in that shape, today. A wiki page about it, a licence, a link or a granted access are steps toward that, not the thing itself. Consumers should not need dataset-specific code: a second dataset comes out in the same shape as the first.

Everything else in the repo serves this. In particular `wiki-llm/` (§5) is the memory of this work — what each dataset is, how it is reached, how it is shaped — and not the work itself. Literature and source surveys are done when asked, to decide which data to make accessible next.

## 2. Who the data is for

The research develops a **small language model that extracts structured clinical information from oncology records** (radiology reports, pathology notes, clinical summaries) of cancer patients treated at **Hadassah Ein Kerem** (Hebrew University of Jerusalem; supervisors Prof. Tom Hope and Dr. Shai Rosenberg). Target variables: **RECIST 1.1 response** (CR/PR/SD/PD, longitudinal, usually inferred from free text), **overall stage 0–IV with sub-stages**, and a third, not yet specified. Experiments and models live in the sibling repo `OncoLens-lab`.

What that asks of the data layer: whole patient timelines with dates, so that no document after the labeled time point is used as input; the patient as the unit, so splits never put one patient in train and test; and the answers kept apart from the model input. Hadassah records cannot leave the hospital, so public and synthetic corpora stand in for development; the same shape is what the Hadassah data will need later.

## 3. The shape

One patient = `{patient_id, documents: [{seq, type, date, text}], y}`; `y` is optional; the model input drops everything but the id and the documents. The reference implementation is `oncolens/mmai.py`, used as shown in `README.md`. The shape was asked for in these words: "a JSON object containing a collection of documents grouped by patient (ignoring images); if there's a `y`, great, if not, that's fine."

## 4. Adding a dataset

"Use this dataset" means: through to a model reading it. Look at the data where it lives (schemas, sizes; without downloading when it can be read remotely), write the loader in `oncolens/` with offline tests, run one full pass to measure what is really there (counts, dates, label coverage, broken records), and record the measured shape and how to call the loader on the dataset's page in `wiki-llm/datasets/`. Datasets are read where they live; nothing patient-level is stored in this repo.

## 5. Repository structure

| Path | Purpose |
|---|---|
| `oncolens/` | The loaders: stream a dataset from where it lives into the patient shape (`oncolens/mmai.py`) |
| `tests/` | Offline tests (`uv run pytest`); live Hub checks are marked `network` (`uv run pytest -m network`) |
| `README.md` | How to use the loaders |
| `wiki-llm/` | Memory of the data layer: `datasets/` (one page per dataset: what it is, access route, measured shape, loader), `literature/`, `findings/`, `systems/` (Hadassah EMR), `purpose.md`, `gap_map.md` (what stands between the research and data a model can read), `index.md`, `log.md` |
| `pyproject.toml` | `uv` project for `oncolens` |
| `skills-lock.json` | Installed agent skills |
| `.grow-autonomy/rejects.md` | Record of rejected work and what changed because of it. For the maintainer, not instructions |

## 6. Data handling rules

- Hadassah patient records are protected health information, governed by hospital and ethics approvals. They are never in this repo: not in code, notebooks, logs, fixtures, tests, docs or chat.
- Never print, paste or summarize individual patient records. Use aggregate statistics, synthetic data or de-identified examples.
- Do not send data or excerpts to external services or APIs. If a task seems to need raw patient-level output, stop and ask.
- Public and synthetic datasets carry their own licences (e.g. CC BY-NC, DUAs). The licence goes on the dataset's page and into the loader's output (`source.license`).

## 7. Working conventions

- Python: `uv` only (`uv sync`, `uv add`, `uv run`); version as pinned in `.python-version`.
- Lint and format `oncolens/` and `tests/` with `uv run ruff check --fix` and `uv run ruff format`; tests with `uv run pytest -q`. Tests do not hit the network by default and do not need real patient data.
- Ask before adding dependencies, and before anything that touches real clinical data, shares output outside the lab, or changes cohort definitions or the evaluation protocol: those affect the thesis claims. Supervisors decide what may leave the hospital.

## 8. Open items

- The third target variable, cohort inclusion and evaluation metrics are not yet recorded. Ask the user rather than inventing them; record them in `wiki-llm/purpose.md`.
- Only one dataset (MMAI synthetic) has a loader so far.
