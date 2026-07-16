#!/usr/bin/env python3
"""
Private Voice Journal — Awesome On-Device AI
Speak your thoughts — Whisper transcribes locally, a local LLM reflects
and tracks patterns across entries. Your most private thoughts stay private.

Usage:
    python journal.py                        # record today's entry
    python journal.py --audio note.m4a       # use an existing audio file
    python journal.py --read                 # read past entries
    python journal.py --weekly               # weekly pattern analysis
    python journal.py --journal-dir ~/journal # custom journal location
"""

import argparse
import json
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import mlx_whisper
from mlx_lm import load, stream_generate
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table

console = Console()

DEFAULT_WHISPER     = "mlx-community/whisper-small-mlx"
DEFAULT_LLM         = "mlx-community/Llama-3.2-3B-Instruct-4bit"
DEFAULT_JOURNAL_DIR = Path.home() / ".private_voice_journal"
SAMPLE_RATE         = 16000
MAX_TOKENS          = 600


# ── Audio recording ────────────────────────────────────────────────────────────

def record_audio(duration: int) -> np.ndarray:
    import sounddevice as sd
    console.print(f"\n[bold red]● Recording[/bold red] — speak freely ({duration}s) · Ctrl+C to stop early\n")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
    try:
        for i in range(duration):
            time.sleep(1)
            remaining = duration - i - 1
            if remaining > 0:
                console.print(f"  [dim]{remaining}s remaining...[/dim]", end="\r")
    except KeyboardInterrupt:
        console.print("\n[yellow]Recording stopped.[/yellow]")
    sd.wait()
    console.print("[green]✓[/green] Recording complete\n")
    return audio.flatten()


def save_wav(audio: np.ndarray, path: str):
    import soundfile as sf
    sf.write(path, audio, SAMPLE_RATE)


# ── Transcription ──────────────────────────────────────────────────────────────

def transcribe(audio_path: str) -> str:
    with console.status("[cyan]Transcribing with Whisper (local)...[/cyan]"):
        result = mlx_whisper.transcribe(audio_path, path_or_hf_repo=DEFAULT_WHISPER, verbose=False)
    return result.get("text", "").strip()


# ── LLM reflection ─────────────────────────────────────────────────────────────

def generate_reflection(transcript: str, model, tokenizer, date_str: str) -> str:
    system = (
        "You are a compassionate, non-judgmental journaling companion. "
        "When someone shares their thoughts, you offer gentle reflection — "
        "noticing themes, emotions, and patterns without lecturing. "
        "Be warm, brief, and insightful. Do not give unsolicited advice."
    )
    user = (
        f"Journal entry from {date_str}:\n\n{transcript}\n\n"
        "Write a brief, empathetic reflection on this entry. "
        "Notice 1-2 key themes or emotions. Ask one open-ended question "
        "to prompt deeper reflection. Keep it to 3-4 sentences."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": user},
    ]
    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        prompt = f"SYSTEM: {system}\nUSER: {user}\nASSISTANT:"

    result = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=200):
        token = chunk.text if hasattr(chunk, "text") else chunk
        print(token, end="", flush=True)
        result += token
    print()
    return result.strip()


def generate_weekly_analysis(entries: list[dict], model, tokenizer) -> str:
    entries_text = ""
    for e in entries[-7:]:
        entries_text += f"**{e['date']}:** {e['transcript'][:500]}\n\n"

    system = (
        "You are a journaling analyst who helps people understand patterns in their thoughts. "
        "Be insightful, warm, and specific. Reference actual content from the entries."
    )
    user = (
        f"Here are journal entries from the past week:\n\n{entries_text}\n"
        "Write a weekly reflection covering:\n"
        "1. Recurring themes or topics (with examples)\n"
        "2. Emotional patterns — what feelings came up most?\n"
        "3. Things that seem to matter most to this person right now\n"
        "4. One gentle question or observation to carry into next week\n\n"
        "Be specific and warm. 150-200 words."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": user},
    ]
    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        prompt = f"SYSTEM: {system}\nUSER: {user}\nASSISTANT:"

    result = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
        token = chunk.text if hasattr(chunk, "text") else chunk
        print(token, end="", flush=True)
        result += token
    print()
    return result.strip()


# ── Journal storage ────────────────────────────────────────────────────────────

def load_journal(journal_dir: Path) -> list[dict]:
    index_path = journal_dir / "index.json"
    if index_path.exists():
        return json.loads(index_path.read_text())
    return []


def save_entry(journal_dir: Path, entries: list[dict], transcript: str,
               reflection: str, date_str: str):
    journal_dir.mkdir(parents=True, exist_ok=True)

    # Save full entry as markdown
    filename  = f"{date_str.replace(' ', '_').replace(':', '-')}.md"
    entry_path = journal_dir / filename
    content = (
        f"# Journal Entry — {date_str}\n\n"
        f"## My Thoughts\n\n{transcript}\n\n"
        f"---\n\n## Reflection\n\n{reflection}\n\n"
        f"---\n*Private · Transcribed locally · Never uploaded*\n"
    )
    entry_path.write_text(content)

    # Update index
    entries.append({
        "date":       date_str,
        "file":       filename,
        "transcript": transcript,
        "words":      len(transcript.split()),
    })
    (journal_dir / "index.json").write_text(json.dumps(entries, indent=2))
    return str(entry_path)


def show_entries(entries: list[dict]):
    if not entries:
        console.print("[dim]No journal entries yet. Run without --read to record your first entry.[/dim]")
        return
    table = Table(title="Journal Entries", show_header=True, header_style="bold cyan")
    table.add_column("Date", width=20)
    table.add_column("Words", justify="right", width=8)
    table.add_column("Preview")
    for e in reversed(entries[-20:]):
        preview = e["transcript"][:60].replace("\n", " ")
        if len(e["transcript"]) > 60:
            preview += "..."
        table.add_row(e["date"], str(e["words"]), preview)
    console.print(table)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Private voice journal powered by Whisper + MLX.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--audio",   help="Use an existing audio file instead of recording")
    group.add_argument("--read",    action="store_true", help="Show past journal entries")
    group.add_argument("--weekly",  action="store_true", help="Generate weekly pattern analysis")

    parser.add_argument("--duration",     type=int, default=180, help="Recording duration in seconds")
    parser.add_argument("--journal-dir",  default=str(DEFAULT_JOURNAL_DIR), help="Journal storage directory")
    parser.add_argument("--llm-model",    default=DEFAULT_LLM)
    parser.add_argument("--no-reflect",   action="store_true", help="Skip LLM reflection")
    args = parser.parse_args()

    journal_dir = Path(args.journal_dir)
    entries     = load_journal(journal_dir)

    console.print(Panel.fit(
        "[bold cyan]📔 Private Voice Journal[/bold cyan]\n"
        "[dim]Runtime:[/dim] Whisper + MLX · No internet · No API key\n"
        f"[dim]Journal:[/dim] {journal_dir} · {len(entries)} entries",
        border_style="cyan"
    ))

    # -- Read mode
    if args.read:
        show_entries(entries)
        return

    # -- Weekly analysis mode
    if args.weekly:
        if len(entries) < 2:
            console.print("[yellow]Need at least 2 entries for a weekly analysis.[/yellow]")
            return
        with console.status(f"[cyan]Loading {args.llm_model.split('/')[-1]}...[/cyan]"):
            model, tokenizer = load(args.llm_model)
        console.rule("[bold]Weekly Reflection[/bold]")
        console.print()
        generate_weekly_analysis(entries, model, tokenizer)
        return

    # -- Record or load audio
    if args.audio:
        audio_path = args.audio
        if not Path(audio_path).exists():
            console.print(f"[red]File not found: {audio_path}[/red]")
            sys.exit(1)
    else:
        audio_data = record_audio(args.duration)
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        save_wav(audio_data, tmp.name)
        audio_path = tmp.name

    # -- Transcribe
    transcript = transcribe(audio_path)
    if not transcript:
        console.print("[red]Empty transcript. Try speaking more clearly or use a different audio file.[/red]")
        sys.exit(1)

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    console.rule("[bold]Your Entry[/bold]")
    console.print(f"\n{transcript}\n")
    console.print(f"[dim]({len(transcript.split())} words)[/dim]\n")

    # -- Reflect
    reflection = ""
    if not args.no_reflect:
        with console.status(f"[cyan]Loading {args.llm_model.split('/')[-1]}...[/cyan]"):
            model, tokenizer = load(args.llm_model)

        console.rule("[bold]Reflection[/bold]")
        console.print()
        reflection = generate_reflection(transcript, model, tokenizer, date_str)
        console.print()

    # -- Save
    out_path = save_entry(journal_dir, entries, transcript, reflection, date_str)
    console.print(f"[green]✓[/green] Entry saved to [bold]{out_path}[/bold]")
    console.print("[dim]Nothing was sent to any server.[/dim]")


if __name__ == "__main__":
    main()
