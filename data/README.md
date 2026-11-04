# `data/` — patient records as Markdown

One Markdown file per patient. Real and synthetic records share **exactly one shape**, so no consumer
(benchmark, trainer, notebook) can tell them apart except through the `source` field.

```
data/
  msk-chord-mini/      source: msk-chord        real, de-identified subset of MSK-CHORD   (split: test)
  synthetic-chord/     source: synthetic-chord  schema-faithful synthetic twin            (split: train | test)
```

Each corpus folder holds `<patient_id>.md` files and a `README.md` stating provenance and license.

## Record shape (the contract)

```markdown
---
patient_id: P-0001234          # synthetic: S-000042
source: msk-chord              # msk-chord | synthetic-chord
split: test                    # train | test — decided per patient, never per file
cancer_type: Non-Small Cell Lung Cancer
outcomes:                      # ground truth; NEVER part of a prompt
  os_status: DECEASED          # LIVING | DECEASED
  os_months: 14.2
  metastatic_sites: [Bone, Liver]   # sorted subset of the NLP site vocabulary below; [] when none
---
# Patient P-0001234

## Demographics
- Sex: Female
- Age: 63
- Smoking: Former/Current

## Disease
- Cancer type: Non-Small Cell Lung Cancer
- Highest recorded stage: Stage 4
- Tumor registry entries: 1
- Biomarkers: PD-L1 history: Yes          # only fields that were reported; omit the line if none

## Treatment
- Prior medication before MSK: No prior medications
- Systemic agents, in order: CARBOPLATIN, PEMETREXED
```

Rules:

1. **Everything under `outcomes:` is withheld from models.** The Markdown body must not contain or imply any
   outcome value (no survival, no metastatic-site list, no `DECEASED`). A consumer renders prompts from the body only.
2. Site vocabulary (from MSK-CHORD NLP tumour-site flags): `Adrenal Glands, Bone, CNS/Brain, Intra Abdominal,
   Liver, Lung, Lymph Node, Other, Pleura, Reproductive Organs`.
3. Frontmatter keys and section headings are fixed. Optional lines may be absent; sections may not.
4. `split` is patient-level. A patient id appears in exactly one split of exactly one corpus.
5. No file contains free-text clinical notes or anything that is not derived from the structured columns above.

## Provenance and license

MSK-CHORD (Jee et al., *Nature* 2024) is **CC BY-NC-ND 4.0**. This repository is private and used for
non-commercial research. The real subset is verbatim values from the public release (no modification of
values, only re-formatting) and must not be redistributed. The synthetic corpus is sampled from aggregate
statistics, not from a model fitted on records, and is likewise kept inside this private repository until the
supervisors decide otherwise (see `wiki-llm/datasets/msk-chord.md`, Caveats).
