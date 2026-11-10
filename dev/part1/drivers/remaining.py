import pandas as pd, sys, textwrap
sys.stdout.reconfigure(encoding='utf-8')
SP = r"C:\Users\tejas\AppData\Local\Temp\claude\deab2937ad871fff\63c6304a-a82d-4ec7-8d90-b0b10b1173c2\scratchpad" + "\\"
new = pd.concat([pd.read_csv(SP + "new_golden.csv", keep_default_na=False), pd.read_csv(SP + "new_valid.csv", keep_default_na=False)])
old = pd.concat([pd.read_csv(SP + "old_golden.csv", keep_default_na=False), pd.read_csv(SP + "old_valid.csv", keep_default_na=False)]).set_index("id")
bad = new[(~new["correct"].astype(str).eq("True")) | (new["expected_status"] != new["actual_status"])]
print(len(bad), "rows still wrong (answer or status)\n")
for _, r in bad.iterrows():
    o = old.loc[r["id"]]
    print(f"[{r['id']}] {r['category']} | status {r['expected_status']} -> {r['actual_status']} (old {o['actual_status']}) | correct {r['correct']} (old {o['correct']})")
    print("   Q:", textwrap.shorten(r["question"], 120)); print("   EXPECT:", textwrap.shorten(r["expected_answer"], 100))
    print("   GOT   :", textwrap.shorten(r["actual_answer"], 230), "| cites:", r["citations"])
