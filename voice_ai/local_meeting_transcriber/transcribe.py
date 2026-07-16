#!/usr/bin/env python3
"""
Local Meeting Transcriber — Awesome On-Device AI
Transcribe any recorded meeting entirely on-device using Whisper.
Outputs a timestamped transcript + extracted action items.
No audio ever leaves your machine. No API key.

Usage:
    python transcribe.py --audio meeting.m4a
    python transcribe.py --audio call.mp3 --format markdown
    python transcribe.py --audio standup.wav --speakers 3
"""

import argparse
import sys
from datetime import timedelta
from pathlib import Path

import mlx_whisper
from mlx_lm import load, stream_generate
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

console = Console()

DEFAULT_WHISPER = "mlx-community/whisper-small-mlx"
DEFAULT_LLM     = "mlx-community/Llama-3.2-3B-Instruct-4bit"
MAX_TOKENS      = 600


def transcribe_with_timestamps(audio_path: str, whisper_model: str) -> list[dict]:
    """Transcribe audio, returning segments with timestamps."""
    with console.status("[cyan]Transcribing with Whisper (local)...[/cyan]"):
        result = mlx_whisper.transcribe(
            audio_path,
            path_or_hf_repo=whisper_model,
            verbose=False,
            word_timestamps=False,
        )

    segments = result.get("segments", [])
    if not segments:
        # Fallback: no segments, just full text
        text = result.get("text", "").strip()
        if text:
            return [{"start": 0.0, "end": 0.0, "text": text}]
        console.print("[red]No transcript produced. Check your audio file.[/red]")
        sys.exit(1)

    return [
        {
            "start": s.get("start", 0.0),
            "end":   s.get("end",   0.0),
            "text":  s.get("text",  "").strip(),
        }
        for s in segments
        if s.get("text", "").strip()
    ]


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS."""
    td = timedelta(seconds=int(seconds))
    total_seconds = int(td.total_seconds())
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def build_transcript_text(segments: list[dict]) -> str:
    """Build clean transcript text (no timestamps) for LLM processing."""
    return " ".join(s["text"] for s in segments)


def extract_action_items(transcript: str, model, tokenizer) -> str:
    """Use local LLM to extract action items from the transcript."""
    system = (
        "You are a meeting assistant that extracts action items from transcripts. "
        "Be specific: include who is responsible (if mentioned) and what they need to do. "
        "If no action items are mentioned, say so."
    )
    user = (
        "Extract all action items from this meeting transcript. "
        "Format as a numbered list. Include the owner (if mentioned) and deadline (if mentioned). "
        "If there are no action items, write 'No action items identified.'\n\n"
        f"TRANSCRIPT:\n{transcript[:3000]}"  # cap at 3000 chars for context
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

    result = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
        token = chunk.text if hasattr(chunk, "text") else chunk
        print(token, end="", flush=True)
        result += token
    print()
    return result.strip()


def generate_summary(transcript: str, model, tokenizer) -> str:
    """Generate a brief meeting summary."""
    system = "You are a concise meeting summarizer."
    user = (
        "Summarize this meeting in 3-5 sentences. Cover: main topic, key decisions, "
        "and next steps.\n\n"
        f"TRANSCRIPT:\n{transcript[:3000]}"
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

    result = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=300):
        token = chunk.text if hasattr(chunk, "text") else chunk
        print(token, end="", flush=True)
        result += token
    print()
    return result.strip()


def save_output(audio_path: str, segments: list[dict], summary: str, action_items: str,
                fmt: str) -> str:
    stem     = Path(audio_path).stem
    out_path = Path(audio_path).parent / f"{stem}_transcript.md"

    duration = format_timestamp(segments[-1]["end"]) if segments else "unknown"
    word_count = sum(len(s["text"].split()) for s in segments)

    lines = [
        f"# Meeting Transcript — {stem}",
        f"",
        f"**Duration:** {duration} · **Words:** {word_count:,} · "
        f"**Segments:** {len(segments)}",
        f"",
        f"---",
        f"",
        f"## Summary",
        f"",
        summary,
        f"",
        f"---",
        f"",
        f"## Action Items",
        f"",
        action_items,
        f"",
        f"---",
        f"",
        f"## Full Transcript",
        f"",
    ]

    if fmt == "timestamped":
        for s in segments:
            ts   = format_timestamp(s["start"])
            lines.append(f"**[{ts}]** {s['text']}")
    else:
        full_text = " ".join(s["text"] for s in segments)
        lines.append(full_text)

    lines += [
        "",
        "---",
        "*Transcribed locally with Whisper · No audio was uploaded to any server*",
    ]

    out_path.write_text("\n".join(lines))
    return str(out_path)


def main():
    parser = argparse.ArgumentParser(description="Transcribe meetings locally with Whisper.")
    parser.add_argument("--audio",         required=True, help="Path to audio file")
    parser.add_argument("--whisper-model", default=DEFAULT_WHISPER, help="Whisper model repo")
    parser.add_argument("--llm-model",     default=DEFAULT_LLM, help="LLM for summary + action items")
    parser.add_argument(
        "--format",
        default="timestamped",
        choices=["timestamped", "plain"],
        help="Transcript format"
    )
    parser.add_argument("--no-summary",    action="store_true", help="Skip summary and action items")
    parser.add_argument("--save",          action="store_true", help="Save output to markdown file")
    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        console.print(f"[red]File not found: {audio_path}[/red]")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold cyan]📝 Local Meeting Transcriber[/bold cyan]\n"
        f"[dim]File:[/dim] {audio_path.name}\n"
        "[dim]Runtime:[/dim] Whisper + MLX · No internet · No API key",
        border_style="cyan"
    ))

    # Step 1: Transcribe
    segments = transcribe_with_timestamps(str(audio_path), args.whisper_model)
    duration = format_timestamp(segments[-1]["end"]) if segments and segments[-1]["end"] > 0 else "—"
    word_count = sum(len(s["text"].split()) for s in segments)
    console.print(f"[green]✓[/green] Transcribed: [bold]{word_count:,} words[/bold] · {duration} · {len(segments)} segments\n")

    # Step 2: Show transcript
    console.rule("[bold]Transcript[/bold]")
    console.print()
    for s in segments:
        if args.format == "timestamped" and s["start"] > 0:
            ts = format_timestamp(s["start"])
            console.print(f"[dim][{ts}][/dim] {s['text']}")
        else:
            console.print(s["text"])
    console.print()

    summary      = ""
    action_items = ""

    if not args.no_summary:
        # Step 3: Load LLM
        with console.status(f"[cyan]Loading {args.llm_model.split('/')[-1]}...[/cyan]"):
            model, tokenizer = load(args.llm_model)
        console.print(f"[green]✓[/green] Model loaded\n")

        full_transcript = build_transcript_text(segments)

        # Step 4: Summary
        console.rule("[bold]Meeting Summary[/bold]")
        console.print()
        summary = generate_summary(full_transcript, model, tokenizer)
        console.print()

        # Step 5: Action items
        console.rule("[bold]Action Items[/bold]")
        console.print()
        action_items = extract_action_items(full_transcript, model, tokenizer)
        console.print()

    # Step 6: Save
    if args.save:
        out = save_output(str(audio_path), segments, summary, action_items, args.format)
        console.print(f"[green]✓[/green] Saved to [bold]{out}[/bold]")

    console.print("[dim]Done. No audio was sent to any server.[/dim]")


if __name__ == "__main__":
    main()
