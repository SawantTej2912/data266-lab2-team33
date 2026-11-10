"""Drive a running kernel.
  python kx.py CONN exec FILE            -> run a python file's code in the kernel
  python kx.py CONN cells NB FIRST LAST  -> run the code cells at notebook positions FIRST..LAST
"""
import sys, json, re, time, queue
from jupyter_client import BlockingKernelClient

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
conn, cmd = sys.argv[1], sys.argv[2]
kc = BlockingKernelClient(connection_file=conn)
kc.load_connection_file()
kc.start_channels()
kc.wait_for_ready(timeout=120)

ANSI = re.compile(r"\x1b\[[0-9;]*m")

def run(code, timeout=3600):
    msg_id = kc.execute(code)
    start = time.time()
    failed = False
    while True:
        if time.time() - start > timeout:
            print("!! timeout"); return False
        try:
            msg = kc.get_iopub_msg(timeout=5)
        except queue.Empty:
            continue
        if msg["parent_header"].get("msg_id") != msg_id:
            continue
        kind, content = msg["msg_type"], msg["content"]
        if kind == "stream":
            if content["name"] == "stdout" or "Warning" not in content["text"][:200]:
                sys.stdout.write(content["text"])
        elif kind in ("execute_result", "display_data"):
            text = content["data"].get("text/plain", "")
            if text:
                print(text)
        elif kind == "error":
            failed = True
            print("!! ERROR", content["ename"], content["evalue"])
            print(ANSI.sub("", "\n".join(content["traceback"]))[-2500:])
        elif kind == "status" and content["execution_state"] == "idle":
            return not failed

def strip_magics(code):
    return "\n".join(line for line in code.split("\n") if not line.lstrip().startswith("%"))

if cmd == "exec":
    ok = run(open(sys.argv[3], encoding="utf-8").read())
elif cmd == "cells":
    nb = json.load(open(sys.argv[3], encoding="utf-8"))
    first, last = int(sys.argv[4]), int(sys.argv[5])
    ok = True
    for i in range(first, last + 1):
        cell = nb["cells"][i]
        if cell["cell_type"] != "code":
            continue
        code = strip_magics("".join(cell["source"]))
        if not code.strip():
            continue
        print(f"----- cell {i} ({cell['id'][:8]}) -----", flush=True)
        t = time.time()
        ok = run(code)
        print(f"[{time.time() - t:.1f}s]", flush=True)
        if not ok:
            break
kc.stop_channels()
sys.exit(0 if ok else 1)
