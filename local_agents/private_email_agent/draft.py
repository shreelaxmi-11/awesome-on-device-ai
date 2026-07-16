#!/usr/bin/env python3
"""
Private Email Drafting Agent — Awesome On-Device AI
Paste bullet points or a situation description — get a professional email draft.
Multiple tones, follow-up support, reply drafting. No API key. No cloud.

Usage:
    python draft.py                           # interactive mode
    python draft.py --tone formal             # formal email
    python draft.py --type followup           # follow-up email
    python draft.py --type reply --context "original email text here"
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
MAX_TOKENS    = 600

TONES = {
    "professional": "professional and polished — clear, respectful, and direct",
    "friendly":     "warm and friendly — approachable but still professional",
    "formal":       "formal — precise, structured, suitable for executives or official correspondence",
    "assertive":    "assertive and confident — clear about needs, no hedging",
    "concise":      "very brief and direct — 3-5 sentences maximum",
}

EMAIL_TYPES = {
    "new":      "draft a new email from scratch",
    "followup": "draft a follow-up to a previous conversation",
    "reply":    "draft a reply to an incoming email",
    "decline":  "politely decline a request or invitation",
    "request":  "make a clear, compelling request",
    "intro":    "write a professional introduction or outreach email",
}


def get_context(args) -> tuple[str, str]:
    """Get the bullet points / situation from user."""
    email_type = EMAIL_TYPES.get(args.type, EMAIL_TYPES["new"])
    tone_desc  = TONES.get(args.tone, TONES["professional"])

    console.print(f"\n[bold]📧 Email type:[/bold] {args.type.title()} · [bold]Tone:[/bold] {args.tone.title()}")

    if args.type == "reply" and args.context:
        original = args.context
    elif args.type in {"reply", "followup"}:
        console.print("[dim]Paste the original email or context you're responding to (Enter twice when done):[/dim]\n")
        lines = []
        blank = 0
        while True:
            try:
                line = input()
            except (KeyboardInterrupt, EOFError):
                break
            if line == "":
                blank += 1
                if blank >= 2:
                    break
                lines.append(line)
            else:
                blank = 0
                lines.append(line)
        original = "\n".join(lines).strip()
    else:
        original = ""

    console.print("\n[dim]Enter your bullet points or a description of what you want to say (Enter twice when done):[/dim]\n")
    lines = []
    blank = 0
    while True:
        try:
            line = input()
        except (KeyboardInterrupt, EOFError):
            break
        if line == "":
            blank += 1
            if blank >= 2:
                break
            lines.append(line)
        else:
            blank = 0
            lines.append(line)

    bullets = "\n".join(lines).strip()
    return bullets, original


def draft_email(model, tokenizer, bullets: str, original: str,
                email_type: str, tone: str, recipient: str) -> str:
    tone_desc = TONES.get(tone, TONES["professional"])

    if email_type in {"reply", "followup"} and original:
        context_section = f"\nORIGINAL EMAIL / CONTEXT:\n{original}\n"
    else:
        context_section = ""

    recipient_line = f"Recipient: {recipient}\n" if recipient else ""

    system = (
        "You are a professional email writer. "
        "When given bullet points or a situation description, you draft a polished email. "
        "Write the full email including subject line. "
        "Match the requested tone exactly. "
        "Output only the email — no explanation, no commentary."
    )

    user = (
        f"Write a {tone_desc} {email_type} email.\n"
        f"{recipient_line}"
        f"{context_section}"
        f"\nKey points / what to convey:\n{bullets}\n\n"
        "Write the complete email with subject line and body. Output only the email."
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": user},
    ]

    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        prompt = f"SYSTEM: {system}\nUSER: {user}\nASSISTANT:"

    console.rule("[bold]📧 Draft[/bold]")
    console.print()

    result = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
        token = chunk.text if hasattr(chunk, "text") else chunk
        print(token, end="", flush=True)
        result += token
    print("\n")
    return result.strip()


def main():
    parser = argparse.ArgumentParser(description="Local email drafting agent.")
    parser.add_argument("--model",     default=DEFAULT_MODEL)
    parser.add_argument("--tone",      default="professional", choices=list(TONES.keys()))
    parser.add_argument("--type",      default="new", choices=list(EMAIL_TYPES.keys()),
                        dest="type", help="Email type: new, followup, reply, decline, request, intro")
    parser.add_argument("--context",   help="Original email text (for reply/followup)")
    parser.add_argument("--recipient", help="Recipient name/role for context")
    parser.add_argument("--output",    help="Save draft to this file")
    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold cyan]📧 Private Email Drafting Agent[/bold cyan]\n"
        "[dim]Runtime:[/dim] MLX (Apple Silicon) · No internet · No API key\n"
        "[dim]Your email content stays on your machine[/dim]",
        border_style="cyan"
    ))

    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    while True:
        bullets, original = get_context(args)

        if not bullets:
            console.print("[yellow]No input provided.[/yellow]")
            break

        draft = draft_email(
            model, tokenizer, bullets, original,
            args.type, args.tone,
            args.recipient or ""
        )

        if args.output:
            Path(args.output).write_text(draft)
            console.print(f"[green]✓[/green] Saved to [bold]{args.output}[/bold]")

        again = Prompt.ask("\n[dim]Draft another? ([bold]y[/bold]/n)[/dim]", default="n").strip().lower()
        if again != "y":
            break
        args.context = None

    console.print("[dim]Nothing was sent to any server.[/dim]")


if __name__ == "__main__":
    main()
