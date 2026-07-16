# ⚖️ Cross-Runtime Inference Comparison

Compare MLX, LiteRT-LM, and Ollama on the same hardware. Latency, memory, and quality trade-offs explained.

[![Hardware](https://img.shields.io/badge/Hardware-M3%20Pro%2018GB-black?style=flat-square)](#)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)

---

## Runtime Comparison (M3 Pro 18GB · Qwen3-4B class model)

| Runtime | TTFT | Gen (tok/s) | Memory | Platforms | API Key? |
|---------|------|-------------|--------|-----------|---------|
| **MLX** | ~16ms | **44.6** | 3.3 GB | macOS (Apple Silicon) only | No |
| **LiteRT-LM** | 541ms | 2.8 | 2.9 GB | macOS · Linux · Windows · Android | No |
| **Ollama** | ~80ms | ~35 | 3.5 GB | macOS · Linux · Windows | No |
| **llama.cpp** | ~60ms | ~38 | 3.2 GB | All platforms | No |

---

## When to use each runtime

**MLX** — Best for Apple Silicon Macs where decode speed matters. Interactive chat, real-time generation. 16× faster decode than LiteRT-LM on the same chip.

**LiteRT-LM** — Best for cross-platform or Android deployment. Same Python code runs on macOS, Linux, Windows, and Android. Google-supported and actively developed for mobile/edge.

**Ollama** — Best for quickest local setup and REST API compatibility. `ollama serve` gives you an OpenAI-compatible API endpoint locally. Easiest for integrating with existing tooling.

**llama.cpp** — Best for maximum portability and model format support. Runs on virtually any hardware including CPU-only. The GGUF ecosystem is the largest in local AI.

---

## Run the comparison

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/cross_platform/cross_runtime_comparison

# MLX
pip install mlx-lm
python compare.py --runtime mlx --model mlx-community/Qwen3-4B-Instruct-2507-4bit

# LiteRT-LM (requires .litertlm model file)
pip install litert-lm-api
python compare.py --runtime litert --model-path /path/to/model.litertlm

# Ollama (requires Ollama installed)
ollama pull qwen3:4b
python compare.py --runtime ollama --model qwen3:4b
```

---

## For PMs: The key trade-off

If you're deciding which runtime to build on:

- **User is on Apple Silicon Mac** → MLX. No contest on speed.
- **User is on Android or mixed device fleet** → LiteRT-LM. Only runtime with real Android support.
- **You want an API server** → Ollama. Drop-in replacement for OpenAI API.
- **You need CPU-only or unusual hardware** → llama.cpp.

---

## Part of [Awesome On-Device AI](../../README.md)
