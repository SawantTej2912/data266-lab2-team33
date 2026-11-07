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
|-- notebooks/        p1_rag_final.ipynb, p2_finetune.ipynb (planned), p3_agents.ipynb (planned)
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

## Part 2: Fine-tuning Stable Diffusion 1.5 with LoRA (in progress)

Nothing is trained yet. This is the plan and the folder structure. Results will be added when the notebooks have run.

| Item | Choice |
|---|---|
| Dataset | Pokemon BLIP captions (`reach-vb/pokemon-blip-captions`) |
| Base model | `stable-diffusion-v1-5/stable-diffusion-v1-5`, 512x512 |
| Run 1 | LoRA, rank 8 |
| Run 2 | LoRA, rank 32 (same data and same number of steps as run 1) |
| Training | Local RTX 4090, kept under 16 GB of GPU memory, fp16 |
| Random seed | 266 (also used for the 90/10 train/test split) |
| Environment | Separate conda environment `data266_lab2_part2` |

Environment: the exact setup is at the top of `requirements-part2.txt` (Python 3.11, the same CUDA 13.0 PyTorch build as Part 1). The Jupyter kernel is called `DATA266 Lab2 Part2 GPU`.

Licenses: the Pokemon BLIP captions dataset is `cc-by-nc-sa-4.0` (attribution, non-commercial, share-alike) and Stable Diffusion 1.5 uses the CreativeML OpenRAIL-M license. The Pokemon characters are copyrighted, so our model and images are for non-commercial research only.

Where the Part 2 files go:

```
data/part2/                        prompts (written before training), train/test split lists
outputs/part2/
|-- data_prep/                     counts of removed images, split lists
|-- runs/run1_lora_r8/             training log and summary of run 1 (weights go to Hugging Face)
|-- runs/run2_lora_r32/            training log and summary of run 2
|-- generated/{base,run1_lora_r8,run2_lora_r32}/   the 40 images of each model (go to Hugging Face)
|-- grids/                         side-by-side grids for 8 prompts
|-- metrics/                       KID, CLIP score and LPIPS results (csv)
|-- human_eval/                    blinded image pairs and the rating sheets
`-- safety/                        NSFW check and memorization check
scripts/part2/                     the diffusers LoRA training script
notebooks/p2_finetune.ipynb        may be split into a few notebooks later
```

Model weights, generated images and processed images are not stored in Git. They go to Hugging Face.
