"""Put the improved cells into the Part 1 notebook (cells 30, 32, 34, 36, 45, 46, 48, their descriptions, and a new validation cell)."""
import nbformat

SP = r"C:\Users\tejas\AppData\Local\Temp\claude\deab2937ad871fff\63c6304a-a82d-4ec7-8d90-b0b10b1173c2\scratchpad" + "\\"
PATH = r"C:\Users\tejas\Desktop\GPU_LAB_2\notebooks\p1_rag_final.ipynb"

nb = nbformat.read(PATH, as_version=4)
cells = nb.cells


def text(name):
    return open(SP + name, encoding="utf-8").read()


def check(index, kind, first_words):
    assert cells[index].cell_type == kind and "".join(cells[index].source).startswith(first_words), (index, kind, "".join(cells[index].source)[:60])


# ---- code cells that change
check(30, "code", "# Hybrid retrieval")
check(32, "code", "import ast")
check(34, "code", "# Resolve follow-up")
check(36, "code", "conversation_memory = {}")
check(45, "code", "import time")
check(46, "code", "baseline_eval = ")
check(48, "code", "human_path = ")
cells[30].source = text("p1_new30.py")
cells[32].source = text("p1_new32.py")
cells[34].source = text("p1_new34.py")
cells[36].source = text("p1_new36.py")
cells[45].source = text("p1_new45.py")

# ---- the evaluation summary also reports the estimated competition score
cell46 = "".join(cells[46].source)
old = '''    median_seconds=("seconds", "median")
).reset_index()'''
new = '''    median_seconds=("seconds", "median"),
    estimated_score=("estimated_score", "mean")    # rough local version of the competition score (see 8.2)
).reset_index()'''
assert cell46.count(old) == 1
cell46 = cell46.replace(old, new)
old = '''summary["median_seconds"] = summary["median_seconds"].round(2)'''
assert cell46.count(old) == 1
cell46 = cell46.replace(old, old + '''\nsummary["estimated_score"] = summary["estimated_score"].round(3)''')
cells[46].source = cell46

# ---- the human sheet is only reused for the answers that were rated
cells[48].source = '''human_path = OUT_DIR / "human_groundedness.csv"

# The ratings belong to the answers that the raters saw. If the answers of the system have changed since then, the old
# sheet is kept under another name and a fresh sheet is written, so old ratings are never used for new answers.
current_answers = final_eval.set_index("id")["actual_answer"].astype(str).str.strip()
already_rated = False
if human_path.exists():
    old_sheet = pd.read_csv(human_path, dtype=str, keep_default_na=False)
    has_ratings = bool((old_sheet["rater_1"] != "").any() or (old_sheet["rater_2"] != "").any())
    rated_answers = old_sheet.set_index("id")["actual_answer"].astype(str).str.strip().reindex(current_answers.index)
    if has_ratings and bool((rated_answers == current_answers).all()):
        already_rated = True
    elif has_ratings:
        archive_path = OUT_DIR / "human_groundedness_previous_answers.csv"
        old_sheet.to_csv(archive_path, index=False)
        print("The answers have changed since the ratings were made. The old ratings are saved in", archive_path.name)

if not already_rated:
    human_eval = final_eval[["id", "question", "actual_answer", "citations"]].copy()
    human_eval["rater_1"] = ""
    human_eval["rater_2"] = ""
    human_eval.to_csv(human_path, index=False)
    print("Human-rating template saved:", human_path.resolve())
else:
    human_eval = old_sheet

ratings = human_eval[(human_eval["rater_1"] != "") & (human_eval["rater_2"] != "")].copy()
human_average, human_agreement = None, None

if len(ratings) == 25:
    r1 = ratings["rater_1"].astype(float)
    r2 = ratings["rater_2"].astype(float)
    human_average = round(pd.concat([r1, r2]).mean(), 2)
    human_agreement = round((abs(r1 - r2) <= 1).mean(), 3)
    print("Average groundedness:", human_average)
    print("Agreement within one point:", human_agreement)
else:
    print(f"Human ratings completed: {len(ratings)}/25")

# One results table with all four kinds of measurement
results_table = summary.copy()
results_table["human_groundedness"] = ["n/a (baseline not rated)" if s == "Dense baseline" else human_average for s in results_table["system"]]
results_table["rater_agreement"] = ["n/a" if s == "Dense baseline" else human_agreement for s in results_table["system"]]
results_table.to_csv(OUT_DIR / "results_table.csv", index=False)
print()
print(results_table.to_string(index=False))'''

# ---- descriptions
cells[31].source = """## 5. Grounded Answer Generation

Retrieved evidence is passed to the language model to generate a concise answer with the required status, citations, and figure references.

The answer is then checked with general rules (no rule depends on a question):

- A `not_found` answer must say that the documents do not contain the information. A real answer with a stray `not_found` is kept if its numbers are in the evidence, and a wrong `not_found` is rescued if the model can copy, word for word, a sentence of the evidence that answers the question (the question's country or name must appear in that source, and a separate yes/no question confirms it).
- A *why* question that takes something for granted that the evidence contradicts gets the status `false_premise`. The model writes the assumption and what the evidence says, and a separate short question compares the two statements.
- Two trusted documents that report different numbers for the same quantity give the status `conflict` (forecasts, approximate values and stated revisions are not conflicts), and the higher-trust value is preferred.
- An outturn or a revised value is given together with the value it replaces.
- A table or figure is cited together with its page, as in the sample submission."""

cells[33].source = """## 6. Conversation Handling

Conversation memory is kept separately for each conversation so follow-up questions and user-provided assumptions do not modify the read-only knowledge base.

A question that asks what the documents report never uses the user's temporary facts. A temporary fact that applies to the question (same country, variable and year) is used and always shown next to what the documents report."""

md44 = "".join(cells[44].source)
cells[44].source = md44 + """
- **Estimated competition score:** a rough local version of the Kaggle score (0.4 answer correctness + 0.2 status + 0.2 figure references + 0.2 citations). The expected citations are the expected sources plus the page of every expected table or figure. The real answer key is hidden, so this is only an estimate."""

cells[47].source = """### 8.3 Human Groundedness Evaluation

Both team members rate each of the 25 final answers from 1 to 5 for groundedness (is every claim supported by the cited source?). The template below is saved to `outputs/part1/human_groundedness.csv`. Fill the `rater_1` and `rater_2` columns and run the cell again to get the average rating and the share of answers where the two raters are within one point. A sheet that already contains ratings is kept only if its answers are identical to the current answers of the system. Otherwise the old sheet is saved as `human_groundedness_previous_answers.csv` and a new sheet is written, so ratings are never used for answers that the raters did not see."""

# ---- a new section after the golden evaluation: the validation questions
validation_md = nbformat.v4.new_markdown_cell("""### 8.2b Fresh validation questions (local check)

`data/part1/validation_set.csv` holds 34 further questions that were written and committed to Git **before** the answer logic above was improved. They cover conflicts, false premises, revisions, follow-up questions and values given by the user. The improvements were developed with the golden set and these questions, so neither is a completely untouched test (the hidden Kaggle questions are). The cell is skipped when the file is not there, for example on Kaggle.""")

validation_code = nbformat.v4.new_code_cell('''validation_path = DATA_DIR / "validation_set.csv"

if validation_path.exists():
    validation_set = pd.read_csv(validation_path, dtype=str, keep_default_na=False)
    validation_set["turn"] = validation_set["turn"].astype(int)
    validation_set["expected_sources"] = validation_set["expected_sources"].apply(lambda s: [x for x in s.split("|") if x])

    validation_results = pd.concat([
        evaluate_system(dense_baseline_retrieve, "Dense baseline", items=validation_set),
        evaluate_system(hybrid_retrieve, "Final hybrid", items=validation_set),
    ], ignore_index=True)
    validation_results["status_correct"] = validation_results["expected_status"] == validation_results["actual_status"]

    validation_summary = validation_results.groupby("system").agg(
        answer_correct=("correct", "sum"),
        status_correct=("status_correct", "sum"),
        citation_accuracy=("citation_accuracy", "mean"),
        median_seconds=("seconds", "median"),
        estimated_score=("estimated_score", "mean")
    ).reset_index().round(3)
    validation_summary["answer_correct"] = validation_summary["answer_correct"].astype(str) + f"/{len(validation_set)}"
    validation_summary["status_correct"] = validation_summary["status_correct"].astype(str) + f"/{len(validation_set)}"

    validation_results.to_csv(OUT_DIR / "validation_results.csv", index=False)
    print(validation_summary.to_string(index=False))
    print()
    print("Answers correct by question type")
    print(validation_results.pivot_table(index="category", columns="system", values="correct", aggfunc="sum").to_string())
else:
    print("validation_set.csv not found, this check is skipped.")''')

cells.insert(47, validation_md)
cells.insert(48, validation_code)

nbformat.write(nb, PATH)
print("notebook now has", len(cells), "cells")
