# 📔 Private Voice Journal

Speak your thoughts. Whisper transcribes locally. A local LLM reflects gently and tracks patterns across entries. Your most private thoughts stay on your machine.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![Whisper](https://img.shields.io/badge/Whisper-mlx--whisper-orange?style=flat-square)](https://github.com/ml-explore/mlx-examples)
[![MLX](https://img.shields.io/badge/LLM-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Record yourself speaking — about your day, a worry, something you're grateful for, anything. Whisper transcribes it on-device. A local LLM offers a gentle reflection and, after several entries, identifies patterns across your week.

```
📔 Your Entry (3 min recording)

I've been feeling overwhelmed with the roadmap planning. There are so many
competing priorities and I'm not sure which battles to pick. I keep thinking
about that conversation with my manager last week — it's stuck in my head...

---

Reflection

There's a real tension here between wanting to do everything well and
recognizing your own bandwidth. The word "battles" is interesting — it suggests
this feels like conflict, not just prioritization. What would it feel like to
choose one thing that truly matters to you this week, and let the rest wait?
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/voice_ai/private_voice_journal
pip install -r requirements.txt

# Record and journal (3 minutes by default)
python journal.py

# Use an existing audio file
python journal.py --audio voice_memo.m4a

# Read past entries
python journal.py --read

# Weekly pattern analysis (needs 2+ entries)
python journal.py --weekly
```

---

## How it works

```
Microphone / audio file
    → mlx-whisper (on-device transcription)
    → transcript saved locally
    → local LLM: gentle reflection on today's entry
    → entry saved as markdown in ~/.private_voice_journal/
    → (optional) weekly: local LLM reads last 7 entries, finds patterns
```

---

## Journal Storage

Entries saved to `~/.private_voice_journal/` by default:
- One markdown file per entry (timestamped)
- `index.json` for quick lookups and weekly analysis

```bash
# Use a different location
python journal.py --journal-dir ~/Documents/journal

# Just transcribe, skip LLM reflection
python journal.py --no-reflect
```

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum
- Microphone access (for recording mode)

---

## Privacy

Journaling is one of the most private activities there is. This app was designed with that in mind:
- No audio is uploaded anywhere
- No transcript leaves your machine
- No service has access to your entries
- You can read, edit, or delete your journal files directly

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
