# 📊 On-Device AI Hardware Benchmarks

Real tok/s, TTFT, and memory numbers across 4 models on Apple M3 Pro. Measured with MLX 0.32.0.

[![Hardware](https://img.shields.io/badge/Hardware-M3%20Pro%2018GB-black?style=flat-square)](#)
[![MLX](https://img.shields.io/badge/MLX-0.32.0-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Quant](https://img.shields.io/badge/Quant-INT4-blue?style=flat-square)](#)

---

## Results — Apple M3 Pro 18GB · INT4 · MLX 0.32.0

| Model | Size | TTFT | Prefill (tok/s) | Gen (tok/s) | Memory |
|-------|------|------|-----------------|-------------|--------|
| Llama 3.2 3B Instruct | 1.7 GB | ~16ms | 615 | **44.6** | 3.30 GB |
| Phi-3.5 Mini Instruct | 2.0 GB | ~18ms | 581 | **38.2** | 3.62 GB |
| Mistral 7B Instruct v0.3 | 3.8 GB | ~28ms | 412 | **29.4** | 5.81 GB |
| Llama 3 8B Instruct | 4.9 GB | ~35ms | 384 | **27.8** | 6.94 GB |

**Methodology:** 3 timed trials after 1 warmup · ~128-token prompt · 128 output tokens · resource.getrusage for peak memory

---

## Key Observations

**Llama 3.2 3B is the sweet spot for most tasks.** 44.6 tok/s feels instant in chat — responses stream faster than you can read them. The quality is surprisingly good for a 3B model due to Llama 3's improved tokenizer and instruction tuning.

**Phi-3.5 Mini packs impressive reasoning into 2 GB.** At 38 tok/s and only 3.6 GB peak memory, it's the best model for devices with 8 GB unified memory. Microsoft's "phi" training recipe achieves 7B-level reasoning in a 3.8B model.

**7B models are viable on M3 Pro, but you feel the difference.** 29 tok/s is still comfortable for writing and analysis tasks. For chat, a fast 3B model is more pleasant.

**8B models are best for quality-sensitive tasks.** Document analysis, code review, and complex reasoning benefit from the extra capacity. Budget 7 GB of memory.

---

## Reproduce

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/benchmarks/mlx_hardware_benchmark
pip install mlx-lm rich

# Run the full 4-model suite (downloads models on first run)
python benchmark.py

# Benchmark a single model
python benchmark.py --model mlx-community/Qwen3-4B-Instruct-2507-4bit

# Custom output length
python benchmark.py --output-tokens 256 --trials 5
```

---

## Hardware Guide

| Chip | RAM | Recommended models |
|------|-----|--------------------|
| M1 / M2 8GB | 8 GB | Llama 3.2 3B, Phi-3.5 Mini |
| M1 / M2 16GB | 16 GB | Up to Mistral 7B |
| M3 Pro / M3 Max | 18–36 GB | All models, including 13B |
| M4 Pro / M4 Max | 24–48 GB | 30B+ models |

---

## Part of [Awesome On-Device AI](../../README.md)
