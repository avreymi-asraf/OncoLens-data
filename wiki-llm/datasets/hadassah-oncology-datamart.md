---
type: dataset
node_id: ds:hadassah-oncology-datamart
title: "Hadassah Oncology DataMart"
maintainer: "Hadassah Medical Center — Prof. Shai Rosenberg's team"
url: "https://www.thejc.com/sponsored/how-hadassah-hospital-is-transforming-cancer-care-k2jerv34"
access: in-hospital-only
license: "Hospital-internal; Helsinki approval required"
n_patients: "≈260,000 patient records (claimed); 30,000 cancer patient records used for one validation"
time_span: "unknown; Hadassah computerized records date to the 1980s (fundraising source)"
modalities: [structured, notes, genomic]
oncology_coverage: "all oncology (assumed)"
language: "he + en (assumed — verify)"
data_model: "unknown"
supports_targets: [overall-survival, progression, treatment-response, toxicity, ed-visit-admission, short-term-mortality, metastasis]
resemblance_to_hadassah: high
credibility: C (sponsored fundraising article, Oct 2026)
primary_doc_read: "yes — JC sponsored article (full text)"
updated: 2026-10-31
---
# Hadassah Oncology DataMart

## What it is
A sponsored Hadassah UK feature (JC, 1 Oct 2026) says Prof. Rosenberg and team built the **Oncology DataMart**, "one of Israel's largest oncology databases", which "integrates 260,000 patient records with sophisticated genomic analysis". The same piece mentions an AI model by Rosenberg that detects "a significant genetic mutation found in around half of all tumours" at **96.5% accuracy**, "now being validated using data from 30,000 cancer patient records".

Related published work from the same group: **MESiCA** (Yaacov … Rosenberg, *Cell Reports Medicine* 2024) — neural embeddings that detect dominant mutational signatures from targeted-panel data with few mutations; validated on >60,000 cancer samples ([Hadassah press release](https://www.hadassah.org/press-release/ai-model-developed-by-hadassah-cancer-research-institute-can-detect-dominant-mutational-signatures-using-only-a-few-mutations)). The press release does not say whether Hadassah EMR data was used.

## Why it matters
This is most likely the real data OncoLens will train on. Every other page in `datasets/` is either (a) a public proxy to develop methods before access, (b) an external validation cohort, or (c) a synthetic substitute.

## Caveats
- Single, promotional source. "260,000 patient records" vs. "30,000 cancer patient records" — the unit is unclear (patients? documents? all-hospital vs. oncology?). Ask the supervisors.
- If the cohort is defined by genomic sequencing (as the "genomic analysis" framing suggests), it inherits the same **selection bias** MSK-CHORD reports: sequenced patients over-represent advanced or progressing disease ([[literature/jee-2024-msk-chord]]).

## Sources
- [JC sponsored feature (Hadassah UK), 2026](https://www.thejc.com/sponsored/how-hadassah-hospital-is-transforming-cancer-care-k2jerv34) — C
- [Hadassah press release on MESiCA, Jul 2024](https://www.hadassah.org/press-release/ai-model-developed-by-hadassah-cancer-research-institute-can-detect-dominant-mutational-signatures-using-only-a-few-mutations) — B
- [Technion alumni profile: Head of AI in Oncology](https://excellence.technion.ac.il/alumni/?id=2697) — B
