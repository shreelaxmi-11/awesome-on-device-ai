# 🔬 Local Research Agent

Give it a topic — it breaks it into sub-questions, answers each one, then synthesizes a structured report. A multi-step reasoning agent that runs entirely on-device.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

A three-step agent loop:

1. **Decompose** — breaks the research topic into focused sub-questions
2. **Research** — answers each sub-question with a full local LLM pass
3. **Synthesize** — writes a coherent final report integrating all findings

```
Topic: "Trade-offs between on-device AI and cloud AI"

Sub-question 1: What are the latency characteristics of each approach?
→ On-device AI eliminates network round-trips, giving sub-100ms latency...

Sub-question 2: How do they compare on privacy and data residency?
→ On-device AI keeps all data local by definition. Cloud AI requires...

...

📄 Final Research Report

Executive Summary:
On-device and cloud AI represent fundamentally different architectural choices
with distinct trade-offs across latency, privacy, cost, and capability...
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
python research.py --topic "on-device AI for healthcare" --depth deep

# Save the report
python research.py "edge computing vs cloud computing" --output report.md

# Interactive mode
python research.py --interactive
```

---

## Depth Modes

| Mode | Sub-questions | Best for |
|------|--------------|---------|
| `quick` | 3 | Fast overview, ~5 minutes |
| `deep` | 6 | Comprehensive analysis, ~10 minutes |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum
- A 7B model gives noticeably richer research output

```bash
python research.py "your topic" --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

---

## Privacy

All research runs locally. Use for sensitive competitive analysis, internal strategy topics, or any research you wouldn't want sent to a cloud AI service.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
