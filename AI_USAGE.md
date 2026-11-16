# AI usage

This file lists the AI assistants we used for the code and documents in this repository, and what we used them for. It covers Parts 1, 2 and 3.

## ChatGPT

Used outside the repository for:

- discussing the architecture of the Part 1 system;
- debugging help;
- implementation guidance;
- designing the evaluation;
- paraphasing parts of the report.

## Claude Code (Anthropic), in VS Code

Used inside the repository for:

- inspecting the repository and the notebook;
- diagnosing extraction and retrieval problems;


## How the golden set was used

- The golden set was written before these changes and committed to Git first (commit `c9a95c3`). None of its questions comes from `Questions.csv`.
- The system was developed and checked with the public `Questions.csv`.
- After the golden set was written, its results were looked at: to choose between the 3B and 7B vision-language models (the 7B model scored higher and was kept) and to read the failures. Prompt changes after that were kept general. The golden-set scores are therefore a fair comparison of baseline and final system, but they are not a completely untouched hold-out.
- No answers and no question-specific rules are written into the code.

## Part 1: improvement round after the first Kaggle score

After the public Kaggle score of 61, I used Claude Code to improve it. What it did:

- It read the golden-set failures and the notebook's own answers to the public `Questions.csv` (there is no answer key for them) and diagnosed the weak points: wrong `not_found` statuses, almost no `conflict` or `false_premise` answers, citations without the page of a table or figure, and answers that leave out the replaced value or what the documents report.
- It rewrote five cells of `notebooks/p1_rag_final.ipynb` (retrieval, answer generation, follow-up resolution, conversation handling, evaluation) with general rules and short checking prompts. The work files are in `dev/part1/`. It also added the validation evaluation cell and a rule so that old human ratings are never reused for new answers.

Limits of the numbers: the improvements were developed with the golden set and the validation questions, so those scores are higher than what an untouched test would give. The hidden Kaggle set is the real test. The human groundedness ratings made before this round belong to the old answers and have to be made again; the notebook archives the old sheet and writes a new one.

## Part 2 (fine-tuning Stable Diffusion with LoRA)

The design choices (Pokemon BLIP captions, Stable Diffusion 1.5, LoRA rank 8 against rank 32, fp16, seed 266, local GPU kept under 16 GB) were chosen by the team member. Claude Code then planned the Part 2 code and files:

- the `data266_lab2_part2` environment, `requirements-part2.txt`, the model cards, and the Part 2 sections of the README;
- running the notebooks and the Hugging Face upload, using the Hugging Face token that the team member gave it for this purpose.

Claude Code wrote the notes about what the generated images show. I wrote them after looking at the images and then corrected two statements that were stronger than the images supported. The 20 prompts were committed to Git before training started (commit `9cf9213`). The number of training steps was raised from 1500 to 3000 after looking at one generated image, not after looking at any test metric. The blinded human evaluation has not been done yet.

## Part 3 (multi-agent image system)

The design choices (five agents, plain Python functions with one shared dataclass, Qwen2.5-VL-7B in 4-bit as in Part 1, our Part 2 LoRA from Hugging Face for domain style, InstructPix2Pix for edits, a Gradio demo) were chosen by me and my teammate. Claude Code then planned and wrote almost all of the Part 3 files:

How the test cases were used:

- The 15 scenarios and the 10 red-team cases were written and committed to Git (commit `9807497`) before any agent code existed. The 10 extra red-team cases were committed (commit `32462c5`) before they were run.
- While building the agents, Claude Code tried them on about 20 other development requests that are not among the test cases (for example a charcoal drawing, pixel art, "change the car to green", a request to describe an image with hidden text) and changed the prompts and settings from what it saw there. The scenarios and red-team cases were then run once to get the reported results.

## Review

We reviewed the generated code and ran the notebook ourselves with Restart & Run All. The vision-language and embedding models that are part of the system are project components, not coding assistants. They are listed in `README.md`.

---

# Shriram's work (`notebooks/p1_rag.ipynb`, `p2_finetune.ipynb`, `p3_agents.ipynb`, `p3_evaluate.ipynb`, `outputs/part*_shriram/`)

The section above covers Tejas's files. This section covers mine. Everything below it is about my own copies of the three parts and does not describe his work.

## Cursor with Claude (Anthropic)

Used inside the repository, on my machine, for all three parts. It had read and write access to my files and ran shell commands. I ran every notebook myself in Colab; the assistant never had access to the GPU session, to Google Drive, or to Kaggle, and could not see any result until I downloaded the executed notebook back and gave it to it.

### Part 1

I brought it a notebook that scored 0.562 on the public leaderboard and asked it to find out why. Over four rounds it read the executed notebook and the golden-set failures and rewrote eight cells:

- the answering rules prompt, after we found that a sample label in the JSON example was being copied verbatim into answers that named no figure;
- the JSON parser, with a fallback that recovers an answer from prose when the model does not return JSON, and later a second model pass that converts a prose reply into JSON;
- retrieval: keyword expansion groups for revision and forecast vocabulary, and a separation between the question shown to the model and the question sent to the index, which was the cause of a session override leaking across years;
- the conversation handler's regular expressions for detecting an override and for detecting a question about the documents themselves;
- the grading helper, where a number-extraction regular expression was reading "1961-2010" as two numbers and marking two correct answers wrong;
- the evidence selection, the crop resolution, and the citation fallback.

It also wrote the retrieval ablation, the failure attribution table and the safety probe cell, and it audited a review of my notebook that I had obtained separately from ChatGPT: of the six points in that review it judged three correct and three likely to lower the score, and I applied only the three it supported.

Honesty about the numbers, in addition to the team note above: the changes listed here were chosen by reading golden-set failures, so the golden-set score is a development number and not an untouched hold-out. The public leaderboard went 0.562, 0.612, then a fall, then 0.65, and the golden set only started moving in the same direction as the leaderboard on the last run. No answer and no question-specific rule is hard-coded; the assistant was told not to write any, and I checked.

The cross-encoder reranker was tested for the S.5 bonus and measured on the golden set. It does not improve Recall@5 or MRR@5 here, because exact-label figure routing already pins the correct crop and the cross-encoder displaces it, so the final system does not use one. The ablation reports the measured result rather than claiming an improvement.

### Part 2

I chose the design (Stable Diffusion 1.5, the Pokemon BLIP captions dataset, LoRA rank 8 against rank 32 at 3000 steps, fp16, seed 266, one 16 GB GPU). The assistant then wrote the notebook: data cleaning and the perceptual duplicate check, the two training runs through the diffusers LoRA script, generation, and the KID, CLIP, LPIPS, memorization and NSFW evaluation cells. It diagnosed two runtime errors from tracebacks I pasted: the fp16 gradient unscaling failure, which needed the mixed precision flag passed to the training script and not only to `accelerate launch`, and a call to `Tensor.round()` with a positional argument. While fixing the second it noticed that the memorization check was being run against the base model rather than the fine-tuned one, which would have made the result meaningless, and changed it.

The Hugging Face push used a write token that I pasted into the settings cell at run time. The token is not in the committed notebook; the cell ships with an empty string in its place.

At one point the assistant expanded Part 2 beyond the baseline that Tejas and I had agreed I would run. I pointed this out, it confirmed from `CONTRIBUTIONS.md` that the agreed split gives Part 2 to Tejas, and it restored the split table and his model in the README. The extra rank-8 against rank-32 comparison was kept as my own run, and the graded blinded human evaluation remains Tejas's.

### Part 3

I chose the design (five agents, one typed state object, the Part 2 LoRA for the domain-style route, a revise loop capped at two passes, JSON traces, a Gradio app). The assistant wrote `scripts/part3/agents.py`, both notebooks, the 15 scenarios and the 10 red-team cases, and the evaluation. The scenarios and red-team cases were written and committed before any of them were run.

Two things it found by reading the executed notebooks: a dependency pin that had already caused a crash in Part 1 and was still present in both Part 3 notebooks, and a mismatch in the output safety gate, where the comment described a two-signal rule but the code blocked on the vision model alone and was refusing valid generations. The gate now blocks only when the Stable Diffusion checker and the vision model agree.

It also pointed out that two of the ten red-team cases are recorded as attacks that succeeded, but that both are checked with a forbidden-substring rule that fires when the reply merely reports the text visible in the image, which Task 3.1 requires the vision agent to do. We are resolving that through the human rubric rather than by editing the check after seeing the result.

### Repository work

The assistant also managed my Git branch, wrote the commit messages, and kept the commits additive so that none of Tejas's files were modified or deleted. It stripped the Hugging Face token out of an executed notebook before anything was committed and checked that it had not reached an earlier commit.

## ChatGPT

Used outside the repository for:

- a review of the Part 1 notebook, which I then brought back for a second opinion as described above;
- reformatting `outputs/part1_shriram/human_groundedness.csv` after I broke its column alignment while typing my ratings in. It was asked to repair the formatting only. The question, answer and citation columns were not changed, and I checked them afterwards.

## Review

I read the generated code and ran every notebook myself with Restart and Run All before the results in this repository were recorded.
