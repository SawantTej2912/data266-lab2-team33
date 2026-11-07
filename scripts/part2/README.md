# Part 2 scripts

- `train_text_to_image_lora.py` - the LoRA training example script from the `diffusers` library, **version v0.42.1, not changed** (Apache-2.0 license, see the header of the file). Source: https://github.com/huggingface/diffusers/blob/v0.42.1/examples/text_to_image/train_text_to_image_lora.py
- `run_training.py` - our small wrapper. It limits the GPU memory (so a run also fits on a 16 GB GPU), runs the script above, and writes the peak GPU memory and the training time to a json file.

Both are called from `notebooks/p2_2_finetune.ipynb`.
