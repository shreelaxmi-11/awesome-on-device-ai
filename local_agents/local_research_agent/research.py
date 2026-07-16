#!/usr/bin/env python3
"""
Local Research Agent — Awesome On-Device AI
Give it a research topic — it breaks the question into sub-questions,
answers each one using local knowledge, then synthesizes a final report.
No API key. No internet. Runs entirely on-device.

Usage:
    python research.py "What are the trade-offs between RAG and fine-tuning?"
    python research.py --topic "on-device AI vs cloud AI" --depth deep
    python research.py --interactive
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
DEPTH_CONFIG  = {
    "quick": {"sub_questions": 3, "label": "Quick (3 sub-questions)"},
    "deep":  {"sub_questions": 6, "label": "Deep (6 sub-questions)"},
}


def generate(model, tokenizer, system: str, user: str, max_tokens: int = MAX_TOKENS,
             stream: bool = True) -> str:
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

    result = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=max_tokens):
        token = chunk.text if hasattr(chunk, "text") else chunk
        if stream:
            print(token, end="", flush=True)
        result += token
    if stream:
        print()
    return result.strip()


def break_into_sub_questions(model, tokenizer, topic: str, n: int) -> list[str]:
    """Ask the LLM to generate n sub-questions for the research topic."""
    console.print(f"\n[cyan]Breaking '{topic}' into {n} sub-questions...[/cyan]")

    system = (
        "You are a research planning assistant. "
        "When given a research topic, generate focused sub-questions that together "
        "would give a comprehensive understanding of the topic. "
        "Return ONLY the questions, one per line, numbered. No extra text."
    )
    user = (
        f"Generate exactly {n} focused research sub-questions for this topic:\n\n"
        f"'{topic}'\n\n"
        f"The questions should cover different aspects and together give a complete picture. "
        f"Number them 1 through {n}."
    )

    raw = generate(model, tokenizer, system, user, max_tokens=400, stream=False)

    # Parse numbered questions
    questions = []
    for line in raw.split("\n"):
        line = line.strip()
        if line and line[0].isdigit():
            # Remove leading number and punctuation
            q = line.lstrip("0123456789.)- ").strip()
            if q:
                questions.append(q)

    # Fallback if parsing fails
    if len(questions) < 2:
        questions = [line.strip() for line in raw.split("\n") if line.strip()]

    return questions[:n]


def answer_sub_question(model, tokenizer, topic: str, question: str, idx: int) -> str:
    """Answer a single sub-question in the context of the research topic."""
    system = (
        "You are an expert researcher and analyst. "
        "Answer research questions comprehensively and accurately. "
        "Use concrete examples and evidence where relevant. "
        "Be balanced — present multiple perspectives on contested topics."
    )
    user = (
        f"Research topic: {topic}\n\n"
        f"Sub-question {idx}: {question}\n\n"
        "Provide a thorough, accurate answer to this specific sub-question."
    )

    console.rule(f"[bold cyan]Sub-question {idx}: {question}[/bold cyan]")
    console.print()
    result = generate(model, tokenizer, system, user, max_tokens=MAX_TOKENS)
    console.print()
    return result


def synthesize_report(model, tokenizer, topic: str,
                      questions: list[str], answers: list[str]) -> str:
    """Synthesize all sub-question answers into a coherent final report."""
    # Build context from Q&A pairs
    qa_text = ""
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        qa_text += f"Sub-question {i}: {q}\nAnswer: {a}\n\n"

    system = (
        "You are an expert research writer. "
        "Synthesize research findings into a clear, well-structured report. "
        "Integrate the findings coherently — do not just list Q&A pairs. "
        "Structure: Executive Summary → Key Findings → Analysis → Conclusion."
    )
    user = (
        f"Write a comprehensive research report on: '{topic}'\n\n"
        f"Based on these research findings:\n\n{qa_text}\n\n"
        "Write a well-structured report that synthesizes these findings into "
        "a coherent narrative. Include an executive summary at the start."
    )

    console.rule("[bold green]📄 Final Research Report[/bold green]")
    console.print()
    result = generate(model, tokenizer, system, user, max_tokens=1200)
    console.print()
    return result


def run_research(model, tokenizer, topic: str, depth: str, output_file: str | None):
    n = DEPTH_CONFIG[depth]["sub_questions"]

    console.print(Panel.fit(
        f"[bold]Research Topic:[/bold] {topic}\n"
        f"[dim]Depth:[/dim] {DEPTH_CONFIG[depth]['label']} · "
        f"[dim]Model:[/dim] model loaded",
        border_style="cyan"
    ))

    # Step 1: Break into sub-questions
    questions = break_into_sub_questions(model, tokenizer, topic, n)
    if not questions:
        console.print("[red]Failed to generate sub-questions.[/red]")
        return

    console.print(f"\n[green]✓[/green] Generated {len(questions)} sub-questions:\n")
    for i, q in enumerate(questions, 1):
        console.print(f"  {i}. {q}")
    console.print()

    # Step 2: Answer each sub-question
    answers = []
    for i, q in enumerate(questions, 1):
        answer = answer_sub_question(model, tokenizer, topic, q, i)
        answers.append(answer)

    # Step 3: Synthesize final report
    report = synthesize_report(model, tokenizer, topic, questions, answers)

    # Save if requested
    if output_file:
        content = f"# Research Report: {topic}\n\n{report}\n\n---\n\n## Sub-Questions\n\n"
        for i, (q, a) in enumerate(zip(questions, answers), 1):
            content += f"### {i}. {q}\n\n{a}\n\n"
        Path(output_file).write_text(content)
        console.print(f"[green]✓[/green] Saved to [bold]{output_file}[/bold]")


def main():
    parser = argparse.ArgumentParser(description="Local research agent powered by MLX.")
    parser.add_argument("topic",      nargs="?",         help="Research topic (or use --topic)")
    parser.add_argument("--topic",    dest="topic_flag", help="Research topic")
    parser.add_argument("--model",    default=DEFAULT_MODEL)
    parser.add_argument("--depth",    default="quick", choices=["quick", "deep"],
                        help="Research depth: quick (3 sub-Qs) or deep (6 sub-Qs)")
    parser.add_argument("--output",   help="Save the report to a markdown file")
    parser.add_argument("--interactive", action="store_true",
                        help="Prompt for topic interactively")
    args = parser.parse_args()

    # Resolve topic
    topic = args.topic or args.topic_flag
    if args.interactive or not topic:
        topic = Prompt.ask("[bold cyan]Research topic[/bold cyan]").strip()
    if not topic:
        console.print("[red]Please provide a research topic.[/red]")
        sys.exit(1)

    console.print(Panel.fit(
        "[bold cyan]🔬 Local Research Agent[/bold cyan]\n"
        "[dim]Runtime:[/dim] MLX (Apple Silicon) · No internet · No API key\n"
        "[dim]How it works:[/dim] Topic → sub-questions → local answers → synthesized report",
        border_style="cyan"
    ))

    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    run_research(model, tokenizer, topic, args.depth, args.output)
    console.print("[dim]Research complete. Nothing was sent to any server.[/dim]")


if __name__ == "__main__":
    main()
