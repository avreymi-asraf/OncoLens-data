---
type: literature
node_id: lit:tabular-synth-benchmarks
title: "Benchmarks of tabular synthetic data generators for health (SynMeter, TabDDPM-EHR, health evaluation framework)"
year: 2025
tags: ["synthetic-data", "tabular", "benchmark"]
updated: 2026-10-31
---
# Tabular generator benchmarks

- **SynMeter** (arXiv 2402.06806): tuned TabDDPM is best on fidelity and utility but weaker on privacy.
- **Ceritli et al.** (arXiv 2302.14679): TabDDPM beats others on mixed-type EHR on all metrics except privacy → privacy–utility trade-off.
- **Health evaluation framework** (PMC12058740, 2025): 5 generators × 3 medical datasets, with/without differential privacy; DP improves privacy, often costs fidelity/utility.
- Tooling: **synthcity** (fidelity, utility, fairness, privacy metrics), **SDV/SDGym**.

Target match: `G4`. Use as a baseline for a one-row-per-patient feature table.
