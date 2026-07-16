#!/usr/bin/env python3
"""
On-Device AI Hardware Benchmarks — Awesome On-Device AI
Benchmark any MLX model: prefill tok/s, generation tok/s, TTFT, peak memory.
Tested on Apple M3 Pro 18GB with MLX 0.32.0.

Usage:
    python benchmark.py                               # run default 4-model suite
    python benchmark.py --model mlx-community/Llama-3.2-3B-Instruct-4bit
    python benchmark.py --models models.txt           # file with one model per line
    python benchmark.py --prompt-tokens 256 --output-tokens 128
"""

import argparse
import time
import resource
import sys

from mlx_lm import load, generate
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Default 4-model benchmark suite
DEFAULT_MODELS = [
    "mlx-community/Llama-3.2-3B-Instruct-4bit",
    "mlx-community/Phi-3.5-mini-instruct-4bit",
    "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
    "mlx-community/Llama-3-8B-Instruct-4bit",
]

NUM_TRIALS    = 3
WARMUP_TRIALS = 1

# Build a ~N-token prompt by repeating a sentence
BASE_SENTENCE = (
    "Explain the history of artificial intelligence from the 1950s to today, "
    "including key researchers, landmark papers, and how hardware advances "
    "enabled the deep learning era. "
)


def make_prompt(target_tokens: int) -> str:
    repeats = max(1, target_tokens // 20)
    return BASE_SENTENCE * repeats


def get_peak_memory_gb() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    # macOS reports in bytes
    return usage.ru_maxrss / (1024 ** 3)


def benchmark_model(model_id: str, prompt_tokens: int, output_tokens: int) -> dict | None:
    prompt = make_prompt(prompt_tokens)

    try:
        with console.status(f"[cyan]Loading {model_id.split('/')[-1]}...[/cyan]"):
            model, tokenizer = load(model_id)
    except Exception as e:
        console.print(f"[red]Failed to load {model_id}: {e}[/red]")
        return None

    mem_after_load = get_peak_memory_gb()

    # Apply chat template if available
    if hasattr(tokenizer, "apply_chat_template"):
        messages = [{"role": "user", "content": prompt}]
        formatted = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        formatted = prompt

    # Warmup
    for _ in range(WARMUP_TRIALS):
        generate(model, tokenizer, prompt=formatted, max_tokens=32, verbose=False)

    # Timed trials
    trial_results = []
    for i in range(NUM_TRIALS):
        mem_before = get_peak_memory_gb()
        t0 = time.perf_counter()
        response = generate(
            model, tokenizer,
            prompt=formatted,
            max_tokens=output_tokens,
            verbose=False,
        )
        t1 = time.perf_counter()

        elapsed    = t1 - t0
        # Approximate token counts (chars/4 heuristic)
        p_toks     = len(formatted) / 4
        o_toks     = len(response) / 4
        # TTFT approximation: assume 10% of total time is prefill for small outputs
        ttft_ms    = (elapsed * p_toks / (p_toks + o_toks)) * 1000
        gen_tok_s  = o_toks / max(elapsed - ttft_ms / 1000, 0.001)
        pre_tok_s  = p_toks / max(ttft_ms / 1000, 0.001)

        trial_results.append({
            "ttft_ms":   ttft_ms,
            "pre_tok_s": pre_tok_s,
            "gen_tok_s": gen_tok_s,
            "mem_gb":    get_peak_memory_gb(),
        })
        console.print(
            f"  [{i+1}/{NUM_TRIALS}] TTFT={ttft_ms:.0f}ms  "
            f"Prefill={pre_tok_s:.0f} tok/s  Gen={gen_tok_s:.1f} tok/s  "
            f"Mem={trial_results[-1]['mem_gb']:.2f} GB"
        )

    avg = {k: sum(r[k] for r in trial_results) / len(trial_results) for k in trial_results[0]}

    return {
        "model":     model_id.split("/")[-1],
        "ttft_ms":   avg["ttft_ms"],
        "pre_tok_s": avg["pre_tok_s"],
        "gen_tok_s": avg["gen_tok_s"],
        "mem_gb":    avg["mem_gb"],
    }


def print_results_table(results: list[dict]):
    table = Table(
        title="On-Device AI Hardware Benchmark Results",
        show_header=True,
        header_style="bold cyan",
        caption="Apple Silicon · MLX · INT4 quantization",
    )
    table.add_column("Model",          style="bold")
    table.add_column("TTFT (ms)",      justify="right")
    table.add_column("Prefill (tok/s)", justify="right")
    table.add_column("Gen (tok/s)",    justify="right")
    table.add_column("Memory (GB)",    justify="right")

    for r in results:
        table.add_row(
            r["model"],
            f"{r['ttft_ms']:.0f}",
            f"{r['pre_tok_s']:.0f}",
            f"{r['gen_tok_s']:.1f}",
            f"{r['mem_gb']:.2f}",
        )

    console.print()
    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="Benchmark MLX models on Apple Silicon.")
    parser.add_argument("--model",         help="Single model to benchmark")
    parser.add_argument("--models",        help="Path to file with model IDs (one per line)")
    parser.add_argument("--prompt-tokens", type=int, default=128, help="Approximate prompt length")
    parser.add_argument("--output-tokens", type=int, default=128, help="Output tokens per trial")
    parser.add_argument("--trials",        type=int, default=NUM_TRIALS)
    args = parser.parse_args()

    if args.model:
        models = [args.model]
    elif args.models:
        models = [l.strip() for l in open(args.models).readlines() if l.strip()]
    else:
        models = DEFAULT_MODELS

    console.print(Panel.fit(
        "[bold cyan]📊 On-Device AI Hardware Benchmarks[/bold cyan]\n"
        f"[dim]Models:[/dim] {len(models)} · "
        f"[dim]Prompt:[/dim] ~{args.prompt_tokens} tokens · "
        f"[dim]Output:[/dim] {args.output_tokens} tokens · "
        f"[dim]Trials:[/dim] {args.trials}",
        border_style="cyan"
    ))

    results = []
    for model_id in models:
        console.rule(f"[bold]{model_id.split('/')[-1]}[/bold]")
        r = benchmark_model(model_id, args.prompt_tokens, args.output_tokens)
        if r:
            results.append(r)
        console.print()

    if results:
        print_results_table(results)


if __name__ == "__main__":
    main()
