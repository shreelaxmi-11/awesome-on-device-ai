# 🌍 LiteRT-LM Desktop Python

Google's LiteRT-LM running via Python on macOS. The same code runs on Linux, Windows, and Android — cross-platform local AI without rewriting anything.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![LiteRT-LM](https://img.shields.io/badge/Runtime-LiteRT--LM-blue?style=flat-square)](https://developers.google.com/edge/litert-lm)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-black?style=flat-square)](#)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

A streaming chat app powered by LiteRT-LM — Google's cross-platform inference runtime. Unlike MLX (Apple Silicon only), this runs on any platform with a GPU.

```
$ python chat.py --model-path qwen3-4b.litertlm --backend gpu

🌍 LiteRT-LM Desktop Chat
Backend: GPU · Platform: Cross-platform (macOS · Linux · Windows · Android)

Loading model (GPU)...
✓ Model loaded

You: Explain the difference between on-device AI and cloud AI.
Assistant: On-device AI runs the model directly on your hardware — your laptop,
           phone, or edge device — without sending data to a server. The key
           advantages are latency (no network round-trip), privacy (data never
           leaves the device), and offline capability...

You: How does LiteRT-LM compare to MLX?
Assistant: LiteRT-LM and MLX are both on-device runtimes, but they solve
           different problems. MLX is optimized specifically for Apple Silicon —
           it achieves ~45 tok/s on M3 Pro by exploiting the chip's unified
           memory architecture. LiteRT-LM trades that peak performance for
           portability: the same model and Python code runs on macOS, Linux,
           Windows, and Android...
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/cross_platform/litert_lm_desktop
pip install -r requirements.txt

# Download a model from HuggingFace (litert-community)
# Then run:
python chat.py --model-path /path/to/model.litertlm
```

Download `.litertlm` models from [litert-community on HuggingFace](https://huggingface.co/litert-community).

---

## Usage

```bash
# GPU backend (default, recommended)
python chat.py --model-path qwen3-4b.litertlm

# CPU backend (slower, works on any machine)
python chat.py --model-path qwen3-4b.litertlm --backend cpu
```

---

## Supported Models

| Model | Size | Format |
|-------|------|--------|
| Gemma 4B | ~2.5 GB | `.litertlm` |
| Qwen3-4B-Instruct-2507 | ~2.87 GB | `.litertlm` |
| Gemma 7B | ~4.5 GB | `.litertlm` |

---

## How it works

```
.litertlm model file
    → LiteRT-LM Engine loaded with GPU or CPU backend
    → conversation object created (maintains context)
    → user message sent via async streaming API
    → chunks streamed to terminal as they arrive
    → conversation persists for multi-turn dialogue
```

---

## Why LiteRT-LM vs MLX?

| | MLX | LiteRT-LM |
|-|-----|-----------|
| Platforms | macOS (Apple Silicon only) | macOS, Linux, Windows, Android |
| Gen speed (M3 Pro, 4B model) | 44.6 tok/s | 2.8 tok/s |
| Same Python code cross-platform | ✗ | ✓ |
| Official Google support | — | ✓ |

Use MLX when peak speed matters. Use LiteRT-LM when cross-platform compatibility matters. See [MLX vs LiteRT-LM benchmark](../../benchmarks/mlx_vs_litert_lm/) for full numbers.

---

## Requirements

- Python 3.9+
- Works on macOS, Linux, or Windows (not Apple Silicon specific)
- GPU recommended (CUDA on Linux/Windows, Metal on macOS)

---

## Privacy

No API key required. The model runs locally after the initial download. No data leaves your machine.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
