# 🎯 LoRA Fine-tuning on Personal Data

Fine-tune any MLX-compatible LLM on your own writing using LoRA. Creates a lightweight adapter. Training stays entirely on your machine — your data never leaves your device.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/finetuning/lora_on_personal_data
pip install -r requirements.txt

# Step 1: Prepare your writing as training data
python train.py --prepare --input your_emails_or_notes.txt

# Step 2: Fine-tune with LoRA (100 iterations ~5 min on M3 Pro)
python train.py --train --model mlx-community/Llama-3.2-3B-Instruct-4bit

# Step 3: Test the result
python train.py --chat
```

---

## What data to use

Any text that represents your writing style: emails, blog posts, notes, Slack messages, essays. Aim for at least 50-100 paragraphs. The more, the better.

---

## How it works

MLX LoRA training (`mlx_lm.lora`) fine-tunes only a small set of adapter weights (~1-2% of total parameters). The adapter is saved as a small `.npz` file (~50 MB). The base model is unchanged.

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+ · mlx-lm >= 0.31.0
- 16 GB unified memory recommended for 7B models

---

## Part of [Awesome On-Device AI](../../README.md)
