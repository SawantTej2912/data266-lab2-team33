# Contributions

Team: **Pair_Programming_Team_33**

| Member | Accounts used |
|---|---|
| Tejas | GitHub `SawantTej2912` (all commits and pushes so far), Hugging Face `SawantTej`, Kaggle |
| Shriram | TODO (Shriram): add your GitHub handle if you push to the repository |

Both members contribute to all three parts. This file says who did what. The section about Tejas is complete. **Shriram fills in his own section below** (the cells marked TODO).

**How to read the Git history.** All commits so far are under Tejas's GitHub account, so the history does not show who wrote which line, and it does not show Shriram's work. The code and the documents were written with AI assistants (Claude Code and ChatGPT) that Tejas directed; what each assistant did is described in `AI_USAGE.md`. Each member must be able to explain every part in the demo.

## Tejas

Tejas set up and directed the work with the AI assistants, chose the design in each part, ran everything on his own GPU (RTX 4090, kept below 16 GB as the lab requires), and did the Kaggle submission, the Hugging Face uploads and the GitHub pushes. The code listed below was written by the AI assistants at Tejas's direction and then run and checked by him (`AI_USAGE.md` says what each assistant wrote). What was implemented:

### Part 1 - Multimodal RAG (`notebooks/p1_rag_final.ipynb`)

- **Ingestion:** reads the three PDFs and `kb_manifest.json` (document IDs and trust levels); cuts the text into chunks; saves every numbered figure and table as an image (PyMuPDF); describes each figure with a vision-language model so it can be found by text search; reads tables as exact text too.
- **Index:** one ChromaDB collection for all items (text chunks, pages, figure descriptions, table rows) with `doc_id`, `page`, `figure_id` and `trust_level`, built with BGE-small embeddings and rebuilt from the PDFs on every run (the knowledge base is read-only).
- **Retrieval:** dense search plus BM25 keyword search, combined with reciprocal rank fusion, and an exact lookup when a question names a figure or table.
- **Answering:** Qwen2.5-VL-7B-Instruct in 4-bit, returning an answer, a status, citations and figure references. It follows the lab's rules: a revision replaces an earlier value, an actual result replaces a forecast, conflicts are reported, false premises are rejected, and the low-trust Appendix C is never used as evidence.
- **Conversations:** a separate memory per `conversation_id`; values given by the user ("assume ...") stay in that conversation, are never written to the index, and requests to change the documents permanently are refused; a safe calculator for arithmetic.
- **Kaggle:** the notebook finds the data by itself and runs both locally and on Kaggle; Tejas ran it on Kaggle and submitted `submission.csv` (public leaderboard score 61 at the time of submission).
- **Evaluation:** a 25-question golden set (written and committed before the system was changed; no question comes from `Questions.csv`), a dense-only baseline against the final hybrid system (answer correctness 18/25 against 20/25, Recall@5 0.875 against 0.938, citation accuracy 0.76 against 0.78), safety probes for the traps in Appendix C, and the human groundedness ratings (average 4.22 of 5).

### Part 2 - Fine-tuning Stable Diffusion 1.5 (`notebooks/p2_*.ipynb`)

- **Choices made by Tejas:** the Pokemon BLIP captions dataset, Stable Diffusion 1.5 as the base model, LoRA with rank 8 against rank 32, fp16, seed 266, and a separate environment.
- **Data preparation:** cleaning (3 near-duplicate images removed, 830 of 833 kept), the 90/10 split (747 train, 83 test), resizing to 512x512, the dataset description with its limitations, and the 20 fixed prompts (committed to Git before any training).
- **Training:** the two LoRA runs with the unchanged diffusers training script and a small wrapper (`scripts/part2/run_training.py`) that caps GPU memory at 15 GB and records peak memory and time; 3000 steps each (peak under 4 GB).
- **Generation and evaluation:** 120 images (20 prompts x 2 seeds x 3 models), side-by-side grids, KID (0.0947 for the base model, 0.0356 for the final rank-32 model), CLIP score, LPIPS diversity, failure modes, the NSFW check and the memorization check.
- **Human evaluation:** the blinded web form for 25 image pairs and the analysis of the ratings from 3 raters (the final model wins 74.7% for domain style and 56% for prompt match). Tejas also found the outside rater.
- **Hugging Face:** both LoRA models, the model card of the final run and a dataset with all generated images and their metadata.
- **Extra experiments (optional):** four more LoRA runs (learning rate, rank 64, Min-SNR loss weighting, 5000 steps) and a guidance test, judged with a decision rule written before the runs. No run beat the final model; the results are an ablation in the README.

### Part 3 - Multi-agent image system (`notebooks/p3_*.ipynb`, `scripts/part3/`)

- **Design chosen by Tejas:** five agents (planner, vision understanding, prompt engineering, image generation, critique) as plain Python functions on one shared dataclass, Qwen2.5-VL-7B in 4-bit as in Part 1, Stable Diffusion 1.5 with the **Part 2 LoRA loaded from Hugging Face** for domain-style requests, InstructPix2Pix for edits.
- **Orchestration:** the revise loop (at most 2 revisions), a JSON trace of every request, and clear messages for vague requests, missing or damaged images and errors inside an agent; everything fits on a 16 GB GPU (peak 11.6 GB with a 15 GB limit).
- **Safety:** a planner that refuses unsafe requests (rules and the vision-language model, spaced-out letters collapsed, a check for named real people), hidden instructions in images that are reported but never obeyed, and an output check by the critic (CLIP score, a model judgement, the Stable Diffusion safety checker).
- **Demo app:** a Gradio app (`scripts/part3/app.py`) that shows what each agent did.
- **Evaluation:** 15 test scenarios, 10 red-team cases and 10 extra red-team cases written and committed before the system was run; every scenario run with and without the critique loop (12 of 15 pass with it, 9 without); the blinded rating form for the two raters; critic agreement 7 of 9; 0 of 10 required attacks succeeded. One attack of the extra set got through in the first round; Tejas and the assistant added a check to the planner and kept the first-round result in the notebook.
- **Documentation:** system card and safety notes in the README, `requirements-part3.txt`, and the architecture diagram.

### Whole repository

- Three conda environments (`data266_lab2`, `data266_lab2_part2`, `data266_lab2_part3`), the pinned `requirements*.txt` files, one executed notebook per task with the run-information cell, `README.md` (how to run each part and the results), `AI_USAGE.md`, and this file.
- The Git repository `data266-lab2-team33`: the commits listed in the appendix and the pushes to GitHub.
- The human evaluation of all three parts: Tejas was one of the raters in all three, and organised the rating with Shriram (and, in Part 2, with the outside rater). The rating forms, the checks that the rated images were unchanged and the notebook runs that fill the results were done with the AI assistant.

## Shriram

*Shriram fills in this section. Replace each TODO with what you did, and add the files or notebooks that show it (for example the notebooks you ran, the baseline you built, the parts of the report you wrote).*

- **Part 1:** rated the 25 answers for groundedness. TODO (Shriram): what else you did.
- **Part 2:** rated the 25 image pairs. TODO (Shriram): what else you did. The lab requires you to run the complete pipeline, at least as a working baseline.
- **Part 3:** judged the 29 test cases on your own and resolved the two disagreements with Tejas (`outputs/part3/human_eval/ratings/ratings_Shriram.csv` and `resolution.csv`). TODO (Shriram): what else you did. The lab requires you to run the complete pipeline, at least as a working baseline.
- **Report, demo and other work:** TODO (Shriram).

## Who led which task

The lab lets each member lead one task in Parts 2 and 3. The other member still runs the complete pipeline, at least as a working baseline.

| Part | Task | Lead |
|---|---|---|
| 2 | 2.1 Data preparation | TODO |
| 2 | 2.2 Fine-tuning | TODO |
| 2 | 2.3 Image generation | TODO |
| 2 | 2.4 Evaluation, safety and documentation | TODO |
| 3 | 3.1 Agents | TODO |
| 3 | 3.2 Orchestration, failure handling and demo app | TODO |
| 3 | 3.3 Evaluation, safety and documentation | TODO |

## Human evaluation raters

| Part | Raters | Files |
|---|---|---|
| 1 (groundedness, 25 answers) | Tejas and Shriram | `outputs/part1/human_groundedness.csv` |
| 2 (25 image pairs) | Tejas, Shriram and Atharva (a friend of Tejas, not in the team) | `outputs/part2/human_eval/ratings/` |
| 3 (29 test cases) | Tejas and Shriram | `outputs/part3/human_eval/ratings/` |

## AI assistants

See `AI_USAGE.md`.

## Appendix: what the Git history shows

| Commit | Part | What it contains |
|---|---|---|
| `7e04cde` | 1 | First commit: the Part 1 notebook, the small provided data files and `.gitignore` |
| `c9a95c3` | 1 | The 25-question golden set, committed before the system was changed |
| `7610a00` | 1 | Restructured notebook (Kaggle-ready, ChromaDB for all items, conversation handling, evaluation), README and requirements |
| `389a987` | 1 | The executed notebook with saved outputs, `submission.csv`, README, requirements and `AI_USAGE.md` |
| `9cf9213` | 2 | Data preparation notebook, the split lists and the 20 fixed prompts (before any training) |
| `13c6c96` | 2 | Training script and wrapper, the notebooks, results, safety checks, README and requirements |
| `21476c0`, `ff965e0` | 2 | The extra experiments: the notebook with its decision rule (before the runs), then the results |
| `9807497` | 3 | The 15 test scenarios, the 10 red-team cases and their input images (before any agent code) |
| `f7bec84` | 3 | The five agents with the shared state, the revise loop and the JSON trace |
| `32462c5` | 3 | The 10 extra red-team cases (before they were run) |
| `387cf9f`, `34ce32c` | 3 | Changes made while testing, including the planner check for named real people |
| `1092d65` | 3 | Executed notebooks, evaluation results, the Gradio app, requirements and README |
| `b928b4a` | 1, 2 | The Part 2 human evaluation and the Part 1 groundedness ratings |
| `7d2c7c5` | 3 | The Part 3 human evaluation in the results |
| `0f657aa` | 1 | Part 1 notebook run again with the ratings, and the Part 1 results in the README |
