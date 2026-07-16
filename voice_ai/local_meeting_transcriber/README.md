# 📝 Local Meeting Transcriber

Transcribe any recorded meeting entirely on-device. Outputs a timestamped transcript, meeting summary, and extracted action items. No audio leaves your machine.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![Whisper](https://img.shields.io/badge/Whisper-mlx--whisper-orange?style=flat-square)](https://github.com/ml-explore/mlx-examples)
[![MLX](https://img.shields.io/badge/LLM-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Drop any meeting recording — Zoom export, QuickTime recording, voice memo — and get back a structured document:

```
## Summary
The team aligned on a Q3 roadmap shift: deprioritize the analytics dashboard
and focus engineering on the core onboarding flow. Key blocker is API rate
limits from the payments provider. Next step is to escalate with their
enterprise team this week.

## Action Items
1. Shreelaxmi — draft updated PRD with revised Q3 scope by Friday
2. Rohan — email payments provider for enterprise rate limit increase (this week)
3. Priya — share Figma prototype in Slack by EOD Thursday

## Full Transcript
[00:00] Welcome everyone, let's get started with the Q3 planning review...
[00:42] So the main issue is that the analytics dashboard is taking up...
[02:15] Right, so my proposal is to push that to Q4 and refocus...
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/voice_ai/local_meeting_transcriber
pip install -r requirements.txt

# Transcribe a meeting
python transcribe.py --audio meeting.m4a

# Save to markdown file
python transcribe.py --audio call.mp3 --save

# Transcript only, no LLM summary
python transcribe.py --audio standup.wav --no-summary

# Plain format (no timestamps)
python transcribe.py --audio meeting.m4a --format plain --save
```

---

## How it works

```
Meeting audio file
    → mlx-whisper (Whisper running on Apple Neural Engine)
    → timestamped segments
    → local LLM pass 1: meeting summary
    → local LLM pass 2: action item extraction
    → combined markdown output
```

Both Whisper and the LLM run locally via MLX. No audio or transcript is ever sent to a server.

---

## Supported Formats

MP3 · M4A · WAV · FLAC · OGG · OPUS · MP4 (audio) — anything ffmpeg can read.

---

## Models

| Component | Default | Notes |
|-----------|---------|-------|
| Transcription | `mlx-community/whisper-small-mlx` | 315 MB · fast, accurate |
| Summary + AIs | `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB |

For long or noisy recordings, try `whisper-medium-mlx` for better transcription.

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

Your meeting audio never leaves your machine. No cloud transcription service (Otter.ai, Fireflies, etc.) sees your conversations. Especially important for client calls, internal strategy discussions, or any confidential meeting.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
