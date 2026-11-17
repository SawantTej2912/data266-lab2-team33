import json, re, shutil
from pathlib import Path
import pandas as pd
import pymupdf

LAB = Path("/Users/x-sdundigalla/Desktop/GenAI/Lab2")
DATA, OUT = LAB / "data/part1", LAB / "outputs/part1_shriram"

manifest = json.loads((DATA / "kb_manifest.json").read_text())
files = {d["doc_id"]: DATA / d["file"] for d in manifest["documents"]}
docs = {k: pymupdf.open(v) for k, v in files.items()}
titles = {d["doc_id"]: d["title"] for d in manifest["documents"]}

visual_index = pd.read_csv(OUT / "visual_index.csv")
page_of = {(r.doc_id, r.figure_id.lower()): r.page for r in visual_index.itertuples()}
crops = {p.name: p for p in (OUT / "visuals").glob("*.png")}

evaluation = pd.read_csv(OUT / "evaluation_results.csv")
final = evaluation[evaluation["system"] != "dense baseline"].set_index("id")
rated = pd.read_csv("/tmp/ratings_backup_both_columns.csv").set_index("id")
merged = pd.read_csv(OUT / "human_groundedness.csv").set_index("id")
golden = {g["id"]: g for g in json.loads((DATA / "golden_set.json").read_text())}

REDO = list(merged.index)   # Tejas rates all 25 himself, nothing carried over


def crop_for(doc_id, label):
    stem = f"{doc_id}_p{page_of.get((doc_id, label.lower()), '')}_{re.sub(r'[^A-Za-z0-9]+', '_', label)}"
    return crops.get(stem + ".png")


def source_text(tag):
    """The actual words behind a citation like DOC3:Table B-1 or DOC1:p10."""
    doc_id, ref = tag.split(":", 1)
    if doc_id not in docs:
        return None, None
    if ref.lower().startswith("p") and ref[1:].isdigit():
        page = int(ref[1:])
        return docs[doc_id][page - 1].get_text().strip(), None
    page = page_of.get((doc_id, ref.lower()))
    if page is None:
        return None, None
    return docs[doc_id][page - 1].get_text().strip(), crop_for(doc_id, ref)


review_dir = OUT / "groundedness_sources"
shutil.rmtree(review_dir, ignore_errors=True)
review_dir.mkdir(parents=True, exist_ok=True)

lines = [
    "# Groundedness review — all 25 answers from the graded Kaggle run",
    "",
    "Rate each answer 1–5 for **groundedness**: does the cited source actually support what the",
    "answer claims? Not whether the answer is the one you hoped for — whether the words below it",
    "back it up.",
    "",
    "| | meaning |",
    "|---|---|",
    "| 5 | every claim is in the cited source, with the same numbers |",
    "| 4 | supported, with a small wording or unit slip |",
    "| 3 | partly supported; something is added or missing |",
    "| 2 | the source is related but does not support the claim |",
    "| 1 | the source does not support it at all, or the number is not there |",
    "",
    "Each answer below is the one the **graded Kaggle run** produced, copied from",
    "`outputs/part1_shriram/evaluation_results.csv`. Under it is the full text of every source it",
    "cited. Write your number on the `rating_tejas:` line in `human_groundedness.csv`.",
    "",
    "---",
    "",
]

for qid in REDO:
    answer = str(final.loc[qid, "answer"]).strip()
    citations = str(final.loc[qid, "citations"]).strip()
    status = str(final.loc[qid, "status"]).strip()
    previous = rated.loc[qid, "answer"]
    gold = golden.get(qid, {})

    lines += [f"## {qid}", "", f"**Question.** {merged.loc[qid, 'question']}", ""]
    lines += [f"**The answer the system gave.** {answer}", ""]
    lines += [f"- status: `{status}`", f"- citations: `{citations}`", ""]
    if gold.get("expected_answer"):
        lines += [f"- the golden set expected: {gold['expected_answer']}", ""]
    # Shriram's score is deliberately not shown. Seeing it first would turn the agreement
    # statistic into a measure of anchoring rather than of two independent judgements.

    lines += ["### What the cited sources actually say", ""]
    if citations.upper() in ("NONE", "NAN", ""):
        lines += ["The answer cites nothing. Rate whether a claim is being made that would have needed a source.", ""]
    for tag in [t.strip() for t in citations.split(",") if ":" in t]:
        text, crop = source_text(tag)
        lines += [f"**`{tag}`**", ""]
        if crop is not None:
            target = review_dir / crop.name
            shutil.copy(crop, target)
            lines += [f"![{tag}](groundedness_sources/{crop.name})", ""]
        if text:
            lines += ["```", text[:3500], "```", ""]
        else:
            lines += ["_source not found in the documents — that alone is worth a low rating._", ""]

    lines += ["**rating_tejas:** ____", "", "---", ""]

(OUT / "groundedness_review.md").write_text("\n".join(lines))
print(f"wrote groundedness_review.md for {len(REDO)} questions: {', '.join(REDO)}")
print(f"crops copied: {len(list(review_dir.glob('*.png')))}")
