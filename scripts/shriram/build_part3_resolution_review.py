#!/usr/bin/env python3
"""Lay out the Part 3 checks the two raters disagreed on, so they can be settled together.

    python3 scripts/shriram/build_part3_resolution_review.py

Each entry shows the check, what each rater said, the input and output images, and the
reply from the request's JSON trace. Decisions go in the `final_judgement` column of
outputs/shriram/part3/human_eval/ratings/resolution.csv as yes or no, with a short `note`.
That is the same shape as the resolution file Tejas's own Part 3 evaluation used.
"""

import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "shriram" / "part3"
HE = OUT / "human_eval"
REVIEW = HE / "resolution_review.md"
IMAGES = HE / "resolution_images"

shriram = pd.read_csv(HE / "ratings" / "ratings_Shriram.csv")
tejas = pd.read_csv(HE / "ratings" / "ratings_Tejas.csv")
disagree = shriram[shriram["judgement"] != tejas["judgement"]].copy()
disagree["tejas"] = tejas.loc[disagree.index, "judgement"]


def trace(item):
    stem = item.rsplit("_r", 1)[0]
    folder = ("redteam/traces" if stem.startswith("R")
              else f"scenarios_{'with' if '_with_' in item else 'without'}_critic/traces")
    path = OUT / folder / f"{stem}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def local(drive_path):
    if not isinstance(drive_path, str) or "part3_shriram/" not in drive_path:
        return None
    candidate = OUT / drive_path.split("part3_shriram/", 1)[1]
    return candidate if candidate.exists() else None


shutil.rmtree(IMAGES, ignore_errors=True)
IMAGES.mkdir(parents=True, exist_ok=True)

lines = [
    f"# Part 3: the {len(disagree)} checks we judged differently",
    "",
    f"Shriram and Tejas agree on {len(shriram) - len(disagree)} of {len(shriram)} checks. These "
    "are the rest. Settle each one together and write **yes** or **no** in the "
    "`final_judgement` column of `ratings/resolution.csv`, with a one-line `note` saying why.",
    "",
    "This is not a tie-break for its own sake. Under Shriram's sheet the critique loop improves "
    "the pass rate and under Tejas's it reduces it, so how these land decides what Part 3 "
    "claims.",
    "",
    "---",
    "",
]

for row in disagree.itertuples():
    tr = trace(row.item)
    rubric = str(row.rubric_line)
    lines += [f"## {row.item}", "", f"**Request.** {row.request}", ""]
    if tr:
        lines += [f"- route: `{tr.get('route', '?')}` &nbsp; outcome: "
                  f"`{tr.get('outcome', '?')}` &nbsp; revisions: {tr.get('revisions', '?')}", ""]

    if rubric.startswith("The attack did NOT succeed:"):
        lines += ["**Check.** The attack must NOT succeed. It would have succeeded if: "
                  + rubric.split(":", 1)[1].strip(), "",
                  "_**yes** means the system defended._", ""]
    else:
        lines += [f"**Check.** {rubric}", ""]

    lines += [f"**Shriram said {row.judgement}. &nbsp; Tejas said {row.tejas}.**", ""]

    produced, given = local(row.image), local(tr.get("image"))
    if produced is not None:
        shutil.copy(produced, IMAGES / produced.name)
        if given is not None:
            shutil.copy(given, IMAGES / given.name)
            lines += ["| input | what the system produced |", "|---|---|",
                      f"| ![input](resolution_images/{given.name}) "
                      f"| ![output](resolution_images/{produced.name}) |", ""]
        else:
            lines += [f"![output](resolution_images/{produced.name})", ""]

    message = str(tr.get("message", "")).strip()
    if message:
        lines += ["**What the system replied.**", "", "```", message[:1800], "```", ""]

    lines += ["**final_judgement (yes / no):** ____ &nbsp;&nbsp; **note:** ____", "", "---", ""]

REVIEW.write_text("\n".join(lines))
print(f"wrote {REVIEW.relative_to(ROOT)} for {len(disagree)} disputed checks")
print(f"images copied: {len(list(IMAGES.glob('*')))}")
