# Part 1 improvement work

Status: **done and merged into the notebook** (`notebooks/p1_rag_final.ipynb`).

These are the work files that produced the new cells:

- `cells/` - the final text of the five replaced notebook cells (retrieval, answer generation, follow-ups, conversation handling, evaluation).
- `patches/` - the scripts that rebuilt those cells from the original cells (`patch*.py`, `verify_block.txt`) and wrote them into the notebook (`assemble_p1.py`, `reassemble_p1.py`).
- `drivers/` - the development evaluation drivers (they use absolute paths of the development session).
- `results/` - development results of the old and the new code on the golden set and on the validation set.

The rollback tag of the version that scored 61 on the public Kaggle leaderboard is `p1-checkpoint-1`.

## Final numbers (computed by the notebook, see the README)

| Set | System | Answer correct | Status correct | Estimated score |
|---|---|---|---|---|
| Golden (25) | dense baseline | 21 | - | 0.870 |
| Golden (25) | final hybrid | 23 | - | 0.944 |
| Validation (34) | dense baseline | 26 | 32 | 0.804 |
| Validation (34) | final hybrid | 27 | 31 | 0.847 |
| Validation (34) | version before the improvements | 18 | 27 | 0.667 |

The estimated score is a rough local version of the competition score. Both sets were used during development, so they are not untouched tests.

## What is left

1. Both team members rate the 25 new answers in `outputs/part1/human_groundedness.csv` (1-5, groundedness). The old ratings belong to the old answers and are archived.
2. Run the notebook again to compute the human average and agreement.
3. Run the notebook on Kaggle (it has to finish within 90 minutes; it takes about 20 minutes on an RTX 4090, a T4 is slower), submit `submission.csv` and compare with the public score of 61.
4. Optional bonus: add a reranker and show the improvement on the golden set.
Memory fix (Kaggle T4): memory freed after every model call, three-level fallback on a GPU out-of-memory error (smaller images, shorter text, no optional checks), size cap on the evidence of the short checks, expandable_segments. Tested with the GPU capped to 13 GB and eager attention: the old code lost 5 of 40 questions, the new code lost none.
