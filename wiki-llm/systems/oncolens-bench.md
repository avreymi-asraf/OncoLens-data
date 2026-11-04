---
type: system
node_id: sys:oncolens-bench
title: "OncoLens benchmark (wiki-driven LLM evaluation over patient-record corpora)"
status: active
updated: 2026-11-04
---
# System: OncoLens benchmark

> Repo: OncoLens-data, package `oncolens/` | Entry points: `python -m oncolens.bench`, `python -m oncolens.check`
> Monitored: `oncolens/*.py`, `data/README.md` (record contract), `datasets/msk-chord.md` (`supports_targets`).

## What it does
Scores a language model on binary questions about a patient, asked from the patient's Markdown record. The record body is the whole prompt input; the ground truth (`outcomes:` in the frontmatter) is withheld and used only to label. Only `split: test` is scored; `train` is reserved for later training.

## Architecture (one idea per module)
| Module | Role |
|---|---|
| `records.py` | Loads `data/<corpus>/*.md` into typed `Record`s, validating each against the contract in `data/README.md`. `Record.prompt_text` is the leak-safe view (body only). |
| `wiki.py` | **The wiki connection.** Reads `supports_targets` from [[datasets/msk-chord]] frontmatter. |
| `tasks.py` | Registry of implemented tasks: `overall-survival` (deceased?) and `metastasis` (liver among sites?). Each has a question, options A/B, and `label(record)`. `select_tasks` intersects wiki targets with the registry and returns the rest as **unsupported** (`progression`, `treatment-response` today) instead of dropping them. |
| `models.py` | `Model.generate(prompts)`. `HFModel` (transformers, greedy, left padding, chat template when the tokenizer has one) and `Fixed` (`fixed:A`, GPU-free). |
| `bench.py` | `run(model, corpora, tasks)` -> per (source, task): accuracy, balanced accuracy, parse rate, majority baseline, n. CLI prints a table to stderr and a flat JSON dict as the last stdout line. |
| `check.py` | The connection check (below). |

Flow: wiki `supports_targets` -> `select_tasks` -> for each corpus x task: `Task.prompt(record)` -> `Model.generate` -> `parse_choice` (first standalone capital A/B) -> scores. Unparseable output counts as wrong and lowers `parse_rate`.

## Metrics
Flat keys `<source>/<task>/{accuracy,balanced_accuracy,parse_rate,majority_baseline,n}`, plus `mean_*` over all cells, `model`, `n`, `unsupported_targets` and `data_hash` (SHA-256 prefix of the data dir). **Primary metric: `mean_balanced_accuracy`.** Read accuracy next to `majority_baseline`: a model that always answers the common class already scores that.

## How to run
```
uv run python -m oncolens.check                                   # connection check, no GPU, exit 1 on failure
uv run python -m oncolens.bench --model fixed:A --limit 10        # wiring smoke run
uv run --extra gpu python -m oncolens.bench --model <hf-id>       # real run (Colab / GPU)
```
Options: `--data data --wiki wiki-llm --limit N` (N test patients per source; limited runs are not comparable to full ones).

## Connection check (`guard_cmd`)
Runs on the real files; one PASS/FAIL line per seam: (1) every record parses against the contract, (2) patient ids unique across corpora and splits, (3) no outcome value in any body and every rendered prompt equals body + fixed task text, (4) wiki targets resolve to registered tasks, (5) train/test patient-disjoint, (6) full `run` with `fixed:A` over every (source, task) matches hand-computed always-A accuracy.

## Known limits
- Both tasks are binary and ignore follow-up time; `overall-survival` is "deceased at end of follow-up".
- `Systemic agents` in real records come from full follow-up and may reflect later disease course (see `data/msk-chord-mini/README.md`), so scores can be optimistic.
- Parsing takes the first standalone capital A/B, so a sentence starting with the article "A" would be misread.
