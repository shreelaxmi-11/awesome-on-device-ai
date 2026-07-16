# ✍️ Local Writing Assistant

Turn bullet points, rough notes, or outlines into polished prose — locally. No API key, no cloud, five modes.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Give it bullet points or rough notes. Get back a polished draft in seconds. Five modes: general writing, professional email, blog post, formal report, and rewrite/improve.

```
Input (bullet points):
• Q2 revenue up 23% YoY
• Main driver: enterprise contracts (3 new logos)
• Churn decreased from 8% to 5.2%
• Headcount grew from 47 to 61
• Next quarter: investing in sales team, targeting 4 more enterprise logos

Output (executive summary):
Q2 delivered strong results, with revenue growing 23% year-over-year driven
primarily by enterprise expansion — we closed three new logos, bringing our
enterprise base to a new high. Equally encouraging, churn fell from 8.0% to
5.2%, reflecting improved retention across our customer base. The team grew
from 47 to 61 to support this momentum. Looking ahead to Q3, our focus turns
to further enterprise growth, with a targeted investment in our sales organization
and a goal of four additional enterprise logo wins.
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/starter_apps/local_writing_assistant
pip install -r requirements.txt
python write.py
```

---

## Usage

```bash
# Interactive mode (paste bullets, get a draft)
python write.py

# Draft a professional email
python write.py --mode email

# Write a blog post from your outline
python write.py --mode blog

# Generate a formal report
python write.py --mode report

# Rewrite and improve existing text
python write.py --mode rewrite

# Load bullets from a file
python write.py --input notes.txt --mode email

# Save the output
python write.py --mode blog --output post.md
```

---

## Modes

| Mode | What it does |
|------|-------------|
| `general` | Transforms notes into clear, well-structured prose |
| `email` | Drafts professional business emails |
| `blog` | Writes blog posts with a hook, body, and conclusion |
| `report` | Creates formal reports with section headings |
| `rewrite` | Rewrites existing text to be cleaner and more compelling |

---

## Supported Models

| Model | Size | Speed (M3 Pro) |
|-------|------|----------------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s |
| `mlx-community/Llama-3-8B-Instruct-4bit` | 4.9 GB | 28 tok/s |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

Your notes and drafts never leave your machine. The LLM runs locally via MLX — no API key, no network requests after the initial model download.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
