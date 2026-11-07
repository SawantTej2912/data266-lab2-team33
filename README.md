# DATA 266 - Lab 2

This repository holds our work for DATA 266 Lab 2. The lab has three parts:

1. **Part 1** - a question-answering system (multimodal RAG) over three economics PDFs, also entered in a Kaggle class competition.
2. **Part 2** - fine-tuning a diffusion model for image generation.
3. **Part 3** - a multi-agent system for image understanding and generation.

Part 1 is described first, then Part 2. Part 3 will be added when it is done.

## Repository layout (all parts)

Every part follows the same pattern: its notebook is in `notebooks/`, its input files are in `data/partN/`, and everything it creates is in `outputs/partN/`.

```
GPU_LAB_2/
|-- README.md, requirements.txt, AI_USAGE.md, CONTRIBUTIONS.md
|-- notebooks/        p1_rag_final.ipynb, p2_1_data_prep / p2_2_finetune / p2_3_generate_evaluate (.ipynb), p3_agents.ipynb (planned)
|-- data/             part1/ (provided files), part2/ (our prompts and split lists), part3/ (planned)
|-- outputs/          part1/, part2/, part3/ (planned)  - created by the notebooks
|-- scripts/part2/    training script for Part 2
`-- archive/          old copies, kept on this computer only (not in Git)
```

## Part 1: Multimodal RAG over a read-only knowledge base

The system answers questions about three PDF documents (their text, figures and tables). For every question it returns an answer, a status (`answered`, `not_found`, `conflict`, `false_premise` or `session_override`), the sources it used (citations) and the figures or tables it used (figure references).

How it works, in short:

1. Read the PDFs and `kb_manifest.json` (document IDs and trust levels).
2. Cut the text into chunks and save every numbered figure and table as an image. Tables are also read as exact text.
3. Describe each figure and table with a vision-language model so they can be found by a text search.
4. Store everything in ChromaDB (text chunks, pages, figure descriptions and table rows) together with `doc_id`, `page`, `figure_id` and `trust_level`.
5. Retrieve with dense search (ChromaDB) plus BM25 keyword search. If a question names a figure or table, that exact one is retrieved.
6. Write the answer with the vision-language model, using the answering rules from the lab (a revision replaces the earlier value, an actual result replaces a forecast, conflicts, false premises, and never using the low-trust Appendix C).
7. Keep a separate memory for each conversation. A value given by the user ("assume ...") is used only in that conversation.
8. Read the questions file, write `submission.csv` and check it with the validator.
9. Evaluate a dense-only baseline and the final system on our 25-question golden set, and run safety checks on the Appendix C traps.

**The knowledge base is read-only.** The documents are never changed. Values given by a user are kept only in that conversation's memory, are never written to ChromaDB, and are forgotten when the conversation ends. Requests to change the documents permanently are refused. ChromaDB is rebuilt from the PDFs every time the notebook runs.

## Folder structure

```
GPU_LAB_2/
|-- README.md
|-- requirements.txt            pinned packages for Part 1
|-- AI_USAGE.md                 which AI assistants we used and for what
|-- CONTRIBUTIONS.md            who did what, meeting recordings
|-- submission.csv              made by the notebook (local run)
|-- notebooks/
|   `-- p1_rag_final.ipynb      the whole Part 1 submission
|-- data/part1/                 files provided for Part 1 (see below)
`-- outputs/part1/              made by the notebook
    |-- visuals/                the 36 figure and table images
    |-- chroma_db/              the vector database
    |-- evaluation_results.csv  one row per golden question and system
    |-- evaluation_summary.csv  baseline and final system, side by side
    |-- results_table.csv       results table including the human rating columns
    |-- safety_probes.csv       Appendix C safety checks
    `-- human_groundedness.csv  sheet for the two raters
```

`chroma_db/`, `visuals/` and the PDFs are not stored in Git, because the notebook rebuilds them or the course provides them.

## Required Part 1 input files

Put these files in `data/part1/` (they come from Canvas or the Kaggle Data tab):

- `Document.pdf`
- `Document2_Supplement_A_Outturns_2011-2013.pdf`
- `Document3_Briefing_B_Labour_Prices_Policy.pdf`
- `kb_manifest.json`
- `Questions.csv`
- `validate_submission.py`

(`sample_submission.csv` is only a format example and is not needed to run the notebook.)

## Setup

We used Python 3.11 and a CUDA GPU.

```
conda create -n data266_lab2 python=3.11
conda activate data266_lab2
pip install -r requirements.txt
```

If `torch` installs without GPU support, install the CUDA build from https://pytorch.org first, then run the command above.

## How to run the notebook

1. Open `notebooks/p1_rag_final.ipynb` in VS Code or Jupyter and choose the environment above as the kernel.
2. Use **Restart & Run All**. Run it this way every time, so the saved outputs match the code. The notebook has no manual steps.
3. The first run downloads the models from Hugging Face (about 16 GB for the 7B model, so it takes a while).
4. On our RTX 4090 the whole notebook takes roughly 12 minutes.

The notebook creates everything it needs: the figure images, the database, the evaluation files and `submission.csv`.

### Which questions file is used (`QUESTIONS_PATH`)

The notebook reads the questions from the path in the environment variable `QUESTIONS_PATH`. If the variable is not set, it uses `Questions.csv` in the data folder. The graders use this to run their hidden question set. To use another file, set the variable before starting the notebook, for example in PowerShell:

```
$env:QUESTIONS_PATH = "C:\path\to\other_questions.csv"
```

The questions file must have the columns `id, conversation_id, turn, question_id, question`. It is read as text and the rows are answered conversation by conversation, in turn order.

### Where the results are saved

- Locally, figure images, the database and the evaluation files go to `outputs/part1/`, and `submission.csv` goes to the repository root.
- On Kaggle they go to `/kaggle/working/outputs/part1/` and `/kaggle/working/submission.csv`.

### How `submission.csv` is made and checked

The notebook answers every question and writes `submission.csv` with the columns `id, conversation_id, question_id, answer, figure_references, citations, status`. Lists are joined with commas and an empty list is written as `NONE`. Right after that, the notebook runs the validator.

You can also run the validator yourself:

```
python data/part1/validate_submission.py submission.csv data/part1/Questions.csv
```

It prints `valid: 40 rows` when the format is correct.

## Models used in Part 1

| Role | Model ID |
|---|---|
| Text embeddings | `BAAI/bge-small-en-v1.5` |
| Vision-language model (figure descriptions and answers) | `Qwen/Qwen2.5-VL-7B-Instruct`, loaded in 4-bit (NF4, float16 compute) |
| Smaller alternative we also tried | `Qwen/Qwen2.5-VL-3B-Instruct` (set `VLM_NAME` and `LOAD_IN_4BIT` in the setup cell) |

Other tools: ChromaDB (vector database), `rank_bm25` (keyword search), PyMuPDF (PDF reading). No hosted API is used. Everything runs on the local GPU. The random seed is 266 and the models answer without sampling, so reruns give the same answers.

## Running on Kaggle

1. Make a notebook inside the competition, so the competition files are attached under `/kaggle/input/`.
2. Upload `notebooks/p1_rag_final.ipynb`, choose a GPU (T4 or P100) and switch Internet on, because the libraries and models are downloaded.
3. Run all cells. The notebook finds the data folder by itself, reads `QUESTIONS_PATH` and writes `/kaggle/working/submission.csv`.

The lab requires all work to fit on one 16 GB GPU. With 4-bit loading the 7B model takes about 6 GB of GPU memory, and the notebook must finish within 90 minutes on Kaggle.

## Notes

- All settings (model names, 4-bit switch, image size limit, paths) are in the "Setup: Paths and Settings" cell.
- The model weights are downloaded by the notebook and are not stored in this repository.

## Part 2: Fine-tuning Stable Diffusion 1.5 with LoRA

We fine-tuned Stable Diffusion 1.5 on Pokemon artwork with LoRA, trained two runs that differ only in the LoRA rank, and compared both with the base model. The notebooks are finished and executed. The blinded human evaluation still needs its ratings (see below).

| Item | Choice |
|---|---|
| Dataset | Pokemon BLIP captions (`reach-vb/pokemon-blip-captions`, cc-by-nc-sa-4.0), 833 images, 830 after cleaning |
| Split | 90/10 with seed 266: 747 train, 83 test |
| Base model | `stable-diffusion-v1-5/stable-diffusion-v1-5`, 512x512 |
| Run 1 / Run 2 | LoRA rank 8 / LoRA rank 32. Same data, 3000 steps, batch size 4, learning rate 1e-4 (cosine), fp16, seed 266 |
| Training | Local RTX 4090, limited to 15 GB of GPU memory (both runs peaked below 4 GB, so they also fit a 16 GB GPU) |
| Generation | 20 fixed prompts x 2 seeds (0 and 1) x 3 models, 30 steps, guidance 7.5 |

### Notebooks (run them in this order, each with Restart & Run All)

Use the Jupyter kernel `DATA266 Lab2 Part2 GPU` (environment `data266_lab2_part2`, see `requirements-part2.txt` for the setup).

1. `notebooks/p2_1_data_prep.ipynb` (under 1 minute): loads the data, removes corrupted and duplicate images, splits 90/10, resizes to 512x512, describes the dataset, and writes the 20 prompts. The prompts were committed to Git before training started.
2. `notebooks/p2_2_finetune.ipynb` (about 35 minutes on an RTX 4090): trains the two runs with the unchanged diffusers script in `scripts/part2/` and prints the training table (parameters, learning rate, steps, batch size, peak memory, time).
3. `notebooks/p2_3_generate_evaluate.ipynb` (about 4 minutes): generates the images, makes the grids, computes KID, CLIP score and LPIPS, runs the NSFW and memorization checks, shows the failure modes, prepares the human evaluation and uploads to Hugging Face. To skip the upload set `UPLOAD_TO_HF = False` in its settings cell. To upload you need to be logged in (`huggingface-cli login`).

### Results

The final table is saved in `outputs/part2/metrics/results_table.csv` (KID: lower is better; the plus-minus is the spread over 100 subsets of 20 images, so it is only a rough guide):

| Model | KID (in-domain) | CLIP score | LPIPS diversity | Training GPU-hours | Peak GPU memory |
|---|---|---|---|---|---|
| Base SD 1.5 (baseline) | 0.0947 +/- 0.0090 | 32.82 | 0.830 | - | - |
| Run 1, LoRA rank 8 | 0.0531 +/- 0.0065 | 32.01 | 0.769 | 0.271 | 3.70 GB |
| **Run 2, LoRA rank 32 (final)** | **0.0356 +/- 0.0068** | 32.13 | 0.755 | 0.269 | 3.75 GB |

Both runs move the images much closer to the dataset (lower KID), rank 32 more than rank 8, at almost the same cost. The price is a small loss in prompt alignment (CLIP) and diversity. Prompts with several objects, counts or colours still go wrong. We chose run 2 because it has the lowest KID and its images clearly look like the dataset (flat cartoon creatures on a white background). More detail, the failure modes and the safety checks are in notebook 3.

The notebook also covers the two checks required for safety: the Stable Diffusion safety checker flagged 9 of 120 images (6 of them from the rank-32 run), and we looked at all of them (harmless cartoon creatures, false alarms); and a memorization check shows that the generated images are not closer to the training images than unseen test images are.

### Human evaluation (still to do)

The lab needs a blinded comparison of 25 image pairs (final run against the base model) by at least 3 raters: both team members and one person outside the team.

1. Send `outputs/part2/human_eval/rating_form.html` to each rater (it works offline in any browser; do not send `answer_key.csv`).
2. Each rater fills it in and clicks *Download my ratings*, which saves a `ratings_<name>.csv` file.
3. Put all rating files into `outputs/part2/human_eval/ratings/` and run notebook 3 again. The win rate and the rater agreement appear in its results table.

### Hugging Face

- Models: https://huggingface.co/SawantTej/pokemon-sd15-lora-r8 and https://huggingface.co/SawantTej/pokemon-sd15-lora-r32 (the card of the rank-32 model is the full model card of the final run)
- All generated images with prompt, seed and model: https://huggingface.co/datasets/SawantTej/pokemon-sd15-lora-generations

### Where the Part 2 files are

```
data/part2/                        the 20 prompts (prompts.json, prompts.csv)
outputs/part2/
|-- data_prep/                     split lists and cleaning summary (the 512x512 images are not in Git)
|-- runs/run1_lora_r8/             training log, loss log and summary of run 1 (the weights are on Hugging Face)
|-- runs/run2_lora_r32/            the same for run 2
|-- metrics/                       training table, loss curves, KID / CLIP / LPIPS results, results table
|-- human_eval/                    answer key and the folder for the rating files
|-- safety/                        NSFW check and memorization check (csv)
`-- generated/, grids/             the 120 images and the figures (not in Git, the images are on Hugging Face)
scripts/part2/                     the diffusers training script (unchanged, v0.42.1) and our small wrapper
```

### Limits and licenses

- The data is small and uniform, and the BLIP captions are weak and often wrong, so the model is good at the dataset's look but poor at counting, colours and arrangement.
- The characters are copyrighted and the dataset license is cc-by-nc-sa-4.0, so the models and images are for non-commercial research and education only. Stable Diffusion 1.5 uses the CreativeML OpenRAIL-M license.
- A first trial with 1500 steps changed the style only partly, so we raised the budget to 3000 steps before the final runs. This was decided from the diffusers reference recipe and from one generated image, not from a test metric.