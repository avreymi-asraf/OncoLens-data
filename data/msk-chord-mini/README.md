# msk-chord-mini

60 real, de-identified patients from the public MSK-CHORD release (Jee et al., *Nature* 2024,
cBioPortal study `msk_chord_2024`), one Markdown file each, all `split: test`.
The record shape is defined in `data/README.md`.

| Cancer type | LIVING | DECEASED |
|---|---|---|
| Breast Cancer | 6 | 6 |
| Colorectal Cancer | 6 | 6 |
| Non-Small Cell Lung Cancer | 6 | 6 |
| Pancreatic Cancer | 6 | 6 |
| Prostate Cancer | 6 | 6 |

## Provenance and license
- Source: https://www.cbioportal.org/study/summary?id=msk_chord_2024, Memorial Sloan Kettering Cancer Center.
- License: **CC BY-NC-ND 4.0**. Non-commercial research only, no redistribution, and no derivative may be published.
  This folder stays inside the private OncoLens repository.
- Values are verbatim from the release; only the layout changed (`os_months` is printed to 0.1 month).

## How it was built
Eligible patients have exactly one cancer type and known sex, age and stage. For every cancer type,
6 LIVING and 6 DECEASED patients were drawn at random with seed `2024`.
- `metastatic_sites`: the NLP tumour-site flags that are `Yes` (`Unknown` counts as absent).
- `Systemic agents, in order`: anti-cancer agents (chemo, hormone, targeted, biologic, immuno, investigational)
  by first start day. These come from the full follow-up, so they can reflect later disease course.
- `Biomarkers`: PD-L1 history, HR, HER2 and Gleason score, only where reported.

## Regenerate
`uv run scripts/extract_chord.py <raw msk_chord_2024 dir> --seed 2024 --per-group 6`
