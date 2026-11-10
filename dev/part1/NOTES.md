# Part 1 improvement work (checkpoint)

Status when this checkpoint was saved: **work in progress. The submitted notebook `notebooks/p1_rag_final.ipynb` is NOT changed yet.**
The rollback tag of the submitted version is `p1-checkpoint-1`.

## Why
Kaggle public score was 61. Diagnosis (see the chat summary): wrong `not_found` statuses, almost no `conflict` / `false_premise` answers,
citations without the page of a table or figure, and answers that leave out the replaced value or what the documents report.

## Evaluation setup
- Golden set (25, in the notebook) and a fresh validation set `data/part1/validation_set.csv` (34 questions, committed before any change).
- `estimated_score` = local proxy of the competition score: 0.4 answer + 0.2 status + 0.2 figure references + 0.2 citations.
  The real answer key is hidden, so this is only an estimate. (Two test-text artifacts in the validation file were corrected: V09, V12, V20, V21.)

## Results so far (same harness, old vs new code)
| Set | | answer correct | status correct | estimated score |
|---|---|---|---|---|
| Golden (25) | old | 20 | 22 | 0.795 |
| Golden (25) | new (6th run) | 21 | 25 | 0.891 |
| Validation (34) | old | 18 | 27 | 0.667 |
| Validation (34) | new (6th run) | 28 | 33 | 0.870 |
Median seconds per question: 3.1 (old) -> about 5.5 (new), on an RTX 4090.

## What the new code does (files in `cells/`)
- `p1_new30.py` (notebook cell 30, retrieval): a document named in the question (Document 1, Supplement A, Briefing B) always contributes its best 2 pages.
- `p1_new32.py` (cell 32, answering): not_found answers must read like not_found; a real answer with a stray not_found is kept if its numbers are in the evidence;
  page citation added next to every cited table or figure; longer prompt (2-4 sentences, reasons, name the replaced value, prefer exact tables);
  KEY TABLE LINES (best matching exact table lines); then four checks: `check_false_premise` (why-questions, two-step then a yes/no comparison),
  `rescue_not_found` (verbatim quote + entity guard + yes/no), `check_conflict` (candidate values per document, no forecasts/approximations/revisions, yes/no same quantity),
  `add_replaced_value`.
- `p1_new34.py` (cell 34): follow-ups are resolved with the most recent question first; "themselves/itself" count as follow-up cues.
- `p1_new36.py` (cell 36): questions about the documents ignore the user's temporary facts; a fact that applies is used and always shown next to what the documents report.
- `p1_new45.py` (cell 45): `evaluate_system(..., items=...)` and the `estimated_competition_score` proxy.
The `patches/` folder rebuilds these cells from the original notebook cells (`patch*.py`, `verify_block.txt`).
`drivers/` and `kx.py` run them in a persistent kernel (paths inside are absolute scratch paths of the session; adjust them).

## Still failing (6th run)
G13 (old value of a revised pair), G21 and G24 (answer lacks the revised value), G16 (document value missing), V13 (DOC3 sentence misread),
V15 (reason missing), V22/V26 (explanation wording, Okun arithmetic), V28/V34 (table reading in a follow-up).

## Next steps
1. Put the five new cells into `notebooks/p1_rag_final.ipynb` (replace cells 30, 32, 34, 36, 45; add a cell that evaluates `data/part1/validation_set.csv` when the file exists, skipped on Kaggle).
2. Re-run the whole notebook (about 15-20 min locally), check `submission.csv` with the validator, update README results.
3. Run it on Kaggle (must finish within 90 minutes), submit, compare with the public score 61.
4. Optional bonus: add a reranker and show the improvement on the golden set.
