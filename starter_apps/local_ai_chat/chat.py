#!/usr/bin/env python3
"""
Local AI Chat — Awesome On-Device AI
A private, streaming chatbot that runs entirely on your machine.
No API key. No cloud. No data leaving your device.

Usage:
    python chat.py
    python chat.py --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
    python chat.py --system "You are a helpful coding assistant."
"""

import argparse
import sys
from pathlib import Path

from mlx_lm import load, stream_generate
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule

console = Console()

DEFAULT_MODEL  = "mlx-community/Llama-3.2-3B-Instruct-4bit"
DEFAULT_SYSTEM = "You are a helpful, concise AI assistant. Answer clearly and accurately."
MAX_TOKENS     = 1024
MAX_HISTORY    = 20  # messages to keep in context window


def build_prompt(messages: list[dict], tokenizer) -> str:
    if hasattr(tokenizer, "apply_chat_template"):
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    # fallback for models without chat template
    parts = []
    for m in messages:
        role = m["role"].upper()
        parts.append(f"{role}: {m['content']}")
    return "\n".join(parts) + "\nASSISTANT:"


def chat_loop(model, tokenizer, system_prompt: str):
    history: list[dict] = []

    console.print(Panel.fit(
        "[bold cyan]💬 Local AI Chat[/bold cyan]\n"
        "[dim]Runtime:[/dim] MLX (Apple Silicon) · No internet · No API key\n"
        "[dim]Commands:[/dim] [bold]exit[/bold] to quit · [bold]/clear[/bold] to reset history · [bold]/system[/bold] to see system prompt",
        border_style="cyan"
    ))
    console.print()

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "q"}:
            console.print("[dim]Goodbye.[/dim]")
            break

        if user_input.lower() == "/clear":
            history.clear()
            console.print("[dim]History cleared.[/dim]\n")
            continue

        if user_input.lower() == "/system":
            console.print(Panel(system_prompt, title="System Prompt", border_style="dim"))
            continue

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-MAX_HISTORY:])
        messages.append({"role": "user", "content": user_input})

        prompt = build_prompt(messages, tokenizer)

        # Stream response
        console.print("\n[bold green]Assistant[/bold green]")
        response_text = ""
        for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
            token = chunk.text if hasattr(chunk, "text") else chunk
            print(token, end="", flush=True)
            response_text += token
        print("\n")

        # Update history
        history.append({"role": "user",      "content": user_input})
        history.append({"role": "assistant", "content": response_text.strip()})


def main():
    parser = argparse.ArgumentParser(description="Local AI chatbot powered by MLX.")
    parser.add_argument("--model",  default=DEFAULT_MODEL, help="HuggingFace model repo (mlx-community/*)")
    parser.add_argument("--system", default=DEFAULT_SYSTEM, help="System prompt for the assistant")
    args = parser.parse_args()

    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded: [bold]{args.model.split('/')[-1]}[/bold]\n")

    chat_loop(model, tokenizer, args.system)


if __name__ == "__main__":
    main()
