---
type: dataset
node_id: ds:trinetx
title: "TriNetX federated network (Hadassah is a member since 2018)"
maintainer: "TriNetX"
url: "https://hadassahinternational.org/hadassah-is-first-israeli-hospital-to-join-global-research-network/"
access: commercial
license: "Member institutions; self-service aggregate queries; datasets by agreement"
n_patients: ">100M patients, 15 countries"
time_span: "varies"
modalities: [structured]
oncology_coverage: "all (coded diagnoses, meds, labs; oncology module varies)"
language: "coded"
data_model: "TriNetX standard model (terminologies assumed ICD/LOINC/RxNorm-style — inference, verify)"
supports_targets: [overall-survival, ed-visit-admission, short-term-mortality]
resemblance_to_hadassah: high (Hadassah data is in it, presumably)
credibility: B (Hadassah + TriNetX press releases)
primary_doc_read: "yes — Hadassah International announcement (Sept 2018)"
updated: 2026-10-31
---
# TriNetX

Hadassah became the **first Israeli hospital to join TriNetX** (4 Sept 2018, led by Prof. Eyal Mishani, R&D). Shaare Zedek joined in July 2023.

## Why it matters (inference — verify)
1. Joining TriNetX normally requires mapping the local EMR to TriNetX's standard terminologies. If that mapping exists at Hadassah, it is a ready-made **schema harmonization** — useful as the target schema for synthetic data and for OMOP/MEDS conversion.
2. Through the network, Hadassah investigators can run **aggregate cohort queries on global data** — a cheap way to check whether a Hadassah finding generalizes.

## Sources
- [Hadassah International, 2018](https://hadassahinternational.org/hadassah-is-first-israeli-hospital-to-join-global-research-network/) — B
- [TriNetX press: Hadassah joins](https://trinetx.com/?p=127659) — C
- [Shaare Zedek joins, 2023](https://www.prnewswire.com/il/news-releases/shaare-zedek-medical-center-joins-the-trinetx-network-to-increase-clinical-trial-participation-and-attain-access-to-global-real-world-data-for-investigator-initiated-research-301880047.html) — C
