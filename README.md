# oncolens

Small Python package for reading research datasets **straight from the Hugging Face Hub, without downloading them**.
No patient data is stored in this repo.

Right now it has one loader, `oncolens.mmai`. It reads the DFCI MatchMiner-AI synthetic oncology corpus
([`ksg-dfci/mmai-synthetic-1225`](https://huggingface.co/datasets/ksg-dfci/mmai-synthetic-1225), CC BY-NC 4.0,
fully synthetic: 63,865 patients, 846,577 documents) and returns **one patient at a time as a Python dict**. Each
dict holds that patient's documents and, optionally, the answers (`y`).

## Install

From the repo root:

```bash
uv sync                      # installs huggingface_hub + pyarrow
uv run pytest                # offline tests
uv run pytest -m network     # one live test that streams from the Hub
```

If Hub requests fail with 401/403, log in once with `hf auth login`.

## Quick start

```python
from oncolens import mmai

for patient in mmai.iter_patients(split="test", sample=0.01, limit=5):
    x = mmai.model_input(patient)   # what the model sees
    y = patient["y"]                # the answers: never put these in the prompt
    print(x["patient_id"], len(x["documents"]), [d["stage"] for d in y["diagnoses"]])
```

`iter_patients` is a generator. Nothing is written to disk. The parquet files are read over HTTP, using only the
columns the loader needs, and patients come out one by one with bounded memory (~0.5 GB). The first patient
arrives after ~10–20 s, and a full pass takes ~15 min.

## What a patient looks like

```python
{
  "patient_id": "mmai-3f2a9c41d07e",      # opaque hash, safe to show a model
  "pseudo_mrn": 1, "split": "test",
  "source": {"repo": ..., "revision": ..., "license": "CC BY-NC 4.0"},
  "documents": [
    {"seq": 0, "type": "pathology_report", "date": "2019-07-16", "text": "...", "flag": None},
    ...
  ],
  "y": {                                  # None when with_y=False
    "event_history": "At age 58, ...",    # the timeline the notes were generated from
    "diagnoses": [{"age": 58, "stage": "IIIB", "stage_raw": "stage IIIb", "text": "..."}],
    "document_events": [{"seq": 0, "age": 58, "event": "..."}],
    "trial": {"nct_id": ..., "title": ..., "space": ..., "designed_eligible": True, "llm_judged_eligible": False},
    "patient_summary": None,              # filled only with with_summary=True
  },
}
```

Document `type` is one of `clinical_note`, `imaging_report`, `pathology_report` or `ngs_report`. `date` is
`None` unless you pass `with_dates=True`.

`mmai.model_input(patient)` reduces this to `{"patient_id", "documents": [{seq, type, date, text}]}`. It drops
the split, source, MRN and `y`, as well as the 3 corpus documents flagged as unusable (LLM refusals and notes
generated from placeholder events).

## `iter_patients` options

| Argument | Default | What it does |
|---|---|---|
| `split` | `None` | Keep only `"train"`, `"val"` or `"test"` |
| `limit` | `None` | Stop after N patients |
| `sample` | `None` | Keep a deterministic fraction of patients (e.g. `0.01`), spread over the whole file |
| `with_y` | `True` | Attach `y` |
| `with_dates` | `False` | Attach a date to each document (adds ~3–4 min up front) |
| `with_summary` | `False` | Put the LLM `patient_summary` into `y` (needs `with_y`) |
| `revision` | pinned commit | Dataset version, pinned so results are reproducible |

**Use `sample=` for a representative subset.** The file is sorted by trial space and design, so `limit=20` on
its own returns 20 very similar patients who were all designed to be eligible.

## Streaming data into a model

The pattern is: stream patients, turn each one into a prompt with `model_input`, call your model, and compare
the output with `y`. You never hold the whole dataset in memory.

### One patient at a time

```python
import json
from oncolens import mmai

def my_model(prompt: str) -> str:
    ...  # your SLM / LLM call (transformers pipeline, vLLM, an API client, ...)

INSTRUCTION = "Read the oncology documents below and return the overall cancer stage (0, I, II, III or IV) as JSON."

results = []
for patient in mmai.iter_patients(split="test", sample=0.01, limit=100, with_dates=True):
    x = mmai.model_input(patient)
    prompt = INSTRUCTION + "\n\n" + json.dumps(x, ensure_ascii=False)
    prediction = my_model(prompt)

    diagnoses = patient["y"]["diagnoses"]
    gold = diagnoses[-1]["stage"] if diagnoses else None   # last diagnosis is usually the trial-relevant one
    results.append({"patient_id": x["patient_id"], "prediction": prediction, "gold": gold})
```

### In batches (for GPU inference)

```python
from itertools import batched   # Python 3.12+
from oncolens import mmai

patients = mmai.iter_patients(split="test", sample=0.05, with_y=True)
try:
    for batch in batched(patients, 16):
        prompts = [build_prompt(mmai.model_input(p)) for p in batch]
        outputs = my_model_batch(prompts)
        golds = [p["y"] for p in batch]
        ...
finally:
    patients.close()   # releases the HTTP connection if you stop early
```

### As a PyTorch `IterableDataset`

```python
import torch
from oncolens import mmai

class MMAIStream(torch.utils.data.IterableDataset):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
    def __iter__(self):
        for patient in mmai.iter_patients(**self.kwargs):
            yield mmai.model_input(patient), patient["y"]

loader = torch.utils.data.DataLoader(MMAIStream(split="train", sample=0.1), batch_size=None)  # num_workers=0
```

Keep `num_workers=0`: every worker would stream the same file from the start.

### From the command line (JSON Lines)

The CLI writes one patient per line, so you can pipe it into any other process:

```bash
# full patient objects (with y) into a file
uv run python -m oncolens.mmai --split test --sample 0.01 --limit 20 --dates -o /tmp/mmai_test20.jsonl

# only model inputs, streamed to another program
uv run python -m oncolens.mmai --split test --sample 0.01 --model-input | python my_inference.py
```

Flags: `--split`, `--limit`, `--sample`, `--dates`, `--summary`, `--no-y`, `--model-input`, `--revision`, `-o`.

## Caveats

- **`y` comes from the generator, not from clinicians.** `diagnoses[].stage` is regex-parsed from the timeline
  (it parses a stage for ~78% of patients) and is a convenience, not a gold label. There is no RECIST CR/PR/SD/PD
  code in the dataset; `document_events` are free text.
- The generator saw the whole timeline, so a note can mention events dated after its own event.
- `with_dates=True` leaves every date `None` for ~4.5% of patients, whose date headers don't line up with their
  notes.
- The data is non-commercial (CC BY-NC 4.0).

More detail is in the module docstring of [`oncolens/mmai.py`](oncolens/mmai.py) and in
[`wiki-llm/datasets/mmai-synthetic.md`](wiki-llm/datasets/mmai-synthetic.md).
