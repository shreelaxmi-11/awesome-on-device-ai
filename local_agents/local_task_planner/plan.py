#!/usr/bin/env python3
"""
Local Task Planner — Awesome On-Device AI
Describe a goal — local LLM breaks it into tasks, estimates effort,
identifies dependencies, and outputs a structured action plan.
No API key. No cloud. Your plans stay private.

Usage:
    python plan.py "Launch a product beta in 6 weeks"
    python plan.py --interactive
    python plan.py --goal "Write a research paper" --output plan.md
"""

import argparse
import sys
from pathlib import Path

from mlx_lm import load, stream_generate
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
MAX_TOKENS    = 1000

PLAN_SYSTEM = (
    "You are an expert project manager and strategic planner. "
    "When given a goal, you break it down into a clear, actionable plan. "
    "Be specific, realistic, and practical. "
    "Include time estimates where possible. "
    "Structure your output clearly with sections."
)

PLAN_PROMPT_TEMPLATE = (
    "Create a detailed action plan for this goal:\n\n"
    "**Goal:** {goal}\n"
    "{context_section}\n"
    "Structure your plan as:\n\n"
    "## Overview\n"
    "1-2 sentences on the approach and key success criteria.\n\n"
    "## Phases\n"
    "Break the goal into 3-5 logical phases, each with:\n"
    "- Phase name and estimated duration\n"
    "- 3-5 concrete tasks\n"
    "- Key output/deliverable\n\n"
    "## Risks & Mitigations\n"
    "Top 2-3 risks and how to handle them.\n\n"
    "## Definition of Done\n"
    "How you know the goal is complete.\n"
)


def generate_plan(model, tokenizer, goal: str, context: str = "") -> str:
    context_section = f"\n**Context:** {context}" if context else ""
    user_content = PLAN_PROMPT_TEMPLATE.format(
        goal=goal,
        context_section=context_section
    )

    messages = [
        {"role": "system", "content": PLAN_SYSTEM},
        {"role": "user",   "content": user_content},
    ]

    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        prompt = f"SYSTEM: {PLAN_SYSTEM}\nUSER: {user_content}\nASSISTANT:"

    console.rule("[bold]📋 Action Plan[/bold]")
    console.print()

    result = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
        token = chunk.text if hasattr(chunk, "text") else chunk
        print(token, end="", flush=True)
        result += token
    print("\n")
    return result.strip()


def main():
    parser = argparse.ArgumentParser(description="Local AI task planner.")
    parser.add_argument("goal",         nargs="?", help="Your goal")
    parser.add_argument("--goal",       dest="goal_flag", help="Your goal (alternative)")
    parser.add_argument("--context",    help="Additional context about constraints, team, timeline")
    parser.add_argument("--model",      default=DEFAULT_MODEL)
    parser.add_argument("--output",     help="Save plan to this file")
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()

    goal = args.goal or args.goal_flag
    if args.interactive or not goal:
        goal = Prompt.ask("[bold cyan]What is your goal?[/bold cyan]").strip()
    if not goal:
        console.print("[red]Please provide a goal.[/red]")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold cyan]📋 Local Task Planner[/bold cyan]\n"
        f"[dim]Goal:[/dim] {goal[:80]}{'...' if len(goal) > 80 else ''}\n"
        "[dim]Runtime:[/dim] MLX · No internet · No API key",
        border_style="cyan"
    ))

    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    plan = generate_plan(model, tokenizer, goal, args.context or "")

    if args.output:
        content = f"# Action Plan: {goal}\n\n{plan}\n"
        Path(args.output).write_text(content)
        console.print(f"[green]✓[/green] Saved to [bold]{args.output}[/bold]")

    console.print("[dim]Nothing was sent to any server.[/dim]")


if __name__ == "__main__":
    main()
