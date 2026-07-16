# 🌍 LiteRT-LM Desktop Python

Google's LiteRT-LM running via Python on macOS. Cross-platform inference with Gemma and Qwen models, GPU-accelerated.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![LiteRT-LM](https://img.shields.io/badge/Runtime-LiteRT--LM-blue?style=flat-square)](https://developers.google.com/edge/litert-lm)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-black?style=flat-square)](#)

---

## Why LiteRT-LM?

MLX is Apple Silicon only. LiteRT-LM runs the same model on macOS, Linux, Windows, and Android — the same Python code works across all platforms.

Trade-off: MLX is 16× faster on decode (see [MLX vs LiteRT-LM Benchmark](../../benchmarks/mlx_vs_litert_lm/)). Use LiteRT-LM when cross-platform compatibility matters more than peak speed.

---

## Install

```bash
pip install litert-lm-api
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/cross_platform/litert_lm_desktop
pip install -r requirements.txt
python chat.py --model-path /path/to/model.litertlm
```

Download models from [litert-community on HuggingFace](https://huggingface.co/litert-community).

---

## Supported Models

| Model | Size | Format |
|-------|------|--------|
| Gemma 4B | ~2.5 GB | `.litertlm` |
| Qwen3-4B-Instruct-2507 | ~2.87 GB | `.litertlm` |
| Gemma 7B | ~4.5 GB | `.litertlm` |

---

## Benchmark Results (M3 Pro 18GB)

See [MLX vs LiteRT-LM Benchmark](../../benchmarks/mlx_vs_litert_lm/) for detailed numbers. Summary:
- GPU TTFT: 541ms
- GPU Gen: 2.81 tok/s
- Memory: 2.87 GB

---

## Part of [Awesome On-Device AI](../../README.md)
