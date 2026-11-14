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
# run_vlm frees the GPU memory after every call
vlm_cell = next(c for c in nb.cells if c.cell_type == "code" and "def run_vlm" in "".join(c.source))
vlm_text = "".join(vlm_cell.source)
old_tail = '''    return vlm_processor.batch_decode(
        generated_ids,
        skip_special_tokens=True
    )[0].strip()'''
if old_tail in vlm_text:
    vlm_cell.source = vlm_text.replace(old_tail, '''    reply = vlm_processor.batch_decode(
        generated_ids,
        skip_special_tokens=True
    )[0].strip()

    del inputs, generated_ids
    torch.cuda.empty_cache()           # a 15 GB GPU (Kaggle T4) has little room for long prompts
    return reply''')
    print("run_vlm updated")

# first cell: memory is not split into fixed blocks (fewer out-of-memory errors on a 15 GB GPU). It must be set before torch is imported.
first = next(c for c in nb.cells if c.cell_type == "code")
text = "".join(first.source)
assert text.startswith("# Cell 1 - Reproducibility")
if "expandable_segments" not in text:
    old = "import os\nimport sys\nimport random"
    assert text.count(old) == 1
    first.source = text.replace(old, 'import os\n\n# Memory is not split into fixed blocks: fewer out-of-memory errors on a 15 GB GPU (must be set before torch is imported)\nos.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")\n\nimport sys\nimport random')
    print("first cell updated")
nbformat.write(nb, PATH)
