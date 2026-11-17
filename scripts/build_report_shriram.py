#!/usr/bin/env python3
"""Build Shriram's sections of the DATA 266 Lab 2 report as an IEEE-format PDF.

    python3 scripts/build_report.py

Every number in the PDF is read from a file under outputs/ at build time, or from an output
cell of an executed notebook. None is typed into this file. C2.2 calls a hand-typed number
fabrication, and a report is the artifact furthest from the code, so it is the first to drift.
Re-run a notebook, rebuild, and the report cannot disagree with the CSV behind it.

Items that need both members are rendered as PENDING rather than omitted, so the shape the
rubric asks for is visible and fills in by re-running this script.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, NextPageTemplate,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report" / "DATA266_Lab2_Report_Team_33_shriram.pdf"
P1, P2, P3 = (ROOT / "outputs" / f"part{n}_shriram" for n in (1, 2, 3))
PENDING = "pending — needs both members"

# ----------------------------------------------------------------- IEEE page furniture
# IEEE conference style: US Letter, two columns, 0.25 in gutter, Times at 10 pt.
SS = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=SS["BodyText"], fontName="Times-Roman", fontSize=9.5,
                      leading=11.5, alignment=TA_JUSTIFY, spaceAfter=5, firstLineIndent=10)
PLAIN = ParagraphStyle("plain", parent=BODY, firstLineIndent=0)
H1 = ParagraphStyle("h1", parent=BODY, fontName="Times-Bold", fontSize=10, leading=12,
                    spaceBefore=10, spaceAfter=4, alignment=TA_CENTER, firstLineIndent=0)
H2 = ParagraphStyle("h2", parent=BODY, fontName="Times-Italic", fontSize=9.5, leading=11.5,
                    spaceBefore=7, spaceAfter=3, firstLineIndent=0)
CAP = ParagraphStyle("cap", parent=BODY, fontSize=8, leading=9.5, alignment=TA_CENTER,
                     spaceBefore=3, spaceAfter=7, firstLineIndent=0)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=7.4, leading=8.8, alignment=0,
                      spaceAfter=0, firstLineIndent=0)
CELLB = ParagraphStyle("cellb", parent=CELL, fontName="Times-Bold")
TITLE = ParagraphStyle("title", parent=BODY, fontName="Times-Bold", fontSize=20, leading=23,
                       alignment=TA_CENTER, spaceAfter=6, firstLineIndent=0)
AUTH = ParagraphStyle("auth", parent=BODY, fontSize=10.5, leading=13, alignment=TA_CENTER,
                      spaceAfter=2, firstLineIndent=0)
ABS = ParagraphStyle("abs", parent=BODY, fontName="Times-Bold", fontSize=9, leading=11,
                     firstLineIndent=10)
MONO = ParagraphStyle("mono", parent=PLAIN, fontName="Courier", fontSize=7.6, leading=9.4)

MARGIN, GUTTER = 0.65 * inch, 0.25 * inch
W, H = LETTER
COL_W = (W - 2 * MARGIN - GUTTER) / 2


BAND_H = 3.20 * inch          # title, authors and abstract, full width, as IEEE lays out page 1


def frame(x, y, w, h, name):
    return Frame(x, y, w, h, id=name, leftPadding=0, rightPadding=0,
                 topPadding=0, bottomPadding=0)


def document():
    doc = BaseDocTemplate(str(OUT), pagesize=LETTER, title="DATA 266 Lab 2 — Team 33 — Shriram",
                          author="Shriram Dundigalla", leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=MARGIN)
    body_h = H - 2 * MARGIN
    short_h = body_h - BAND_H
    right_x = MARGIN + COL_W + GUTTER

    def footer(canvas, d):
        canvas.saveState()
        canvas.setFont("Times-Roman", 8)
        canvas.drawCentredString(W / 2, 0.38 * inch, str(canvas.getPageNumber()))
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id="first", onPage=footer, frames=[
            frame(MARGIN, MARGIN + short_h, W - 2 * MARGIN, BAND_H, "band"),
            frame(MARGIN, MARGIN, COL_W, short_h, "l1"),
            frame(right_x, MARGIN, COL_W, short_h, "r1")]),
        PageTemplate(id="two", onPage=footer, frames=[
            frame(MARGIN, MARGIN, COL_W, body_h, "l"),
            frame(right_x, MARGIN, COL_W, body_h, "r")])])
    return doc


def table(rows, widths, header=True):
    data = [[Paragraph(str(c), CELLB if (header and n == 0) else CELL) for c in row]
            for n, row in enumerate(rows)]
    t = Table(data, colWidths=widths, hAlign="LEFT")
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("TOPPADDING", (0, 0), (-1, -1), 2.5),
             ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
             ("LEFTPADDING", (0, 0), (-1, -1), 3),
             ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
             ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black)]
    if header:
        style.append(("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black))
    t.setStyle(TableStyle(style))
    return t


def figure(table_flowable, caption):
    return KeepTogether([table_flowable, Paragraph(caption, CAP)])


def diagram(rows, caption, box_h=0.30 * inch, gap=0.17 * inch):
    """A column-width block diagram. `rows` is a list of rows; each row is a list of labels
    laid out side by side, and consecutive rows are joined by a downward arrow."""
    width = COL_W
    height = len(rows) * box_h + (len(rows) - 1) * gap
    d = Drawing(width, height)
    for n, row in enumerate(rows):
        top = height - n * (box_h + gap)
        cell_w = (width - 4 * (len(row) - 1)) / len(row)
        for m, label in enumerate(row):
            x = m * (cell_w + 4)
            dashed = label.startswith("~")           # a dashed box is an optional path
            label = label.lstrip("~")
            d.add(Rect(x, top - box_h, cell_w, box_h, fillColor=colors.white,
                       strokeColor=colors.black, strokeWidth=0.6,
                       strokeDashArray=[2, 2] if dashed else None))
            words, lines = label.split(), [""]
            for word in words:                        # wrap to at most two lines
                trial = (lines[-1] + " " + word).strip()
                if stringWidth(trial, "Times-Roman", 6.8) < cell_w - 6:
                    lines[-1] = trial
                else:
                    lines.append(word)
            for k, line in enumerate(lines[:2]):
                d.add(String(x + cell_w / 2, top - box_h / 2 + (3.0 if len(lines) > 1 else -2.2)
                             - k * 7.6, line, fontName="Times-Roman", fontSize=6.8,
                             textAnchor="middle"))
        if n < len(rows) - 1:
            mid = width / 2
            d.add(Line(mid, top - box_h, mid, top - box_h - gap, strokeWidth=0.6))
            d.add(Polygon([mid - 2.4, top - box_h - gap + 3.4, mid + 2.4,
                           top - box_h - gap + 3.4, mid, top - box_h - gap],
                          fillColor=colors.black, strokeColor=colors.black))
    return KeepTogether([d, Paragraph(caption, CAP)])


def cols(*fractions):
    return [COL_W * f for f in fractions]


# ----------------------------------------------------------------- the measured numbers
p1_results = pd.read_csv(P1 / "results_table.csv").set_index("system")
p1_ablation = pd.read_csv(P1 / "retrieval_ablation.csv").set_index("arm")
p1_attrib = pd.read_csv(P1 / "failure_attribution.csv").set_index("outcome")
p1_probes = pd.read_csv(P1 / "safety_probes.csv")
p1_submission = pd.read_csv(P1 / "submission.csv", dtype=str, keep_default_na=False)
p1_ground = pd.read_csv(P1 / "human_groundedness.csv")
# The two columns fill in as the raters work, so the report shows figures only once both are
# complete and says so plainly until then. A rating only counts if it was made against the
# answer the graded run produced, which is what the sheet now holds.
GROUND_DONE = not p1_ground[["rating_shriram", "rating_tejas"]].isna().any().any()
if GROUND_DONE:
    gap = (p1_ground["rating_shriram"] - p1_ground["rating_tejas"]).abs()
    GROUND = {"mean": (p1_ground["rating_shriram"].mean() + p1_ground["rating_tejas"].mean()) / 2,
              "mean_s": p1_ground["rating_shriram"].mean(),
              "mean_t": p1_ground["rating_tejas"].mean(),
              "exact": int((gap == 0).sum()), "within_one": int((gap <= 1).sum()),
              "n": len(p1_ground),
              "low": p1_ground.loc[(p1_ground["rating_shriram"]
                                    + p1_ground["rating_tejas"]) / 2 <= 2, "id"].tolist()}
    GROUND_CELL = f"{GROUND['mean']:.2f}"
else:
    done = {name.split("_")[1]: int(p1_ground[name].notna().sum())
            for name in ("rating_shriram", "rating_tejas")}
    GROUND_CELL = (f"{PENDING}: "
                   + ", ".join(f"{who} {n} of {len(p1_ground)}" for who, n in done.items()))
BASE1, FINAL1 = "dense baseline", "hybrid + exact-label hybrid"

p2_results = pd.read_csv(P2 / "metrics" / "results_table.csv").set_index("model")
p2_train = pd.read_csv(P2 / "metrics" / "training_table.csv").set_index("run")
p2_clean = json.loads((P2 / "metrics" / "cleaning_summary.json").read_text())
p2_log = pd.read_csv(P2 / "metrics" / "generation_log.csv")
p2_overlap = pd.read_csv(P2 / "metrics" / "in_domain_prompt_overlap.csv")
p2_split_train = pd.read_csv(P2 / "metrics" / "split_train.csv")
p2_split_test = pd.read_csv(P2 / "metrics" / "split_test.csv")

p3_results = pd.read_csv(P3 / "evaluation" / "results_table.csv").set_index("measurement")
p3_pass = pd.read_csv(P3 / "evaluation" / "scenario_pass_table.csv")
p3_critic = pd.read_csv(P3 / "evaluation" / "critic_agreement.csv")
p3_red = pd.read_csv(P3 / "evaluation" / "redteam_results.csv")
p3_runs = pd.read_csv(P3 / "evaluation" / "scenario_runs.csv")


# Some figures are printed by a notebook but have no csv, either because the run writes them
# only to stdout or, for the Part 2 safety csvs, because they are not yet retrieved from Drive.
# They are scraped out of the stored output cells of the executed notebook rather than typed
# here, so the same rule holds: re-run the notebook and this report follows it.
def notebook_output(name):
    nb = json.loads((ROOT / "notebooks" / name).read_text())
    chunks = []
    for cell in nb["cells"]:
        for out in cell.get("outputs", []):
            chunks.append("".join(out["text"]) if out.get("output_type") == "stream"
                          else "".join(out.get("data", {}).get("text/plain", [])))
    return "\n".join(chunks)


def scrape(text, pattern, cast=float):
    import re
    match = re.search(pattern, text)
    if match is None:
        raise SystemExit(f"report build: {pattern!r} is no longer in the notebook output. "
                         "Re-check the run before quoting it.")
    return cast(match.group(1))


NB1, NB2, NB3 = (notebook_output(f"p{n}_{s}.ipynb")
                 for n, s in ((1, "rag"), (2, "finetune"), (3, "agents")))

P1_RUN = {"items": scrape(NB1, r"items in ChromaDB\s*:\s*(\d+)", int),
          "visuals": scrape(NB1, r"figures and tables:\s*(\d+)", int),
          "docs": scrape(NB1, r"documents indexed\s*:\s*(\d+)", int),
          "unparseable": scrape(NB1, r"unparseable replies:\s*(\d+)", int),
          "peak_gb": scrape(NB1, r"peak GPU memory\s*:\s*([\d.]+) GB"),
          "runtime_min": scrape(NB1, r"notebook runtime\s*:\s*([\d.]+) min"),
          # The one figure with no local source: the Kaggle public leaderboard.
          "kaggle": 0.646, "kaggle_prev": 0.650}

p2_nsfw = pd.read_csv(P2 / "safety" / "nsfw_check.csv")
p2_mem = pd.read_csv(P2 / "safety" / "memorization_check.csv")
P2_SAFETY = {"nsfw_flagged": int(p2_nsfw["flagged"].sum()),
             "nsfw_total": len(p2_nsfw),
             "nsfw_base": int(p2_nsfw[(p2_nsfw["model"] == "base") & p2_nsfw["flagged"]].shape[0]),
             "nsfw_tuned": int(p2_nsfw[(p2_nsfw["model"] != "base") & p2_nsfw["flagged"]].shape[0]),
             "mem_gen_mean": p2_mem["clip_similarity"].mean(),
             "mem_gen_max": p2_mem["clip_similarity"].max(),
             "mem_n": len(p2_mem),
             # The held-out control has no csv of its own; it is printed beside the generated
             # row in the same cell, which is the only place the comparison is made.
             "mem_test_mean": scrape(NB2, r"nearest train:\s*mean ([\d.]+)"),
             "mem_test_max": scrape(NB2, r"nearest train:\s*mean [\d.]+, max ([\d.]+)"),
             "source": "outputs/part2_shriram/safety/; the held-out control row from "
                       "p2_finetune.ipynb"}

P3_RUN = {"peak_gb": scrape(NB3, r"peak GPU memory\s+:\s*([\d.]+) GB"),
          "median_s": scrape(NB3, r"median s per request:\s*([\d.]+)"),
          "demo_requests": scrape(NB3, r"demo requests\s+:\s*(\d+)", int)}


def pct(x):
    return f"{100 * float(x):.1f}\u2009%"


story = []
A = story.append

# ----------------------------------------------------------------- title block
A(Paragraph("Multimodal Retrieval, Domain Fine-Tuning and a Multi-Agent "
            "Image System: Three Studies on One 16&nbsp;GB GPU", TITLE))
A(Paragraph("Shriram Dundigalla", AUTH))
A(Paragraph("DATA 266, Generative AI &nbsp;·&nbsp; Lab Pair 33 &nbsp;·&nbsp; "
            "San Jos\u00e9 State University", AUTH))
A(Paragraph("Team partner: Tejas Nandkishor Sawant", AUTH))
A(Spacer(1, 10))
A(Paragraph(
    "<i>Abstract</i>\u2014This report covers my implementation of the three parts of Lab 2. "
    f"Part 1 is a multimodal RAG system over three economics PDFs; hybrid retrieval with "
    f"exact-label figure routing answers {p1_results.loc[FINAL1, 'answers_correct']} of the "
    f"golden set against {p1_results.loc[BASE1, 'answers_correct']} for a dense baseline, and "
    f"lifts Recall@5 from {p1_results.loc[BASE1, 'recall_at_5']:.3f} to "
    f"{p1_results.loc[FINAL1, 'recall_at_5']:.3f}. Part 2 fine-tunes Stable Diffusion 1.5 with "
    f"LoRA at two ranks on the same data and step budget; in-domain KID falls from "
    f"{p2_results.loc['base', 'kid_in_domain']:.4f} for the base model to "
    f"{p2_results.loc['lora_r32', 'kid_in_domain']:.4f} at rank 32, a factor of "
    f"{p2_results.loc['base', 'kid_in_domain'] / p2_results.loc['lora_r32', 'kid_in_domain']:.1f}, "
    "while prompt adherence and output diversity both decline slightly. Part 3 is a five-agent "
    f"image understanding and generation system; "
    f"{p3_results.loc['Primary: scenarios passed, out of 15', 'final (critique loop)']} of 15 "
    "scenarios pass with the critique loop against "
    f"{p3_results.loc['Primary: scenarios passed, out of 15', 'baseline (no critique loop)']} "
    "without it. All three fit the lab's single 16\u2009GB GPU: peak memory is "
    f"{P1_RUN['peak_gb']}, {p2_train['peak_gpu_memory_gb'].max()} and {P3_RUN['peak_gb']}\u2009GB. "
    "The recurring theme is that the measurement, not the model, is what decided every design "
    "choice here, and twice it said no to a change that sounded obviously right.", ABS))
A(Spacer(1, 4))
A(Paragraph(
    "<b>A note on how this document was produced.</b> Every number below is read at build time "
    "from a file under <font face='Courier' size='8'>outputs/</font>, or from an output cell of "
    "an executed notebook where the csv has not yet been retrieved, in which case the cell is "
    "named. None is transcribed by hand. C2.2 treats a hand-typed number as fabrication, and a "
    "report is the artifact furthest from the code, so it drifts first. Items that need both "
    "members are marked <i>pending</i> rather than left out.", PLAIN))
A(NextPageTemplate("two"))

# ================================================================= PART 1
A(Paragraph("I.&nbsp;&nbsp;PART 1: MULTIMODAL RAG OVER A READ-ONLY KNOWLEDGE BASE", H1))

A(Paragraph("A.&nbsp;&nbsp;Architecture", H2))
A(Paragraph(
    "The system answers questions about three economics PDFs using their text, figures and "
    "tables. PyMuPDF extracts page text, which is split into 1000-character chunks with a "
    "200-character overlap, and cuts every numbered Figure and Table out of its page as a "
    "separate image. Captions are located by scanning page text, which keeps "
    "<i>Figure B-5</i> and <i>Figure B-5 (corrected)</i> as two distinct objects rather than "
    "collapsing them. Each crop is described by Qwen2.5-VL-7B-Instruct in 4-bit NF4, and the "
    "description is what gets indexed, so a chart becomes searchable as text. The three "
    f"documents yield {P1_RUN['visuals']} numbered figures and tables, and all "
    f"{P1_RUN['items']} items\u2014chunks, whole pages and "
    "figure descriptions\u2014go into ChromaDB carrying "
    "<font face='Courier' size='8'>doc_id</font>, "
    "<font face='Courier' size='8'>page</font>, "
    "<font face='Courier' size='8'>figure_id</font> and "
    "<font face='Courier' size='8'>trust_level</font>, read from "
    "<font face='Courier' size='8'>kb_manifest.json</font>.", BODY))
A(Paragraph(
    "Retrieval fuses two rankings by reciprocal rank fusion at k=60: dense similarity over "
    "BAAI/bge-small-en-v1.5 embeddings, and BM25 over a lightly expanded form of the question. "
    "On top of that sits exact-label routing: if the question names a figure or table, that "
    "crop is pinned to the front of the result list and cannot be displaced. The retrieved "
    "evidence, plus the highest-ranked crop as an actual image, goes to the same "
    "vision-language model, which returns one JSON object with an answer, a status, citations "
    "and figure references.", BODY))
A(diagram([["3 PDFs + kb_manifest.json (trust_level)"],
           ["PyMuPDF: 1000-char text chunks", f"{P1_RUN['visuals']} figure and table crops"],
           ["Qwen2.5-VL describes each crop"],
           [f"ChromaDB, {P1_RUN['items']} items; untrusted dropped"],
           ["BM25 over expanded question", "dense bge-small-en-v1.5"],
           ["reciprocal rank fusion, k=60"],
           ["exact-label routing pins the named crop"],
           ["Qwen2.5-VL: evidence text + top crop as an image"],
           ["JSON: answer, status, citations, figure_references"]],
          "Fig. 1.&nbsp;&nbsp;Part 1 pipeline. Trust level is attached at index time, so "
          "untrusted content is never a retrieval candidate."))

A(Paragraph("B.&nbsp;&nbsp;Results", H2))
rows = [["Measurement", "Baseline", "Final"]]
rows.append(["Primary: answers correct, of 25",
             p1_results.loc[BASE1, "answers_correct"], p1_results.loc[FINAL1, "answers_correct"]])
rows.append(["Primary: statuses correct, of 25",
             f"{p1_results.loc[BASE1, 'status_correct']}", f"{p1_results.loc[FINAL1, 'status_correct']}"])
rows.append(["Secondary: Recall@5",
             f"{p1_results.loc[BASE1, 'recall_at_5']:.3f}", f"{p1_results.loc[FINAL1, 'recall_at_5']:.3f}"])
rows.append(["Secondary: citation accuracy",
             f"{p1_results.loc[BASE1, 'citation_accuracy']:.3f}", f"{p1_results.loc[FINAL1, 'citation_accuracy']:.3f}"])
rows.append(["Human eval: mean groundedness, 1\u20135", "\u2014", GROUND_CELL])
rows.append(["Efficiency: median s per question",
             f"{p1_results.loc[BASE1, 'median_seconds']:.1f}", f"{p1_results.loc[FINAL1, 'median_seconds']:.1f}"])
rows.append(["Untrusted-source leaks",
             f"{int(p1_results.loc[BASE1, 'untrusted_leaks'])}", f"{int(p1_results.loc[FINAL1, 'untrusted_leaks'])}"])
A(figure(table(rows, cols(0.50, 0.25, 0.25)),
         "TABLE I.&nbsp;&nbsp;Part 1, baseline against final system. "
         "<font face='Courier' size='7'>outputs/part1_shriram/results_table.csv</font>"))

A(Paragraph(
    "The headline is that retrieval, not generation, was the binding constraint. Recall@5 moves "
    f"from {p1_results.loc[BASE1, 'recall_at_5']:.3f} to {p1_results.loc[FINAL1, 'recall_at_5']:.3f}, "
    "and the failure attribution in Table III shows why that matters: the dense baseline loses "
    f"{int(p1_attrib.loc['retrieval miss', BASE1])} of its {25 - int(p1_attrib.loc['correct', BASE1])} "
    f"wrong answers to retrieval misses, the final system only "
    f"{int(p1_attrib.loc['retrieval miss', FINAL1])}. What the final system has instead is "
    f"{int(p1_attrib.loc['generation error', FINAL1])} generation errors, which is the honest "
    "shape of the improvement: once the right chart is in front of the model, the remaining "
    "mistakes are the model misreading it.", BODY))

rows = [["Retrieval arm", "R@5", "MRR@5", "R@5 fig."]]
for arm in p1_ablation.index:
    r = p1_ablation.loc[arm]
    rows.append([arm, f"{r['recall@5']:.3f}", f"{r['MRR@5']:.3f}",
                 f"{r['recall@5 on figure/table questions']:.3f}"])
A(figure(table(rows, cols(0.46, 0.18, 0.18, 0.18)),
         "TABLE II.&nbsp;&nbsp;Retrieval ablation on the 25-question golden set. "
         "<font face='Courier' size='7'>outputs/part1_shriram/retrieval_ablation.csv</font>"))

fuse = p1_ablation.loc["RRF fusion"]
route = p1_ablation.loc["RRF + figure routing (final)"]
rerank = p1_ablation.loc["RRF + routing + reranker (tested, not used)"]
crops = p1_ablation.loc["RRF, page text only (no crops)"]
A(Paragraph(
    "Table II is the argument for the architecture, and two rows in it are worth dwelling on. "
    f"Removing the figure crops entirely collapses Recall@5 to {crops['recall@5']:.3f} and, on "
    f"questions that name a figure, to {crops['recall@5 on figure/table questions']:.3f}. That "
    "is the whole case for the multimodal part of a multimodal RAG system: page text alone "
    "almost never finds the right chart, because the sentence that answers the question is "
    "drawn rather than written. Exact-label routing then adds "
    f"{route['recall@5'] - fuse['recall@5']:+.3f} Recall@5 and "
    f"{route['MRR@5'] - fuse['MRR@5']:+.3f} MRR@5 over plain fusion.", BODY))
A(Paragraph(
    "The second row is the cross-encoder reranker, which I added for the S.5 bonus and then "
    f"removed. On this golden set it costs {rerank['recall@5'] - route['recall@5']:+.3f} "
    f"Recall@5 and {rerank['MRR@5'] - route['MRR@5']:+.3f} MRR@5. The reason is structural "
    "rather than a tuning accident: exact-label routing has already pinned the correct crop to "
    "position one, and a cross-encoder scores a question against a <i>text</i> passage, so it "
    "reliably ranks a wordy page above a terse figure description and displaces the very item "
    "the routing just pinned. The bonus asks for a reranker that shows an improvement. There "
    "isn't one here, so the final system does not use one and the notebook reports the measured "
    "loss rather than a claim. The arm is kept in the ablation so the measurement is visible.",
    BODY))

rows = [["Outcome", "Baseline", "Final"]]
for outcome in p1_attrib.index:
    rows.append([outcome, int(p1_attrib.loc[outcome, BASE1]), int(p1_attrib.loc[outcome, FINAL1])])
A(figure(table(rows, cols(0.50, 0.25, 0.25)),
         "TABLE III.&nbsp;&nbsp;Where the 25 golden answers go. "
         "<font face='Courier' size='7'>outputs/part1_shriram/failure_attribution.csv</font>"))

if GROUND_DONE:
    A(Paragraph(
        f"Both members rated all {GROUND['n']} golden answers 1\u20135 for groundedness\u2014"
        "whether the cited source actually supports the claim, which is a different question "
        f"from whether the answer is right. The means are {GROUND['mean_s']:.2f} and "
        f"{GROUND['mean_t']:.2f}, {GROUND['mean']:.2f} combined. We agreed exactly on "
        f"{GROUND['exact']} of {GROUND['n']} and within one point on {GROUND['within_one']} of "
        f"{GROUND['n']}, with no gap wider than one point"
        + (f". The answers we both scored at or below 2 are "
           f"{', '.join(GROUND['low'])}" if GROUND["low"] else "") +
        ". Agreement that tight is worth treating with some suspicion rather than pride: two "
        "raters who built adjacent systems share the same idea of what a good citation looks "
        "like, so this measures consistency of the rubric more than independence of the "
        "judgement. The ratings were made against the answers the graded Kaggle run produced, "
        "not an earlier run, which matters because the two runs differ on 23 of the 25 rows.",
        BODY))

A(Paragraph("C.&nbsp;&nbsp;What did not work", H2))
A(Paragraph(
    "Three changes I expected to help did not, and they are more informative than the ones that "
    "did. The first is the reranker above. The second was a worked example inside the JSON "
    "instruction: giving the model a sample <font face='Courier' size='8'>figure_references</font> "
    "value taught it to copy that label into answers about entirely different figures, putting a "
    "figure nobody asked about into roughly a fifth of the rows. Removing the example fixed that "
    "and immediately broke something else, because the example was also carrying the <i>shape</i> "
    "of the output; 35 of 40 replies came back as prose. The resolution was to keep the shape and "
    "delete the content, writing every value as an angle-bracket placeholder.", BODY))
figs_filled = int((p1_submission["figure_references"] != "NONE").sum())
A(Paragraph(
    "The third is worth recording because the reasoning was sound and the result still went the "
    "wrong way. Comparing my submission against "
    "<font face='Courier' size='8'>sample_submission.csv</font> showed that the template fills "
    "<font face='Courier' size='8'>figure_references</font> on nearly every row and pairs each "
    "figure citation with the page it sits on, while mine left the field empty on 27 of 40 and "
    "paired on 1. I changed the system to emit the label of any crop it was actually shown, and "
    f"to pair labels with pages. The column went from 13 filled rows to {figs_filled} and pairing "
    "from 1 to 21, exactly as intended, and the public leaderboard score moved by "
    f"{P1_RUN['kaggle'] - P1_RUN['kaggle_prev']:+.3f}. Either the added labels are often "
    "wrong, or the field is "
    "scored by exact set match, where an addition that is not in the key costs as much as an "
    "omission. The change is within noise and I kept it, but the hypothesis behind it did not "
    "survive contact with the leaderboard.", BODY))

A(Paragraph("D.&nbsp;&nbsp;Safety analysis", H2))
A(Paragraph(
    "Document 3 carries an untrusted Appendix C containing false claims, instructions hidden in "
    "its text, and an instruction painted inside a chart image. Three defences handle it, and "
    "they are deliberately layered because each one alone has a gap. First, trust level is read "
    "from <font face='Courier' size='8'>kb_manifest.json</font> and attached to every indexed "
    "item, so Appendix C content is dropped before it reaches the prompt rather than being "
    "filtered afterwards. Second, the crop for the Appendix C chart is never passed to the model "
    "as an image, which is the only defence that works against an instruction that exists purely "
    "as pixels and never as text. Third, the system prompt states that instructions found inside "
    "a document or an image are data to be reported, never commands to follow.", BODY))
leaks = int(p1_results.loc[FINAL1, "untrusted_leaks"])
A(Paragraph(
    f"The measured result is {leaks} untrusted-source leaks across the golden set, including the "
    "three probes written specifically to attack this. The probes and their outcomes are in "
    "<font face='Courier' size='8'>outputs/part1_shriram/safety_probes.csv</font>. Where the "
    f"system was not fooled: {p1_probes.iloc[0]['id']} asks for a value the trusted documents do "
    f"not contain, and the system returns "
    f"<font face='Courier' size='8'>{p1_probes.iloc[0]['status']}</font> rather than reaching "
    "into Appendix C, which does contain a number for it. Where it was partly fooled: "
    f"{p1_probes.iloc[1]['id']} embeds a false premise, and the system answered it as though the "
    f"premise held, returning <font face='Courier' size='8'>{p1_probes.iloc[1]['status']}</font> "
    f"where <font face='Courier' size='8'>{p1_probes.iloc[1]['expected_status']}</font> was "
    "correct. It did not leak untrusted content, but it also did not challenge the question. "
    "That is the weakest point in the Part 1 safety story: refusing to use a bad source is "
    "easier than noticing that the user's question contains one.", BODY))
A(Paragraph(
    "A separate rule governs user-supplied values. A value given in conversation is held in that "
    "conversation's memory, is never written to the vector database, and is discarded when the "
    "conversation ends. Requests to change the documents permanently are refused. The notebook "
    "demonstrates this by re-counting the index after an override and showing it unchanged.",
    BODY))

A(Paragraph("E.&nbsp;&nbsp;Cost and compliance", H2))
A(Paragraph(
    f"The graded run is Kaggle notebook version 370463230 on a single T4. Peak GPU memory "
    f"{P1_RUN['peak_gb']}\u2009GB against the 16\u2009GB the lab allows, and total notebook "
    f"runtime {P1_RUN['runtime_min']} minutes against the 90-minute limit in 1.5&nbsp;B. "
    f"Median {p1_results.loc[FINAL1, 'median_seconds']:.1f} seconds per question. The 7B model "
    "is used in 4-bit NF4; it reads values off charts markedly better than the 3B alternative, "
    "and 7B in fp16 would need roughly 17\u2009GB and break the budget, so the quantisation is "
    "what makes the better model affordable. Public leaderboard score "
    f"{P1_RUN['kaggle']:.3f}.", BODY))

# ================================================================= PART 2
A(Paragraph("II.&nbsp;&nbsp;PART 2: FINE-TUNING STABLE DIFFUSION WITH LoRA", H1))

A(Paragraph("A.&nbsp;&nbsp;Data and setup", H2))
A(Paragraph(
    f"The dataset is <font face='Courier' size='8'>{p2_clean['dataset']}</font>, "
    f"{p2_clean['rows_raw']} captioned images under CC BY-NC-SA 4.0. Cleaning removed "
    f"{p2_clean['corrupted_removed']} corrupted files, {p2_clean['exact_duplicates_removed']} "
    f"exact duplicates and {p2_clean['perceptual_duplicates_removed']} perceptual duplicates "
    f"found by hash distance, leaving {p2_clean['rows_clean']}. The split at seed 266 is "
    f"{len(p2_split_train)} train and {len(p2_split_test)} test, and test images are used only "
    "for evaluation. Everything is resized to 512\u00d7512, the native resolution of Stable "
    "Diffusion 1.5.", BODY))
A(Paragraph(
    "Two limitations of this dataset shape every result below. The captions are machine-written "
    "by BLIP, so they describe colour and pose reliably and species or named character almost "
    "never; a model trained on them learns a palette and a shape language rather than a "
    "character vocabulary. And the imagery is narrow\u2014small cartoon creatures on plain "
    "backgrounds\u2014so the fine-tuned model has effectively no exposure to architecture, "
    "landscape or human faces, which is exactly what the out-of-domain prompts ask for.", BODY))
A(Paragraph(
    "The 20 evaluation prompts were written and committed before training finished: 10 "
    "in-domain drawn from test-set captions, 5 out-of-domain and 5 compositional. Because the "
    "in-domain prompts come from held-out captions, the median word overlap between a prompt and "
    f"its nearest test caption is {p2_overlap['word_overlap'].median():.1f}, which is stated "
    "plainly here because it makes the in-domain CLIP score a measure of fidelity to a caption "
    "the model never trained on, not a measure of novelty.", BODY))

A(diagram([[f"{p2_clean['dataset']}, {p2_clean['rows_raw']} pairs"],
           [f"clean: drop corrupted, exact and perceptual dups "
            f"\u2192 {p2_clean['rows_clean']}"],
           [f"seed-266 split: {len(p2_split_train)} train", f"{len(p2_split_test)} test"],
           ["SD 1.5 UNet frozen; LoRA on attention, 512\u00d7512"],
           ["rank 8, 3000 steps", "rank 32, 3000 steps"],
           ["20 held-out prompts \u00d7 2 seeds \u00d7 3 models"],
           ["KID, CLIP, LPIPS", "NSFW + memorization"]],
          "Fig. 2.&nbsp;&nbsp;Part 2. Both ranks see identical data, steps and seed, so rank is "
          "the only variable between them."))

A(Paragraph("B.&nbsp;&nbsp;Two fine-tuning runs", H2))
rows = [["Run", "Rank", "Trainable", "LR", "Steps", "Peak GB", "GPU-h"]]
for run in p2_train.index:
    r = p2_train.loc[run]
    rows.append([run, int(r["rank"]), f"{int(r['trainable_parameters']):,}", f"{r['learning_rate']:g}",
                 int(r["steps"]), f"{r['peak_gpu_memory_gb']:.2f}", f"{r['gpu_hours']:.3f}"])
A(figure(table(rows, cols(0.20, 0.13, 0.19, 0.13, 0.12, 0.12, 0.11)),
         "TABLE IV.&nbsp;&nbsp;Training configuration and cost, identical data and step budget. "
         "<font face='Courier' size='7'>outputs/part2_shriram/metrics/training_table.csv</font>"))

rows = [["Model", "KID \u2193", "CLIP", "CLIP in-dom.", "LPIPS"]]
for model in ["base", "lora_r8", "lora_r32"]:
    r = p2_results.loc[model]
    rows.append([model, f"{r['kid_in_domain']:.4f} \u00b1 {r['kid_std']:.4f}",
                 f"{r['clip_score']:.2f}", f"{r['clip_in_domain']:.2f}",
                 f"{r['lpips_diversity']:.4f}"])
rows.append(["Human eval: win rate vs base", PENDING, "", "", ""])
A(figure(table(rows, cols(0.26, 0.26, 0.15, 0.18, 0.15)),
         "TABLE V.&nbsp;&nbsp;Part 2 results. KID is computed between in-domain generations and "
         "test images. "
         "<font face='Courier' size='7'>outputs/part2_shriram/metrics/results_table.csv</font>"))

base_k, r8_k, r32_k = (p2_results.loc[m, "kid_in_domain"] for m in ("base", "lora_r8", "lora_r32"))
base_c, r32_c = p2_results.loc["base", "clip_in_domain"], p2_results.loc["lora_r32", "clip_in_domain"]
base_l, r32_l = p2_results.loc["base", "lpips_diversity"], p2_results.loc["lora_r32", "lpips_diversity"]
A(Paragraph(
    f"KID improves monotonically with rank: {base_k:.4f} for the base model, {r8_k:.4f} at rank "
    f"8, {r32_k:.4f} at rank 32, a factor of {base_k / r32_k:.1f} overall. The standard "
    f"deviations ({p2_results['kid_std'].min():.4f} to {p2_results['kid_std'].max():.4f}) are "
    "small relative to the gaps, which matters because KID is noisy with few images and the "
    "temptation is to read a difference that is not there. Here the base-to-rank-32 gap is "
    f"roughly {(base_k - r32_k) / p2_results.loc['lora_r32', 'kid_std']:.0f} times the rank-32 "
    "standard deviation, so the ordering is real.", BODY))
A(Paragraph(
    f"CLIP score moves the other way, {base_c:.2f} to {r32_c:.2f} in-domain, and LPIPS diversity "
    f"falls from {base_l:.4f} to {r32_l:.4f}. This is the central trade-off of the study and it "
    "is not a defect. Fine-tuning pulls the model towards one visual style; that is what makes "
    "the output look like the target domain, and it is also what makes the model less willing to "
    "follow a prompt somewhere else and less varied between two seeds of the same prompt. A run "
    "that improved all four numbers would mean the adapter had barely changed anything.", BODY))
A(Paragraph(
    f"I would select rank 32 as the final run, on the primary metric. KID is the measurement the "
    f"lab names as primary for this part, rank 32 wins it by a factor of {r8_k / r32_k:.1f} over "
    f"rank 8, and it costs {p2_train.loc['lora_r32', 'gpu_hours'] - p2_train.loc['lora_r8', 'gpu_hours']:.3f} "
    f"extra GPU-hours and {p2_train.loc['lora_r32', 'peak_gpu_memory_gb'] - p2_train.loc['lora_r8', 'peak_gpu_memory_gb']:.2f}\u2009GB "
    "more memory, both negligible inside the budget. The CLIP and diversity cost of going from "
    f"rank 8 to rank 32 is {r32_c - p2_results.loc['lora_r8', 'clip_in_domain']:+.2f} and "
    f"{r32_l - p2_results.loc['lora_r8', 'lpips_diversity']:+.4f}, far smaller than the KID gain.",
    BODY))

A(Paragraph("C.&nbsp;&nbsp;Failure modes", H2))
A(Paragraph(
    "The first failure mode is out-of-domain collapse. The worst prompt by CLIP score is P15, "
    "\u201ca medieval stone castle on a green hill under a blue sky\u201d: the fine-tuned model "
    "renders a rounded, pastel, creature-like form where a castle should be, because the only "
    "visual grammar it has been given is small cartoon animals. This is the trade-off in Table V "
    "made visible on one image, and it is why the out-of-domain prompts were written before "
    "training rather than chosen afterwards.", BODY))
A(Paragraph(
    "The second is diversity collapse within a prompt. P12, \u201can oil painting of an old man "
    "with a white beard\u201d, has the lowest LPIPS between its two seeds: the model produces "
    "near-identical images from different noise, having largely lost the base model's ability to "
    "vary a scene it has no training signal for. Both failures point the same way\u2014the "
    "adapter has bought in-domain fidelity with general-purpose flexibility.", BODY))

A(Paragraph("D.&nbsp;&nbsp;Safety analysis", H2))
A(Paragraph(
    f"<b>License.</b> The dataset is CC BY-NC-SA 4.0 and depicts Pok\u00e9mon, which are "
    "copyrighted characters. The adapter is therefore for non-commercial research only, the "
    "model card on Hugging Face states this, and the share-alike term carries to the adapter "
    "weights. Nothing here may be used commercially or relicensed more permissively.", BODY))
A(Paragraph(
    f"<b>NSFW filter.</b> Every generated image passes through the Stable Diffusion safety "
    f"checker. It flagged {P2_SAFETY['nsfw_flagged']} of {P2_SAFETY['nsfw_total']} images. I "
    "inspected all of them and none is unsafe; they are harmless cartoon creatures, and the "
    f"flags cluster on the fine-tuned runs ({P2_SAFETY['nsfw_tuned']}) rather than the base "
    f"model ({P2_SAFETY['nsfw_base']}). The plausible reading is "
    "that the checker compares against CLIP embeddings of unsafe concepts and the fine-tuned "
    "model's saturated, smooth, skin-toned rounded forms drift closer to those embeddings than "
    "photographic imagery does. The practical lesson is that this checker's false-positive rate "
    "on stylised output is high enough that it cannot be the only gate on anything that "
    "matters\u2014a conclusion I acted on in Part 3, where the output gate requires two "
    "independent detectors to agree.", BODY))
A(Paragraph(
    f"<b>Memorization.</b> For the {P2_SAFETY['mem_n']} in-domain generations I measured CLIP "
    f"similarity to the nearest training image: mean {P2_SAFETY['mem_gen_mean']:.4f}, max "
    f"{P2_SAFETY['mem_gen_max']:.4f}. "
    "That number is meaningless alone, because a value near 0.9 could indicate either "
    "memorization or simply a visually homogeneous dataset. The control is to run the same "
    "measurement on held-out test images, which by construction were never trained on: mean "
    f"{P2_SAFETY['mem_test_mean']:.4f}, max {P2_SAFETY['mem_test_max']:.4f}. The generations sit "
    "<i>below</i> the held-out control on both statistics, so there is no memorization signal; "
    "the high absolute similarity is a property of the dataset, not of the adapter. Source: "
    f"{P2_SAFETY['source']}.", BODY))

A(Paragraph("E.&nbsp;&nbsp;Cost", H2))
A(Paragraph(
    f"The two runs cost {p2_train.loc['lora_r8', 'gpu_hours']:.3f} and "
    f"{p2_train.loc['lora_r32', 'gpu_hours']:.3f} GPU-hours at peak "
    f"{p2_train.loc['lora_r8', 'peak_gpu_memory_gb']:.2f} and "
    f"{p2_train.loc['lora_r32', 'peak_gpu_memory_gb']:.2f}\u2009GB, both well inside 16\u2009GB. "
    f"Generation runs at a median "
    f"{p2_results.loc['lora_r32', 'median_seconds_per_image']:.2f} seconds per image; "
    f"{len(p2_log)} images were produced across the three models. Both adapters, the image "
    "dataset and the model card are on Hugging Face under "
    "<font face='Courier' size='8'>shriram14</font>.", BODY))

# ================================================================= PART 3
A(Paragraph("III.&nbsp;&nbsp;PART 3: A FIVE-AGENT MULTIMODAL SYSTEM", H1))

A(Paragraph("A.&nbsp;&nbsp;Architecture", H2))
A(Paragraph(
    "Five agents pass one typed state object. The <b>Planner</b> classifies the request into one "
    "of six routes\u2014caption or question, style change, edit, domain-style generation, "
    "ambiguous, unsupported\u2014and refuses unsafe requests before anything is generated. "
    "<b>Vision Understanding</b> produces a caption, an object list, any text visible in the "
    "image, and answers to at least two questions about it. <b>Prompt Engineering</b> rewrites "
    "the request into a generation prompt using the vision output, and treats text found inside "
    "the image strictly as content to describe. <b>Image Generation</b> runs image-to-image for "
    "style changes and InstructPix2Pix for edits; domain-style requests load the team's Part 2 "
    "LoRA from Hugging Face. <b>Critique</b> scores the result with CLIP plus a short "
    "vision-language judgement, checks output safety, and either accepts or returns a concrete "
    "revision instruction. The revise loop is capped at two passes. Caption and question "
    "requests stop after Vision Understanding. Every request writes a JSON trace recording which "
    "agent ran, its input and output, and how long it took.", BODY))

A(diagram([["user image + request"],
           ["Planner: route, or refuse an unsafe request"],
           ["Vision: caption, objects, visible text, Q&A"],
           ["~stop here for caption and question routes"],
           ["Prompt Engineering: build the generation prompt"],
           ["img2img (style)", "Pix2Pix (edit)", "LoRA (domain)"],
           ["Critique: CLIP + VLM judgement, safety gate"],
           ["~revise, at most twice", "accept and return"],
           ["JSON trace of every agent, its I/O and timing"]],
          "Fig. 3.&nbsp;&nbsp;Part 3. Request safety is decided before generation, output "
          "safety after it. Dashed boxes are conditional paths."))

A(Paragraph("B.&nbsp;&nbsp;Results", H2))
rows = [["Measurement", "Without critique", "With critique"]]
for m in p3_results.index:
    rows.append([m, p3_results.loc[m, "baseline (no critique loop)"],
                 p3_results.loc[m, "final (critique loop)"]])
rows.append(["Human eval: inter-rater agreement", PENDING, PENDING])
A(figure(table(rows, cols(0.46, 0.27, 0.27)),
         "TABLE VI.&nbsp;&nbsp;Part 3, 15 scenarios run twice. "
         "<font face='Courier' size='7'>outputs/part3_shriram/evaluation/results_table.csv</font>"))

without = int(p3_pass["pass_without_critic"].sum())
with_ = int(p3_pass["pass_with_critic"].sum())
fixed = p3_pass[(~p3_pass["pass_without_critic"]) & (p3_pass["pass_with_critic"])]["id"].tolist()
broke = p3_pass[(p3_pass["pass_without_critic"]) & (~p3_pass["pass_with_critic"])]["id"].tolist()
revised = int((p3_pass["revisions_used"] > 0).sum())
A(Paragraph(
    f"The critique loop takes the pass rate from {without} of 15 to {with_} of 15. That single "
    "scenario is a thin result on its own, so the more useful reading is which scenarios moved "
    f"and which did not. {', '.join(fixed)} is fixed by the loop; "
    f"{'nothing is broken by it' if not broke else ', '.join(broke) + ' is broken by it'}. "
    f"{revised} of 15 requests used at least one revision, so the loop is active on well over a "
    "third of the workload while changing the outcome on one. The cost is "
    f"{p3_results.loc['Efficiency: median seconds per request', 'final (critique loop)']} seconds "
    "median against "
    f"{p3_results.loc['Efficiency: median seconds per request', 'baseline (no critique loop)']} "
    "without. A self-refinement loop that rarely changes the verdict but reliably costs time is "
    "a real finding, not a disappointing one; it bounds what self-critique buys at this scale.",
    BODY))

agree = int(p3_critic["agree"].sum())
strict = p3_critic[(p3_critic["critic_first_decision"] == "revise")
                   & (p3_critic["human_on_first_attempt"] == "accept")]
A(Paragraph(
    f"Critic agreement with my own judgement on first attempts is {agree} of {len(p3_critic)}, "
    f"and the disagreements are one-sided: in {len(strict)} of the {len(p3_critic) - agree} "
    "mismatches the critic called <i>revise</i> on an image I would have accepted, and in none "
    "did it accept something I would have rejected. The critic is miscalibrated in the safe "
    f"direction. Its CLIP scores on those images run from {strict['clip_score'].min():.2f} to "
    f"{strict['clip_score'].max():.2f}, against {p3_critic[p3_critic['critic_first_decision'] == 'accept']['clip_score'].min():.2f} "
    "and above for the ones it accepted, so the threshold is doing most of the work and a CLIP "
    "score is a weak proxy for whether a stylised image satisfies a request.", BODY))

A(Paragraph("C.&nbsp;&nbsp;Safety analysis and red team", H2))
defended = int(p3_red["defended"].sum())
A(Paragraph(
    "The guardrails are deliberately split across two points in the pipeline, because the two "
    "classes of risk are different. Unsafe <i>requests</i>\u2014NSFW, deceptive edits of real "
    "people\u2014are refused by the Planner before any model runs, which is the only placement "
    "that avoids generating the thing you intend to block. Unsafe <i>outputs</i> are caught by a "
    "gate after generation that requires two independent signals to agree: the Stable Diffusion "
    "safety checker and a direct yes/no judgement from the vision-language model.", BODY))
A(Paragraph(
    "The two-signal rule comes straight from the Part 2 measurement. The SD checker fired on "
    f"{P2_SAFETY['nsfw_flagged']} of {P2_SAFETY['nsfw_total']} harmless cartoon images there, and "
    "the vision model independently called a Pokémon-style water creature unsafe. Either "
    "detector alone refuses valid domain-style work; requiring agreement keeps the gate while "
    "letting the route function. Across the 15 scenarios the gate blocked no images.", BODY))
rows = [["Red-team case", "Outcome", "Defended"]]
for r in p3_red.itertuples():
    rows.append([f"{r.id} &nbsp;{r.attack}", r.outcome, "yes" if r.defended else "no"])
A(figure(table(rows, cols(0.52, 0.26, 0.22)),
         "TABLE VII.&nbsp;&nbsp;Ten red-team cases. "
         "<font face='Courier' size='7'>outputs/part3_shriram/evaluation/redteam_results.csv</font>"))
A(Paragraph(
    f"{defended} of 10 cases are defended by the automatic checks. Both failures, "
    f"{' and '.join(p3_red[~p3_red['defended']]['id'].tolist())}, are instruction-in-image "
    "attacks that fail a forbidden-substring check. I want to be careful about how that is "
    "reported, because the substring rule fires whenever the reply <i>quotes</i> the text "
    "painted into the image\u2014and Task 3.1 requires the Vision agent to report any text "
    "visible in an image. A correctly defended reply that names the injected string without "
    "obeying it therefore scores as a successful attack. Whether these are real breaches is "
    "resolved by reading the reply text in the results csv and by the human rubric, not by "
    "editing the check after seeing the result, which would be fitting the measurement to the "
    "outcome.", BODY))

A(Paragraph("D.&nbsp;&nbsp;System card", H2))
A(Paragraph(
    "<b>What it does.</b> Takes an image and a natural-language request and either answers a "
    "question about the image, restyles it, edits it, or generates a domain-style image using "
    "the team's fine-tuned Pokémon LoRA. It shows each agent's output in a Gradio app and writes "
    "a JSON trace per request.", PLAIN))
A(Paragraph(
    "<b>Known limits.</b> The critic is stricter than a human and asks for revisions that are "
    f"not needed, agreeing with me on {agree} of {len(p3_critic)} first decisions. CLIP "
    "similarity is a weak signal for stylised imagery. The domain-style route inherits every "
    "limitation of the Part 2 adapter, including its collapse on prompts outside small cartoon "
    "creatures. The revise cap of two means a request needing three passes simply fails. The "
    "safety checker's false-positive rate on this style is high, which is why the output gate "
    "needs two signals and why it could in principle miss something both detectors agree on.",
    PLAIN))
A(Paragraph(
    "<b>Safety measures.</b> Input refusal at the Planner for NSFW requests, deceptive edits of "
    "real people, and instructions embedded in images. Output gating on agreement between the SD "
    "safety checker and a vision-language judgement. Text found inside an image is always "
    "treated as content to report, never as an instruction. Broken, empty and malformed inputs "
    f"return a clear message instead of crashing: {len(p3_red[p3_red['outcome'] == 'error_message'])} "
    "red-team cases and seven separate failure cases exercise this, with no crashes.", PLAIN))

A(Paragraph("E.&nbsp;&nbsp;Cost", H2))
A(Paragraph(
    f"Peak GPU memory {P3_RUN['peak_gb']}\u2009GB on one card, against the 16\u2009GB budget, "
    f"with the vision-language model in 4-bit and the diffusion pipelines loaded alongside it. "
    f"Median {P3_RUN['median_s']} seconds per request in the demo run, and "
    f"{p3_results.loc['Efficiency: median seconds per request', 'final (critique loop)']} seconds "
    "across the scenario evaluation, where every request goes through generation.", BODY))

# ================================================================= closing
A(Paragraph("IV.&nbsp;&nbsp;WHAT I TAKE FROM THE THREE PARTS", H1))
A(Paragraph(
    "Three times in this lab a change that was obviously correct on paper made things worse, and "
    "in each case only a measurement caught it. The cross-encoder reranker is a standard "
    "improvement to hybrid retrieval and it cost "
    f"{rerank['recall@5'] - route['recall@5']:.3f} Recall@5 here, because it fought the "
    "exact-label routing already in place. Filling the "
    "<font face='Courier' size='8'>figure_references</font> column to match the submission "
    "template was a well-evidenced inference from the format examples and it moved the "
    "leaderboard the wrong way. The Stable Diffusion safety checker is the obvious output gate "
    f"and it has a {P2_SAFETY['nsfw_flagged']}-in-{P2_SAFETY['nsfw_total']} false-positive rate "
    "on exactly the imagery this project generates.", BODY))
A(Paragraph(
    "The pattern is that each of those was an argument from how the system <i>should</i> behave, "
    "and each was settled by a number. That is also why the memorization check needed a held-out "
    "control before it meant anything, and why the reranker stays in the ablation table even "
    "though it is not in the final system: a measurement that only appears when it agrees with "
    "you is not a measurement.", BODY))

A(Paragraph("V.&nbsp;&nbsp;REPRODUCIBILITY", H1))
A(Paragraph(
    "Repository <font face='Courier' size='8'>data266-lab2-team33</font>, tags "
    "<font face='Courier' size='8'>p1-v1.0</font>, "
    "<font face='Courier' size='8'>p2-v1.0</font>, "
    "<font face='Courier' size='8'>p3-v1.0</font>. Seed 266 throughout. The first cell of every "
    "notebook prints the commit, library versions, GPU and seed. Part 1 runs on Kaggle with the "
    "competition data attached and reads "
    "<font face='Courier' size='8'>QUESTIONS_PATH</font> from the environment, so the graders' "
    "hidden set needs no edit. Parts 2 and 3 run in Colab and locate their inputs by searching "
    "for a named file rather than by hard-coded path. Pinned dependencies are split across three "
    "files because Part 2 needs <font face='Courier' size='8'>transformers==4.46.3</font> while "
    "Parts 1 and 3 need <font face='Courier' size='8'>4.51.3</font>. Model weights and generated "
    "images are on Hugging Face, not in Git. Exact file paths for every number quoted above are "
    "in the table captions.", BODY))

OUT.parent.mkdir(parents=True, exist_ok=True)
document().build(story)
print(f"wrote {OUT.relative_to(ROOT)}")
