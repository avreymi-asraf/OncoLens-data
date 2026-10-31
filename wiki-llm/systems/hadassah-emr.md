---
type: system
node_id: sys:hadassah-emr
title: "Hadassah Ein Kerem oncology EMR (primary project data)"
status: placeholder
updated: 2026-10-31
---
# System: Hadassah Ein Kerem Oncology EMR

> Repo: none (data lives inside the hospital) | Fingerprint: n/a
> Monitored: n/a — no patient data in any repo, ever. See [[purpose]] §3.

## What is known (from AGENT.md and public sources)
- **Source:** EMR of cancer patients treated at Hadassah Ein Kerem. Clinical, longitudinal, sensitive (PHI).
- **Owner/steward on the project:** Dr. Shai Rosenberg — Head of AI in Oncology / Computational Medicine Service at Hadassah ([HUJI page](https://medicine.ada.huji.ac.il/en/research/shair/Pages/research.aspx)). Works with Hadassah IT on "clinically applicable Digital Medicine and AI projects".
- **Likely underlying asset:** the **Oncology DataMart** — see [[datasets/hadassah-oncology-datamart]] (≈260K patient records + genomic analysis; sponsored source, unverified).
- **Hadassah has joined TriNetX (Sept 2018)** — first Israeli hospital to do so ([Hadassah Intl.](https://hadassahinternational.org/hadassah-is-first-israeli-hospital-to-join-global-research-network/)). A TriNetX node normally means local EMR data is mapped to TriNetX's standard model; see [[datasets/trinetx]].
- **EHR-to-EDC:** Hadassah uses YonaLink to stream EHR data into clinical-trial EDC systems ([press](https://oilnow.gy/business-wire/hadassah-selects-yonalinks-ehr-to-edc-clinical-trial-platform-to-securely-and-seamlessly-integrate-clinical-care-and-research-data/)). Implies an existing EHR → structured mapping layer.
- **Hadassah "Data Research Unit"** and a "data lake" combining genomic, lab, clinical and imaging data are mentioned on Hadassah fundraising sites (credibility C).
- **"Integrative Medical Intelligence" platform** — a Hadassah staff LinkedIn post claims a national strategic mandate from the Israel Innovation Authority to build a multimodal, longitudinal hospital+community data platform. Unverified (credibility D). Context: the Innovation Authority + MoH funded research-data infrastructure in health organizations (₪40M to 19 programs in 2022, ₪55M in 2021).

## TODO — ask the supervisors / Hadassah IT (do not guess)
- [ ] EMR vendor and version. (Elad Health's **Chameleon** runs in >80% of Israeli hospitals incl. government and Clalit hospitals; Hadassah not confirmed.)
- [ ] Which tables exist: demographics, diagnoses (ICD-9/10? ICD-O-3?), staging, pathology, labs, medications/chemo orders, radiotherapy, imaging reports, free-text notes (Hebrew / English / mixed), death dates (linked to population registry?), genomic panels.
- [ ] Time span, number of oncology patients, per-cancer-type counts (aggregate only).
- [ ] Is there an existing OMOP / TriNetX / MDClone mapping we can reuse?
- [ ] Access model: on-prem secure room? Remote enclave? Can de-identified or synthetic derivatives leave the hospital?
- [ ] Helsinki (IRB) approval status and scope.
- [ ] Is there a Hebrew de-identification tool in use (e.g. Safe Harbor)?

## Experiment Language
Not defined yet. Record the canonical data model (proposed: MEDS or OMOP — see [[literature/standards-oncology-data-models]]) once chosen.
