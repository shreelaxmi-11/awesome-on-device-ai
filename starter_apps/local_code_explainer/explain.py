#!/usr/bin/env python3
"""
Local Code Explainer — Awesome On-Device AI
Paste or load any code snippet — get a clear explanation from a local LLM.
No API key. No cloud. No code leaves your machine.

Usage:
    python explain.py                          # paste code interactively
    python explain.py --file my_script.py      # explain a file
    python explain.py --file app.py --mode review   # code review mode
    python explain.py --mode docstring         # generate docstrings
"""

import argparse
import sys
from pathlib import Path

from mlx_lm import load, stream_generate
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax

console = Console()

DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
MAX_TOKENS    = 1024

MODES = {
    "explain": {
        "label": "Explain Code",
        "emoji": "🔍",
        "prompt_template": (
            "Explain the following code clearly and concisely. Cover:\n"
            "1. What it does (1-2 sentences)\n"
            "2. How it works (step by step)\n"
            "3. Any important edge cases or potential issues\n\n"
            "Code:\n```\n{code}\n```"
        ),
        "system": (
            "You are a senior software engineer who explains code clearly to developers of all levels. "
            "Be precise, concise, and educational. Use plain English."
        ),
    },
    "review": {
        "label": "Code Review",
        "emoji": "👀",
        "prompt_template": (
            "Review the following code as a senior engineer would. Cover:\n"
            "1. Correctness — any bugs or logical errors?\n"
            "2. Performance — any inefficiencies?\n"
            "3. Readability — naming, structure, clarity?\n"
            "4. Best practices — style, error handling, edge cases?\n"
            "5. Suggested improvements (with code where helpful)\n\n"
            "Code:\n```\n{code}\n```"
        ),
        "system": (
            "You are a senior software engineer conducting a thorough but constructive code review. "
            "Be specific, actionable, and kind. Quote the relevant code when suggesting changes."
        ),
    },
    "docstring": {
        "label": "Generate Docstrings",
        "emoji": "📝",
        "prompt_template": (
            "Add clear, complete docstrings to every function and class in the following code. "
            "Use the appropriate format for the language (Google style for Python). "
            "Return only the full code with docstrings added — no explanation.\n\n"
            "Code:\n```\n{code}\n```"
        ),
        "system": (
            "You are an expert at writing clear, complete documentation. "
            "Write docstrings that explain purpose, parameters, return values, and raises. "
            "Return only code, no prose explanation."
        ),
    },
    "optimize": {
        "label": "Optimize Code",
        "emoji": "⚡",
        "prompt_template": (
            "Optimize the following code for performance and readability. "
            "Explain what you changed and why, then show the optimized version.\n\n"
            "Code:\n```\n{code}\n```"
        ),
        "system": (
            "You are an expert in code optimization. Focus on algorithmic improvements, "
            "idiomatic rewrites, and reduced complexity. Always explain your changes."
        ),
    },
    "test": {
        "label": "Generate Tests",
        "emoji": "🧪",
        "prompt_template": (
            "Write comprehensive unit tests for the following code. "
            "Cover happy paths, edge cases, and error conditions. "
            "Use appropriate testing frameworks for the language.\n\n"
            "Code:\n```\n{code}\n```"
        ),
        "system": (
            "You are an expert in software testing. Write clear, complete tests that "
            "actually catch bugs. Use descriptive test names. Return only test code."
        ),
    },
}


def get_code(args) -> str:
    """Read code from file or interactive input."""
    if args.file:
        path = Path(args.file)
        if not path.exists():
            console.print(f"[red]File not found: {path}[/red]")
            sys.exit(1)
        code = path.read_text()
        console.print(f"\n[dim]File:[/dim] {path.name} ({len(code.splitlines())} lines)\n")
        # Show syntax-highlighted preview (first 30 lines)
        preview = "\n".join(code.splitlines()[:30])
        suffix = path.suffix.lstrip(".") or "text"
        console.print(Syntax(preview, suffix, theme="monokai", line_numbers=True))
        if len(code.splitlines()) > 30:
            console.print(f"[dim]... {len(code.splitlines()) - 30} more lines[/dim]")
        console.print()
        return code

    # Interactive paste
    mode_info = MODES[args.mode]
    console.print(f"\n[bold]{mode_info['emoji']} {mode_info['label']} Mode[/bold]")
    console.print("[dim]Paste your code below. Press Enter twice when done:[/dim]\n")

    lines = []
    blank_count = 0
    while True:
        try:
            line = input()
        except (KeyboardInterrupt, EOFError):
            break
        if line == "":
            blank_count += 1
            if blank_count >= 2:
                break
            lines.append(line)
        else:
            blank_count = 0
            lines.append(line)

    return "\n".join(lines).strip()


def run_mode(model, tokenizer, code: str, mode: str):
    mode_info = MODES[mode]
    user_content = mode_info["prompt_template"].format(code=code)

    messages = [
        {"role": "system", "content": mode_info["system"]},
        {"role": "user",   "content": user_content},
    ]

    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        prompt = f"SYSTEM: {mode_info['system']}\nUSER: {user_content}\nASSISTANT:"

    console.rule(f"[bold]{mode_info['emoji']} {mode_info['label']}[/bold]")
    console.print()

    result = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
        token = chunk.text if hasattr(chunk, "text") else chunk
        print(token, end="", flush=True)
        result += token
    print("\n")
    return result.strip()


def main():
    parser = argparse.ArgumentParser(description="Explain, review, or improve code using a local LLM.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="MLX model repo")
    parser.add_argument(
        "--mode",
        default="explain",
        choices=list(MODES.keys()),
        help="Mode: explain, review, docstring, optimize, test"
    )
    parser.add_argument("--file",   help="Path to a code file to load")
    parser.add_argument("--output", help="Save the output to this file")
    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold cyan]🔍 Local Code Explainer[/bold cyan]\n"
        f"[dim]Mode:[/dim] {MODES[args.mode]['label']} · "
        f"[dim]Model:[/dim] {args.model.split('/')[-1]}\n"
        "[dim]Runtime:[/dim] MLX (Apple Silicon) · No internet · No API key",
        border_style="cyan"
    ))

    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    code = get_code(args)
    if not code:
        console.print("[yellow]No code provided.[/yellow]")
        sys.exit(0)

    output = run_mode(model, tokenizer, code, args.mode)

    if args.output:
        Path(args.output).write_text(output)
        console.print(f"[green]✓[/green] Saved to [bold]{args.output}[/bold]")

    console.print("[dim]Nothing was sent to any server.[/dim]")


if __name__ == "__main__":
    main()
