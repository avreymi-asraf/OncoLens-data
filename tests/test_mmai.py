"""Tests for oncolens.mmai. Offline by default; the one network test is marked and skipped unless ``-m network``."""

from __future__ import annotations

import json
from typing import Any

import pytest

from oncolens import mmai

HISTORY = (
    "The patient is a 58-year-old female named Test Person.\n"
    "At age 58, the patient was diagnosed with stage IIA (T2N1M0) invasive ductal carcinoma of the breast, "
    "primary site C50.9, histology 8500/3.\n"
    "{e0}\n"
    "At age 58, the patient began adjuvant doxorubicin.\n"
    "{e1}\n"
    "At age 63, due to a new diagnosis of hormone-refractory disease, switched to fulvestrant.\n"
    "{e2}"
)
EVENTS = [
    ("pathology_report", "At age 58, surgical pathology showed invasive ductal carcinoma."),
    ("imaging_report", "At age 60, surveillance CT showed no metastatic lesions."),
    ("clinical_note", "At age 63, PET-CT showed metastatic disease; cancer present and progressing."),
]


def masked(i: int) -> str:
    parts = {}
    for j, (doc_type, text) in enumerate(EVENTS):
        wrapped = f"<BEGIN EVENT CORRESPONDING TO SYNTHETIC NOTE> <{doc_type}>{text} "
        wrapped += "<END EVENT CORRESPONDING TO SYNTHETIC NOTE>"
        parts[f"e{j}"] = wrapped if j == i else text
    return HISTORY.format(**parts)


def note_rows(mrn: int, split: str = "train", positive: int = 1) -> list[dict[str, Any]]:
    return [
        {
            "pseudo_mrn": mrn,
            "event_type": doc_type,
            "event_text": text,
            "masked_text": masked(i),
            "synthetic_note": f"**Report {i}** for patient {mrn}",
            "split": split,
            "note_is_from_positive_prompt": positive,
        }
        for i, (doc_type, text) in enumerate(EVENTS)
    ]


# ---- grouping -------------------------------------------------------------------------------------------------


def test_group_consecutive_keeps_groups_split_across_batches():
    batches = [[1, 1], [1, 2], [2, 3]]  # a group that straddles batch boundaries, as pyarrow batches do
    rows = (x for batch in batches for x in batch)
    assert [(k, len(g)) for k, g in mmai.group_consecutive(rows, key=lambda x: x)] == [(1, 3), (2, 2), (3, 1)]


def test_group_consecutive_rejects_ungrouped_input():
    with pytest.raises(ValueError, match="not contiguous"):
        list(mmai.group_consecutive([1, 2, 1], key=lambda x: x))


# ---- parsing --------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("diagnosed with stage IIA (T2N1M0) carcinoma", "IIA"),
        ("clinical stage III (AJCC 8th) with TNM T4a N2 M0, summary stage: III", "III"),
        ("T3c N1 M0, Stage IIIC (AJCC 8th)", "IIIC"),
        ("Stage IIIb disease", "IIIB"),
        ("stage IVB (AJCC 8th)", "IVB"),
        ("stage 4 disease", "IV"),
        ("stage IIIC2 endometrial", "IIIC2"),
        ("FIGO stage IB3 cervical", "IB3"),
        ("summary stage: II, grade 2", None),
        ("extensive-stage small cell lung cancer", None),
        ("the stage is unknown", None),
        ("overall AJCC stage III (IIIb), T3 N1", "IIIB"),
        ("stage III (IVa) mismatch keeps the group", "III"),
    ],
)
def test_parse_stage(text: str, expected: str | None):
    parsed = mmai.parse_stage(text)
    assert (parsed[0] if parsed else None) == expected


def test_strip_event_markers_restores_plain_timeline():
    history = mmai.strip_event_markers(masked(1))
    assert "<" not in history and ">" not in history
    assert history == mmai.strip_event_markers(masked(0)) == mmai.strip_event_markers(masked(2))
    assert EVENTS[1][1] in history.splitlines()


def test_parse_diagnoses_skips_lines_without_stage_or_codes():
    diagnoses = mmai.parse_diagnoses(mmai.strip_event_markers(masked(0)))
    assert len(diagnoses) == 1  # "new diagnosis of hormone-refractory disease" has no stage/ICD/TNM evidence
    assert diagnoses[0]["age"] == 58 and diagnoses[0]["stage"] == "IIA"


def test_parse_document_dates():
    text = "2019-07-16 pathology_report **Path** x\n2019-12-26 imaging_report body\n2020-01-01 is not a header"
    assert mmai.parse_document_dates(text) == [("2019-07-16", "pathology_report"), ("2019-12-26", "imaging_report")]
    assert mmai.parse_document_dates(None) == []


# ---- patient assembly -----------------------------------------------------------------------------------------


def test_build_patient_shape_and_y():
    trial = {"nct_id": "NCT0", "title": "T", "this_space": "S", "eligibility_result": 0.0}
    dates = [("2019-07-16", "pathology_report"), ("2020-01-02", "imaging_report"), ("2024-05-06", "clinical_note")]
    patient = mmai.build_patient(note_rows(7), trial=trial, dates=dates)
    assert patient["patient_id"] == mmai.opaque_patient_id(7) and patient["split"] == "train"
    assert patient["pseudo_mrn"] == 7 and "flag" in patient["documents"][0]
    assert [d["seq"] for d in patient["documents"]] == [0, 1, 2]
    assert [d["date"] for d in patient["documents"]] == [d for d, _ in dates]
    y = patient["y"]
    assert y["diagnoses"][0]["stage"] == "IIA"
    assert [e["age"] for e in y["document_events"]] == [58, 60, 63]
    assert y["trial"] == {
        "nct_id": "NCT0",
        "title": "T",
        "space": "S",
        "designed_eligible": True,
        "llm_judged_eligible": False,
    }


def test_build_patient_leaves_dates_null_when_headers_do_not_line_up():
    dates = [("2019-07-16", "pathology_report"), ("2024-05-06", "clinical_note")]  # one note missing
    patient = mmai.build_patient(note_rows(7), dates=dates)
    assert all(d["date"] is None for d in patient["documents"])


def test_build_patient_without_y():
    assert mmai.build_patient(note_rows(7), with_y=False)["y"] is None


def test_build_patient_rejects_mixed_splits():
    rows = note_rows(7)
    rows[1]["split"] = "test"
    with pytest.raises(ValueError, match="several splits"):
        mmai.build_patient(rows)


def test_model_input_carries_no_answers():
    patient = mmai.build_patient(note_rows(7), trial={"nct_id": "NCT0", "this_space": "S", "eligibility_result": 1})
    blob = json.dumps(mmai.model_input(patient))
    assert set(mmai.model_input(patient)) == {"patient_id", "documents"}
    for leak in ["BEGIN EVENT", "At age", "stage IIA", "NCT0", "progressing", "pseudo_mrn", '"split"', "flag"]:
        assert leak not in blob
    assert set(mmai.model_input(patient)["documents"][0]) == set(mmai.MODEL_DOCUMENT_KEYS)


def test_patients_from_rows_filters_split_and_limits():
    rows = note_rows(1, "train") + note_rows(2, "test") + note_rows(3, "test") + note_rows(4, "test")
    test_patients = list(mmai.patients_from_rows(iter(rows), split="test", limit=2))
    assert [p["pseudo_mrn"] for p in test_patients] == [2, 3]
    assert list(mmai.patients_from_rows(iter(rows), limit=0)) == []
    with pytest.raises(ValueError):
        list(mmai.patients_from_rows(iter(rows), split="dev"))


def test_main_writes_jsonl(monkeypatch, tmp_path, capsys):
    rows = note_rows(1) + note_rows(2)
    rows[0]["event_text"] = "(This line omitted to comply with criteria)"
    requested = {}

    def fake_iter_rows(filename, columns, **kwargs):
        requested["columns"] = list(columns)
        return iter(rows)

    monkeypatch.setattr(mmai, "iter_rows", fake_iter_rows)
    monkeypatch.setattr(mmai, "load_trial_labels", lambda **k: pytest.fail("--model-input must not load y"))
    out = tmp_path / "p.jsonl"
    mmai.main(["--limit", "2", "--model-input", "-o", str(out)])
    lines = [json.loads(line) for line in out.read_text().splitlines()]
    assert [p["patient_id"] for p in lines] == [mmai.opaque_patient_id(1), mmai.opaque_patient_id(2)]
    assert all(set(p) == {"patient_id", "documents"} for p in lines)
    assert "event_text" in requested["columns"] and "masked_text" not in requested["columns"]
    assert [d["seq"] for d in lines[0]["documents"]] == [1, 2]  # placeholder flagged even without y


def test_opaque_patient_id_hides_mrn():
    ids = {mmai.opaque_patient_id(m) for m in (1, 2, 999_999, 1_000_000)}
    assert len(ids) == 4 and all(i.startswith("mmai-") and len(i) == 17 for i in ids)
    assert mmai.opaque_patient_id(5) == mmai.opaque_patient_id(5)


def test_sample_is_deterministic_and_spread():
    kept = [m for m in range(1, 20_001) if mmai.sample_bucket(m) < 0.05]
    assert 800 < len(kept) < 1200
    assert kept[0] < 200 and kept[-1] > 19_800
    rows = [r for m in range(1, 200) for r in note_rows(m)]
    first = [p["pseudo_mrn"] for p in mmai.patients_from_rows(iter(rows), sample=0.1, limit=5)]
    assert first == [m for m in range(1, 200) if mmai.sample_bucket(m) < 0.1][:5]


@pytest.mark.parametrize(
    ("note", "event", "flag"),
    [
        ("I’m sorry, but I can’t help with that.", "At age 50, CT showed progression.", "refusal"),
        ("", "At age 50, CT showed progression.", "refusal"),
        ("**Report** long clinical text", "(This line omitted to comply with criteria)", "placeholder_event"),
        (
            "**Report** long clinical text",
            "but we can treat as an event type not listed; skip this.)",
            "placeholder_event",
        ),
        ("**Report** long clinical text", "At age 50, CT showed progression.", None),
        ("**Report** long clinical text", "Post‑operative day 2, the patient was ambulating.", None),
        ("**Report** long clinical text", "At week 3, MRI showed partial response.", None),
        ("**Report** long clinical text", "The oncologist noted progression.", None),
        ("**Report** long clinical text", None, None),
    ],
)
def test_document_flag(note, event, flag):
    assert mmai.document_flag(note, event) == flag


def test_model_input_drops_flagged_documents_but_keeps_seq():
    rows = note_rows(7)
    rows[1]["synthetic_note"] = "I'm sorry, but I can't help with that."
    patient = mmai.build_patient(rows)
    assert [d["flag"] for d in patient["documents"]] == [None, "refusal", None]
    assert [d["seq"] for d in mmai.model_input(patient)["documents"]] == [0, 2]
    assert len(mmai.model_input(patient, include_flagged=True)["documents"]) == 3


def test_registry_line_without_diagnosis_word_is_a_diagnosis():
    line = "At age 52, primary site C50.9, histology 8500/3, pT1c N0 M0, stage IA."
    assert mmai.is_diagnosis_line(line)
    assert not mmai.is_diagnosis_line("At age 52, the patient began adjuvant doxorubicin.")


def test_iter_patients_rejects_bad_arguments_before_any_download(monkeypatch):
    monkeypatch.setattr(mmai, "iter_rows", lambda *a, **k: pytest.fail("must not download"))
    for kwargs in [{"split": "dev"}, {"limit": -1}, {"sample": 0}, {"with_y": False, "with_summary": True}]:
        with pytest.raises(ValueError):
            mmai.iter_patients(with_dates=True, **kwargs)
    assert list(mmai.iter_patients(limit=0, with_dates=True)) == []


# ---- live smoke test ------------------------------------------------------------------------------------------


@pytest.mark.network
def test_stream_first_patients_from_hub():
    patients = list(mmai.iter_patients(limit=2))
    assert [p["pseudo_mrn"] for p in patients] == [1, 2]
    first = patients[0]
    assert len(first["documents"]) == 16 and first["documents"][0]["type"] == "pathology_report"
    assert first["y"]["diagnoses"][0]["stage"] == "IIA"
    assert first["y"]["trial"]["nct_id"]
