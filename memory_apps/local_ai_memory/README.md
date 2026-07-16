# 🧠 Local AI Memory

A chatbot that actually remembers you across sessions. Facts, preferences, and context stored in a local JSON file. No cloud memory, no API key — everything private.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Chat with an LLM that remembers things about you between sessions. When you share information, it extracts and stores facts locally. Next time you open it, those facts are back in the system prompt.

```
Session 1:
You: I'm a PM at a fintech startup, working on a payments product.
Assistant: Great to meet you! What aspects of payments are you working on?
🧠 Remembered: User is a PM at a fintech startup working on payments.

Session 2 (next day):
You: Can you help me think through my roadmap?
Assistant: Sure! Given you're building a payments product at a fintech startup,
           let's start with the core flows — what's your biggest friction point
           right now: onboarding, transaction speed, or failure rates?
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/memory_apps/local_ai_memory
pip install -r requirements.txt
python chat.py
```

Memory is saved to `~/.local_ai_memory.json` by default.

---

## Usage

```bash
# Start chatting (memory auto-loads)
python chat.py

# See what the AI remembers about you
python chat.py --show-memory

# Clear all memory
python chat.py --clear-memory

# Use a custom memory file (for different personas/contexts)
python chat.py --memory-file ~/work_memory.json
python chat.py --memory-file ~/personal_memory.json

# Use a stronger model
python chat.py --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

**In-chat commands:**
- `/memory` — show stored facts
- `/forget` — clear all memory
- `exit` — quit

---

## How it works

```
On every turn:
  1. System prompt = base instructions + all stored facts
  2. LLM responds normally, with full context of who you are
  3. A second LLM pass extracts any new facts from the turn
  4. New facts saved to JSON, system prompt refreshed for next turn
```

Memory is a simple JSON file — you can read, edit, or delete it at any time.

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

Memory is stored locally in a JSON file on your machine. Nothing is ever sent to a cloud service. You can view and edit the memory file directly:

```bash
cat ~/.local_ai_memory.json
```

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
