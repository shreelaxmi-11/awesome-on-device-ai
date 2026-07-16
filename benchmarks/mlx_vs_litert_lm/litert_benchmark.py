#!/usr/bin/env python3
"""
LiteRT-LM Benchmark — Qwen3-4B-Instruct-2507 on Apple Silicon
Measures TTFT, prefill tok/s, generation tok/s, and peak memory.
Part of the MLX vs LiteRT-LM comparison.

Requires:
    pip install litert-lm-api
    Download: litert-community/Qwen3-4B-Instruct-2507 from HuggingFace

Usage:
    python litert_benchmark.py --model-path /path/to/model.litertlm
    python litert_benchmark.py --model-path /path/to/model.litertlm --backend cpu
"""

import argparse
import time
import resource
import asyncio
import sys

from rich.console import Console
from rich.table import Table

console = Console()

NUM_TRIALS    = 5
MAX_TOKENS    = 128

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
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 ** 3)


async def run_trial_async(engine) -> dict:
    conversation = engine.create_conversation()
    tokens = []
    ttft_s = None
    t_start = time.perf_counter()

    async for chunk in conversation.send_message_async(PROMPT):
        if ttft_s is None:
            ttft_s = time.perf_counter() - t_start
        tokens.append(chunk)
        if len(tokens) >= MAX_TOKENS:
            break

    t_end = time.perf_counter()

    full_text = "".join(tokens)
    total_time = t_end - t_start
    gen_time = total_time - (ttft_s or 0)
    output_tokens = len(full_text) / 4

    return {
        "ttft_ms":       (ttft_s or 0) * 1000,
        "output_tokens": output_tokens,
        "gen_tok_s":     output_tokens / max(gen_time, 0.001),
        "memory_gb":     get_memory_gb(),
    }


def run_trial(engine) -> dict:
    return asyncio.run(run_trial_async(engine))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", required=True, help="Path to .litertlm model file")
    parser.add_argument("--backend",    default="gpu", choices=["gpu", "cpu"],
                        help="Inference backend")
    parser.add_argument("--trials",     type=int, default=NUM_TRIALS)
    args = parser.parse_args()

    try:
        import litert_lm
        from litert_lm import Backend
    except ImportError:
        console.print("[red]litert-lm-api not installed. Run: pip install litert-lm-api[/red]")
        sys.exit(1)

    console.print(f"\n[bold cyan]LiteRT-LM Benchmark[/bold cyan] — backend: {args.backend}\n")

    backend = Backend.GPU() if args.backend == "gpu" else Backend.CPU()

    with console.status(f"[cyan]Loading model ({args.backend.upper()})...[/cyan]"):
        try:
            engine = litert_lm.Engine(args.model_path, backend=backend)
        except Exception as e:
            console.print(f"[red]Failed to load model: {e}[/red]")
            sys.exit(1)
    console.print("[green]✓[/green] Model loaded\n")

    results = []
    for i in range(args.trials):
        label = "[dim]Warmup[/dim]" if i == 0 else f"Trial {i}"
        with console.status(f"[cyan]{label}...[/cyan]"):
            r = run_trial(engine)
        if i > 0:
            results.append(r)
        console.print(f"  Trial {i}: TTFT={r['ttft_ms']:.0f}ms · {r['gen_tok_s']:.2f} gen tok/s · {r['memory_gb']:.2f} GB")

    avg_ttft = sum(r["ttft_ms"]  for r in results) / len(results)
    avg_gen  = sum(r["gen_tok_s"] for r in results) / len(results)
    avg_mem  = sum(r["memory_gb"] for r in results) / len(results)

    table = Table(title=f"LiteRT-LM Results ({args.backend.upper()})", show_header=True, header_style="bold cyan")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Backend",      args.backend.upper())
    table.add_row("Trials",       str(len(results)))
    table.add_row("TTFT (ms)",    f"{avg_ttft:.0f}")
    table.add_row("Gen tok/s",    f"{avg_gen:.2f}")
    table.add_row("Memory (GB)",  f"{avg_mem:.2f}")

    console.print()
    console.print(table)


if __name__ == "__main__":
    main()
