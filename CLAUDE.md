# Project instructions

Empirical paper: energy efficiency of LLM-generated code (Claude, GPT, Gemini via their
official CLIs) across Python/Java/C++ and several hardware platforms. Authors: Brisild Capani,
Seyyid. Overview: `README.md`.

## Language
- Talk to the authors in German. Notes and docs in `notes/` and `experiment/*.md` are German.
- The paper (`paper/`) and code comments are English.

## Keep the decision log up to date (mandatory)
Every methodological decision, deviation, or noteworthy observation (e.g. a dataset bug, a
measurement problem, a pilot result, a changed parameter) must be added to
`notes/entscheidungsprotokoll.md` **in the same turn**, with: ID, date, decision/observation,
rationale, the paper section where it belongs, and whether the paper already mentions it
(✅ / ⏳ / 🔁 superseded). Also update the "Offene Punkte fürs Paper" list at the end.
When a decision changes, mark the old entry 🔁 and add a new one; never silently rewrite.

## Keep other docs consistent
- If a change affects the design, update `notes/experimental-design.md`.
- If a change affects folder contents, update `README.md` and `experiment/ERKLAERUNG.md`.
- If the paper states something the experiment no longer does, fix the paper and log it.

## Conventions
- **Length limit: target 500 words, hard ceiling about 700–800 words** for the paper body,
  excluding references and abstract (given requirement). Check the word count after every
  substantial paper edit (`texcount`) and prefer cutting over adding. Keep all important
  points, but state each in one sentence; details go to tables and the replication package.
  See decision G6.
- Results are hypotheses until measured; never write findings into the paper before data exist.
- Prompt templates are included verbatim in the paper appendix from `experiment/prompts/`.
- Verify citations against arXiv/Crossref before adding them to `paper/references.bib`.
- Build the paper with `cd paper && latexmk -pdf main.tex` (output in `paper/build/`).
