---
license: creativeml-openrail-m
base_model: stable-diffusion-v1-5/stable-diffusion-v1-5
library_name: diffusers
tags:
- stable-diffusion
- text-to-image
- lora
- diffusers
datasets:
- reach-vb/pokemon-blip-captions
---

# Pokemon LoRA for Stable Diffusion 1.5 (rank 32) - selected as the final model

A LoRA adapter for `stable-diffusion-v1-5/stable-diffusion-v1-5`, fine-tuned on Pokemon artwork with BLIP captions. It is one of two runs of DATA 266 Lab 2 (rank 8 and rank 32, same data and steps).
**This is the run we selected as final**, because its in-domain images are closest to the test images (lowest KID).

## Usage

```python
import torch
from diffusers import StableDiffusionPipeline
pipe = StableDiffusionPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5", torch_dtype=torch.float16).to("cuda")
pipe.load_lora_weights("SawantTej/pokemon-sd15-lora-r32")
image = pipe("a cartoon bird with a hat on its head", num_inference_steps=30).images[0]
```

## Training data
`reach-vb/pokemon-blip-captions` (license cc-by-nc-sa-4.0), 833 images. After removing duplicates: 830 images. Split 90/10 with seed 266: 747 training images (this model) and 83 test images (only used for evaluation). Images are 512x512.

## Training settings
LoRA on the attention layers of the UNet, rank 32 (6,377,472 trainable parameters), learning rate 0.0001 (cosine schedule), 3000 steps, batch size 4 (about 16.1 epochs), fp16 mixed precision, seed 266, trained with the diffusers `train_text_to_image_lora.py` script on one RTX 4090 (peak GPU memory 3.75 GB, 16.1 minutes).

## Results (our evaluation, 20 prompts x 2 seeds, 30 steps, guidance 7.5)
- KID against the 83 test images (20 in-domain generations): 0.0356 (base model: 0.0947).
- CLIP score: 32.13 on all prompts (base model: 32.82).
- LPIPS diversity between two seeds: 0.755 (base model: 0.830).
- Human comparison with the base model: not available yet.

## Limitations
- The training set is small and very uniform (single characters on a white background). The style may carry over to unrelated prompts (we did not see this on our 5 out-of-domain test prompts), and prompts with several objects, counts or colours often go wrong.
- The captions were written by a model (BLIP) and many do not match the pictures.
- KID is computed on only 20 generated images, so small differences are not meaningful.
- The generated images were checked with the Stable Diffusion safety checker: 9 of 120 images were flagged. We looked at all of them: they are harmless cartoon creatures (false alarms of the checker).

## License and intended use
The Pokemon characters are copyrighted and the training data is licensed cc-by-nc-sa-4.0, so this model and its images are for **non-commercial research and education only**. The base model is under the CreativeML OpenRAIL-M license, which also applies to this adapter.
