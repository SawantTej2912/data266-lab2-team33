# AI usage

This file lists the AI assistants we used for the code and documents in this repository, and what we used them for. It covers Part 1 so far. Parts 2 and 3 will be added when they are done.

## ChatGPT

Used outside the repository for:

- discussing the architecture of the Part 1 system;
- debugging help;
- implementation guidance;
- designing the evaluation;
- drafting parts of the report.

## Claude Code (Anthropic), in VS Code

Used inside the repository for:

- inspecting the repository and the notebook;
- diagnosing extraction and retrieval problems;
- making code and repository edits.

In the latest Claude Code session it made substantial edits to `notebooks/p1_rag_final.ipynb`: it rewrote the 25-question golden set, restructured the setup so the notebook runs both locally and on Kaggle, moved all searchable items into one ChromaDB collection, replaced the model-based detection of user-supplied values with rule-based detection, changed how conversation memory and revision notices are used, added a safe calculator for arithmetic, rewrote the evaluation metrics, and added the Appendix C safety probes. It also wrote `requirements.txt`, `README.md`, this file and the `CONTRIBUTIONS.md` template.

## How the golden set was used

- The golden set was written before these changes and committed to Git first (commit `c9a95c3`). None of its questions comes from `Questions.csv`.
- The system was developed and checked with the public `Questions.csv`.
- After the golden set was written, its results were looked at: to choose between the 3B and 7B vision-language models (the 7B model scored higher and was kept) and to read the failures. Prompt changes after that were kept general. The golden-set scores are therefore a fair comparison of baseline and final system, but they are not a completely untouched hold-out.
- No answers and no question-specific rules are written into the code.

## Review

We reviewed the generated code and ran the notebook ourselves with Restart & Run All. The vision-language and embedding models that are part of the system are project components, not coding assistants. They are listed in `README.md`.
