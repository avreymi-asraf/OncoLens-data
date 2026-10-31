---
type: literature
node_id: lit:pang-2024-cehr-gpt
title: "CEHR-GPT: Generating EHR with chronological patient timelines"
year: 2024
tags: ["synthetic-data", "omop", "meds", "generative"]
updated: 2026-10-31
---
# Pang et al., arXiv 2402.04400 (2024)

## One-Line Thesis
GPT over a CEHR-BERT-style patient representation that encodes **time intervals** generates timelines that convert back to OMOP with almost no temporal loss; utility = similar outcome prevalence and similar model performance; privacy = membership and attribute inference risks reported low.

## Reusable Ingredients
* If Hadassah data is mapped to OMOP/MEDS, CEHR-GPT is the most direct way to get a **shareable synthetic OMOP twin** (pip `cehrgpt`, MEDS supported). Target match: `G4`, `G2`.

## Limitations
OMOP-coded events only; oncology episodes (lines of therapy, staging) depend on OMOP oncology extension coverage.
