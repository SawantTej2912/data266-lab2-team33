SP = r"C:\Users\tejas\AppData\Local\Temp\claude\deab2937ad871fff\63c6304a-a82d-4ec7-8d90-b0b10b1173c2\scratchpad" + "\\"
exec(open(SP + "dev_setup.py", encoding="utf-8").read())
import time, pandas as pd
for name in ("p1_new30.py", "p1_new32.py", "p1_new34.py", "p1_new36.py"):
    exec(open(SP + name, encoding="utf-8").read())
print("new code loaded")
t0 = time.time()
new_golden = evaluate_system(hybrid_retrieve, "new", items=golden_set)
new_valid = evaluate_system(hybrid_retrieve, "new", items=validation_set)
new_golden.to_csv(SP + "new_golden.csv", index=False); new_valid.to_csv(SP + "new_valid.csv", index=False)
print()
summarize(new_golden, "NEW system, golden set")
summarize(new_valid, "NEW system, validation set")
print("elapsed", round(time.time() - t0), "s")
old_g = pd.read_csv(SP + "old_golden.csv", keep_default_na=False); old_v = pd.read_csv(SP + "old_valid.csv", keep_default_na=False)
print()
for label, old, new in (("golden", old_g, new_golden), ("validation", old_v, new_valid)):
    m = old.merge(new, on="id", suffixes=("_old", "_new"))
    ch = m[(m["correct_old"].astype(str) != m["correct_new"].astype(str)) | (m["actual_status_old"] != m["actual_status_new"]) | ((m["estimated_score_old"].astype(float) - m["estimated_score_new"].astype(float)).abs() > 0.01)]
    print(f"--- {label}: changed rows ({len(ch)})")
    for _, r in ch.iterrows():
        print(f"{r['id']} [{r['category_new']}] correct {r['correct_old']}->{r['correct_new']} | status {r['actual_status_old']}->{r['actual_status_new']} (expected {r['expected_status_new']}) | score {float(r['estimated_score_old']):.2f}->{float(r['estimated_score_new']):.2f}")


