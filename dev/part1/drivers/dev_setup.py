# Run inside the kernel: load the validation set, define the new harness, evaluate the CURRENT (old) system
import pandas as pd, re
exec(open(SP + "p1_new45.py", encoding="utf-8").read())

validation_set = pd.read_csv(r"..\data\part1\validation_set.csv", dtype=str, keep_default_na=False)
validation_set["turn"] = validation_set["turn"].astype(int)
validation_set["expected_sources"] = validation_set["expected_sources"].apply(lambda s: [x for x in s.split("|") if x])


def summarize(df, label):
    status_ok = (df["expected_status"] == df["actual_status"])
    print(f"== {label}: n={len(df)} | answer correct {int(df['correct'].sum())} | status ok {int(status_ok.sum())} | "
          f"estimated competition score {df['estimated_score'].mean():.3f} | citation acc {df['citation_accuracy'].astype(float).mean():.3f} | median s {df['seconds'].median():.1f}")
    g = df.assign(status_ok=status_ok).groupby("category").agg(n=("id", "count"), correct=("correct", "sum"), status_ok=("status_ok", "sum"), score=("estimated_score", "mean"))
    print(g.round(2).to_string())
