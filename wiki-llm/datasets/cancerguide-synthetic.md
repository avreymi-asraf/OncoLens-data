---
type: dataset
node_id: ds:cancerguide-synthetic
title: "CancerGUIDE synthetic NSCLC patient notes (Microsoft Research)"
maintainer: "Microsoft Research"
url: "https://huggingface.co/datasets/microsoft/CancerGUIDE"
access: open
license: "Card says CC BY 4.0; repo metadata says MIT — reconcile before reuse"
n_patients: "316 notes (165 structured-derived, 151 unstructured)"
time_span: "n/a"
modalities: [notes]
oncology_coverage: "NSCLC"
language: "en"
data_model: "patient_id, patient_note, label (25 treatment classes)"
supports_targets: [treatment-response]
resemblance_to_hadassah: low
credibility: A (dataset card read; arXiv 2509.07325)
primary_doc_read: "yes — HF dataset card"
updated: 2026-10-31
---
# CancerGUIDE synthetic notes

GPT-4.1-generated NSCLC notes, each labelled with a guideline treatment recommendation; paired paper has a 121-case expert-annotated real-note benchmark. **Use:** a worked example of LLM-generated oncology notes with labels by construction, and a template for generating **Hebrew** synthetic notes on-prem. Single snapshot per patient, not a timeline.

## Sources
- [HF dataset card](https://huggingface.co/datasets/microsoft/CancerGUIDE) — A
- [arXiv 2509.07325 (hyper.ai mirror)](https://hyper.ai/de/papers/2509.07325) — B
