---
type: dataset
node_id: ds:<slug>
title: "<Dataset name>"
maintainer: "<org>"
url: "<direct URL>"
access: open | credentialed-DUA | application | commercial | in-hospital-only | method/tool
loader: "oncolens.<module> | none yet"   # none yet = a model cannot read this dataset today
license: "<license>"
n_patients: "<number or unknown>"
time_span: "<years>"
modalities: [structured, notes, genomic, imaging, registry]
oncology_coverage: "<cancer types / none>"
language: "<en / he / ...>"
data_model: "<OMOP / FHIR / mCODE / MEDS / PRISSMM / custom>"
supports_targets: [overall-survival, progression, treatment-response, toxicity, ed-visit-admission, short-term-mortality, metastasis]
resemblance_to_hadassah: high | medium | low
credibility: A (peer-reviewed/official primary) | B (official secondary / docs) | C (vendor / press / sponsored) | D (unverified)
primary_doc_read: "yes — <which> | no"
updated: 2026-10-31
---
# <Dataset name>

## What it is
## Access path
## Reading it with a model
<!-- Loader and how to call it, the measured shape (patients, documents, dates, y coverage), what is broken or missing. If there is no loader: what stands in the way. -->
## Why it matters for OncoLens
## Caveats
## Sources
