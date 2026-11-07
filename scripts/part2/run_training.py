"""Run the diffusers LoRA training script and record its peak GPU memory and training time.

The GPU memory is capped, so a run that works here also fits on a 16 GB GPU (Kaggle T4 or Colab T4).

Usage:
    python run_training.py --memory_limit_gb 15 --summary summary.json -- <arguments of train_text_to_image_lora.py>
"""
import argparse
import json
import runpy
import sys
import time
from pathlib import Path

import torch

parser = argparse.ArgumentParser()
parser.add_argument("--memory_limit_gb", type=float, default=15.0, help="GPU memory the run may use")
parser.add_argument("--summary", required=True, help="json file that receives the measurements")
known, training_args = parser.parse_known_args()
training_args = [a for a in training_args if a != "--"]

# Cap the GPU memory. The run stops with an out-of-memory error if it needs more than this.
total_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
torch.cuda.set_per_process_memory_fraction(min(1.0, known.memory_limit_gb / total_gb))
torch.cuda.reset_peak_memory_stats()

script = Path(__file__).with_name("train_text_to_image_lora.py")
sys.argv = [str(script)] + training_args

start = time.time()
runpy.run_path(str(script), run_name="__main__")      # runs the diffusers script in this process
seconds = time.time() - start

summary = {
    "gpu": torch.cuda.get_device_name(0),
    "memory_limit_gb": known.memory_limit_gb,
    "peak_memory_allocated_gb": round(torch.cuda.max_memory_allocated() / 1024**3, 2),
    "peak_memory_reserved_gb": round(torch.cuda.max_memory_reserved() / 1024**3, 2),
    "training_seconds": round(seconds, 1),
    "arguments": training_args,
}
Path(known.summary).write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
