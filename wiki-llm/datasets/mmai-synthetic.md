---
type: dataset
node_id: ds:mmai-synthetic
title: "MatchMiner-AI (MMAI) synthetic oncology corpus — DFCI"
maintainer: "Dana-Farber Cancer Institute (HF org ksg-dfci)"
url: "https://huggingface.co/datasets/ksg-dfci/mmai-synthetic-1225"
access: open
loader: "oncolens.mmai"
license: "CC BY-NC 4.0 (1225 release); 0426/0526 releases are CC BY-NC-ND 4.0"
n_patients: "63,865 synthetic patients, 846,577 notes"
time_span: "synthetic per-note dates (range not measured)"
modalities: [notes, genomic]
oncology_coverage: "pan-cancer (solid + heme), generated per ClinicalTrials.gov trial 'space'"
language: "en"
data_model: "custom parquet (pseudo_mrn × note rows; patient-level side tables)"
supports_targets: [progression, treatment-response, metastasis]
resemblance_to_hadassah: medium
credibility: B (official dataset card + direct inspection of every file used)
primary_doc_read: "yes — HF dataset card; all used parquet schemas and a full pass over the notes"
updated: 2026-11-14
---
# MatchMiner-AI synthetic oncology corpus (DFCI)

> **Purpose:** a large, open, fully synthetic set of *longitudinal, multi-document* oncology patient records. Here the state (stage, response, progression) has to be put together across many dated notes of different kinds. It is the closest open match to the OncoLens extraction task ([[purpose]]).

## What it is
DFCI generated this corpus to train clinical-trial-matching models (MatchMiner-AI). The process:
1. Parse cancer trials from ClinicalTrials.gov into "clinical spaces" (age, sex, cancer type, histology, extent of disease, biomarkers, prior treatment).
2. Have an LLM write a longitudinal event timeline for a synthetic patient who is either eligible or ineligible for one space.
3. Have an LLM write one note per timeline event.

Measured at revision `b1845aae` with a full pass on 2026-11-14:

| | |
|---|---|
| Patients | **63,865**, with one trial space each |
| Documents | **846,577**, about 13.3 per patient (range 1–38) |
| Document types | 449,505 clinical notes · 224,315 imaging · 94,706 pathology · 78,051 NGS reports |
| Splits (per patient) | train 52,315 · val 5,637 · test 5,913 |
| Document length | p50 6.8K chars; one patient's documents p50 85K chars (≈21K tokens), p99 134K, max 257K |
| Dates | synthetic `YYYY-MM-DD` per note, attached for 61,014 patients (95.5%) where the type sequence lines up; always chronological; content-checked on 400 patients (5,578/5,578 documents matched their note). The other 4.5% get `null`: a note was dropped, or two adjacent notes are swapped in order |
| Images | none |

**Releases.** The HF org `ksg-dfci` has three releases:
- `1225`: 2025-12-15, CC BY-NC. Used here.
- `0426`: embeddings only.
- `0526`: 2026-06, newer but CC BY-NC-ND.

1225 is chosen for its licence, since it allows derivatives, not for being the newest.

## Access path (no download)
Use `oncolens/mmai.py` in this repo. It streams from the Hub with `HfFileSystem` + `pyarrow`, reading only the needed columns over HTTP range requests.

```bash
uv run python -m oncolens.mmai --split test --sample 0.01 --limit 20 --dates -o /tmp/mmai.jsonl   # full objects
uv run python -m oncolens.mmai --limit 5 --model-input                                           # model input only
```

```python
from oncolens import mmai
for p in mmai.iter_patients(split="test", sample=0.01, limit=20, with_dates=True):
    x, y = mmai.model_input(p), p["y"]
```

- **Output:** one JSON object per patient: `patient_id` (an opaque hash), `documents[{seq, type, date, text}]`, and a separate `y`.
- **Cost:**
  - The first patient arrives in about 6–20 s.
  - A full pass takes about 11–20 min, with about 0.5 GB of RAM.
  - `with_dates` adds about 4 min up front, because the dates live in an unsorted 1 GB column.
- **Why a forward stream:** `all_synthetic_notes.parquet` is one 7 GB row group with no page index, sorted by `pseudo_mrn`. Each patient's notes are contiguous, so a forward stream is the only efficient access pattern.
- **Don't use the HF viewer or `load_dataset` default config:** it resolves to `all_training_data.parquet` (text/label pairs for the embedder).

## What can serve as `y`
Everything below is from the generator side. Nothing in it is a human annotation.

| `y` field | Source | Notes |
|---|---|---|
| `event_history` | `masked_text`, with the event markers removed | The full timeline the notes were written from ("At age 58, …"). It is identical across all of a patient's notes (checked on every patient). |
| `diagnoses[]` (`stage`, `stage_raw`, `text`) | diagnosis lines of the timeline | 99.0% of patients have at least one; overall stage is parsed for **79.4%**. Unstaged examples seen include leukaemias and myelofibrosis, which have no TNM stage. Multiple primaries occur, in timeline order. |
| `document_events[]` | `event_text` per note | The prompt each note was written from, e.g. "cancer present and progressing" or "partial response". Free text only: **no RECIST CR/PR/SD/PD codes** anywhere. |
| `trial` | `space_specific_eligibility_checks` + `note_is_from_positive_prompt` | Gives the space text, `designed_eligible` (50.1%) and `llm_judged_eligible` (47.1%). The two agree for only 63.3% of patients. |
| `patient_summary` (opt-in) | same file | An LLM summary with staging, biomarkers and treatment lines, with dates. |

## Why it matters for OncoLens
- It is the right input shape: many dated, typed documents per patient (oncologist notes, imaging, pathology, NGS), and the patient state has to be put together across them.
- It has scale and a patient-level split, so the leak-free split rule in [[purpose]] holds out of the box.
- Stage (79%) and response or progression wording (per note) can be taken from the generator truth without any annotation. That supports a silver-label pre-training or evaluation stage before Hadassah data ([[findings/synthetic-data-strategy]], job A).
- It is English and US-style. It does not stand in for Hebrew or Hadassah note style ([[datasets/hebrew-clinical-nlp]]).

## Caveats
- **Future leakage inside the notes.** The generator saw the whole timeline when writing each note, so earlier notes can mention later events. Per-time-point tasks need care. Labelling a patient as of their last event is safe.
- **Raw `pseudo_mrn` leaks the design label.** Every MRN below 1,000,000 is designed-eligible. File order is grouped by trial space and by design. The loader therefore emits a hashed `patient_id` and offers `sample=`, since `limit=N` alone gives a narrow, all-eligible slice.
- **A few broken notes.** There is 1 LLM refusal ("I'm sorry, but I can't help with that.") and 2 placeholder events. These are flagged and left out of `model_input`.
- **Not a gold standard.** Stage is parsed by regex from LLM-written timelines. The response wording is not RECIST-coded. The trial eligibility labels come from an LLM judge.
- **Context length.** A patient averages about 21K tokens of notes, so a small model needs chunking or a long context.
- **Use restrictions.** CC BY-NC means no commercial use. The data is synthetic, so there are no PHI rules.

## Sources
- [HF dataset card, ksg-dfci/mmai-synthetic-1225](https://huggingface.co/datasets/ksg-dfci/mmai-synthetic-1225) — B
- Direct inspection: parquet schemas of all files used, plus full validation passes with `oncolens.mmai` (2026-11-14) — A (own measurement)
