#!/usr/bin/env python3
"""
Cross-Runtime Inference Comparison — Awesome On-Device AI
Benchmark MLX, LiteRT-LM, or Ollama on the same prompt.
Compare TTFT, generation speed, and memory across runtimes.

Usage:
    python compare.py --runtime mlx --model mlx-community/Qwen3-4B-Instruct-2507-4bit
    python compare.py --runtime litert --model-path /path/to/model.litertlm
    python compare.py --runtime ollama --model qwen3:4b
"""

import argparse
import asyncio
import resource
import sys
import time

from rich.console import Console
from rich.table import Table

console = Console()

PROMPT = (
    "Explain the difference between on-device AI and cloud AI. "
    "Cover latency, privacy, cost, and capability trade-offs. "
    "Give a concrete example of when each is the right choice."
)
MAX_TOKENS = 128


def get_memory_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 ** 3)


def benchmark_mlx(model_id: str) -> dict:
    from mlx_lm import load, generate

    t0 = time.perf_counter()
    model, tokenizer = load(model_id)
    load_time = time.perf_counter() - t0

    t1 = time.perf_counter()
    response = generate(model, tokenizer, prompt=PROMPT, max_tokens=MAX_TOKENS, verbose=False)
    gen_time = time.perf_counter() - t1

    output_tokens = len(response) / 4
    return {
        "runtime":    "MLX",
        "load_time":  load_time,
        "gen_tok_s":  output_tokens / max(gen_time, 0.001),
        "memory_gb":  get_memory_gb(),
        "output":     response[:100],
    }


async def _litert_stream(engine, prompt: str) -> tuple[float, str]:
    conversation = engine.create_conversation()
    tokens = []
    ttft = None
    t0 = time.perf_counter()
    async for chunk in conversation.send_message_async(prompt):
        if ttft is None:
            ttft = time.perf_counter() - t0
        tokens.append(chunk)
        if len(tokens) >= MAX_TOKENS:
            break
    return ttft or 0, "".join(tokens)


def benchmark_litert(model_path: str) -> dict:
    try:
        import litert_lm
        from litert_lm import Backend
    except ImportError:
        console.print("[red]pip install litert-lm-api[/red]")
        sys.exit(1)

    t0 = time.perf_counter()
    engine = litert_lm.Engine(model_path, backend=Backend.GPU())
    load_time = time.perf_counter() - t0

    t1 = time.perf_counter()
    ttft, response = asyncio.run(_litert_stream(engine, PROMPT))
    gen_time = time.perf_counter() - t1

    output_tokens = len(response) / 4
    return {
        "runtime":    "LiteRT-LM",
        "load_time":  load_time,
        "ttft_ms":    ttft * 1000,
        "gen_tok_s":  output_tokens / max(gen_time - ttft, 0.001),
        "memory_gb":  get_memory_gb(),
        "output":     response[:100],
    }


def benchmark_ollama(model: str) -> dict:
    try:
        import requests
    except ImportError:
        console.print("[red]pip install requests[/red]")
        sys.exit(1)

    t0 = time.perf_counter()
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": PROMPT, "options": {"num_predict": MAX_TOKENS}},
        stream=True, timeout=120
    )
    import json
    tokens = []
    ttft = None
    for line in response.iter_lines():
        if line:
            d = json.loads(line)
            if d.get("response"):
                if ttft is None:
                    ttft = time.perf_counter() - t0
                tokens.append(d["response"])
    gen_time = time.perf_counter() - t0
    output = "".join(tokens)

    return {
        "runtime":    "Ollama",
        "ttft_ms":    (ttft or 0) * 1000,
        "gen_tok_s":  len(output) / 4 / max(gen_time, 0.001),
        "memory_gb":  get_memory_gb(),
        "output":     output[:100],
    }


def print_results(result: dict):
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    for k, v in result.items():
        if k == "output":
            continue
        if isinstance(v, float):
            table.add_row(k, f"{v:.2f}")
        else:
            table.add_row(k, str(v))
    console.print(table)
    console.print(f"\n[dim]Response preview: {result.get('output', '')[:80]}...[/dim]\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime",    required=True, choices=["mlx", "litert", "ollama"])
    parser.add_argument("--model",      help="Model ID (for mlx or ollama)")
    parser.add_argument("--model-path", help="Path to .litertlm file (for litert)")
    args = parser.parse_args()

    if args.runtime == "mlx":
        result = benchmark_mlx(args.model or "mlx-community/Llama-3.2-3B-Instruct-4bit")
    elif args.runtime == "litert":
        if not args.model_path:
            console.print("[red]--model-path required for litert[/red]")
            sys.exit(1)
        result = benchmark_litert(args.model_path)
    elif args.runtime == "ollama":
        result = benchmark_ollama(args.model or "llama3.2:3b")

    print_results(result)


if __name__ == "__main__":
    main()
