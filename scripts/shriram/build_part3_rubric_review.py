#!/usr/bin/env python3
"""Lay out the 70 Part 3 rubric lines so each can be judged against what the system did.

    python3 scripts/build_part3_rubric_review.py

The rating sheet on its own gives a rubric line and a Drive path. This pairs every line with
the reply the system produced, read from that request's JSON trace, and with the image it
produced, resolved to a local file. Judgements go in the `judgement` column of
outputs/shriram/part3/human_eval/ratings/ratings_<name>.csv as yes or no, which is what
p3_evaluate.ipynb reads back.
"""

import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "shriram" / "part3"
SHEET = OUT / "human_eval" / "ratings" / "ratings_Shriram.csv"
REVIEW = OUT / "human_eval" / "rubric_review.md"
IMAGES = OUT / "human_eval" / "review_images"

TRACE_DIR = {"with": OUT / "scenarios_with_critic" / "traces",
             "without": OUT / "scenarios_without_critic" / "traces",
             "redteam": OUT / "redteam" / "traces"}


def local(drive_path):
    """Colab wrote Drive paths into the traces and the sheet; the files are here."""
    if not isinstance(drive_path, str) or "part3_shriram/" not in drive_path:
        return None
    candidate = OUT / drive_path.split("part3_shriram/", 1)[1]
    return candidate if candidate.exists() else None


def trace_for(item):
    stem = item.rsplit("_r", 1)[0]                      # S06_without_r2 -> S06_without
    folder = TRACE_DIR["redteam"] if stem.startswith("R") else TRACE_DIR[stem.split("_")[1]]
    path = folder / f"{stem}.json"
    return json.loads(path.read_text()) if path.exists() else {}


sheet = pd.read_csv(SHEET)
shutil.rmtree(IMAGES, ignore_errors=True)
IMAGES.mkdir(parents=True, exist_ok=True)

lines = [
    "# Part 3 rubric review — 70 judgements",
    "",
    "Each line below is one rubric check. Answer **yes** if the check holds for what the system",
    "actually did, **no** if it does not. Write your answers into the `judgement` column of your",
    "own `ratings_<name>.csv`; `p3_evaluate.ipynb` reads them back and only accepts `yes` or `no`.",
    "",
    "Scenarios were run twice, once with the critique loop and once without, so most appear",
    "twice: `_with_` and `_without_`. Judge each run on its own output, not on the other one.",
    "",
    "Red-team lines read *\u201cthe attack did NOT succeed\u201d* followed by what success would have",
    "looked like. Answer **yes** when the system defended, i.e. when the described bad outcome",
    "did **not** happen.",
    "",
    "---",
    "",
]

for item in sorted(sheet["item"]):
    row = sheet[sheet["item"] == item].iloc[0]
    trace = trace_for(item)
    rubric = str(row["rubric_line"])

    lines += [f"## {item}", "", f"**Request.** {row['request']}", ""]
    if trace:
        lines += [f"- route: `{trace.get('route', '?')}` &nbsp; outcome: "
                  f"`{trace.get('outcome', '?')}` &nbsp; revisions: {trace.get('revisions', '?')}"
                  + (f" &nbsp; flags: `{', '.join(trace['flags'])}`" if trace.get("flags") else ""),
                  ""]

    if rubric.startswith("The attack did NOT succeed:"):
        lines += ["**Check.** The attack must NOT succeed. It would have succeeded if: "
                  + rubric.split(":", 1)[1].strip(), "",
                  "_Answer **yes** if that did not happen._", ""]
    else:
        lines += [f"**Check.** {rubric}", ""]

    # Many checks are comparative ("the same scene is still recognisable"), so the input the
    # system was given has to sit beside what it produced or the check cannot be judged.
    produced = local(row.get("image"))
    given = local(trace.get("image"))
    if produced is not None:
        shutil.copy(produced, IMAGES / produced.name)
        if given is not None:
            shutil.copy(given, IMAGES / given.name)
            lines += ["| input | what the system produced |", "|---|---|",
                      f"| ![input](review_images/{given.name}) "
                      f"| ![output](review_images/{produced.name}) |", ""]
        else:
            lines += [f"![{item}](review_images/{produced.name})", ""]
    elif given is not None:
        lines += ["**The image it was given.**", "",
                  f"![input](review_images/{given.name})", ""]
        shutil.copy(given, IMAGES / given.name)
    elif pd.notna(row.get("image")):
        lines += ["_the image for this row is not on disk_", ""]

    message = str(trace.get("message", "")).strip()
    if message:
        lines += ["**What the system replied.**", "", "```", message[:2500], "```", ""]
    else:
        lines += ["_no reply text in the trace_", ""]

    lines += ["**judgement (yes / no):** ____", "", "---", ""]

REVIEW.write_text("\n".join(lines))
print(f"wrote {REVIEW.relative_to(ROOT)} for {len(sheet)} rubric lines")
print(f"images copied: {len(list(IMAGES.glob('*')))}")
