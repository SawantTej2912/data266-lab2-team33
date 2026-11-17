import pandas as pd, sys, textwrap
sys.stdout.reconfigure(encoding='utf-8')
SP = r"C:\Users\tejas\AppData\Local\Temp\claude\deab2937ad871fff\63c6304a-a82d-4ec7-8d90-b0b10b1173c2\scratchpad" + "\\"
og, ov = pd.read_csv(SP + "old_golden.csv", keep_default_na=False), pd.read_csv(SP + "old_valid.csv", keep_default_na=False)
ng, nv = pd.read_csv(SP + "new_golden.csv", keep_default_na=False), pd.read_csv(SP + "new_valid.csv", keep_default_na=False)
old = pd.concat([og, ov]).set_index("id"); new = pd.concat([ng, nv]).set_index("id")
for i in ["V12", "V13", "V16", "V17", "V20", "V21", "V28", "V29", "V30", "V31", "V34", "G14", "G24"]:
    o, n = old.loc[i], new.loc[i]
    print(f"[{i}] expect {n['expected_status']}: {textwrap.shorten(n['expected_answer'], 90)}")
    print(f"   OLD ({o['actual_status']}): {textwrap.shorten(o['actual_answer'], 230)}")
    print(f"   NEW ({n['actual_status']}): {textwrap.shorten(n['actual_answer'], 260)} | cites {n['citations']}")
