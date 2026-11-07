# AI usage

This file lists the AI assistants we used for the code and documents in this repository, and what we used them for. It covers Parts 1 and 2. Part 3 will be added when it is done.

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

## Part 2 (fine-tuning Stable Diffusion with LoRA)

The design choices (Pokemon BLIP captions, Stable Diffusion 1.5, LoRA rank 8 against rank 32, fp16, seed 266, local GPU kept under 16 GB) were chosen by the team member. Claude Code then planned and wrote almost all of the Part 2 code and files:

- the three notebooks (`p2_1_data_prep`, `p2_2_finetune`, `p2_3_generate_evaluate`), including the cleaning rule for duplicate images, the 20 fixed prompts, the metrics (KID, CLIP score, LPIPS), the NSFW and memorization checks, and the blinded human-evaluation web form;
- the small training wrapper `scripts/part2/run_training.py` (the training script itself is the unchanged diffusers example);
- the `data266_lab2_part2` environment, `requirements-part2.txt`, the model cards, and the Part 2 sections of the README;
- running the notebooks and the Hugging Face upload, using the Hugging Face token that the team member gave it for this purpose.

Claude Code also wrote the notes about what the generated images show. It wrote them after looking at the images and then corrected two statements that were stronger than the images supported. The 20 prompts were committed to Git before training started (commit `9cf9213`). The number of training steps was raised from 1500 to 3000 after looking at one generated image, not after looking at any test metric. The blinded human evaluation has not been done yet.

## Review

We reviewed the generated code and ran the notebook ourselves with Restart & Run All. The vision-language and embedding models that are part of the system are project components, not coding assistants. They are listed in `README.md`.
