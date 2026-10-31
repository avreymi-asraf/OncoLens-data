---
type: finding
topic: data-source-landscape
status: active
confidence: initial
supporting_experiments: []
updated: 2026-10-31
---
# Finding: Data-source landscape for OncoLens

> Raw: `wiki-llm/datasets/*.md` (23 pages), `wiki-llm/literature/*.md`. Research run 2026-10-31, English + Hebrew searches, ~45 queries, primary documents read where marked on each page.

## Summary Thesis
No public dataset replaces Hadassah's EMR — the gap is Hebrew notes, Israeli practice patterns, and a full longitudinal oncology course. The useful plan is in **three tiers**: (1) public *proxies* to build and test the method before data access (MSK-CHORD first), (2) *external validation* cohorts (GENIE BPC internationally; Clalit / Sourasky / INCR in Israel), and (3) *synthetic* data generated inside Hadassah for sharing and for code development (see [[findings/synthetic-data-strategy]]).

## 1. The story in order
1. **The primary asset already exists.** Hadassah's Oncology DataMart (≈260K patient records + genomics, Rosenberg team) [[datasets/hadassah-oncology-datamart]] — single promotional source; units unclear. Hadassah has also been a TriNetX node since 2018 [[datasets/trinetx]] and streams EHR data to trial systems via YonaLink, so some EMR→standard mapping work has likely been done already ([[systems/hadassah-emr]]).
2. **The best public analogue is MSK-CHORD** [[datasets/msk-chord]]: same recipe (EMR + panel genomics + NLP-derived note features → survival), published baselines (c-index 0.58–0.83), open on cBioPortal. Its labels come from **GENIE BPC / PRISSMM** curation [[datasets/aacr-genie-bpc]], which therefore is the label schema to copy.
3. **Hebrew is the main technical gap.** No public Hebrew clinical corpus exists. The nearest resources come from **Tel Aviv Sourasky**: HeMed (Hebrew clinical encoder, IRB-restricted) and a 108K-note irAE (toxicity) pipeline [[datasets/sourasky-imedata]], [[datasets/hebrew-clinical-nlp]].
4. **Israeli data at scale exists but sits behind collaborations:** Clalit, Maccabi KSM, MoH TIMNA, INCR [[datasets/clalit-research]], [[datasets/maccabi-ksm]], [[datasets/israel-moh-timna]], [[datasets/israel-national-cancer-registry]].
5. **Synthetic data is feasible but its value depends on the generator.** Rule-based (Synthea) = plumbing only; learned generators (HALO, CEHR-GPT, TabDDPM, MDClone) need real data to train on, so they must run inside Hadassah and pass privacy audits before anything leaves.

## 2. Sources × candidate targets (planning matrix)
Legend: ● strong, ◐ partial, ○ none. Access: O open, C credentialed/DUA, A application/collaboration, $ commercial, H in-hospital.

| Source | Access | OS | Progression | Tx response | Toxicity | ED/admission | Short-term mortality | Metastasis | Hebrew | Role |
|---|---|---|---|---|---|---|---|---|---|---|
| Hadassah DataMart | H | ● | ● | ● | ● | ● | ● | ● | ● (verify) | **primary** |
| MSK-CHORD | O | ● | ● | ◐ | ○ | ○ | ◐ | ● | ○ | proxy + benchmark |
| GENIE BPC | C | ● | ● | ● | ○ | ○ | ◐ | ● | ○ | external validation, label schema |
| MIMIC-IV (+Note) | C | ◐ | ○ | ○ | ◐ | ● | ● | ○ | ○ | pipeline proxy |
| EHRSHOT / MOTOR | C | ◐ | ○ | ○ | ○ | ● | ◐ | ○ | ○ | foundation-model methods |
| TCGA-Reports + GDC | O | ● | ○ | ○ | ○ | ○ | ○ | ◐ | ○ | text→stage, text+genomics→OS |
| CORAL | C | ○ | ◐ | ◐ | ○ | ○ | ○ | ◐ | ○ | IE evaluation only |
| Project Data Sphere | A | ● | ● | ◐ | ● | ○ | ◐ | ○ | ○ | trial endpoints |
| SEER | A | ● | ○ | ○ | ○ | ○ | ○ | ◐ | ○ | survival priors |
| NCDB | — | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | **not accessible** |
| Flatiron | $ | ● | ● | ● | ◐ | ◐ | ● | ◐ | ○ | endpoint definitions |
| TriNetX | $ (member) | ◐ | ○ | ○ | ◐ | ● | ● | ○ | ○ | aggregate generalization checks |
| INCR | A | ● | ○ | ○ | ○ | ○ | ○ | ◐ | n/a | death/stage ground truth |
| TIMNA (MoH) | A | ● | ○ | ○ | ○ | ● | ● | ○ | n/a | national linkage |
| Clalit | A | ● | ◐ | ● | ◐ | ● | ● | ◐ | ● | Israeli external validation |
| Maccabi KSM | A | ● | ○ | ◐ | ○ | ◐ | ● | ○ | ◐ | community outcomes |
| Sourasky I-Medata | A | ◐ | ◐ | ◐ | ● | ◐ | ◐ | ◐ | ● | Hebrew NLP, toxicity |
| Synthea | O | ◐ | ○ | ○ | ○ | ◐ | ◐ | ○ | ○ | code tests only |
| CancerGUIDE / Asclepius | O | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ | note-generation templates |

## 3. Subsurface insights (not visible from any single source)
1. **The ND in MSK-CHORD's license matters.** CC BY-NC-ND forbids distributing derivatives. A synthetic dataset *trained on* MSK-CHORD, or a released re-processed version, may not be shareable. Plan to publish code and metrics, not derived data.
2. **MSK-CHORD's NLP labels came from GENIE BPC curators, and many were wrong.** In discrepant cases clinicians judged the curator label incorrect. Any gold set built at Hadassah needs double curation (as PRISSMM QA does) — otherwise the label noise sets the ceiling.
3. **Sequencing-defined cohorts are biased toward sick patients.** MSK-CHORD admits this; the Hadassah DataMart's "records + genomic analysis" framing suggests the same risk. Cohort definition (`G1`) should state whether entry requires a genomic test.
4. **Hadassah's TriNetX membership (2018) implies an existing standard-terminology mapping.** If Hadassah IT can expose it, schema harmonization (`G2`) and a synthetic twin become much cheaper. Inference — verify.
5. **Chameleon (Elad Health) runs in >80% of Israeli hospitals, including Sourasky.** If Hadassah also uses it, Sourasky's Hebrew NLP work (HeMed, irAE) was built on the same note structure. Not confirmed for Hadassah — top question for `G2`.
6. **MDClone validations never tested prediction.** Rambam and WashU showed synthetic derivatives reproduce *descriptive* statistics. Whether a model trained on synthetic derivatives keeps its discrimination on real longitudinal oncology data is open — a publishable experiment (`G4`). Also: no evidence Hadassah runs MDClone.
7. **Israeli rules reportedly block public LLM APIs for patient data (MoH, 2026 — press source, confirm).** LLM-generated Hebrew synthetic notes must be produced by on-prem models inside Hadassah, and the source data never leaves.
8. **NCDB is closed to us; SEER just opened.** NCDB requires a US CoC-accredited institution. SEER removed country/email restrictions on 13 June 2025.
9. **Outcome leakage through notes.** Groups using MIMIC-IV-Note drop discharge summaries because they state the outcome. Same risk at Hadassah: any note written after time zero, or summarizing the course, must be excluded.
10. **Unclear numbers about the DataMart.** "260,000 patient records" vs "30,000 cancer patient records" in the same article — whether 260K is patients, documents, or all-hospital is unknown.

## 4. Credibility notes
- A-grade (peer-reviewed / official, read in full or near-full): MSK-CHORD, MIMIC-IV-Note page, EHRSHOT repo, Synthea module source, CancerGUIDE card, SEER/NCDB official pages.
- C/D-grade (promotional or social): Oncology DataMart numbers, Hadassah "Integrative Medical Intelligence", MDClone client lists, Flatiron sizes. Treat as leads, not facts.

## 5. Recommended next steps (for discussion with supervisors)
1. Fix `G1` (target, cohort, time zero) — the matrix in §2 shows OS and progression have the most external support.
2. Start method development on **MSK-CHORD** now (no approvals needed); reproduce its RSF baseline as the reference.
3. Ask Hadassah IT the `G2` questions in [[systems/hadassah-emr]].
4. Apply for **GENIE BPC** (Synapse) as the international external validation set.
5. Open conversations with **Sourasky** (HeMed access) and **Clalit** (Israeli validation).
6. Build a Synthea-based fake Hadassah-shaped dataset for CI tests; plan an in-hospital synthetic twin per [[findings/synthetic-data-strategy]].

## Open Hypotheses
See [[gap_map]] G1–G7.
