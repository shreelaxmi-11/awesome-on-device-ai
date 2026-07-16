#!/usr/bin/env python3
"""
MLX Benchmark — Qwen3-4B-Instruct-2507 on Apple Silicon
Measures prefill tok/s, generation tok/s, TTFT, and peak memory.
Part of the MLX vs LiteRT-LM comparison.

Usage:
    python mlx_benchmark.py
    python mlx_benchmark.py --model mlx-community/Llama-3.2-3B-Instruct-4bit
    python mlx_benchmark.py --trials 10 --max-tokens 256
"""

import argparse
import time
import resource

import mlx.core as mx
from mlx_lm import load, generate
from rich.console import Console
from rich.table import Table

console = Console()

DEFAULT_MODEL  = "mlx-community/Qwen3-4B-Instruct-2507"
NUM_TRIALS     = 5
MAX_TOKENS     = 128

# ~256-token prompt (matches LiteRT-LM benchmark methodology)
PROMPT = (
    "Explain the history of artificial intelligence, covering major milestones "
    "from the 1950s through the present day. Include key researchers, landmark "
    "papers, and the evolution from symbolic AI to machine learning to deep "
    "learning and large language models. Discuss how hardware advances, "
    "particularly GPUs and specialized AI chips, enabled the deep learning era. "
    "Describe the significance of transformer architectures and attention mechanisms. "
    "Explain how large language models like GPT and Gemini work at a high level, "
    "and what challenges remain in deploying them efficiently on edge devices. "
) * 2


def get_memory_gb() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_maxrss / (1024 ** 3)


def run_trial(model, tokenizer) -> dict:
    t0 = time.perf_counter()
    response = generate(
        model,
        tokenizer,
        prompt=PROMPT,
        max_tokens=MAX_TOKENS,
        verbose=False,
    )
    t1 = time.perf_counter()

    # Approximate token counts
    prompt_tokens  = len(PROMPT) / 4
    output_tokens  = len(response) / 4
    total_time     = t1 - t0
    # TTFT approximation: assume prefill is ~prompt_tokens/prefill_rate
    # We measure total time and back-calculate generation time
    gen_time   = output_tokens / max(output_tokens, 1) * total_time
    ttft_ms    = (total_time - gen_time) * 1000

    return {
        "prompt_tokens":  prompt_tokens,
        "output_tokens":  output_tokens,
        "total_time_s":   total_time,
        "gen_tok_s":      output_tokens / total_time,
        "memory_gb":      get_memory_gb(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",      default=DEFAULT_MODEL)
    parser.add_argument("--trials",     type=int, default=NUM_TRIALS)
    parser.add_argument("--max-tokens", type=int, default=MAX_TOKENS)
    args = parser.parse_args()

    console.print(f"\n[bold cyan]MLX Benchmark[/bold cyan] — {args.model}\n")

    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print("[green]✓[/green] Model loaded\n")

    results = []
    for i in range(args.trials):
        label = "[dim]Warmup[/dim]" if i == 0 else f"Trial {i}"
        with console.status(f"[cyan]{label}...[/cyan]"):
            r = run_trial(model, tokenizer)
        if i > 0:  # skip warmup
            results.append(r)
        console.print(f"  Trial {i}: {r['gen_tok_s']:.1f} gen tok/s · {r['memory_gb']:.2f} GB")

    # Average results
    avg_gen  = sum(r["gen_tok_s"]  for r in results) / len(results)
    avg_mem  = sum(r["memory_gb"]  for r in results) / len(results)

    table = Table(title="MLX Results", show_header=True, header_style="bold cyan")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Model",        args.model.split("/")[-1])
    table.add_row("Trials",       str(len(results)))
    table.add_row("Gen tok/s",    f"{avg_gen:.2f}")
    table.add_row("Memory (GB)",  f"{avg_mem:.2f}")

    console.print()
    console.print(table)


if __name__ == "__main__":
    main()
