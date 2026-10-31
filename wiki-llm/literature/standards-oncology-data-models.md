---
type: literature
node_id: lit:standards-oncology-data-models
title: "Oncology data standards: OMOP Oncology extension, mCODE (FHIR), MEDS, PRISSMM"
year: 2026
tags: ["data-model", "omop", "fhir", "meds", "standards"]
updated: 2026-10-31
---
# Oncology data standards

| Standard | What it gives | Status |
|---|---|---|
| **OMOP CDM + Oncology extension** (OHDSI Oncology WG) | `EPISODE` / `EPISODE_EVENT` tables for disease and treatment episodes; cancer modifiers (stage, grade, mets) in `MEASUREMENT`; vocabularies ICD-O-3, NAACCR, HemOnc, CAP; NAACCR ETL | Extension not fully ratified into vanilla CDM (per 2022 WG update / Vanderbilt docs) |
| **mCODE** (HL7 FHIR IG, ASCO + MITRE) | Minimal oncology elements: disease characterization, staging, treatment intent, genomics; STU4 build on US Core 6.1 | Active; US-centric profiles |
| **MEDS** (Medical Event Data Standard) | Minimal event-stream schema for ML; used by EHRSHOT, MOTOR, CEHR-GPT | Active; best for ML pipelines |
| **PRISSMM** (GENIE BPC) | Curation model: per pathology report / imaging report / oncologist assessment | De facto for real-world progression labels |

## Recommendation for `G2`
Map Hadassah data to **MEDS** for modelling (lightweight, tools exist), keep OMOP-oncology episode concepts for lines of therapy and staging, and use **PRISSMM definitions** for any manually curated labels. This choice also makes CEHR-GPT / MOTOR / EHRSHOT tooling usable as-is.

## Sources
- [OHDSI Oncology extension forum](https://forums.ohdsi.org/t/oncology-extension/12909), [Onc WG 2022 update](https://www.ohdsi.org/wp-content/uploads/2022/04/Onc-WG-2022-Community-Update-April-2022.pdf)
- [mCODE IG](https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ImplementationGuide-hl7.fhir.us.mcode.html)
- [MEDS (OHDSI 2026 slides)](https://www.ohdsi.org/wp-content/uploads/2026/05/Meds-Slidedeck.pdf)
- [GENIE BPC QA / PRISSMM (PMC8863125)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8863125/)
