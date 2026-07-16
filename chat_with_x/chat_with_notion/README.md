# 📓 Chat with Notion Export (Local)

Export your Notion workspace and chat with your own notes privately. No API key, no cloud — your knowledge base stays on your machine.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Export your Notion workspace as markdown, load the folder, and ask questions across all your notes. The local LLM answers from your actual content and tells you which page it came from.

```
$ python chat.py --folder ~/Downloads/Notion_Export/

📂 Loading Notion export...
  ✓ Product Roadmap Q3.md
  ✓ Meeting Notes — April.md
  ✓ Engineering Decisions Log.md
  ✓ Competitive Analysis.md
  ... 43 pages loaded, 1,204 chunks indexed.

You: What did we decide about the notification system?

Based on your Engineering Decisions Log, the team decided on March 12 to use
push notifications only for transactional events (not marketing), and to build
the notification service as a separate microservice to allow independent scaling.
The reasoning was to avoid coupling notification logic to the core payment flow.

Source: Engineering Decisions Log.md

You: What's on the Q3 roadmap?

Your Q3 roadmap (Product Roadmap Q3.md) has three themes:
  1. Onboarding redesign — reduce time-to-first-value from 8 min to 3 min
  2. Enterprise features — audit logs, SSO, admin dashboard
  3. Mobile app — iOS first, Android in Q4
  ...
```

---

## How to Export from Notion

1. Open Notion → **Settings & Members** (gear icon)
2. Click **Export all workspace content**
3. Format: **Markdown & CSV** · Include subpages: **Yes**
4. Download the `.zip` file and unzip it

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/chat_with_x/chat_with_notion
pip install -r requirements.txt

python chat.py --folder ~/Downloads/Notion_Export/
```

---

## Usage

```bash
# Chat with your full Notion export
python chat.py --folder ~/Downloads/Notion_Export/

# Ask a single question and exit
python chat.py --folder ~/notion --question "What are my current OKRs?"

# Use a stronger model
python chat.py --folder ~/notion \
  --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

---

## How it works

```
Notion export folder
    → load all .md files recursively
    → use filename as page title for source attribution
    → word-level chunking (400 words, 50-word overlap) across all pages
    → TF-IDF index built in memory
    → per question: cosine similarity retrieval of top-k chunks
    → chunks + page titles injected into LLM context
    → MLX streams the answer with source page attribution
```

---

## Supported Models

| Model | Size | Speed (M3 Pro) | Best for |
|-------|------|----------------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s | Default — most workspaces |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s | Large, complex workspaces |
| `mlx-community/Llama-3-8B-Instruct-4bit` | 4.9 GB | 28 tok/s | Best synthesis quality |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

Your Notion notes never leave your machine. This matters especially for workspaces with product strategy, customer information, financial projections, or internal team discussions.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
