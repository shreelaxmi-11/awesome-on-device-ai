# 📋 Local Contract Analyzer

Upload any contract PDF — get a plain-English breakdown of key terms, obligations, and red flags. Runs entirely on your machine. No API key, no uploads, no lawyer fees for the first pass.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

> **Not legal advice.** This tool helps you understand contracts — consult a qualified attorney for decisions that matter.

---

## What it does

Load a contract PDF and choose your analysis mode: full analysis, plain-English summary, risk scan, or Q&A chat. The local LLM reads your contract and answers without sending it anywhere.

```
📋 Full Analysis

1. Contract Type & Parties
   Service Agreement between Acme Corp (Client) and Freelancer LLC (Provider).
   Effective January 1, 2025.

2. Key Terms
   • Scope: Web development services as defined in Exhibit A
   • Fee: $12,000/month, invoiced on the 1st, due net-30
   • Duration: 12 months, auto-renews unless 60 days notice given

3. Red Flags ⚠️
   • Clause 8.3: IP assignment is extremely broad — ALL work product,
     including pre-existing tools, becomes Client's property. This is unusual.
   • Clause 12.1: Liability cap is $5,000 (less than one month's fee).
     Provider bears unlimited risk above this for any error.

4. Questions to Ask Counsel
   • Does clause 8.3 actually apply to your pre-existing code libraries?
   • Is the non-compete in clause 15 enforceable in your jurisdiction?
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/privacy_apps/local_contract_analyzer
pip install -r requirements.txt

# Full analysis
python analyze.py --pdf contract.pdf

# Plain-English summary
python analyze.py --pdf nda.pdf --mode summary

# Risk scan only
python analyze.py --pdf employment.pdf --mode risks

# Ask specific questions
python analyze.py --pdf agreement.pdf --mode chat
```

---

## Analysis Modes

| Mode | What it does |
|------|-------------|
| `full` | Complete analysis: type, parties, terms, obligations, liability, red flags |
| `summary` | 5-7 bullet plain-English summary of what the contract says |
| `risks` | Focused scan for risky, unusual, or one-sided clauses |
| `chat` | Q&A: ask specific questions about the contract |

---

## Supported Model

Works with any instruction-tuned MLX model. A 7B model gives noticeably better legal reasoning for complex contracts:

```bash
python analyze.py --pdf contract.pdf \
  --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory (16 GB recommended for 7B models)
- Text-based PDF (not scanned/image)

---

## Privacy

Your contract is never uploaded anywhere. The LLM runs locally — critical for contracts containing confidential terms, trade secrets, compensation details, or other sensitive information.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
