# Contributions

Team: **Pair_Programming_Team_33**

| Member | Accounts used |
|---|---|
| Tejas | GitHub `SawantTej2912` (owner of the repository), Hugging Face `SawantTej`, Kaggle |
| Shriram | GitHub `Shriram Dundigalla <shriram.dundigalla09@gmail.com>` (the commits on branch `shriram/lab2-work`), Hugging Face `shriram14`, Kaggle `shriramdundigalla14` |

Both members contribute to all three parts. This file says who did what.

**How to read the Git history.** Each member committed their own work under their own name, so `git log --author` shows who did what. Tejas's commits appear as `SawantTej2912` and `Tejas Sawant`; Shriram's appear as `Shriram Dundigalla`. Shriram's work was first committed on the branch `shriram/lab2-work` and then merged into `main`, where each member's files are kept in their own folder (`notebooks/tejas/`, `notebooks/shriram/`, and the same for `data/`, `outputs/`, `scripts/` and `report/`).

## Tejas

Tejas set up and directed the work with the AI assistants, chose the design in each part, ran everything on his own GPU (RTX 4090, kept below 16 GB as the lab requires), and did the Kaggle submission, the Hugging Face uploads and the GitHub pushes. What was implemented:

### Part 1 - Multimodal RAG (`notebooks/tejas/p1_rag_final.ipynb`)

- **Ingestion:** reads the three PDFs and `kb_manifest.json` (document IDs and trust levels); cuts the text into chunks; saves every numbered figure and table as an image (PyMuPDF); describes each figure with a vision-language model so it can be found by text search; reads tables as exact text too.
- **Index:** one ChromaDB collection for all items (text chunks, pages, figure descriptions, table rows) with `doc_id`, `page`, `figure_id` and `trust_level`, built with BGE-small embeddings and rebuilt from the PDFs on every run (the knowledge base is read-only).
- **Retrieval:** dense search plus BM25 keyword search, combined with reciprocal rank fusion, and an exact lookup when a question names a figure or table.
- **Answering:** Qwen2.5-VL-7B-Instruct in 4-bit, returning an answer, a status, citations and figure references. It follows the lab's rules: a revision replaces an earlier value, an actual result replaces a forecast, conflicts are reported, false premises are rejected, and the low-trust Appendix C is never used as evidence.
- **Conversations:** a separate memory per `conversation_id`; values given by the user ("assume ...") stay in that conversation, are never written to the index, and requests to change the documents permanently are refused; a safe calculator for arithmetic.
- **Kaggle:** the notebook finds the data by itself and runs both locally and on Kaggle; Tejas ran it on Kaggle and submitted `submission.csv` (public leaderboard score 0.761; one Tesla T4, 40 questions answered in 19.1 minutes). Kaggle notebook: https://www.kaggle.com/code/tejassawant291201/data266-lab2-tejas
- **Evaluation:** a 25-question golden set (written and committed before the system was changed; no question comes from `Questions.csv`), a dense-only baseline against the final hybrid system (answer correctness 21/25 against 23/25, Recall@5 0.917 against 0.958, citation accuracy 0.80 against 0.96, median 5.35 against 5.25 seconds per question), 34 further validation questions (26/34 against 27/34), safety probes for the traps in Appendix C, and the human groundedness ratings of the final answers (`outputs/tejas/part1/human_groundedness.csv`).

### Part 2 - Fine-tuning Stable Diffusion 1.5 (`notebooks/tejas/p2_*.ipynb`)

- **Choices made by Tejas:** the Pokemon BLIP captions dataset, Stable Diffusion 1.5 as the base model, LoRA with rank 8 against rank 32, fp16, seed 266, and a separate environment.
- **Data preparation:** cleaning (3 near-duplicate images removed, 830 of 833 kept), the 90/10 split (747 train, 83 test), resizing to 512x512, the dataset description with its limitations, and the 20 fixed prompts (committed to Git before any training).
- **Training:** the two LoRA runs with the unchanged diffusers training script and a small wrapper (`scripts/tejas/part2/run_training.py`) that caps GPU memory at 15 GB and records peak memory and time; 3000 steps each (peak under 4 GB).
- **Generation and evaluation:** 120 images (20 prompts x 2 seeds x 3 models), side-by-side grids, KID (0.0947 for the base model, 0.0356 for the final rank-32 model), CLIP score, LPIPS diversity, failure modes, the NSFW check and the memorization check.
- **Human evaluation:** the blinded web form for 25 image pairs and the analysis of the ratings from 3 raters (the final model wins 74.7% for domain style and 56% for prompt match). Tejas also found the outside rater.
- **Hugging Face:** both LoRA models, the model card of the final run and a dataset with all generated images and their metadata.
- **Extra experiments (optional):** four more LoRA runs (learning rate, rank 64, Min-SNR loss weighting, 5000 steps) and a guidance test, judged with a decision rule written before the runs. No run beat the final model; the results are an ablation in the README.

### Part 3 - Multi-agent image system (`notebooks/tejas/p3_*.ipynb`, `scripts/tejas/part3/`)

- **Design chosen by Tejas:** five agents (planner, vision understanding, prompt engineering, image generation, critique) as plain Python functions on one shared dataclass, Qwen2.5-VL-7B in 4-bit as in Part 1, Stable Diffusion 1.5 with the **Part 2 LoRA loaded from Hugging Face** for domain-style requests, InstructPix2Pix for edits.
- **Orchestration:** the revise loop (at most 2 revisions), a JSON trace of every request, and clear messages for vague requests, missing or damaged images and errors inside an agent; everything fits on a 16 GB GPU (peak 11.6 GB with a 15 GB limit).
- **Safety:** a planner that refuses unsafe requests (rules and the vision-language model, spaced-out letters collapsed, a check for named real people), hidden instructions in images that are reported but never obeyed, and an output check by the critic (CLIP score, a model judgement, the Stable Diffusion safety checker).
- **Demo app:** a Gradio app (`scripts/tejas/part3/app.py`) that shows what each agent did.
- **Evaluation:** 15 test scenarios, 10 red-team cases and 10 extra red-team cases written and committed before the system was run; every scenario run with and without the critique loop (12 of 15 pass with it, 9 without); the blinded rating form for the two raters; critic agreement 7 of 9; 0 of 10 required attacks succeeded. One attack of the extra set got through in the first round; Tejas and the assistant added a check to the planner and kept the first-round result in the notebook.
- **Documentation:** system card and safety notes in the README, `requirements-part3.txt`, and the architecture diagram.

### Whole repository

- Three conda environments (`data266_lab2`, `data266_lab2_part2`, `data266_lab2_part3`), the pinned `requirements*.txt` files, one executed notebook per task with the run-information cell, `README.md` (how to run each part and the results), `AI_USAGE.md`, and this file.
- The Git repository `data266-lab2-team33`: the commits listed in the appendix and the pushes to GitHub.
- The human evaluation of all three parts: Tejas was one of the raters in all three, and organised the rating with Shriram (and, in Part 2, with the outside rater). The rating forms, the checks that the rated images were unchanged and the notebook runs that fill the results were done by both team members.

## Shriram

Shriram built and ran his own complete implementation of all three parts, independently of Tejas's, and led Part 3. Nothing below is a copy of Tejas's code: the two implementations differ in architecture, hyperparameters and evaluation design, and they are kept in separate directories (`outputs/shriram/part1/`, `outputs/shriram/part2/`, `outputs/shriram/part3/`). Everything was run on free Colab and Kaggle GPUs rather than a local card. 

### Part 1 - Multimodal RAG (`notebooks/shriram/p1_rag.ipynb`)

- **Ingestion and index:** PyMuPDF text chunks of 1000 characters with 200 overlap, plus every numbered figure and table cut out of its page as a separate crop; each crop described by Qwen2.5-VL-7B-Instruct in 4-bit NF4 so a chart becomes searchable as text. 302 items in ChromaDB over BGE-small embeddings, each carrying `doc_id`, `page`, `figure_id` and `trust_level` read from `kb_manifest.json`.
- **Retrieval:** reciprocal rank fusion at k=60 over BM25 and dense search, with exact-label figure routing that pins a crop the question names to the front of the list.
- **Evaluation:** a separate 25-question golden set written and committed before the system was tuned, covering six question types. Dense baseline against the final system: answers correct 16/25 against 19/25, Recall@5 0.667 against 0.958, citation accuracy 0.883 against 0.958, 0 untrusted-source leaks in both. A six-arm retrieval ablation (`outputs/shriram/part1/retrieval_ablation.csv`) and a failure attribution that shows retrieval misses falling from 8 to 1.
- **The reranker:** added a cross-encoder arm for the S.5 bonus, measured it, and found it costs 0.187 Recall@5 because it fights the exact-label routing. It is therefore **not** in the final system, and the ablation reports the loss rather than a claim. The bonus asks for an improvement and there is not one here.
- **Safety:** trust level enforced at index time so Appendix C is never a retrieval candidate; the Appendix C chart crop is never passed to the model as an image, which is the only defence against an instruction that exists as pixels; three safety probes in `outputs/shriram/part1/safety_probes.csv`, one of which (the false-premise probe G24) the system does not catch, which is written up as a limitation rather than dropped.
- **Kaggle:** the notebook runs end to end on Kaggle, reads `QUESTIONS_PATH` from the environment so the hidden set needs no edit, and writes `submission.csv` with no manual step. Graded run: notebook version 370463230, one T4, peak 8.51 GB, total runtime 33.4 minutes, public leaderboard 0.646.
- **Human evaluation:** rated the answers for groundedness (`outputs/shriram/part1/human_groundedness.csv`), and rebuilt the review sheet so every rating is made against the cited source text and figure crops rather than the answer alone.

### Part 2 - Fine-tuning Stable Diffusion 1.5 (`notebooks/shriram/p2_finetune.ipynb`)

- **Data:** `reach-vb/pokemon-blip-captions`, 833 pairs, cleaned to 831 (0 corrupted, 0 exact duplicates, 2 perceptual duplicates), split at seed 266 into 747 train and 84 test, resized to 512x512. The 20 evaluation prompts (10 in-domain from held-out captions, 5 out-of-domain, 5 compositional) were committed before training finished.
- **Training:** two LoRA runs at rank 8 and rank 32, both 3000 steps, learning rate 1e-4, effective batch 4, using the unmodified diffusers `train_text_to_image_lora.py`. Cost 0.680 and 0.708 GPU-hours at peak 3.47 and 4.96 GB (`outputs/shriram/part2/metrics/training_table.csv`).
- **Evaluation:** 120 images across three models. In-domain KID 0.0929 for the base model, 0.0507 at rank 8, 0.0274 at rank 32; CLIP score and LPIPS diversity both fall slightly, which is the fidelity-against-flexibility trade-off and is reported as such. Rank 32 selected on the primary metric.
- **Safety:** the Stable Diffusion safety checker flagged 11 of 120 images, all of them inspected and none actually unsafe - a false-positive rate on stylised output high enough that it drove the two-signal output gate used in Part 3. Memorization measured as CLIP similarity to the nearest training image (mean 0.8939) **against a held-out control** (mean 0.9340); the generations sit below the control, so there is no memorization signal. The control is the point: the raw number alone would have been unreadable.
- **Hugging Face:** `shriram14/pokemon-sd15-lora-r8`, `shriram14/pokemon-sd15-lora-r32` with a model card stating the CC BY-NC-SA 4.0 and copyright limits, and the image dataset `shriram14/data266-lab2-part2-images`.

### Part 3 - Multi-agent image system (lead; `notebooks/shriram/p3_agents.ipynb`, `notebooks/shriram/p3_evaluate.ipynb`)

- **Agents:** planner, vision understanding, prompt engineering, image generation and critique, as plain functions over one typed `RequestState`. Six routes, image-to-image for style changes, InstructPix2Pix for edits, and **Tejas's Part 2 LoRA (`SawantTej/pokemon-sd15-lora-r32`) loaded from Hugging Face** for domain-style requests, as the task split requires.
- **Orchestration:** a revise loop capped at two passes, a JSON trace per request recording every agent's input, output and timing, and clear messages for vague requests, missing or damaged images and crashes inside an agent. Peak 8.77 GB, median 18.4 seconds per request.
- **Evaluation:** 15 scenarios (3 in each of 5 categories) and 10 red-team cases, all committed before the agents were run, then run twice - with and without the critique loop. By the automatic checks 14 of 15 pass without it and 15 of 15 with it; under the two raters' agreed rubric the same runs are 11 of 15 and 13 of 15, because the rubric asks whether the result actually looks like what was requested. 6 requests used a revision; the loop costs 25.1 to 28.5 seconds median. Critic agreement with a human on first attempts is 4 of 9, and every disagreement is the critic being stricter than the human, never the other way round.
- **Red team:** 8 of 10 cases defended by the automatic check, 10 of 10 under the human rubric. The two the automatic check marks as breaches are instruction-in-image attacks caught by a forbidden-substring rule that also fires when the reply correctly *quotes* the injected text, which Task 3.1 requires the vision agent to do. This was left for the human rubric to adjudicate rather than fixed by editing the check after seeing the result.
- **Safety:** unsafe requests refused by the planner before anything is generated; unsafe outputs caught by a gate that requires the Stable Diffusion safety checker and an independent vision-language judgement to **agree**, because the Part 2 measurement showed either one alone refuses valid domain-style work.
- **Demo app:** a Gradio app run from the notebook that shows each agent's output and the trace.

### Report, repository and other work

- **Report:** wrote the Shriram sections of the IEEE-format report and the Part 3 system card. The PDF is generated by `scripts/build_report.py`, which reads every number from a file under `outputs/` or from an output cell of an executed notebook at build time; none is typed into the report. Re-running a notebook and rebuilding keeps the report and the CSVs from disagreeing.
- **AI usage:** the Shriram section of `AI_USAGE.md`, including the two runtime errors in Part 2, the memorization check first run against the wrong model, and the Part 3 safety-gate mismatch.
- **Repository:** the branch `shriram/lab2-work`, which adds files only and changes nothing of Tejas's. The one shared file touched is `AI_USAGE.md`, and that commit is 58 insertions and 0 deletions.

### Appendix: Shriram's commits

| Commit | Part | What it contains |
|---|---|---|
| `b4df127` | 1, 2, 3 | Golden set and executed Part 1 notebooks, the Part 2 fine-tuning notebook, the Part 3 notebooks |
| `55d53b1` | 2 | Part 2 executed: the two LoRA runs at rank 8 and 32 |
| `4c9eb44` | 3 | Part 3 executed: the five agents and the full evaluation |
| `2e2c73c` | 3 | Part 3 outputs, JSON traces and evaluation tables |
| `5cfa929` | 1 | Part 1 rerun: Kaggle 0.65 and 19/25 on the golden set |
| `867580b` | 1, 2 | Part 1 outputs refreshed to that run, first Part 2 output files |
| `a8313b6` | all | The Shriram section of `AI_USAGE.md` |
| `9288bd0` | 1 | Groundedness sheet reconciled against the rerun |
| `2aee1b2` | 2 | Part 2 metrics tables |
| `e7adf5d` | 1 | Part 1 run on Kaggle - the notebook the graders re-run for the hidden set |
| `732bc40` | 1 | The Kaggle notebook link, pinned to the graded version |

### Human evaluation on Shriram's side 

- Part 1 groundedness: both members rated all 25 answers of the graded Kaggle run (`outputs/shriram/part1/human_groundedness.csv`). Shriram 4.36, Tejas 4.40, combined 4.38; the two of us give the same score on 22 of 25 and are never more than one point apart.
- Part 2: the blinded 25-pair comparison was rated by three people, one of them outside the team (`outputs/shriram/part2/human_eval/ratings/`). The fine-tuned model wins domain style 89% and prompt match 68%.
- Part 3: both members filled the full 70-check rubric (`outputs/shriram/part3/human_eval/ratings/`). We agreed on 57 of 70; the 13 disagreements were settled one at a time against the traces and images and recorded in `resolution.csv`, with the settled sheet in `ratings_agreed.csv`. Agreed result: 13 of 15 scenarios pass with the critique loop, 11 of 15 without, 10 of 10 red-team attacks defended.

### Meetings and discussion

Throughout the DATA 266 lab, Shriram and I worked as partners and regularly discussed our individual progress, approaches, and results. Most of our discussions took place in person while working in the GPU lab, so we do not have recordings of these meetings.

For **Part 1**, which involved building the RAG system, we discussed which LLM models would be appropriate to use and helped each other refine and tailor the prompts. Although we completed our runs individually, we discussed the approaches we were taking and, after completing the experiments, evaluated each other’s answers and results.

For **Part 2**, we jointly decided to use the Pokémon dataset from Hugging Face. We coordinated throughout the experimentation process, particularly around training decisions such as the number of epochs and other training considerations. Once our individual runs were completed, we reviewed and evaluated each other’s generated outputs and overall results.

For **Part 3**, we again reviewed and evaluated each other’s results. We compared the differences between our outputs and discussed possible reasons for those differences, including how our individual choices and experimental setups may have affected the final results.

Overall, even though each part required us to perform the tasks individually, we regularly coordinated, discussed our decisions and observations, and provided peer evaluation and feedback on each other’s work.

## Who led which task

The lab lets each member lead one task in Parts 2 and 3. The other member still runs the complete pipeline, at least as a working baseline.

| Part | Task | Lead |
|---|---|---|
| 2 | 2.1 Data preparation | Tejas |
| 2 | 2.2 Fine-tuning | Tejas |
| 2 | 2.3 Image generation | Tejas |
| 2 | 2.4 Evaluation, safety and documentation | Tejas |
| 3 | 3.1 Agents | Shriram |
| 3 | 3.2 Orchestration, failure handling and demo app | Shriram |
| 3 | 3.3 Evaluation, safety and documentation | Shriram |

## Human evaluation raters

| Part | Raters | Files |
|---|---|---|
| 1 (groundedness, 25 answers) | Tejas and Shriram | `outputs/tejas/part1/human_groundedness.csv` |
| 2 (25 image pairs) | Tejas, Shriram and Atharva (a friend of Tejas, not in the team) | `outputs/tejas/part2/human_eval/ratings/` |
| 3 (29 test cases) | Tejas and Shriram | `outputs/tejas/part3/human_eval/ratings/` |

Shriram's implementation was rated separately, on its own outputs:

| Part | Raters | Files |
|---|---|---|
| 1 (groundedness, 25 answers) | Shriram and Tejas | `outputs/shriram/part1/human_groundedness.csv` |
| 2 (25 image pairs) | Shriram, Tejas and Anurag (outside the team) | `outputs/shriram/part2/human_eval/ratings/` |
| 3 (70 rubric checks over 15 scenarios x 2 settings and 10 red-team cases) | Shriram and Tejas | `outputs/shriram/part3/human_eval/ratings/` |

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
