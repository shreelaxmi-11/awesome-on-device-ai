# 🔨 Custom Adapter Builder

Pipeline to prepare any text dataset, run LoRA fine-tuning, and export a reusable `.npz` adapter for any MLX-compatible model — entirely on-device.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Three-step pipeline: prepare your text data → train a LoRA adapter → test with the fine-tuned model. The adapter is a small `.npz` file (~50 MB) you can reuse across sessions or share with trusted parties.

```
$ python train.py --prepare --input my_writing.txt
✓ 847 training examples → train.jsonl, valid.jsonl

$ python train.py --train --model mlx-community/Llama-3.2-3B-Instruct-4bit --iters 300
  [iter 10]  loss = 2.71
  [iter 100] loss = 1.84
  [iter 200] loss = 1.23
  [iter 300] loss = 0.91
✓ Adapter saved → ./lora_adapters/

$ python train.py --chat --compare
Base model:   "Thank you for your email. I would be happy to schedule a call."
Your model:   "Hey! Yeah let's find a time — does Thursday work? Happy to do async
               if schedules don't align."
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/finetuning/custom_adapter_builder
pip install -r requirements.txt

# Step 1: Convert your data
python train.py --prepare --input your_text.txt

# Step 2: Train LoRA adapter (100 iters ~5 min on M3 Pro)
python train.py --train

# Step 3: Test your fine-tuned model
python train.py --chat
```

The full implementation and documentation lives in [finetuning/lora_on_personal_data](../lora_on_personal_data/).

---

## What data to use

Any text that represents the style or knowledge you want to capture: emails, blog posts, notes, Slack messages, essays, clinical notes, code comments. Aim for 50–100 paragraphs minimum. More is better.

---

## How it works

```
Your text files
    → chunked into prompt-completion pairs (300-400 words each)
    → saved as train.jsonl + valid.jsonl
    → mlx_lm.lora: fine-tunes only adapter weights (~1-2% of parameters)
    → adapter saved as .npz file — base model is never modified
    → test: load base model + adapter together for inference
```

LoRA (Low-Rank Adaptation) modifies only a small set of adapter matrices rather than the full model weights. The adapter is ~50-100 MB regardless of which base model you use.

---

## Adapter Sizes

| Base Model | Adapter Size | Training Memory | Time (500 iters, M3 Pro) |
|------------|-------------|-----------------|--------------------------|
| Llama 3.2 3B | ~48 MB | ~6 GB | ~20 min |
| Phi-3.5 Mini | ~52 MB | ~7 GB | ~22 min |
| Mistral 7B | ~92 MB | ~12 GB | ~45 min |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+ · mlx-lm >= 0.31.0
- 16 GB unified memory recommended for 7B models

---

## Privacy

Your training data never leaves your machine. No cloud GPU, no data upload, no telemetry. Fine-tuning runs entirely on your Apple Silicon.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
