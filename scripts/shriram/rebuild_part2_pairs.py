#!/usr/bin/env python3
"""Rebuild the 25 blinded Part 2 image pairs from the Hugging Face copy of the generations.

    python3 scripts/shriram/rebuild_part2_pairs.py

Only 7 of the 25 pair folders survived the download from Drive, and each was missing one
side, so the blinded comparison could not be done. The notebook builds the pairs from
random.Random(266), which is deterministic, so running the same draw here reproduces exactly
the pairs and the left/right assignment the notebook wrote. The images come from
shriram14/data266-lab2-part2-images, which holds all 120 generations.

The regenerated answer_key.csv is checked against any existing one rather than trusted.
"""

import json
import random
from pathlib import Path

import pandas as pd
from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "shriram" / "part2" / "human_eval"
PROMPTS = json.loads((ROOT / "data" / "tejas" / "part2" / "prompts.json").read_text())

SEED, GEN_SEEDS, FINAL_RUN = 266, [0, 1], "lora_r32"

cache = Path(snapshot_download("shriram14/data266-lab2-part2-images", repo_type="dataset"))
prompt_text = {p["id"]: p["prompt"] for p in PROMPTS}

# The same draw the notebook made, in the same order, from the same seed.
rng = random.Random(SEED)
pairs = rng.sample([(p["id"], s) for p in PROMPTS for s in GEN_SEEDS], 25)

key_rows = []
for n, (prompt_id, seed) in enumerate(pairs, start=1):
    left_is_run = rng.random() < 0.5
    left_model = FINAL_RUN if left_is_run else "base"
    right_model = "base" if left_is_run else FINAL_RUN
    pair_dir = OUT / f"pair_{n:02d}"
    pair_dir.mkdir(parents=True, exist_ok=True)
    for side, model in (("left", left_model), ("right", right_model)):
        source = cache / f"{model}__{prompt_id}__seed{seed}.png"
        if not source.exists():
            raise SystemExit(f"{source.name} is not in the Hugging Face dataset")
        (pair_dir / f"{side}.png").write_bytes(source.read_bytes())
    key_rows.append({"pair": n, "prompt_id": prompt_id, "seed": seed,
                     "left_model": left_model, "right_model": right_model})

key = pd.DataFrame(key_rows)
key_path = OUT / "answer_key.csv"
if key_path.exists():
    existing = pd.read_csv(key_path)
    if not existing.equals(key):
        raise SystemExit("the rebuilt key differs from the committed one; do not overwrite it")
key.to_csv(key_path, index=False)

# A contact sheet so the 25 pairs can be judged without opening 50 files.
lines = ["# Part 2 blinded comparison — 25 pairs", "",
         "For each pair, which image is better? Answer **left** or **right** in both columns of",
         "`ratings/ratings_<name>.csv`:", "",
         "- `better_domain_style` — which looks more like the training domain: flat cartoon",
         "  creature artwork on a plain background.",
         "- `better_prompt_match` — which follows the prompt more faithfully.", "",
         "Which side is the fine-tuned model is recorded in `answer_key.csv`. **Do not open it",
         "before rating**; the comparison is only worth anything blind.", "", "---", ""]
for row in key.itertuples():
    lines += [f"## Pair {row.pair:02d}", "",
              f"**Prompt.** {prompt_text[row.prompt_id]}  _(seed {row.seed})_", "",
              f"| left | right |", "|---|---|",
              f"| ![left](pair_{row.pair:02d}/left.png) | ![right](pair_{row.pair:02d}/right.png) |",
              "", "**better_domain_style:** ____ &nbsp;&nbsp; **better_prompt_match:** ____",
              "", "---", ""]
(OUT / "pair_review.md").write_text("\n".join(lines))

print(f"rebuilt {len(key)} pairs in {OUT.relative_to(ROOT)}")
print(f"fine-tuned model on the left in {(key.left_model == FINAL_RUN).sum()} of 25")
