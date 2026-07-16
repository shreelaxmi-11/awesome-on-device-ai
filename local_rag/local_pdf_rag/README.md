# 📚 Local PDF RAG

Full RAG pipeline for PDFs — chunking, TF-IDF retrieval, local LLM answer. Single question, batch, or interactive chat mode. No API key, no vector database, no cloud.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

A focused RAG template for a single PDF. Ask one question, run a batch of questions from a file, or open an interactive chat. Answers are grounded in the actual document content.

```
$ python rag.py --pdf research_paper.pdf \
    --question "What methodology did the authors use?"

📄 Indexing research_paper.pdf... 47 chunks indexed.

Question: What methodology did the authors use?

The authors used a mixed-methods approach combining quantitative benchmarks
with qualitative user studies. For the quantitative component, they measured
inference latency, memory usage, and throughput across five hardware targets
(Section 3.2). The user study recruited 24 participants and used a Likert
scale to assess perceived response quality across three LLM backends
(Section 3.4)...

Sources: chunks 12, 13, 31 (pages 4–5, 10)
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/local_rag/local_pdf_rag
pip install -r requirements.txt
python rag.py --pdf your_document.pdf
```

---

## Usage

```bash
# Interactive chat with a PDF
python rag.py --pdf document.pdf

# Single question, get answer and exit
python rag.py --pdf paper.pdf --question "What are the main findings?"

# Batch mode — run all questions from a file
python rag.py --pdf report.pdf --questions questions.txt --output answers.txt

# Use a stronger model
python rag.py --pdf document.pdf --model mlx-community/Mistral-7B-Instruct-v0.3-4bit

# Retrieve more context per question
python rag.py --pdf document.pdf --top-k 6
```

---

## How it works

```
PDF
    → pypdf text extraction
    → word-level chunking (400 words, 50-word overlap)
    → TF-IDF index built in memory (no vector DB needed)
    → per question: cosine similarity retrieval of top-k chunks
    → relevant chunks + question injected into LLM context
    → MLX streams the grounded answer
```

No embedding model required. Pure NumPy TF-IDF — zero extra dependencies beyond pypdf and mlx-lm.

---

## Supported Models

| Model | Size | Speed (M3 Pro) | Best for |
|-------|------|----------------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s | Default — fast and accurate |
| `mlx-community/Phi-3.5-mini-instruct-4bit` | 2.0 GB | 51 tok/s | Technical documents |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s | Dense or complex PDFs |
| `mlx-community/Llama-3-8B-Instruct-4bit` | 4.9 GB | 28 tok/s | Best answer quality |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum
- Text-based PDF (not a scanned image)

---

## Privacy

Your PDF is indexed locally and never transmitted. The LLM runs locally via MLX — no API key, no network requests after the initial model download.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
