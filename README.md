# DATA 266 - Lab 2

Pair_Programming_Team_## - Parts 1 to 3. This file explains how to run each part.

| Part | Notebook | Status |
|---|---|---|
| 1. Multimodal RAG (Kaggle) | `notebooks/p1_rag_final.ipynb` | in progress |
| 2. Fine-tuning diffusion models | `notebooks/p2_finetune.ipynb` | not started |
| 3. Multi-agent image system | `notebooks/p3_agents.ipynb` | not started |

## Part 1 - Multimodal RAG over a read-only knowledge base

`notebooks/p1_rag_final.ipynb` is the whole submission. Running it from top to bottom builds everything it needs and writes all result files by itself, with no manual step.

### What the notebook does

1. Reads the three PDFs and `kb_manifest.json` (document IDs and trust levels).
2. Cuts the text into chunks and saves every numbered figure and table as an image.
3. Describes each image with a vision-language model so figures can be searched. Tables are also read as exact text.
4. Stores every item (text chunks, pages, figure descriptions, table rows) in ChromaDB with `doc_id`, `page`, `figure_id` and `trust_level`.
5. Retrieves with dense search (ChromaDB) plus BM25, fused with reciprocal rank fusion. A figure or table named in the question is always retrieved.
6. Writes the grounded JSON answer (answer, status, citations, figure references) with the vision-language model, applying the answering rules (revisions, outturns, conflicts, false premises, low-trust content).
7. Keeps one memory per `conversation_id`. Values given by the user are stored only in that memory, never in ChromaDB.
8. Reads `Questions.csv`, writes `submission.csv` and validates it with `validate_submission.py`.
9. Evaluates a dense-only baseline and the final system on the 25-question golden set (answer correctness, Recall@5, citation accuracy, median seconds, human groundedness) and runs the safety probes for Document 3 Appendix C.

### Models

| Role | Model |
|---|---|
| Text embeddings | `BAAI/bge-small-en-v1.5` |
| Vision-language model (descriptions, answers) | `Qwen/Qwen2.5-VL-7B-Instruct`, 4-bit (`LOAD_IN_4BIT`); `Qwen/Qwen2.5-VL-3B-Instruct` is the smaller alternative |
| Vector database | ChromaDB |
| Keyword search | `rank_bm25` |

No hosted API is used. Everything runs locally on one GPU and fits in 16 GB.

### Run locally

```
conda create -n data266_lab2 python=3.11
conda activate data266_lab2
pip install -r requirements.txt
```

Open `notebooks/p1_rag_final.ipynb`, choose the kernel and use **Restart & Run All**. Put the three PDFs, `kb_manifest.json`, `Questions.csv` and `validate_submission.py` in `data/part1/` (they are not stored in Git).

Generated files (not stored in Git) go to `outputs/part1/`; `submission.csv` goes to the repository root.

### Run on Kaggle

1. Create a notebook inside the competition, so the competition data is attached under `/kaggle/input/`.
2. Upload `notebooks/p1_rag_final.ipynb` (the commit tagged `p1-v1.0`), choose a GPU (T4 or P100) and turn Internet on, because the models and libraries are downloaded.
3. Run all cells. The notebook finds the data folder by itself and writes `/kaggle/working/submission.csv`.
4. To use a different question file, set the environment variable `QUESTIONS_PATH`.

### Settings

All settings are in the "Setup" cell: model names, `LOAD_IN_4BIT`, the image size limit and the output paths. The random seed is 266.
