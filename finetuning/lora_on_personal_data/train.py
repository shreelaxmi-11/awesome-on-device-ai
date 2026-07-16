#!/usr/bin/env python3
"""
LoRA Fine-tuning on Personal Data — Awesome On-Device AI
Fine-tune any MLX-compatible LLM on your own writing using LoRA.
Creates a lightweight adapter that makes the model sound like you.
Training stays entirely on your machine.

Usage:
    # Prepare your data (one example per line in JSONL format)
    python train.py --prepare --input your_writing.txt

    # Run LoRA training
    python train.py --train --data data/ --model mlx-community/Llama-3.2-3B-Instruct-4bit

    # Chat with your fine-tuned model
    python train.py --chat --adapter adapters/

Requirements:
    pip install mlx-lm

MLX LoRA training uses the built-in mlx_lm.lora module.
See: https://github.com/ml-explore/mlx-examples/tree/main/llms/mlx_lm
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()

DEFAULT_MODEL    = "mlx-community/Llama-3.2-3B-Instruct-4bit"
DEFAULT_ITERS    = 100
DEFAULT_LORA_R   = 8


def prepare_data(input_file: str, output_dir: str, val_split: float = 0.1):
    """Convert raw text to MLX LoRA JSONL format."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    text = Path(input_file).read_text()

    # Split into paragraphs / chunks
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50]

    if len(paragraphs) < 10:
        console.print("[yellow]Warning: fewer than 10 examples. Fine-tuning needs more data for good results.[/yellow]")
        console.print("[dim]Tip: use writing samples, notes, emails, or documents — aim for 100+ paragraphs.[/dim]")

    # Format as instruction-following examples
    examples = []
    for i, para in enumerate(paragraphs):
        # Simple completion format: model learns to continue in your style
        if len(para.split()) < 10:
            continue
        words = para.split()
        mid   = len(words) // 2
        prompt    = " ".join(words[:mid])
        completion = " ".join(words[mid:])
        examples.append({
            "text": f"<s>[INST] Continue this in the same style and voice: {prompt} [/INST] {completion} </s>"
        })

    # Split train/val
    n_val   = max(1, int(len(examples) * val_split))
    n_train = len(examples) - n_val

    train_examples = examples[:n_train]
    val_examples   = examples[n_train:]

    train_path = output_path / "train.jsonl"
    val_path   = output_path / "valid.jsonl"

    with open(train_path, "w") as f:
        for ex in train_examples:
            f.write(json.dumps(ex) + "\n")

    with open(val_path, "w") as f:
        for ex in val_examples:
            f.write(json.dumps(ex) + "\n")

    console.print(f"[green]✓[/green] Prepared {len(train_examples)} train · {len(val_examples)} val examples")
    console.print(f"[dim]Output: {train_path}, {val_path}[/dim]")
    return str(output_path)


def run_training(model: str, data_dir: str, output_dir: str, iters: int, lora_r: int):
    """Run MLX LoRA training via mlx_lm.lora."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "mlx_lm.lora",
        "--model",       model,
        "--train",
        "--data",        data_dir,
        "--adapter-path", str(output_path),
        "--iters",       str(iters),
        "--lora-r",      str(lora_r),
        "--batch-size",  "1",
        "--learning-rate", "1e-5",
        "--steps-per-eval", "10",
        "--val-batches", "5",
    ]

    console.print(f"[cyan]Running:[/cyan] {' '.join(cmd[:6])} ...\n")
    console.print("[dim]Training will print loss every 10 steps. Lower loss = better fit.[/dim]\n")

    result = subprocess.run(cmd)
    if result.returncode == 0:
        console.print(f"\n[green]✓[/green] Training complete. Adapter saved to [bold]{output_path}[/bold]")
    else:
        console.print(f"[red]Training failed with exit code {result.returncode}[/red]")


def run_chat(model: str, adapter_dir: str):
    """Launch a chat session with the fine-tuned model."""
    cmd = [
        sys.executable, "-m", "mlx_lm.generate",
        "--model",       model,
        "--adapter-path", adapter_dir,
        "--prompt",      "Hello! Tell me about yourself.",
        "--max-tokens",  "200",
    ]
    console.print(f"\n[cyan]Testing adapter:[/cyan] {adapter_dir}\n")
    subprocess.run(cmd)

    console.print("\n[dim]For interactive chat with your fine-tuned model:[/dim]")
    console.print(f"[bold]python -m mlx_lm.generate --model {model} --adapter-path {adapter_dir} --prompt YOUR_PROMPT[/bold]")


def main():
    parser = argparse.ArgumentParser(description="LoRA fine-tuning on personal data using MLX.")
    parser.add_argument("--prepare",    action="store_true", help="Prepare training data from raw text")
    parser.add_argument("--train",      action="store_true", help="Run LoRA training")
    parser.add_argument("--chat",       action="store_true", help="Test the fine-tuned model")
    parser.add_argument("--input",      help="Input text file (for --prepare)")
    parser.add_argument("--data",       default="data/",   help="Data directory with JSONL files")
    parser.add_argument("--adapter",    default="adapters/", help="Adapter output/input directory")
    parser.add_argument("--model",      default=DEFAULT_MODEL)
    parser.add_argument("--iters",      type=int, default=DEFAULT_ITERS)
    parser.add_argument("--lora-r",     type=int, default=DEFAULT_LORA_R)
    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold cyan]🎯 LoRA Fine-tuning on Personal Data[/bold cyan]\n"
        "[dim]Runtime:[/dim] MLX LoRA · No internet · No API key\n"
        "[dim]Training stays entirely on your machine[/dim]",
        border_style="cyan"
    ))

    if args.prepare:
        if not args.input:
            console.print("[red]--input required for --prepare[/red]")
            sys.exit(1)
        prepare_data(args.input, args.data)

    elif args.train:
        run_training(args.model, args.data, args.adapter, args.iters, args.lora_r)

    elif args.chat:
        run_chat(args.model, args.adapter)

    else:
        console.print("[dim]Usage:[/dim]")
        console.print("  Step 1: python train.py --prepare --input your_writing.txt")
        console.print("  Step 2: python train.py --train --model mlx-community/Llama-3.2-3B-Instruct-4bit")
        console.print("  Step 3: python train.py --chat")


if __name__ == "__main__":
    main()
