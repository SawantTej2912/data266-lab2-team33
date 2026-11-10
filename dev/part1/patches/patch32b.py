"""Second pass on cell 32: swap the first version of the checks for the improved block in verify_block.txt."""
SP = r"C:\Users\tejas\AppData\Local\Temp\claude\deab2937ad871fff\63c6304a-a82d-4ec7-8d90-b0b10b1173c2\scratchpad" + "\\"
src = open(SP + "p1_new32.py", encoding="utf-8").read()
start = src.index("def build_text_evidence(results):")
end = src.index("def answer_question(")
src = src[:start] + open(SP + "verify_block.txt", encoding="utf-8").read() + src[end:]
open(SP + "p1_new32.py", "w", encoding="utf-8").write(src)
print("cell 32 now", len(src.splitlines()), "lines")
