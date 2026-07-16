# 🔬 MLX vs LiteRT-LM Runtime Comparison

Same model. Same hardware. Two runtimes. Real measured numbers.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![Hardware](https://img.shields.io/badge/Hardware-M3%20Pro%2018GB-black?style=flat-square)](#)
[![Model](https://img.shields.io/badge/Model-Qwen3--4B--Instruct--2507-orange?style=flat-square)](#)

---

## Setup

- **Hardware:** Apple MacBook Pro M3 Pro, 18GB unified memory
- **Model:** `Qwen3-4B-Instruct-2507` (same weights, different format per runtime)
  - MLX format: `mlx-community/Qwen3-4B-Instruct-2507` (INT4, ~2.3 GB)
  - LiteRT-LM format: `litert-community/Qwen3-4B-Instruct-2507` (mixed INT4, ~2.87 GB)
- **Prompt:** ~256 tokens (long AI history explanation prompt, repeated 2×)
- **Output:** 128 tokens per trial
- **Trials:** 5 runs, first run used as warmup

---

## Results

| Metric | MLX (GPU) | LiteRT-LM (GPU) | LiteRT-LM (CPU) |
|--------|-----------|-----------------|-----------------|
| **TTFT** | ~16ms | **541ms** | 8,214ms |
| **Prefill (tok/s)** | **615.28** | 548.2 | — |
| **Generation (tok/s)** | **44.62** | 2.81 | 0.96 |
| **Memory (GB)** | 3.30 | **2.87** | 2.87 |
| **Decode speedup** | **16× faster** | baseline | 0.34× |

---

## Key Findings

**MLX is 16× faster on decode (generation).** This is the dominant cost for interactive use.

**Prefill is nearly equal.** MLX at 615 tok/s vs LiteRT-LM at 548 tok/s — only 12% difference. Prefill cost is amortized over the prompt length, so this matters less for typical chat use.

**LiteRT-LM uses slightly less memory** (2.87 GB vs 3.30 GB). The mixed INT4 quantization is marginally more memory-efficient than MLX's INT4 for this model.

**LiteRT-LM GPU+MTP failed.** The `Qwen3-4B-Instruct-2507` model was not converted with Multi-Token Prediction support, so the MTP acceleration path was unavailable. This is a model-level constraint, not a runtime bug.

---

## Why the gap on decode?

MLX is optimized specifically for Apple Silicon's unified memory architecture. Its Metal kernels for matrix-vector multiplication (the bottleneck during autoregressive decoding) are hand-tuned for the M-series chip's memory bandwidth and tile structure.

LiteRT-LM uses a generic GPU abstraction layer designed to work across GPU architectures (Adreno, Mali, Apple GPU, Vulkan). This cross-platform portability comes at the cost of per-chip optimization — especially on decode, where Apple Silicon's bandwidth advantage can't be fully exploited through a generic kernel.

**Where LiteRT-LM wins:**
- Cross-platform deployment (Android, Chrome, Pixel Watch, Chromebook) — no equivalent for MLX
- Consistent inference behavior across Apple/Android/Chrome targets
- Official Google support and roadmap

**Where MLX wins:**
- Apple Silicon only (M1–M4)
- Interactive applications where latency matters
- Decode speed by a wide margin

---

## Reproduce

```bash
# MLX benchmark
pip install mlx-lm
python mlx_benchmark.py

# LiteRT-LM benchmark (requires downloading the .litertlm model file first)
pip install litert-lm-api
python litert_benchmark.py
```

---

## Part of [Awesome On-Device AI](../../README.md)
