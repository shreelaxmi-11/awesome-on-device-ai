# 📄 Chat with PDF (Local)

Load any PDF and ask questions about it in plain English. Works offline. No API key. Your document never leaves your machine.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Drop any PDF — a contract, research paper, medical report, or financial statement — and ask questions about it. The local LLM answers using only what's in your document.

```
You: What is the termination notice period in this contract?
Assistant: Section 14.2 states the termination notice period is 30 days for
           either party. Written notice must be delivered via certified mail...

You: Are there any unusual liability clauses?
Assistant: Clause 18 limits liability to fees paid in the prior 3 months,
           which is below the industry standard of 6-12 months...

You: Summarize the payment terms.
Assistant: Payment is due net-30 from invoice date. Late payments accrue
           interest at 1.5% per month. The client may withhold payment only
           for disputed invoices, with written notice required within 5 days...
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/starter_apps/local_pdf_chat
pip install -r requirements.txt
python chat.py --pdf your_document.pdf
```

First run downloads the model (~1.7 GB). Subsequent runs are instant.

---

## Usage

```bash
# Chat with any PDF
python chat.py --pdf document.pdf

# Use a stronger model for complex documents
python chat.py --pdf contract.pdf --model mlx-community/Mistral-7B-Instruct-v0.3-4bit

# Retrieve more context per question
python chat.py --pdf report.pdf --top-k 6
```

---

## How it works

```
PDF → pypdf text extraction
    → word-level chunking (400 words, 50-word overlap)
    → TF-IDF index in memory (no vector DB, no embedding model)
    → per query: cosine similarity retrieval of top-k chunks
    → relevant chunks injected into LLM context
    → MLX streams the answer token by token
```

No vector database. No embedding model. Pure NumPy TF-IDF retrieval — fast, accurate, zero extra dependencies beyond pypdf and mlx-lm.

---

## Supported Models

| Model | Size | Speed (M3 Pro) | Best for |
|-------|------|----------------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s | Default — fast, accurate |
| `mlx-community/Phi-3.5-mini-instruct-4bit` | 2.0 GB | 51 tok/s | Technical documents |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s | Long, complex documents |
| `mlx-community/Llama-3-8B-Instruct-4bit` | 4.9 GB | 28 tok/s | Best quality |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

No API key required. No network requests after the initial model download. Your document is indexed in memory and never transmitted anywhere. Ideal for contracts, medical records, financial statements, and legal filings.

---

## Full Implementation

The complete source code and documentation lives in [starter_apps/local_pdf_chat](../../starter_apps/local_pdf_chat/).

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
