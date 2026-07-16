#!/usr/bin/env python3
"""
Voice Notes Summarizer — Awesome On-Device AI
Transcribe and summarize voice notes locally using Whisper + MLX.
No audio ever leaves your machine.

Usage:
    # Transcribe + summarize an audio file
    python summarize.py --audio note.m4a

    # Record live, then transcribe + summarize
    python summarize.py --record --duration 120

    # Just transcribe, skip summarization
    python summarize.py --audio note.m4a --transcribe-only
"""

import argparse
import sys
import time
import tempfile
from pathlib import Path
from datetime import datetime

import numpy as np
import mlx_whisper
from mlx_lm import load, stream_generate
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich import print as rprint

console = Console()

# ── Defaults ───────────────────────────────────────────────────────────────────
WHISPER_MODEL = "mlx-community/whisper-small-mlx"   # ~315 MB, fast and accurate
LLM_MODEL     = "mlx-community/Llama-3.2-3B-Instruct-4bit"
SAMPLE_RATE   = 16000   # Whisper expects 16 kHz
MAX_TOKENS    = 400


# ── Recording ──────────────────────────────────────────────────────────────────

def record_audio(duration: int) -> np.ndarray:
    """Record microphone audio for `duration` seconds. Returns float32 array."""
    import sounddevice as sd

    console.print(f"\n[bold red]● Recording[/bold red] — speak now ({duration}s) · Press Ctrl+C to stop early\n")

    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )

    try:
        for i in range(duration):
            time.sleep(1)
            remaining = duration - i - 1
            if remaining > 0:
                console.print(f"  [dim]{remaining}s remaining...[/dim]", end="\r")
    except KeyboardInterrupt:
        console.print("\n[yellow]Recording stopped early.[/yellow]")

    sd.wait()
    console.print("[green]✓[/green] Recording complete\n")
    return audio.flatten()


def save_audio(audio: np.ndarray, path: str):
    import soundfile as sf
    sf.write(path, audio, SAMPLE_RATE)


# ── Transcription ──────────────────────────────────────────────────────────────

def transcribe(audio_path: str) -> str:
    """Transcribe audio using mlx-whisper."""
    with console.status("[cyan]Transcribing with Whisper (local)...[/cyan]"):
        result = mlx_whisper.transcribe(
            audio_path,
            path_or_hf_repo=WHISPER_MODEL,
            verbose=False
        )
    text = result.get("text", "").strip()
    return text


# ── Summarization ──────────────────────────────────────────────────────────────

SUMMARY_PROMPT_TEMPLATE = """You are a precise note-taking assistant. Summarize the following voice note transcript.

Structure your summary as:
**Main Topic:** one sentence describing what this note is about
**Key Points:** 3-5 bullet points of the most important information
**Action Items:** any tasks, follow-ups, or decisions mentioned (write "None" if there are none)

Keep it concise. Use the speaker's own terminology where possible.

TRANSCRIPT:
{transcript}

SUMMARY:"""


def summarize(transcript: str, model, tokenizer) -> str:
    prompt_text = SUMMARY_PROMPT_TEMPLATE.format(transcript=transcript)

    messages = [
        {"role": "system", "content": "You are a concise, accurate note-taking assistant."},
        {"role": "user",   "content": prompt_text}
    ]

    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        prompt = f"USER: {prompt_text}\nASSISTANT:"

    response = ""
    for token in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
        print(token, end="", flush=True)
        response += token
    print()

    return response.strip()


# ── Output ─────────────────────────────────────────────────────────────────────

def save_output(audio_path: str, transcript: str, summary: str):
    """Save transcript and summary to a markdown file alongside the audio."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    stem = Path(audio_path).stem
    out_path = Path(audio_path).parent / f"{stem}_note_{timestamp}.md"

    content = f"""# Voice Note — {datetime.now().strftime("%B %d, %Y %H:%M")}

## Summary

{summary}

---

## Full Transcript

{transcript}

---
*Transcribed locally with Whisper · Summarized locally with Llama 3.2 · No data left this device*
"""

    out_path.write_text(content)
    return str(out_path)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Transcribe and summarize voice notes locally.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--audio",  help="Path to an audio file (mp3, m4a, wav, flac)")
    group.add_argument("--record", action="store_true", help="Record from microphone")

    parser.add_argument("--duration",        type=int, default=120,
                        help="Recording duration in seconds (default: 120)")
    parser.add_argument("--transcribe-only", action="store_true",
                        help="Only transcribe, skip summarization")
    parser.add_argument("--whisper-model",   default=WHISPER_MODEL,
                        help="Whisper model repo")
    parser.add_argument("--llm-model",       default=LLM_MODEL,
                        help="LLM model repo for summarization")
    parser.add_argument("--save",            action="store_true",
                        help="Save transcript and summary to a markdown file")
    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold cyan]🎙️ Voice Notes Summarizer[/bold cyan]\n"
        "[dim]Runtime:[/dim] Whisper + MLX · No internet · No API key · Your audio stays local",
        border_style="cyan"
    ))

    # ── Step 1: Get audio ──
    audio_path = args.audio

    if args.record:
        audio_data = record_audio(args.duration)
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        save_audio(audio_data, tmp.name)
        audio_path = tmp.name
        console.print(f"[dim]Saved recording to {tmp.name}[/dim]\n")
    else:
        if not Path(audio_path).exists():
            console.print(f"[red]File not found: {audio_path}[/red]")
            sys.exit(1)
        console.print(f"[dim]Audio file: {audio_path}[/dim]\n")

    # ── Step 2: Transcribe ──
    console.rule("[bold]Transcript[/bold]")
    transcript = transcribe(audio_path)

    if not transcript:
        console.print("[red]Whisper returned an empty transcript. Check your audio file.[/red]")
        sys.exit(1)

    console.print(f"\n{transcript}\n")
    console.print(f"[dim]({len(transcript.split())} words)[/dim]\n")

    if args.transcribe_only:
        if args.save:
            out = save_output(audio_path, transcript, "")
            console.print(f"[green]✓[/green] Saved to {out}")
        return

    # ── Step 3: Load LLM + summarize ──
    console.rule("[bold]Summary[/bold]")

    with console.status(f"[cyan]Loading {args.llm_model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.llm_model)
    console.print("[green]✓[/green] Model loaded\n")

    summary = summarize(transcript, model, tokenizer)

    # ── Step 4: Save ──
    if args.save:
        out_path = save_output(audio_path, transcript, summary)
        console.print(f"\n[green]✓[/green] Saved to [bold]{out_path}[/bold]")

    console.print("\n[dim]Done. Nothing was sent to any server.[/dim]")


if __name__ == "__main__":
    main()
