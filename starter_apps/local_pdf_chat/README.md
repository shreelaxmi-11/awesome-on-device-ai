# 📄 Local PDF Chat

Chat with any PDF entirely on-device. No API key. No internet. Your document never leaves your machine.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Load any PDF — a contract, research paper, medical report, financial statement — and ask questions about it in plain English. A local LLM answers using only what's in the document. Nothing is sent to any server.

```
You: What is the termination notice period in this contract?
Assistant: Section 14.2 states the termination notice period is 30 days for either party...

You: Are there any unusual liability clauses?
Assistant: Clause 18 limits liability to the fees paid in the prior 3 months, which is below...
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/starter_apps/local_pdf_chat
pip install -r requirements.txt
python chat.py --pdf your_document.pdf
```

That's it. First run downloads the model (~1.7 GB). Subsequent runs are instant.

---

## Usage

**Basic:**
```bash
python chat.py --pdf document.pdf
```

**With a different model:**
```bash
python chat.py --pdf document.pdf --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

**Retrieve more context per query:**
```bash
python chat.py --pdf document.pdf --top-k 6
```

---

## How it works

```
PDF → text extraction (pypdf)
    → word-level chunking (400 words, 50-word overlap)
    → TF-IDF index (built in-memory, no vector DB needed)
    → per query: cosine similarity retrieval of top-k chunks
    → relevant chunks injected into LLM system prompt
    → MLX streams the response token by token
```

No vector database. No embedding model. No external API. The entire retrieval pipeline is pure NumPy — zero extra dependencies beyond `pypdf` and `mlx-lm`.

---

## Supported Models

Any instruction-tuned model from [mlx-community](https://huggingface.co/mlx-community) works. Recommended:

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
- 8 GB unified memory minimum (16 GB recommended for 7B+ models)

---

## Privacy

- **No API key required** — runs entirely on MLX
- **No network requests** — the model runs locally after the initial download
- **No telemetry** — your document content is never transmitted anywhere
- **No persistence** — conversation history is in-memory only; nothing is written to disk

This makes it suitable for sensitive documents: contracts, medical records, financial statements, legal filings.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
