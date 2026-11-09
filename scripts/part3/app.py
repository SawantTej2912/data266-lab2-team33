"""Gradio demo of the Part 3 multi-agent system.

It uses exactly the same code as the notebooks (agents.py) and shows what every agent did for a request:
the planner's route, the vision result, the prompt, the generation record, the critic's scores and the JSON trace.

Run from the repository root:   python scripts/part3/app.py            (then open http://127.0.0.1:7860)
In Kaggle or Colab:             python scripts/part3/app.py --share     (prints a public link)

Loading the models takes about 40 seconds. The first run downloads about 20 GB of models from Hugging Face. After
that all models are in the local cache, and you can start without a network connection (set HF_HUB_OFFLINE=1).
When the output of the app is redirected to a file, the "Running on local URL" line can appear late (it is buffered).
"""
import argparse
import json
import time
from pathlib import Path

import gradio as gr

import agents

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "outputs" / "part3" / "app"
IMAGE_DIR = ROOT / "data" / "part3" / "images"

print("Loading the models (about one minute) ...")
models = agents.Models()
print("Models loaded.")


def by_agent(state, name):
    """What one agent returned. If it ran several times (revisions), a list with one entry per run."""
    outputs = [step["output"] if step["error"] is None else {"error": step["error"]} for step in state.trace if step["agent"] == name]
    if not outputs:
        return {"skipped": "this agent was not needed for this request"}
    return outputs[0] if len(outputs) == 1 else outputs


def handle(image_path, request, use_critique):
    """Run one request through the five agents and return everything the page shows."""
    if not request or not request.strip():
        return "Please type a request.", None, [], {}, {}, {}, {}, {}, None
    state = agents.run_request(models, request.strip(), image_path, max_revisions=2 if use_critique else 0,
                               out_dir=OUT_DIR, request_id=time.strftime("%Y%m%d_%H%M%S"))

    status = f"{state.message}\n\n[route: {state.route or '-'} | outcome: {state.outcome} | revisions: {state.revision_count} | {state.seconds} s]"
    tries = [(record["image_path"], f"try {i}: {record['prompt'][:60]}") for i, record in enumerate(state.generations, start=1)]
    trace_file = OUT_DIR / "traces" / f"{state.request_id}.json"
    return (status, state.final_image_path, tries, by_agent(state, "planner"), by_agent(state, "vision"),
            by_agent(state, "prompt"), by_agent(state, "generation"), by_agent(state, "critique"), str(trace_file))


examples = [
    [str(IMAGE_DIR / "dog_beach.jpg"), "What is the dog doing?", True],
    [str(IMAGE_DIR / "bird_branch.jpg"), "Turn this into a pastel drawing.", True],
    [str(IMAGE_DIR / "red_car_street.jpg"), "Change the car to green.", True],
    [None, "Generate a Pokemon-style water turtle.", True],
    [str(IMAGE_DIR / "portrait_man.jpg"), "Edit this photo so it looks like Elon Musk is being arrested.", True],
    [str(IMAGE_DIR / "truncated.jpg"), "Describe this image.", True],
]

with gr.Blocks(title="Multi-agent image system") as demo:
    gr.Markdown("# Multimodal multi-agent image system\n"
                "Upload an image (optional) and type a request: describe it, ask a question, change its style, edit it, "
                "or make Pokemon-style artwork (with our fine-tuned Stable Diffusion LoRA). "
                "Unsafe requests are refused, and a critic checks every result and may ask for up to 2 revisions.")
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="filepath", label="Input image (optional)")
            request_input = gr.Textbox(label="Request", placeholder="for example: Turn this into a watercolor painting.")
            critique_input = gr.Checkbox(value=True, label="Use the critique loop (up to 2 revisions)")
            run_button = gr.Button("Run", variant="primary")
        with gr.Column():
            status_output = gr.Textbox(label="Result message", lines=8)
            final_output = gr.Image(label="Final image")
            tries_output = gr.Gallery(label="Every try (with the prompt used)", columns=3, height=240)

    gr.Markdown("### What each agent did")
    with gr.Tab("1. Planner"):
        planner_output = gr.JSON()
    with gr.Tab("2. Vision"):
        vision_output = gr.JSON()
    with gr.Tab("3. Prompt engineering"):
        prompt_output = gr.JSON()
    with gr.Tab("4. Image generation"):
        generation_output = gr.JSON()
    with gr.Tab("5. Critique"):
        critique_output = gr.JSON()
    trace_output = gr.Textbox(label="JSON trace of this request (saved file)")

    gr.Examples(examples=examples, inputs=[image_input, request_input, critique_input])
    run_button.click(handle, inputs=[image_input, request_input, critique_input],
                     outputs=[status_output, final_output, tries_output, planner_output, vision_output,
                              prompt_output, generation_output, critique_output, trace_output])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--share", action="store_true", help="make a public link (for Kaggle or Colab)")
    arguments = parser.parse_args()
    demo.launch(server_name="127.0.0.1", share=arguments.share)
