# 🎙️ Voice Notes Summarizer

Transcribe and summarize voice notes locally using Whisper + MLX. No audio ever leaves your machine.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![Whisper](https://img.shields.io/badge/Whisper-mlx--whisper-orange?style=flat-square)](https://github.com/ml-explore/mlx-examples)
[![MLX](https://img.shields.io/badge/LLM-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Drop any audio file or record live from your microphone. Whisper transcribes it on-device, a local LLM summarizes it into structured notes. The output:

```
Main Topic: Onboarding redesign discussion covering timeline and owner assignments

Key Points:
• New user flow reduces steps from 7 to 3 — targeting 40% drop in abandonment
• Engineering estimate: 3 weeks for backend changes, 1 week for frontend
• A/B test launching week of June 10th with 20% traffic split
• Success metric: D7 retention, not just activation rate

Action Items:
• Shreelaxmi to draft PRD by Friday
• Rohan to sync with data team on metric instrumentation
• Schedule design review for Thursday 3pm
```

Nothing is sent to a server. Your audio file, your words, your notes.

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/voice_ai/voice_notes_summarizer
pip install -r requirements.txt

# Summarize an existing audio file
python summarize.py --audio meeting.m4a

# Record live for 2 minutes, then summarize
python summarize.py --record --duration 120

# Just transcribe (skip summarization)
python summarize.py --audio note.wav --transcribe-only

# Save output to a markdown file
python summarize.py --audio note.m4a --save
```

---

## How it works

```
Audio file / mic recording
    → Whisper (mlx-whisper, runs on Apple Neural Engine)
    → raw transcript
    → structured prompt → local LLM (MLX, Llama 3.2 3B)
    → Main Topic + Key Points + Action Items
    → optional: saved as .md file alongside audio
```

Both models run entirely on-device via MLX. No external APIs. No network requests after the initial one-time model download.

---

## Supported Audio Formats

MP3 · M4A · WAV · FLAC · OGG · OPUS — anything ffmpeg can read.

---

## Models Used

| Component | Default model | Size | Notes |
|-----------|--------------|------|-------|
| Transcription | `mlx-community/whisper-small-mlx` | ~315 MB | Fast, accurate for most accents |
| Summarization | `mlx-community/Llama-3.2-3B-Instruct-4bit` | ~1.7 GB | Concise, structured output |

For longer or complex recordings, try `whisper-medium-mlx` for transcription. For richer summaries, use `Mistral-7B-Instruct-v0.3-4bit`.

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum
- For live recording: microphone access permission

---

## Privacy

- **No API key** — both Whisper and the LLM run locally via MLX
- **No uploads** — your audio is processed in-memory and never transmitted
- **No cloud storage** — output saved locally only if you pass `--save`

Use it for meetings, personal notes, medical information, legal discussions — anything you wouldn't want uploaded to a cloud transcription service.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
