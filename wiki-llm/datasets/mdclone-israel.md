---
type: dataset
node_id: ds:mdclone-israel
title: "MDClone ADAMS platform & synthetic derivatives (Israeli hospitals)"
maintainer: "MDClone (Be'er Sheva) + host hospitals"
url: "https://medinform.jmir.org/2020/2/e16492/"
access: in-hospital-only
license: "Per host institution; synthetic derivatives may be shareable under host policy"
n_patients: "per host"
time_span: "per host"
modalities: [structured]
oncology_coverage: "per host"
language: "n/a (structured)"
data_model: "MDClone event model"
supports_targets: [overall-survival, ed-visit-admission, short-term-mortality]
resemblance_to_hadassah: high (if Hadassah had it — not confirmed)
credibility: A (Rambam JMIR 2020; WashU JAMIA Open 2021) / C (vendor and press)
primary_doc_read: "no — abstracts + summaries"
updated: 2026-10-31
---
# MDClone (synthetic derivatives of real hospital data)

## What it is
A self-service analytics platform (ADAMS) that builds cohorts from a hospital's EMR and can output **synthetic derivatives**: simulated patients that reproduce aggregate statistics without a 1:1 real counterpart.

**Israeli footprint (verified to different degrees):**
- **Rambam** — first health system to implement MDClone; published the validation paper (A).
- **Sheba** — anchor client, first ADAMS Center; Leumit + Sheba built a merged MDClone-based database of Leumit patients treated at Sheba (Innovation Israel page, B).
- **Tel Aviv Sourasky**, **Maccabi** (2017 partnership) — client lists (C).
- MDClone won a **Ministry of Finance tender** for a research-room platform using synthetic, de-identified data (C).
- **Hadassah: no evidence found** in EN or HE searches.

## Evidence on fidelity
- **Rambam, JMIR Med Inform 2020** (Reiner Benaim et al.): 5 observational studies; synthetic results "predictive of" real results. [[literature/reiner-benaim-2020-mdclone-rambam]]
- **WashU, JAMIA Open 2021** ("Spot the difference"): 3 use cases, same conclusion.
- **N3C** preprint compared MDClone derivatives on a 34-site COVID cohort.
- **Gap:** all validations are *descriptive / observational* analyses. None tests whether a **predictive model trained on synthetic derivatives** transfers to real data on a longitudinal oncology task. That is an open, publishable question ([[gap_map]] `G4`).

## Sources
- [Reiner Benaim et al., JMIR Med Inform 2020](https://medinform.jmir.org/2020/2/e16492/) — A
- [Foraker et al., "Spot the difference", JAMIA Open](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7886551/) — A
- [Innovation Israel: research infrastructures in Israeli health](https://innovationisrael.org.il/?p=37064) — B
- [NoCamels 2021](https://nocamels.com/2021/07/israel-mdclone-synthetic-data-healthcare/), [KrASIA](https://kr-asia.com/israels-mdclone-uses-synthetic-data-to-help-health-providers-roll-out-better-smarter-care) — C
