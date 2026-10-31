---
type: dataset
node_id: ds:synthea
title: "Synthea (rule-based synthetic patient generator)"
maintainer: "MITRE / synthetichealth"
url: "https://github.com/synthetichealth/synthea/tree/master/src/main/resources/modules"
access: open
license: "Apache-2.0"
n_patients: "unlimited (generated)"
time_span: "simulated lifetimes"
modalities: [structured]
oncology_coverage: "modules: breast_cancer, colorectal_cancer, lung_cancer, acute_myeloid_leukemia, veteran_lung_cancer, veteran_prostate_cancer (+ bone_marrow_transplant)"
language: "en (FHIR / CSV / OMOP-ish exports)"
data_model: "FHIR R4, C-CDA, CSV"
supports_targets: [overall-survival]
resemblance_to_hadassah: low
credibility: A (module source code read; Chen et al. 2019 validation)
primary_doc_read: "yes — module directory listing + breast/colorectal/lung module JSON"
updated: 2026-10-31
---
# Synthea

## What it is
State-machine simulator of whole patient lifetimes, exporting FHIR. Oncology modules found in the repo (Oct 2026):

| Module | States | Content (from reading the JSON) |
|---|---|---|
| `breast_cancer` (+ submodules `tnm_diagnosis`, `hormone_diagnosis`, `chemotherapy_breast`, `hormonetherapy_breast`, `surgery_therapy_breast`) | 109 | screening mammogram, symptoms, stage I–IV, neoadjuvant chemo cycles, surgery + radiation, improvement/worsening, death. Sources: Komen, ACS |
| `colorectal_cancer` | 106 | adenoma → cancer, screening, stage I–IV, chemo counter, care plans, eventual death |
| `lung_cancer` (+ `lung_cancer_probabilities`) | 99 | stage I–IV, SCLC vs NSCLC chemo, radiation, death. Sources: ACS, Cancer Care Ontario pathway maps |
| `acute_myeloid_leukemia`, `veteran_prostate_cancer`, `veteran_lung_cancer` | — | not inspected |

## Verdict for OncoLens
**Pipeline plumbing only.** Synthea follows guidelines by construction; Chen et al. (2019) showed it "does not model deviations in care" and their outcomes. The lung module has no biomarker-driven therapy states (no EGFR/ALK/PD-L1 found in state names). So there is no realistic signal for treatment response or toxicity. Good for: testing ETL code, FHIR/OMOP conversion, splits and time-zero logic, CI fixtures with zero PHI risk.

## Sources
- [Synthea modules directory](https://github.com/synthetichealth/synthea/tree/master/src/main/resources/modules) — A (read)
- [Chen et al., BMC Med Inform Decis Mak 2019](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6416981/) — A, see [[literature/chen-2019-synthea-validity]]
- [OHDSI 2024 poster evaluating Synthea](https://ohdsi.org/wp-content/uploads/2024/10/41-Wagner-Evaluating_Synthea-Clair-Blacketer.pdf) — B
- [Mendeley: Synthea lung-cancer ML dataset](https://data.mendeley.com/datasets/b24cb4nn8h/1) — B
