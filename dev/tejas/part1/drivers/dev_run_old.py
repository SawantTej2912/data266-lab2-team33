SP = r"C:\Users\tejas\AppData\Local\Temp\claude\deab2937ad871fff\63c6304a-a82d-4ec7-8d90-b0b10b1173c2\scratchpad" + "\\"
exec(open(SP + "dev_setup.py", encoding="utf-8").read())
import time
t0 = time.time()
old_golden = evaluate_system(hybrid_retrieve, "old", items=golden_set)
old_valid = evaluate_system(hybrid_retrieve, "old", items=validation_set)
old_golden.to_csv(SP + "old_golden.csv", index=False); old_valid.to_csv(SP + "old_valid.csv", index=False)
print()
summarize(old_golden, "OLD system, golden set")
summarize(old_valid, "OLD system, validation set")
print("elapsed", round(time.time() - t0), "s")
