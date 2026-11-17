import ast
SP = r"C:\Users\tejas\AppData\Local\Temp\claude\deab2937ad871fff\63c6304a-a82d-4ec7-8d90-b0b10b1173c2\scratchpad" + "\\"
for n in ("p1_new30.py", "p1_new32.py", "p1_new34.py", "p1_new36.py", "p1_new45.py"):
    ast.parse(open(SP + n, encoding="utf-8").read())
print("all new cells parse OK")

