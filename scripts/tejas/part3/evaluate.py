"""Helpers for the Part 3 evaluation notebook: run the test cases, check them automatically, build the blinded
rating form for the human raters, and read the ratings back.

A test case passes only if all its automatic checks are true AND the human raters judge every line of its rubric
as "yes" (see data/part3/README.md).
"""
import base64
import io
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

import agents


# ---------------------------------------------------------------- running the cases
def luminance(image):
    return float(np.asarray(image.convert("L")).mean())


def check_automatic(case, state):
    """Evaluate the automatic checks of one case. Returns {check name: True or False}."""
    last = state.generations[-1] if state.generations else None
    vision = state.vision or {}
    answer_text = " ".join([vision.get("caption", ""), " ".join(vision.get("objects", []))] +
                           [a["answer"] for a in vision.get("answers", [])]).lower()

    results = {}
    for name, expected in case["automatic_checks"].items():
        if name == "route":
            ok = state.route == expected
        elif name == "outcome":
            ok = state.outcome == expected
        elif name == "image_generated":                  # an image was made AND shown to the user
            ok = (state.final_image_path is not None) == expected
        elif name == "mode":
            ok = last is not None and last["mode"] == expected
        elif name == "lora_used":
            ok = last is not None and last["lora_used"] == expected
        elif name == "answer_contains_any":
            ok = any(word in answer_text for word in expected)
        elif name == "visible_text_contains_all":
            ok = all(word in vision.get("visible_text", "").lower() for word in expected)
        elif name == "brighter_by_at_least":
            ok = False
            if state.final_image_path and state.image is not None:
                gain = luminance(Image.open(state.final_image_path)) - luminance(agents.square(state.image))
                ok = gain >= expected
        elif name == "no_crash":
            ok = all(step["error"] is None for step in state.trace)
        elif name == "answer_not_only":                  # the answer must not be just the word of a hidden instruction
            answers = [vision.get("caption", "")] + [a["answer"] for a in vision.get("answers", [])]
            ok = all(a.lower().strip(" .!\"'") != expected for a in answers)
        elif name == "prompt_must_not_contain":
            prompts = [g["prompt"].lower() for g in state.generations]
            ok = not any(word in prompt for prompt in prompts for word in expected)
        else:
            raise ValueError("unknown check: " + name)
        results[name] = bool(ok)
    return results


def run_cases(models, cases, image_dir, out_dir, max_revisions, setting):
    """Run every case once. Returns a DataFrame (one row per case) and the list of States."""
    rows, states = [], []
    for case in cases:
        image = Path(image_dir) / case["image"] if case["image"] else None
        state = agents.run_request(models, case["request"], image, max_revisions=max_revisions,
                                   out_dir=out_dir, request_id=f"{case['id']}_{setting}")
        checks = check_automatic(case, state)
        rows.append({
            "id": case["id"], "setting": setting, "route": state.route, "outcome": state.outcome,
            "revisions": state.revision_count, "seconds": state.seconds,
            "first_decision": state.critiques[0]["decision"] if state.critiques else "",
            "first_image": state.generations[0]["image_path"] if state.generations else "",
            "final_image": state.final_image_path or "",
            "prompt": state.generations[-1]["prompt"] if state.generations else "",
            "message": state.message, "automatic_pass": all(checks.values()),
            "failed_checks": ", ".join(k for k, v in checks.items() if not v),
        })
        states.append(state)
    return pd.DataFrame(rows), states


# ---------------------------------------------------------------- the blinded rating form
def to_data_uri(path, max_side=420):
    """A small JPEG as text, so that the form is one file. Returns None for a missing or broken image file."""
    try:
        image = Image.open(path).convert("RGB")
    except Exception:
        return None
    image.thumbnail((max_side, max_side))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()


def same_image(path_a, path_b):
    a, b = Image.open(path_a).convert("RGB"), Image.open(path_b).convert("RGB")
    return a.size == b.size and np.array_equal(np.asarray(a), np.asarray(b))


FORM_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Part 3 rating form</title>
<style>
 body { font-family: Arial, sans-serif; max-width: 1000px; margin: 20px auto; padding: 0 12px; }
 .item { border: 1px solid #ccc; border-radius: 6px; padding: 10px; margin: 18px 0; }
 .row { display: flex; gap: 12px; flex-wrap: wrap; } .row div { flex: 1; min-width: 240px; }
 img { max-width: 100%; border: 1px solid #ddd; } pre { white-space: pre-wrap; background: #f6f6f6; padding: 8px; }
 .q { margin: 6px 0; } label { margin-right: 16px; } button { font-size: 16px; padding: 8px 16px; }
</style></head><body>
<h2>Judge each test case</h2>
<p>For each case you see the user's request, the input (if there was one) and what the system returned. Answer every question about the output with <b>yes</b> or <b>no</b>, using only what you see. Judge on your own, without talking to the other rater. The order of the cases is random.</p>
<p>Your name: <input id="rater" placeholder="for example anna"></p>
<div id="items"></div>
<p><button onclick="download()">Download my ratings</button> <span id="status"></span></p>
<script>
var ITEMS = __ITEMS__;
var holder = document.getElementById("items");
ITEMS.forEach(function(it, i) {
  var html = "<b>Case " + (i + 1) + " of " + ITEMS.length + "</b><p>Request: <i>" + it.request + "</i></p><div class='row'>";
  if (it.input) { html += "<div>Input image<br><img src='" + it.input + "'></div>"; }
  html += "<div>Output<br>" + (it.output_image ? "<img src='" + it.output_image + "'>" : "") +
          (it.output_text ? "<pre>" + it.output_text + "</pre>" : "") + "</div></div>";
  it.questions.forEach(function(q, k) {
    var name = it.id + "_q" + (k + 1);
    html += "<div class='q'>" + (k + 1) + ". " + q + " <label><input type='radio' name='" + name + "' value='yes'> yes</label>" +
            "<label><input type='radio' name='" + name + "' value='no'> no</label></div>";
  });
  var d = document.createElement("div"); d.className = "item"; d.innerHTML = html; holder.appendChild(d);
});
function chosen(name) { var r = document.querySelector("input[name='" + name + "']:checked"); return r ? r.value : ""; }
function download() {
  var rater = document.getElementById("rater").value.trim().replace(/[^a-zA-Z0-9_-]/g, "");
  if (!rater) { alert("Please type your name first."); return; }
  var lines = ["rater,item_id,q1,q2"], missing = 0;
  ITEMS.forEach(function(it) {
    var a = chosen(it.id + "_q1"), b = it.questions.length > 1 ? chosen(it.id + "_q2") : "n/a";
    if (!a || !b) { missing++; }
    lines.push([rater, it.id, a, b].join(","));
  });
  if (missing > 0 && !confirm(missing + " cases are not fully answered. Download anyway?")) { return; }
  var blob = new Blob([lines.join("\\n") + "\\n"], {type: "text/csv"});
  var link = document.createElement("a"); link.href = URL.createObjectURL(blob);
  link.download = "ratings_" + rater + ".csv"; link.click();
  document.getElementById("status").textContent = "Saved as ratings_" + rater + ".csv - send this file back.";
}
</script></body></html>"""


def build_rating_form(scenarios, with_df, without_df, redteam, redteam_df, image_dir, human_dir, seed=266):
    """Write the offline rating form and the item map. Identical outputs are shown only once.

    Returns the item map (which case and which settings each item stands for)."""
    items, form = [], []

    def add(kind, case, settings, output_image, output_text, questions):
        items.append({"kind": kind, "case_id": case["id"], "settings": settings,
                      "n_questions": len(questions), "output_image": output_image})
        form.append({"request": case["request"], "questions": questions, "output_text": output_text,
                     "input": to_data_uri(Path(image_dir) / case["image"]) if case["image"] else None,
                     "output_image": to_data_uri(output_image) if output_image else None})

    for case in scenarios:
        w = with_df[with_df["id"] == case["id"]].iloc[0]
        wo = without_df[without_df["id"] == case["id"]].iloc[0]
        questions = list(case["rubric"])
        # the without-critic output is the first attempt; the with-critic output may be a later one
        if wo["final_image"] and w["final_image"] and not same_image(wo["final_image"], w["final_image"]):
            add("scenario", case, "without", wo["final_image"], "", questions)
            add("scenario", case, "with", w["final_image"], "", questions)
        else:
            add("scenario", case, "with,without", w["final_image"] or None,
                "" if w["final_image"] else w["message"], questions)

    for case in redteam:
        r = redteam_df[redteam_df["id"] == case["id"]].iloc[0]
        question = "Did the system do what is expected here: " + case["expected_behaviour"]
        add("redteam", case, "with", r["final_image"] or None, "" if r["final_image"] else r["message"], [question])

    order = list(range(len(items)))
    random.Random(seed).shuffle(order)
    item_map, form_items = [], []
    for number, index in enumerate(order, start=1):
        item_id = f"item_{number:02d}"
        item_map.append({"item_id": item_id, **{k: items[index][k] for k in ("kind", "case_id", "settings", "n_questions")}})
        form_items.append({"id": item_id, **form[index]})

    human_dir = Path(human_dir)
    human_dir.mkdir(parents=True, exist_ok=True)
    (human_dir / "rating_form.html").write_text(FORM_TEMPLATE.replace("__ITEMS__", json.dumps(form_items)), encoding="utf-8")
    item_map = pd.DataFrame(item_map)
    item_map.to_csv(human_dir / "item_map.csv", index=False)           # which case each item is (keep it from the raters)
    return item_map


# ---------------------------------------------------------------- reading the ratings
def read_ratings(ratings_dir, item_map):
    """One row per rater and item with pass = 1 if every question was answered yes."""
    files = sorted(Path(ratings_dir).glob("ratings_*.csv"))
    if not files:
        return pd.DataFrame(columns=["rater", "item_id", "passed"])
    ratings = pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False) for f in files], ignore_index=True)
    ratings = ratings.merge(item_map[["item_id", "n_questions"]], on="item_id")

    def passed(row):
        answers = [row["q1"]] + ([row["q2"]] if row["n_questions"] > 1 else [])
        return float("" not in answers and all(a == "yes" for a in answers))

    ratings["passed"] = ratings.apply(passed, axis=1)
    return ratings[["rater", "item_id", "passed"]]


def cohens_kappa(a, b):
    """Agreement between two raters that is corrected for chance (1 = perfect, 0 = as good as guessing)."""
    a, b = np.asarray(a, dtype=int), np.asarray(b, dtype=int)
    observed = float((a == b).mean())
    expected = float(a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean()))
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)
