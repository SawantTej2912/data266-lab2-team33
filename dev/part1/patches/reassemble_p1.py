import nbformat
SP = r"C:\Users\tejas\AppData\Local\Temp\claude\deab2937ad871fff\63c6304a-a82d-4ec7-8d90-b0b10b1173c2\scratchpad" + "\\"
PATH = r"C:\Users\tejas\Desktop\GPU_LAB_2\notebooks\p1_rag_final.ipynb"
nb = nbformat.read(PATH, as_version=4)
targets = [("# Hybrid retrieval", "p1_new30.py"), ("import ast", "p1_new32.py"), ("# Resolve follow-up", "p1_new34.py"),
           ("conversation_memory = {}", "p1_new36.py"), ("import time\n\n# Page of every figure", "p1_new45.py")]
for prefix, name in targets:
    matches = [i for i, c in enumerate(nb.cells) if c.cell_type == "code" and "".join(c.source).startswith(prefix)]
    assert len(matches) == 1, (prefix, matches)
    nb.cells[matches[0]].source = open(SP + name, encoding="utf-8").read()
    print("cell", matches[0], "<-", name)
nbformat.write(nb, PATH)
