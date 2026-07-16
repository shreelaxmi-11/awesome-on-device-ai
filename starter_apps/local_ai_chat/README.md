# 💬 Local AI Chat

A private, streaming chatbot that runs entirely on your machine. No API key, no cloud, no data leaving your device.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

A clean terminal chatbot powered by any MLX model. Streams tokens in real time, keeps conversation history in memory, and accepts a custom system prompt. Zero dependencies beyond `mlx-lm` and `rich`.

```
You: What's the difference between precision and recall?
Assistant: Precision is the fraction of your positive predictions that are actually positive.
           Recall is the fraction of actual positives that your model found...

You: Give me a concrete example with numbers.
Assistant: Say you have 100 emails, 20 are spam...

You: /clear
History cleared.
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/starter_apps/local_ai_chat
pip install -r requirements.txt
python chat.py
```

First run downloads the model (~1.7 GB). Subsequent runs start in seconds.

---

## Usage

```bash
# Default model (Llama 3.2 3B, fast and capable)
python chat.py

# Use a larger model for more complex questions
python chat.py --model mlx-community/Mistral-7B-Instruct-v0.3-4bit

# Set a custom system prompt
python chat.py --system "You are a senior software engineer who gives concise, opinionated answers."

# Coding assistant persona
python chat.py --model mlx-community/Phi-3.5-mini-instruct-4bit \
               --system "You are an expert Python developer. Write clean, idiomatic code."
```

**In-chat commands:**
- `/clear` — wipe conversation history, start fresh
- `/system` — show the current system prompt
- `exit` — quit

---

## Supported Models

| Model | Size | Speed (M3 Pro) | Best for |
|-------|------|----------------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s | Default — everyday tasks |
| `mlx-community/Phi-3.5-mini-instruct-4bit` | 2.0 GB | 51 tok/s | Coding and reasoning |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s | Better reasoning |
| `mlx-community/Llama-3-8B-Instruct-4bit` | 4.9 GB | 28 tok/s | Best quality |
| `mlx-community/Qwen3-4B-Instruct-4bit` | 2.3 GB | 45 tok/s | Multilingual |

Any instruction-tuned model from [mlx-community](https://huggingface.co/mlx-community) works.

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

- **No API key** — the LLM runs entirely via MLX on your chip
- **No network** — after the initial one-time model download, zero internet required
- **No logs** — conversation history is in-memory only; nothing is written to disk

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
