# AI usage

DRAFT - review and correct this before submitting. It must match what was really done.

## Assistants used

| Assistant | Where | What it was used for |
|---|---|---|
| Claude Code (Anthropic), in VS Code | Part 1 | Reviewing the notebook against the lab handout, writing and restructuring notebook cells, running the notebook to test it, and drafting `README.md` and `requirements.txt` |

## Part 1 in more detail

- The first version of the pipeline (ingestion, figure and table extraction, hybrid retrieval, answer generation, conversation handling, evaluation) was written by the team member without an assistant.
- Claude Code then helped with: Kaggle-compatible paths and settings, one ChromaDB collection for all items, rule-based detection of user-supplied values, per-conversation memory, a safe calculator for arithmetic, always adding the documents' revision notices to the evidence, the evaluation metrics, the safety probes for Document 3 Appendix C, and the 25-question golden set.
- No answers or question-specific rules are written into the code.

## How the golden set was used (honest account)

- The 25-question golden set was written before the system was changed and committed to Git first (commit `c9a95c3`). No question in it comes from `Questions.csv`.
- System changes were developed and checked against the public `Questions.csv`, which is a practice set.
- After the golden set was written, its results were looked at twice: to choose between the 3B and 7B vision-language models (the 7B model in 4-bit scored higher and was kept), and to read the failures. Prompt changes made after reading the failures were limited to general ones that the public questions also showed: full-sentence answers, no bare "not_found" text, and no repeated calculation text.
- The golden-set scores in the report are therefore a fair comparison of baseline and final system, but they are not a completely untouched hold-out.

## Parts 2 and 3

Not started yet. Add details here when they are done.
