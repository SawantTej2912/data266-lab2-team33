# AI usage

This file lists the AI assistants we used for the code and documents in this repository, and what we used them for. It covers Parts 1, 2 and 3.

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

## Part 1: improvement round after the first Kaggle score

After the public Kaggle score of 61, Claude Code was asked to find what keeps the score down and to improve it. What it did:

- It read the golden-set failures and the notebook's own answers to the public `Questions.csv` (there is no answer key for them) and diagnosed the weak points: wrong `not_found` statuses, almost no `conflict` or `false_premise` answers, citations without the page of a table or figure, and answers that leave out the replaced value or what the documents report.
- It wrote 34 fresh validation questions from the PDFs (`data/part1/validation_set.csv`) and committed them before changing any code (commit `1f134a9`). After seeing results it corrected the expected text of four of them (V09, V12, V20, V21), because a digit in "Document 1" and one unneeded number made the checker ask for numbers that a correct answer does not need. The correction does not depend on the system's answers.
- It rewrote five cells of `notebooks/p1_rag_final.ipynb` (retrieval, answer generation, follow-up resolution, conversation handling, evaluation) with general rules and short checking prompts. The work files are in `dev/part1/`. It also added the validation evaluation cell and a rule so that old human ratings are never reused for new answers.
- It scanned the final cells for text and IDs of the public and validation questions. Prompt examples that had mirrored evaluation questions were replaced by unrelated ones, and the results were measured again with the unrelated examples.

Limits of the numbers: the improvements were developed with the golden set and the validation questions, so those scores are higher than what an untouched test would give. The hidden Kaggle set is the real test. The human groundedness ratings made before this round belong to the old answers and have to be made again; the notebook archives the old sheet and writes a new one.

## Part 2 (fine-tuning Stable Diffusion with LoRA)

The design choices (Pokemon BLIP captions, Stable Diffusion 1.5, LoRA rank 8 against rank 32, fp16, seed 266, local GPU kept under 16 GB) were chosen by the team member. Claude Code then planned and wrote almost all of the Part 2 code and files:

- the three notebooks (`p2_1_data_prep`, `p2_2_finetune`, `p2_3_generate_evaluate`), including the cleaning rule for duplicate images, the 20 fixed prompts, the metrics (KID, CLIP score, LPIPS), the NSFW and memorization checks, and the blinded human-evaluation web form;
- the small training wrapper `scripts/part2/run_training.py` (the training script itself is the unchanged diffusers example);
- the `data266_lab2_part2` environment, `requirements-part2.txt`, the model cards, and the Part 2 sections of the README;
- running the notebooks and the Hugging Face upload, using the Hugging Face token that the team member gave it for this purpose.

Claude Code also wrote the notes about what the generated images show. It wrote them after looking at the images and then corrected two statements that were stronger than the images supported. The 20 prompts were committed to Git before training started (commit `9cf9213`). The number of training steps was raised from 1500 to 3000 after looking at one generated image, not after looking at any test metric. The blinded human evaluation has not been done yet.

## Part 3 (multi-agent image system)

The design choices (five agents, plain Python functions with one shared dataclass, Qwen2.5-VL-7B in 4-bit as in Part 1, our Part 2 LoRA from Hugging Face for domain style, InstructPix2Pix for edits, a Gradio demo) were chosen by the team member. Claude Code then planned and wrote almost all of the Part 3 files:

- the agents and the orchestrator (`scripts/part3/agents.py`), the evaluation helpers (`scripts/part3/evaluate.py`), the Gradio app (`scripts/part3/app.py`) and the script that makes the test images (`scripts/part3/make_test_images.py`);
- the 15 test scenarios, the 10 red-team cases and the 10 extra red-team cases (`data/part3/`), and the two notebooks (`p3_1_agents`, `p3_2_evaluate`) with the blinded rating form;
- the `data266_lab2_part3` environment, `requirements-part3.txt` and the Part 3 sections of the README.

How the test cases were used:

- The 15 scenarios and the 10 red-team cases were written and committed to Git (commit `9807497`) before any agent code existed. The 10 extra red-team cases were committed (commit `32462c5`) before they were run.
- While building the agents, Claude Code tried them on about 20 other development requests that are not among the test cases (for example a charcoal drawing, pixel art, "change the car to green", a request to describe an image with hidden text) and changed the prompts and settings from what it saw there. The scenarios and red-team cases were then run once to get the reported results.
- After that first run the extra set showed one attack that got through (E07, a face swap with a named real person). Claude Code added a check for named real people to the planner and ran the notebook again. The first-round result of the extra set is saved and shown in the notebook, and the extra set is no longer a hold-out for that defence.
- Claude Code looked at the generated images to describe what works and what does not. Those notes are not the human evaluation. The pass/fail judgement of the scenarios was done by the two team members with the blinded rating form, each on their own; they resolved their two disagreements together, and the notebook uses those decisions.

## Review

We reviewed the generated code and ran the notebook ourselves with Restart & Run All. The vision-language and embedding models that are part of the system are project components, not coding assistants. They are listed in `README.md`.
