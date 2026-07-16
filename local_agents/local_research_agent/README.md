# 🔬 Local Research Agent

Give it a topic — it breaks it into sub-questions, answers each one, then synthesizes a structured report. A multi-step reasoning agent that runs entirely on-device.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

A three-step agent loop that turns any topic into a structured research report, using only your local LLM — no web search, no API, no cloud.

```
$ python research.py "Trade-offs between on-device AI and cloud AI"

Step 1/3 — Decomposing into sub-questions...
  1. What are the latency characteristics of each approach?
  2. How do they compare on privacy and data residency?
  3. What does each cost at scale?

Step 2/3 — Researching each sub-question...
  [1/3] On-device AI eliminates network round-trips, giving sub-100ms TTFT...
  [2/3] On-device AI keeps all data local by definition. Cloud AI requires...
  [3/3] Cloud AI has high per-token costs that scale with usage. On-device...

Step 3/3 — Synthesizing final report...

📄 Research Report: Trade-offs between on-device AI and cloud AI

Executive Summary
On-device and cloud AI represent fundamentally different architectural choices.
On-device AI excels at latency-sensitive, privacy-critical applications where
data cannot leave the device. Cloud AI offers superior capability for tasks
that require the largest models and don't have strict data residency requirements.

[Full report continues...]
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/local_agents/local_research_agent
pip install -r requirements.txt

# Research a topic
python research.py "What are the trade-offs between RAG and fine-tuning?"

# Deep research (6 sub-questions)
python research.py "on-device AI for healthcare" --depth deep

# Save the report to a file
python research.py "edge computing vs cloud computing" --output report.md

# Interactive mode — enter topic at runtime
python research.py --interactive
```

---

## Depth Modes

| Mode | Sub-questions | Approx. time | Best for |
|------|--------------|--------------|---------|
| `quick` | 3 | ~3–5 min | Fast overview of a topic |
| `deep` | 6 | ~8–12 min | Comprehensive analysis |

---

## How it works

```
Topic
    → LLM pass 1: decompose into N focused sub-questions
    → for each sub-question: full LLM pass, save answer
    → LLM pass N+1: synthesize all answers into a coherent report
    → stream to terminal + optionally save as markdown
```

This is a simple but effective agent pattern: decompose → research → synthesize. No tool use, no web access, no framework. Pure sequential LLM calls.

---

## Supported Models

| Model | Size | Speed (M3 Pro) | Best for |
|-------|------|----------------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s | Quick research |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s | Richer synthesis |
| `mlx-community/Llama-3-8B-Instruct-4bit` | 4.9 GB | 28 tok/s | Best report quality |

A 7B model gives noticeably richer synthesis. Worth the wait for deep research.

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

All research runs locally. Use for sensitive competitive analysis, internal strategy topics, or any research you wouldn't want sent to a cloud AI service.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
