"""Stream the DFCI MatchMiner-AI synthetic oncology corpus from Hugging Face, one JSON object per patient.

Source: ``ksg-dfci/mmai-synthetic-1225`` (CC BY-NC 4.0, fully synthetic). Nothing is written to disk: parquet
files are read over HTTP range requests with ``HfFileSystem`` + ``pyarrow``, only the needed columns, in a
forward stream. ``all_synthetic_notes.parquet`` is a single 7 GB row group with no page index, so random
access is not possible; the notes are sorted by ``pseudo_mrn`` and each patient's notes are contiguous, so
patients come out one at a time with bounded memory (~0.5 GB RSS, ~1,000 notes/s, a full pass ~15 min; the first
patient arrives after ~10-20 s).

Each yielded patient::

    {
      "patient_id": "mmai-3f2a9c41d07e",   # opaque hash of pseudo_mrn (the raw MRN leaks the design label)
      "pseudo_mrn": 1, "split": "train",
      "source": {"repo": ..., "revision": ..., "license": "CC BY-NC 4.0"},
      "documents": [{"seq": 0, "type": "pathology_report", "date": "2019-07-16" | None, "text": "...",
                     "flag": None | "refusal" | "placeholder_event"}, ...],
      "y": {...} | None,      # answers taken from the generator side; never put this in the model input
    }

``model_input(patient)`` is the object to hand to a model: ``patient_id`` plus ``documents`` reduced to
``seq/type/date/text``, without flagged documents (LLM refusals such as "I'm sorry, but I can't help with that."
and notes generated from placeholder events -- 3 documents in the whole corpus). No split, source, MRN or ``y``.

What ``y`` holds (all from the dataset, nothing invented; see ``wiki-llm/datasets/mmai-synthetic.md``):

* ``event_history`` -- the generator's full longitudinal timeline the notes were written from ("At age 58, ...").
* ``diagnoses`` -- timeline lines that state a cancer diagnosis, in timeline order (for multi-primary patients the
  trial-relevant cancer is usually the last one), with a regex-parsed overall stage (``stage``, Roman numerals, may
  be None) next to the raw text. Parsing is a convenience, not a gold label.
* ``document_events`` -- per document, the timeline event it was the generation prompt for (e.g. "cancer present
  and progressing"). Free text: there is no RECIST CR/PR/SD/PD code in the dataset. Caveat: the generator saw the
  whole timeline, so a note's text can mention events dated later than its own event.
* ``trial`` -- the clinical-trial "space" the patient was generated for, whether the generator was asked to make
  the patient eligible (``designed_eligible``), and an LLM judge's eligibility call (disagrees with the design for
  about a third of patients).
* ``patient_summary`` -- an LLM-written summary of the patient (only with ``with_summary=True``).

Order: patients come in ``pseudo_mrn`` order, which is grouped by trial space and by design (all designed-eligible
patients first). ``limit=N`` alone therefore gives a narrow, all-eligible slice; use ``sample=`` (a deterministic
hash-based fraction) for a spread-out subset -- it still reads through the file to collect it.

Typical use::

    from oncolens import mmai
    for patient in mmai.iter_patients(split="test", sample=0.01, limit=20, with_dates=True):
        prompt_json = mmai.model_input(patient)
        answer = patient["y"]

CLI (JSON Lines to stdout or a file)::

    uv run python -m oncolens.mmai --split test --sample 0.01 --limit 20 --dates -o /tmp/mmai_test20.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import re
import sys
from collections.abc import Callable, Generator, Hashable, Iterable, Iterator, Sequence
from typing import Any, TypeVar

REPO_ID = "ksg-dfci/mmai-synthetic-1225"
REVISION = "b1845aaed70b8106868e0369c4c013ad24b48e72"  # main as of 2025-12-15
LICENSE = "CC BY-NC 4.0"
NOTES_FILE = "all_synthetic_notes.parquet"
SUMMARIES_FILE = "patient_summaries_and_their_spaces.parquet"
ELIGIBILITY_FILE = "space_specific_eligibility_checks.parquet"
N_PATIENTS = 63_865
N_DOCUMENTS = 846_577
DOC_TYPES = ("clinical_note", "imaging_report", "pathology_report", "ngs_report")
SPLITS = ("train", "val", "test")
MODEL_DOCUMENT_KEYS = ("seq", "type", "date", "text")

_READ_BLOCK = 32 << 20  # bytes per HTTP range read and per pyarrow column-chunk buffer

T = TypeVar("T")
K = TypeVar("K", bound=Hashable)


# --------------------------------------------------------------------------------------------------------------
# Reading from Hugging Face
# --------------------------------------------------------------------------------------------------------------


def iter_rows(
    filename: str, columns: Sequence[str], *, revision: str = REVISION, batch_size: int = 512
) -> Iterator[dict[str, Any]]:
    """Yield rows (as dicts of the requested columns) of one parquet file of the dataset, streamed from the Hub.

    Only the requested columns are fetched, page by page (``pre_buffer=False`` + ``buffer_size``), so memory stays
    bounded even though the files are written as a single huge row group.
    """
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem

    path = f"datasets/{REPO_ID}@{revision}/{filename}"
    with HfFileSystem().open(path, block_size=_READ_BLOCK, cache_type="none") as fh:
        parquet = pq.ParquetFile(fh, buffer_size=_READ_BLOCK, pre_buffer=False)
        for batch in parquet.iter_batches(batch_size=batch_size, columns=list(columns)):
            yield from batch.to_pylist()


def load_trial_labels(*, revision: str = REVISION, with_summary: bool = False) -> dict[int, dict[str, Any]]:
    """Map pseudo_mrn -> trial-space labels (nct_id, title, space, LLM eligibility[, patient_summary]).

    ~5-15 s and a few MB without the summary; ``with_summary`` adds ~80 MB of download.
    """
    columns = ["pseudo_mrn", "nct_id", "title", "this_space", "eligibility_result"]
    if with_summary:
        columns.append("patient_summary")
    return {row.pop("pseudo_mrn"): row for row in iter_rows(ELIGIBILITY_FILE, columns, revision=revision)}


_LONG_TEXT_HEADER = re.compile(r"(?m)^(\d{4}-\d{2}-\d{2}) (" + "|".join(DOC_TYPES) + r")\b")


def parse_document_dates(patient_long_text: str | None) -> list[tuple[str, str]]:
    """Return the ``(date, doc_type)`` headers of a ``patient_long_text`` (the dated, chunk-filtered note concat)."""
    return _LONG_TEXT_HEADER.findall(patient_long_text or "")


def load_document_dates(*, revision: str = REVISION) -> dict[int, list[tuple[str, str]]]:
    """Map pseudo_mrn -> ordered ``(date, doc_type)`` list. Streams ~1 GB of ``patient_long_text``: ~3-4 min.

    The dates exist only in ``patient_long_text`` (synthetic ``YYYY-MM-DD`` per note); only the headers are kept.
    """
    return {
        row["pseudo_mrn"]: parse_document_dates(row["patient_long_text"])
        for row in iter_rows(SUMMARIES_FILE, ["pseudo_mrn", "patient_long_text"], revision=revision, batch_size=256)
    }


# --------------------------------------------------------------------------------------------------------------
# Pure helpers (no network; unit-tested)
# --------------------------------------------------------------------------------------------------------------


def group_consecutive(items: Iterable[T], key: Callable[[T], K]) -> Iterator[tuple[K, list[T]]]:
    """Group consecutive items by ``key``; raise if a key comes back after its group ended (input not grouped)."""
    seen: set[K] = set()
    for k, group in itertools.groupby(items, key=key):
        if k in seen:
            raise ValueError(f"key {k!r} is not contiguous: the input is not grouped by this key")
        seen.add(k)
        yield k, list(group)


def _mrn_digest(mrn: int) -> str:
    return hashlib.sha256(f"{REPO_ID}:{mrn}".encode()).hexdigest()


def opaque_patient_id(mrn: int) -> str:
    """Stable ID that reveals nothing: raw pseudo_mrn values below 1e6 are exactly the designed-eligible patients."""
    return "mmai-" + _mrn_digest(mrn)[:12]


def sample_bucket(mrn: int) -> float:
    """Deterministic pseudo-random number in [0, 1) per patient, for ``sample=`` subsets spread across the file."""
    return int(_mrn_digest(mrn)[12:20], 16) / 16**8


_EVENT_MARKERS = re.compile(
    r"<BEGIN EVENT CORRESPONDING TO SYNTHETIC NOTE>\s*(?:<[a-z_]+>)?|\s*<END EVENT CORRESPONDING TO SYNTHETIC NOTE>"
)
_AGE = re.compile(r"^\s*At (?:the )?age (?:of )?(\d{1,3})\b", re.I)
_ROMAN = r"(0|IV|I{1,3}|[1-4])"
_STAGE = re.compile(r"(?<!summary )\bstage\s*:?\s*" + _ROMAN + r"([A-D]?[1-3]?)(?![A-Za-z0-9])", re.I)
_STAGE_REFINEMENT = re.compile(r"\s*\(\s*(?:stage\s*)?" + _ROMAN + r"([A-D][1-3]?)\s*\)", re.I)
_DIAGNOSIS_WORD = re.compile(r"\bdiagnos[ie]s|\bdiagnosed\b", re.I)
_DIAGNOSIS_EVIDENCE = re.compile(r"\bstage\b|\bC\d{2}(?:\.\d)?\b|\b\d{4}/\d\b|\bT[0-4x][a-d]?\s*N[0-3x]", re.I)
_ICD_O_SITE = re.compile(r"\bC\d{2}(?:\.\d)?\b")
_ICD_O_MORPHOLOGY = re.compile(r"\b\d{4}/\d\b")
_ARABIC_TO_ROMAN = {"0": "0", "1": "I", "2": "II", "3": "III", "4": "IV"}
_REFUSAL = re.compile(r"\s*(?:I(?:'|’)m sorry|I am sorry|Sorry,|I can(?:'|’)t (?:help|comply|assist)|I cannot )", re.I)
_PLACEHOLDER_EVENT = re.compile(r"\s*(?:[(\[]|(?:but|so|we|skip|okay|ok|let's|let us|note:)\b)", re.I)


def strip_event_markers(masked_text: str) -> str:
    """Turn a ``masked_text`` (timeline with one event wrapped in markers) into the plain timeline."""
    return _EVENT_MARKERS.sub("", masked_text).strip()


def age_of(event_line: str | None) -> int | None:
    """Age in years from a timeline line that starts with 'At age N', else None."""
    match = _AGE.match(event_line or "")
    return int(match.group(1)) if match else None


def _roman(group: str) -> str:
    return _ARABIC_TO_ROMAN.get(group, group.upper())


def parse_stage(text: str) -> tuple[str, str] | None:
    """First overall stage mention in ``text`` as ``(normalized, raw)``, e.g. ``("IIIB", "stage IIIb")``.

    Normalization: Roman group (Arabic 1-4 -> I-IV) + upper-case sub-stage. "summary stage" is skipped. A
    parenthetical refinement of the same group is used: "stage III (IIIb)" -> "IIIB".
    """
    match = _STAGE.search(text)
    if not match:
        return None
    group, sub, raw = _roman(match.group(1)), match.group(2).upper(), match.group(0)
    if not sub:
        refinement = _STAGE_REFINEMENT.match(text, match.end())
        if refinement and _roman(refinement.group(1)) == group:
            sub, raw = refinement.group(2).upper(), text[match.start() : refinement.end()]
    return group + sub, raw


def is_diagnosis_line(line: str) -> bool:
    """A timeline line stating a cancer diagnosis: a 'diagnos*' word with stage/ICD-O/TNM evidence, or a registry
    style line with both an ICD-O site and morphology code."""
    if _DIAGNOSIS_WORD.search(line) and _DIAGNOSIS_EVIDENCE.search(line):
        return True
    return bool(_ICD_O_SITE.search(line) and _ICD_O_MORPHOLOGY.search(line))


def parse_diagnoses(event_history: str) -> list[dict[str, Any]]:
    """Diagnosis lines of a timeline, in order, each with age, parsed stage (or None), raw stage text and the line."""
    diagnoses = []
    for line in event_history.splitlines():
        if is_diagnosis_line(line):
            stage = parse_stage(line)
            diagnoses.append(
                {
                    "age": age_of(line),
                    "stage": stage[0] if stage else None,
                    "stage_raw": stage[1] if stage else None,
                    "text": line.strip(),
                }
            )
    return diagnoses


def document_flag(synthetic_note: str | None, event_text: str | None) -> str | None:
    """Why a generated document is not a usable clinical note, or None.

    "refusal": empty, or the generator refused ("I'm sorry, but I can't help with that."). "placeholder_event": the
    note was generated from a non-event -- a bracketed placeholder ("(This line omitted to comply with criteria)") or
    leaked generator chatter ("but we can treat as an event type not listed; ..."). Real events need not start with
    "At age N" (~4% start "At month 3", "Post-operative day 2", "The oncologist ..."), so that is not a test.
    Full corpus at the pinned revision: 1 refusal, 2 placeholder events. ``event_text`` is None when y columns were
    absent; then only refusals are seen.
    """
    note = (synthetic_note or "").strip()
    if not note or (len(note) < 600 and _REFUSAL.match(note)):
        return "refusal"
    if event_text is not None and (not event_text.strip() or _PLACEHOLDER_EVENT.match(event_text)):
        return "placeholder_event"
    return None


def build_patient(
    notes: Sequence[dict[str, Any]],
    *,
    trial: dict[str, Any] | None = None,
    dates: Sequence[tuple[str, str]] | None = None,
    with_y: bool = True,
    revision: str = REVISION,
) -> dict[str, Any]:
    """Assemble one patient object from that patient's note rows (in file order) and optional side tables.

    Dates are attached only when the ``(date, type)`` headers line up one-to-one with the notes' types; otherwise
    every ``date`` is None (4.5% of patients: the long text dropped a note, or lists two adjacent notes in swapped
    order). Type-aligned dates were content-checked on 400 patients: 5,578/5,578 segments matched their note.
    """
    mrn = notes[0]["pseudo_mrn"]
    splits = {n["split"] for n in notes}
    if len(splits) != 1:
        raise ValueError(f"patient {mrn} has notes in several splits: {sorted(splits)}")
    types = [n["event_type"] for n in notes]
    aligned = dates is not None and [t for _, t in dates] == types
    documents = [
        {
            "seq": seq,
            "type": note["event_type"],
            "date": dates[seq][0] if aligned and dates is not None else None,
            "text": note["synthetic_note"] or "",
            "flag": document_flag(note["synthetic_note"], note.get("event_text")),
        }
        for seq, note in enumerate(notes)
    ]
    patient: dict[str, Any] = {
        "patient_id": opaque_patient_id(mrn),
        "pseudo_mrn": mrn,
        "split": splits.pop(),
        "source": {"repo": REPO_ID, "revision": revision, "license": LICENSE},
        "documents": documents,
        "y": None,
    }
    if with_y:
        history = strip_event_markers(notes[0]["masked_text"] or "")
        y: dict[str, Any] = {
            "event_history": history,
            "diagnoses": parse_diagnoses(history),
            "document_events": [
                {"seq": seq, "age": age_of(n["event_text"]), "event": n["event_text"]} for seq, n in enumerate(notes)
            ],
            "trial": None,
            "patient_summary": None,
        }
        positive = {n["note_is_from_positive_prompt"] for n in notes}
        if trial is not None or len(positive) == 1:
            eligibility = (trial or {}).get("eligibility_result")
            y["trial"] = {
                "nct_id": (trial or {}).get("nct_id"),
                "title": (trial or {}).get("title"),
                "space": (trial or {}).get("this_space"),
                "designed_eligible": bool(positive.pop()) if len(positive) == 1 else None,
                "llm_judged_eligible": None if eligibility is None else bool(eligibility),
            }
        if trial is not None:
            y["patient_summary"] = trial.get("patient_summary")
        patient["y"] = y
    return patient


def model_input(patient: dict[str, Any], *, include_flagged: bool = False) -> dict[str, Any]:
    """The JSON object to give a model: opaque patient id and its documents (seq/type/date/text) -- no answers.

    Flagged documents (refusals, placeholder events) are left out unless ``include_flagged``; ``seq`` keeps the
    original positions, so a gap shows where one was dropped.
    """
    documents = [
        {k: doc[k] for k in MODEL_DOCUMENT_KEYS}
        for doc in patient["documents"]
        if include_flagged or doc.get("flag") is None
    ]
    return {"patient_id": patient["patient_id"], "documents": documents}


def _check_selection(split: str | None, limit: int | None, sample: float | None) -> None:
    if split is not None and split not in SPLITS:
        raise ValueError(f"split must be one of {SPLITS}, got {split!r}")
    if limit is not None and limit < 0:
        raise ValueError(f"limit must be >= 0, got {limit}")
    if sample is not None and not 0 < sample <= 1:
        raise ValueError(f"sample must be in (0, 1], got {sample}")


def patients_from_rows(
    rows: Iterable[dict[str, Any]],
    *,
    split: str | None = None,
    limit: int | None = None,
    sample: float | None = None,
    with_y: bool = True,
    trial_labels: dict[int, dict[str, Any]] | None = None,
    document_dates: dict[int, list[tuple[str, str]]] | None = None,
    revision: str = REVISION,
) -> Iterator[dict[str, Any]]:
    """Group note rows (sorted by pseudo_mrn) into patient objects; the network-free core of ``iter_patients``."""
    _check_selection(split, limit, sample)
    if limit == 0:
        return
    emitted = 0
    for mrn, notes in group_consecutive(rows, key=lambda r: r["pseudo_mrn"]):
        if split is not None and notes[0]["split"] != split:
            continue
        if sample is not None and sample_bucket(mrn) >= sample:
            continue
        yield build_patient(
            notes,
            trial=None if trial_labels is None else trial_labels.get(mrn),
            dates=None if document_dates is None else document_dates.get(mrn),
            with_y=with_y,
            revision=revision,
        )
        emitted += 1
        if limit is not None and emitted >= limit:
            return


# --------------------------------------------------------------------------------------------------------------
# Public entry point
# --------------------------------------------------------------------------------------------------------------


def iter_patients(
    *,
    split: str | None = None,
    limit: int | None = None,
    sample: float | None = None,
    with_y: bool = True,
    with_dates: bool = False,
    with_summary: bool = False,
    revision: str = REVISION,
    batch_size: int = 512,
) -> Generator[dict[str, Any], None, None]:
    """Stream patients of the MMAI synthetic corpus from the Hub, in pseudo_mrn order.

    Args:
        split: keep only "train", "val" or "test" patients (splits are per patient; the stream still reads past
            the others).
        limit: stop after this many yielded patients.
        sample: keep a deterministic hash-based fraction of patients (e.g. 0.01), spread over the whole file.
        with_y: attach ``y`` (reads the timeline and per-note event columns plus the small trial-label table).
        with_dates: attach a date to each document. Costs a ~3-4 min pass over ``patient_long_text`` up front.
        with_summary: also put the LLM ``patient_summary`` into ``y`` (requires ``with_y``).
        revision: dataset commit to read; pinned by default for reproducibility.
        batch_size: rows per pyarrow batch.

    Arguments are checked here, before any download starts.
    """
    _check_selection(split, limit, sample)
    if with_summary and not with_y:
        raise ValueError("with_summary puts the summary into y, so it requires with_y=True")
    return _iter_patients(split, limit, sample, with_y, with_dates, with_summary, revision, batch_size)


def _iter_patients(
    split: str | None,
    limit: int | None,
    sample: float | None,
    with_y: bool,
    with_dates: bool,
    with_summary: bool,
    revision: str,
    batch_size: int,
) -> Generator[dict[str, Any], None, None]:
    if limit == 0:
        return
    columns = ["pseudo_mrn", "event_type", "synthetic_note", "split", "event_text"]  # event_text: needed for flags
    if with_y:
        columns += ["masked_text", "note_is_from_positive_prompt"]
    trial_labels = load_trial_labels(revision=revision, with_summary=with_summary) if with_y else None
    document_dates = load_document_dates(revision=revision) if with_dates else None
    rows = iter_rows(NOTES_FILE, columns, revision=revision, batch_size=batch_size)
    yield from patients_from_rows(
        rows,
        split=split,
        limit=limit,
        sample=sample,
        with_y=with_y,
        trial_labels=trial_labels,
        document_dates=document_dates,
        revision=revision,
    )


def main(argv: Sequence[str] | None = None) -> None:
    """Write patients as JSON Lines (one patient object per line)."""
    parser = argparse.ArgumentParser(prog="python -m oncolens.mmai", description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--split", choices=SPLITS)
    parser.add_argument("--limit", type=int, help="number of patients (default: all 63,865)")
    parser.add_argument("--sample", type=float, help="deterministic fraction of patients, spread over the file")
    parser.add_argument("--dates", action="store_true", help="attach document dates (~3-4 min extra up front)")
    parser.add_argument("--summary", action="store_true", help="include the LLM patient_summary in y")
    parser.add_argument("--no-y", action="store_true", help="omit y entirely (faster, smaller)")
    parser.add_argument("--model-input", action="store_true", help="write only model_input(patient) (implies --no-y)")
    parser.add_argument("--revision", default=REVISION)
    parser.add_argument("-o", "--output", help="JSONL path (default: stdout)")
    args = parser.parse_args(argv)
    with_y = not (args.no_y or args.model_input)
    if args.limit is not None and args.limit <= 0:
        parser.error("--limit must be a positive number")
    if args.summary and not with_y:
        parser.error("--summary goes into y; it cannot be combined with --no-y or --model-input")
    try:
        patients = iter_patients(
            split=args.split,
            limit=args.limit,
            sample=args.sample,
            with_y=with_y,
            with_dates=args.dates,
            with_summary=args.summary,
            revision=args.revision,
        )
    except ValueError as error:
        parser.error(str(error))

    out = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    try:
        for patient in patients:
            record = model_input(patient) if args.model_input else patient
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
        out.flush()
    except BrokenPipeError:  # e.g. piped into `head`: stop quietly
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    finally:
        patients.close()  # release the HTTP file handle now
        if out is not sys.stdout:
            out.close()


if __name__ == "__main__":
    main()
