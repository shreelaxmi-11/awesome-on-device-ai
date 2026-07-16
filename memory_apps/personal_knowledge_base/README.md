# 📚 Personal Knowledge Base

Add notes, ideas, and files over time. Build a private local knowledge base you can query with natural language. Stored as plain files on disk. No cloud, no API key.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

A personal second brain that lives on your machine. Add notes, passages, and files. Search with natural language. Chat with everything you've ever added.

```
$ python kb.py add "The key to good prompts is specificity — include the
  format you want, a negative example, and the audience you're writing for"

✓ Added entry #47 (27 words)

$ python kb.py chat

You: What do I know about writing prompts?

Based on your notes, you've captured several prompting principles:

  From entry #47: Specificity is key — include desired format, a negative
  example, and target audience.

  From entry #12 (Feb 2): Chain-of-thought prompting improves reasoning on
  multi-step problems. Prefixing with "Let's think step by step" can add
  10-15% accuracy on benchmarks.

  From your note "Prompting Cheatsheet.md" (added Mar 5): You also noted
  that Claude responds better to positive framing ("do X") than negative
  ("don't do Y").

You: What's the difference between RAG and fine-tuning?

Based on entry #33: RAG is better for factual, up-to-date, or document-specific
knowledge. Fine-tuning is better for style adaptation and task-specific behavior
where the knowledge is stable...
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/memory_apps/personal_knowledge_base
pip install -r requirements.txt

# Add your first note
python kb.py add "Your insight or note here"

# Chat with everything you've added
python kb.py chat
```

KB stored at `~/.personal_knowledge_base/`.

---

## Usage

```bash
# Add a quick note
python kb.py add "The insight or thing you want to remember"

# Add from a file (markdown, text, PDF)
python kb.py add --file my_notes.md --tag "prompting"

# Add interactively (multi-line paste)
python kb.py add --interactive

# Search your KB
python kb.py search "what do I know about prompting?"

# Chat with your entire KB
python kb.py chat

# List all entries
python kb.py list

# Show entries with a specific tag
python kb.py list --tag "product"
```

---

## How it works

```
Add note/file
    → stored as entry in ~/.personal_knowledge_base/
    → TF-IDF index rebuilt across all entries

Search query / chat question
    → cosine similarity retrieval of most relevant entries
    → for search: ranked list of matching entries shown
    → for chat: relevant entries + question injected into LLM context
    → MLX streams the grounded answer citing entry IDs and dates
```

---

## Supported Models

| Model | Size | Speed (M3 Pro) | Best for |
|-------|------|----------------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s | Default |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s | Better synthesis |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

Everything is stored locally in `~/.personal_knowledge_base/`. You can read, edit, back up, or delete these files at any time — they're plain markdown and JSON.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
