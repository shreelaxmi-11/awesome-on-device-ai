#!/usr/bin/env python3
"""
Local Writing Assistant — Awesome On-Device AI
Turn bullet points, outlines, or rough notes into polished prose.
No API key. No cloud. Runs entirely on your machine.

Usage:
    python write.py                         # interactive mode
    python write.py --mode email            # draft professional emails
    python write.py --mode blog             # write blog posts
    python write.py --mode report           # write formal reports
    python write.py --mode rewrite          # rewrite pasted text
    python write.py --input notes.txt       # read bullets from a file
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

DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
MAX_TOKENS    = 800

# ── Mode-specific system prompts ───────────────────────────────────────────────
MODES = {
    "general": {
        "label": "General Writing",
        "emoji": "✍️",
        "system": (
            "You are an expert writer and editor. "
            "When given bullet points, notes, or rough ideas, transform them into polished, "
            "clear, and well-structured prose. Match the appropriate tone and format. "
            "Write directly — do not explain what you are doing, just write."
        ),
    },
    "email": {
        "label": "Professional Email",
        "emoji": "📧",
        "system": (
            "You are a professional business writer. "
            "When given bullet points or a rough description, draft a professional email. "
            "Use a clear subject line (if not provided), a warm but professional tone, "
            "and a concise structure: opening → context → request/information → closing. "
            "Write the full email. Do not explain what you are doing."
        ),
    },
    "blog": {
        "label": "Blog Post",
        "emoji": "📝",
        "system": (
            "You are a skilled blog writer. "
            "When given bullet points or a topic outline, write a compelling blog post "
            "with an engaging title, a hook opening paragraph, well-developed body sections, "
            "and a clear conclusion. Use a conversational but authoritative tone. "
            "Write the full post. Do not explain what you are doing."
        ),
    },
    "report": {
        "label": "Formal Report",
        "emoji": "📊",
        "system": (
            "You are a technical writer specializing in formal reports and documentation. "
            "When given bullet points or an outline, write a structured formal report with "
            "clear section headings, precise language, and professional formatting. "
            "Write the full report. Do not explain what you are doing."
        ),
    },
    "rewrite": {
        "label": "Rewrite / Improve",
        "emoji": "🔄",
        "system": (
            "You are an expert editor. "
            "When given a piece of text, rewrite it to be cleaner, clearer, and more compelling. "
            "Preserve the original meaning and key information. Fix grammar, improve flow, "
            "remove redundancy, and sharpen the language. "
            "Output only the rewritten text. Do not explain your changes."
        ),
    },
}


def get_input_text(args) -> tuple[str, str]:
    """Get the user's input text and a label for display."""
    if args.input:
        path = Path(args.input)
        if not path.exists():
            console.print(f"[red]File not found: {path}[/red]")
            sys.exit(1)
        text = path.read_text().strip()
        return text, f"File: {path.name}"

    # Interactive input
    mode_info = MODES[args.mode]
    console.print(f"\n[bold]{mode_info['emoji']} {mode_info['label']} Mode[/bold]")

    if args.mode == "rewrite":
        console.print("[dim]Paste the text you want rewritten. Press Enter twice when done:[/dim]\n")
    else:
        console.print("[dim]Enter your bullet points or rough notes. Press Enter twice when done:[/dim]\n")

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

    return "\n".join(lines).strip(), "Interactive input"


def generate_draft(model, tokenizer, input_text: str, mode: str) -> str:
    mode_info = MODES[mode]

    if mode == "rewrite":
        user_content = f"Please rewrite the following text:\n\n{input_text}"
    else:
        user_content = f"Please write the following based on these notes/bullet points:\n\n{input_text}"

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
    parser = argparse.ArgumentParser(description="Local writing assistant powered by MLX.")
    parser.add_argument("--model",  default=DEFAULT_MODEL, help="MLX model repo")
    parser.add_argument(
        "--mode",
        default="general",
        choices=list(MODES.keys()),
        help="Writing mode: general, email, blog, report, rewrite"
    )
    parser.add_argument("--input",  help="Path to a text file with your notes/bullets")
    parser.add_argument("--output", help="Save the draft to this file path")
    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold cyan]✍️ Local Writing Assistant[/bold cyan]\n"
        f"[dim]Mode:[/dim] {MODES[args.mode]['label']} · "
        f"[dim]Model:[/dim] {args.model.split('/')[-1]}\n"
        "[dim]Runtime:[/dim] MLX (Apple Silicon) · No internet · No API key",
        border_style="cyan"
    ))

    # Load model
    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    while True:
        # Get input
        input_text, input_label = get_input_text(args)

        if not input_text:
            console.print("[yellow]No input provided. Exiting.[/yellow]")
            break

        # Generate
        draft = generate_draft(model, tokenizer, input_text, args.mode)

        # Optionally save
        if args.output:
            Path(args.output).write_text(draft)
            console.print(f"[green]✓[/green] Saved to [bold]{args.output}[/bold]")

        # Ask to continue
        console.print()
        again = Prompt.ask("[dim]Write another? ([bold]y[/bold]/n)[/dim]", default="n").strip().lower()
        if again != "y":
            break

        # Reset --input for next iteration so we go interactive
        args.input = None

    console.print("\n[dim]Done. Nothing was sent to any server.[/dim]")


if __name__ == "__main__":
    main()
