# Wiki-LLM Chronological Audit Log (`log.md`)

> Append-only record. Format: `## [YYYY-MM-DD HH:MM] <operation> | <target> — <one-line summary>`
> Query recent history with: `grep "^## \[" wiki-llm/log.md | tail -n 10`

## [2026-10-31 22:35] init+ingest | wiki-llm — Initialized wiki-llm/ in OncoLens-data (OncoLens-expriments layout + datasets/). Ingested data-source survey (EN+HE iterative research): 23 dataset pages, 9 literature notes, 2 findings (data-source-landscape, synthetic-data-strategy), gaps G1–G7
## [2026-11-14 18:50] update | purpose, gap_map, index, findings, AGENT.md — Recorded research focus: small LM extracting RECIST 1.1 response and overall stage (third variable TBD) from oncology records; stated repo goal (find/generate and make accessible research data); narrowed G1; flagged survey as predating target
## [2026-11-14 21:30] ingest+code | datasets/mmai-synthetic, oncolens/mmai.py — Added DFCI MMAI synthetic corpus (1225 release, CC BY-NC) page and a Hub-streaming loader yielding one JSON object per patient (documents + generator-side y); validated over the full corpus
## [2026-11-14 22:10] update | AGENT.md, CLAUDE.md, purpose, index, gap_map, datasets/_TEMPLATE — Restated the repo purpose as the user's own words had it (get or generate data, make it accessible in a uniform way to models); wiki is the memory of that work, not the product; AGENT.md loaded via CLAUDE.md; dataset template gained `loader` and 'Reading it with a model'
