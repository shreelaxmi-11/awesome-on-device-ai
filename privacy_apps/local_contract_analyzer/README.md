# 📋 Local Contract Analyzer

Upload any contract PDF — get a plain-English breakdown of key terms, obligations, and red flags. Runs entirely on your machine. No API key, no uploads, no lawyer fees for the first pass.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

> **Not legal advice.** This tool helps you understand contracts — consult a qualified attorney before signing anything important.

---

## What it does

Load a contract PDF and choose your analysis mode: full analysis, plain-English summary, risk scan, or Q&A chat. The local LLM reads your contract and answers without sending it anywhere.

```
$ python analyze.py --pdf employment_offer.pdf

📋 Full Analysis

1. Contract Type & Parties
   Employment Agreement between TechCorp Inc. (Employer) and Jane Doe (Employee).
   Effective March 1, 2025.

2. Key Terms
   • Compensation: $145,000 base + 0.25% equity (4-year vest, 1-year cliff)
   • Role: Senior Product Manager, reporting to VP of Product
   • Start date: March 1, 2025 · Location: San Francisco or remote

3. Red Flags ⚠️
   • Clause 8.3: IP assignment is extremely broad — ALL inventions created
     during employment, even on personal time, become company property.
     This is common but worth negotiating if you do side projects.
   • Clause 15: Non-compete covers a 12-month window and entire "software
     industry." Enforceability varies by state — in California this is
     likely unenforceable, but consult counsel.

4. Questions to Ask
   • Can clause 8.3 be narrowed to inventions directly related to company work?
   • Does the equity include acceleration on acquisition or termination?
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

# Ask specific questions about the contract
python analyze.py --pdf agreement.pdf --mode chat
```

---

## Analysis Modes

| Mode | What it does |
|------|-------------|
| `full` | Complete analysis: type, parties, terms, obligations, liability, red flags |
| `summary` | 5-7 bullet plain-English summary of what the contract says |
| `risks` | Focused scan for risky, unusual, or one-sided clauses |
| `chat` | Q&A: ask specific questions about any part of the contract |

---

## How it works

```
Contract PDF
    → pypdf text extraction
    → word-level chunking (400 words, 50-word overlap)
    → TF-IDF index built in memory
    → for full/summary/risks: top relevant chunks fed to LLM
    → for chat: per-question retrieval of most relevant clauses
    → MLX streams the analysis or answer
```

No vector database. No embedding model. Pure NumPy TF-IDF retrieval — zero extra dependencies beyond pypdf and mlx-lm.

---

## Supported Models

| Model | Size | Speed (M3 Pro) | Best for |
|-------|------|----------------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s | Quick summaries |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s | Better legal reasoning |
| `mlx-community/Llama-3-8B-Instruct-4bit` | 4.9 GB | 28 tok/s | Complex contracts |

A 7B model gives noticeably better analysis for dense legal language.

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory (16 GB recommended for 7B models)
- Text-based PDF (not a scanned image)

---

## Privacy

Your contract is never uploaded anywhere. The LLM runs locally — critical for contracts containing confidential terms, trade secrets, compensation details, or proprietary information.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
