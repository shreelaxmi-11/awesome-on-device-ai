#!/usr/bin/env python3
"""
LiteRT-LM Desktop Chat — Awesome On-Device AI
Cross-platform local LLM chat using Google's LiteRT-LM.
Runs on macOS, Linux, Windows, and Android (same Python code).

Usage:
    python chat.py --model-path /path/to/model.litertlm
    python chat.py --model-path model.litertlm --backend cpu
"""

import argparse
import asyncio
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

DEFAULT_BACKEND = "gpu"
MAX_TOKENS      = 512


async def stream_response(conversation, prompt: str) -> str:
    result = ""
    async for chunk in conversation.send_message_async(prompt):
        print(chunk, end="", flush=True)
        result += chunk
    print()
    return result


def main():
    parser = argparse.ArgumentParser(description="Cross-platform local chat using LiteRT-LM.")
    parser.add_argument("--model-path", required=True, help="Path to .litertlm model file")
    parser.add_argument("--backend",    default=DEFAULT_BACKEND, choices=["gpu", "cpu"])
    args = parser.parse_args()

    try:
        import litert_lm
        from litert_lm import Backend
    except ImportError:
        console.print("[red]litert-lm-api not installed. Run: pip install litert-lm-api[/red]")
        sys.exit(1)

    console.print(Panel.fit(
        "[bold cyan]🌍 LiteRT-LM Desktop Chat[/bold cyan]\n"
        f"[dim]Backend:[/dim] {args.backend.upper()} · "
        f"[dim]Platform:[/dim] Cross-platform (macOS · Linux · Windows · Android)",
        border_style="cyan"
    ))

    backend = Backend.GPU() if args.backend == "gpu" else Backend.CPU()

    with console.status(f"[cyan]Loading model ({args.backend.upper()})...[/cyan]"):
        try:
            engine = litert_lm.Engine(args.model_path, backend=backend)
        except Exception as e:
            console.print(f"[red]Failed to load model: {e}[/red]")
            sys.exit(1)
    console.print(f"[green]✓[/green] Model loaded\n")

    console.print("[dim]Type your message and press Enter. Type [bold]exit[/bold] to quit.[/dim]\n")

    conversation = engine.create_conversation()

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break

        console.print("\n[bold green]Assistant[/bold green]")
        asyncio.run(stream_response(conversation, user_input))
        print()


if __name__ == "__main__":
    main()
