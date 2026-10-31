---
type: dataset
node_id: ds:israel-moh-timna
title: "TIMNA — Israel Ministry of Health Big Data research platform (תמנע)"
maintainer: "Israel Ministry of Health"
url: "https://research-vp.tau.ac.il/sites/resauth.tau.ac.il/files/MOH%20%D7%A7%D7%95%D7%9C%20%D7%A7%D7%95%D7%A8%D7%90-BIG%20DATA.pdf"
access: application
license: "Research inside MoH cloud research rooms; Helsinki approval; data stays in the platform"
n_patients: "national (MoH + regulated reporting bodies)"
time_span: "varies by source"
modalities: [structured, registry]
oncology_coverage: "indirect (national registries reported to MoH)"
language: "he / coded"
data_model: "MoH-specific"
supports_targets: [overall-survival, ed-visit-admission]
resemblance_to_hadassah: medium
credibility: B (MoH call for proposals, MoH documents) / C (press)
primary_doc_read: "partial — search summaries of the MoH call (TAU-hosted PDF) and MoH COVID research-room document"
updated: 2026-10-31
---
# TIMNA (תמנע) — MoH Big Data research platform

## What it is
MoH's national research-data platform, built on MoH databases and data that health bodies report to MoH under regulation. Research runs in **supervised cloud research rooms**; data collected by a researcher stays in TIMNA after the study. The COVID-19 research database (2020) used the same model and required Helsinki approval. A government plan expands TIMNA access to academic and industry researchers.

## Regulatory context found while searching (Hebrew sources)
- **MoH Director-General circulars 2018** (MK01-2018, MK02-2018) define *secondary use of health data* (research and development, not direct care) and interim rules for inter-organization collaborations, based on draft OECD guidance.
- **Health-data portability bill memo (2023)** — receiving/transferring identified medical data would require a licensed officer (memo stage only; final status unverified).
- **MoH directive (2026)** — health organizations must not enter organizational data, patient medical data, staff data or code into **public** generative-AI interfaces. Directly relevant to any LLM-based synthetic-note generation: it must run on approved / on-prem models.
- No MoH guidance specific to **synthetic data** was found.

## Why it matters
A possible second Israeli cohort (national outcomes, linkage) and the governing framework for anything that leaves Hadassah.

## Sources
- [MoH Big Data call for proposals (TAU research authority PDF)](https://research-vp.tau.ac.il/sites/resauth.tau.ac.il/files/MOH%20%D7%A7%D7%95%D7%9C%20%D7%A7%D7%95%D7%A8%D7%90-BIG%20DATA.pdf) — B
- [MoH COVID research-room document](https://www.gov.il/BlobFolder/dynamiccollectorresultitem/answer1_277/he/לפרסום%20632520.pdf) — B
- [MoH circular MK01-2018](https://www.gov.il/BlobFolder/policy/mk01-2018/he/files_circulars_mk_MK01_2018.pdf), [MK02-2018](https://www.gov.il/BlobFolder/policy/mk02-2018/he/files_circulars_mk_MK02_2018.pdf) — A (official)
- [IDI opinion on national health records bill](https://www.idi.org.il/knesset-committees/63227) — B
- [Shibolet law firm on the 2023 bill memo](https://www.shibolet.com/שינויים-בשימוש-במידע-הרפואי-תזכיר-החו/) — B
- [Mako 2026 on MoH genAI directive](https://www.mako.co.il/news-lifestyle/2026_q1/Article-1fc042e638dbc91027.htm) — C
