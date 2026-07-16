# 🎯 LoRA Fine-tuning on Personal Data

Fine-tune any MLX-compatible LLM on your own writing using LoRA. Creates a lightweight adapter that captures your style. Training stays entirely on your machine — your data never leaves your device.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Three-step pipeline: prepare your data → train a LoRA adapter → chat with the fine-tuned model. After training, the model writes in your style.

```
$ python train.py --prepare --input my_emails.txt
✓ Converted 847 examples → train.jsonl, valid.jsonl

$ python train.py --train --model mlx-community/Llama-3.2-3B-Instruct-4bit
  Iteration 1: loss = 2.843
  Iteration 50: loss = 1.912
  Iteration 100: loss = 1.421
  ...
  Iteration 500: loss = 0.814
✓ Adapter saved to ./lora_adapters/

$ python train.py --chat
Base model: "The meeting is scheduled for Tuesday at 2pm."
Your model: "Hey — just looping back on this. We're on for Tues @ 2, lmk if
             anything changes on your end. Should be quick, 30 min max."
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/finetuning/lora_on_personal_data
pip install -r requirements.txt

# Step 1: Convert your writing to training data
python train.py --prepare --input your_emails_or_notes.txt

# Step 2: Fine-tune with LoRA (100 iterations ~5 min on M3 Pro)
python train.py --train --model mlx-community/Llama-3.2-3B-Instruct-4bit

# Step 3: Chat with your fine-tuned model
python train.py --chat
```

---

## What Data to Use

Any text that represents your writing: emails, Slack exports, blog posts, notes, essays. The more the better — aim for at least 50–100 paragraphs of your actual writing.

```bash
# Your email archive (export from Gmail as mbox, then extract text)
python train.py --prepare --input my_emails.txt

# Blog posts or notes
python train.py --prepare --input ~/Documents/my_writing/ --recursive

# Multiple files
python train.py --prepare --input file1.txt file2.md file3.txt
```

---

## Training Options

```bash
# Quick training run (100 iterations, ~5 min on M3 Pro)
python train.py --train --iters 100

# Full training (500 iterations, ~20 min on M3 Pro, better results)
python train.py --train --iters 500

# Fine-tune a 7B model (requires 16 GB+ unified memory)
python train.py --train \
  --model mlx-community/Mistral-7B-Instruct-v0.3-4bit \
  --iters 300
```

---

## How it works

```
Your writing (text files)
    → chunked into prompt-completion pairs
    → saved as JSONL (train.jsonl + valid.jsonl)
    → mlx_lm.lora: fine-tunes only adapter weights (~1-2% of parameters)
    → adapter saved as .npz file (~50 MB) — base model unchanged
    → chat: base model + adapter loaded together for inference
```

LoRA (Low-Rank Adaptation) modifies only a small set of weight matrices. The adapter is tiny (~50 MB) and the base model is never altered — you can combine any adapter with any compatible base model.

---

## Supported Models

| Model | Size | Training memory | Training time (500 iters) |
|-------|------|----------------|--------------------------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | ~6 GB | ~20 min (M3 Pro) |
| `mlx-community/Phi-3.5-mini-instruct-4bit` | 2.0 GB | ~7 GB | ~22 min (M3 Pro) |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | ~12 GB | ~45 min (M3 Pro) |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+ · mlx-lm >= 0.31.0
- 16 GB unified memory recommended for 7B models

---

## Privacy

Your training data never leaves your machine. No cloud GPU, no data upload, no telemetry. Fine-tuning runs entirely on your own Apple Silicon.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
