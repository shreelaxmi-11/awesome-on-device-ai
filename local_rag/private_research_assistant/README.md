# 🔬 Private Research Assistant

Drop a folder of papers, docs, or notes — ask questions across all of them. Local multi-document RAG with source attribution. No API key, no cloud, your research stays private.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Point it at a folder of PDFs, markdown files, and text files. Ask questions across all of them. The answer cites which document the information came from.

```
$ python research.py --folder ~/papers/

📂 Loading 8 documents...
  ✓ attention_is_all_you_need.pdf     (312 chunks)
  ✓ scaling_laws.pdf                  (198 chunks)
  ✓ llama2_paper.pdf                  (441 chunks)
  ✓ on_device_llm_survey.md           (87 chunks)
  ...
  Total: 1,847 chunks indexed.

You: What do the papers say about optimal model size for on-device use?

The on-device LLM survey (on_device_llm_survey.md) recommends models under 7B
parameters for consumer hardware, noting that 3–4B models achieve a practical
quality-latency trade-off on Apple Silicon. The Llama 2 paper (llama2_paper.pdf,
Section 4) found that 7B models with 4-bit quantization fit in 6 GB of memory,
while maintaining 85% of the 13B model's benchmark performance...

Sources: on_device_llm_survey.md · llama2_paper.pdf (p. 8)
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/local_rag/private_research_assistant
pip install -r requirements.txt

# Chat with a folder of documents
python research.py --folder ~/papers/
```

---

## Usage

```bash
# Interactive chat across all documents in a folder
python research.py --folder ~/papers/

# Ask a single question and exit
python research.py --folder ~/docs --question "What are the main findings?"

# Only load specific file types
python research.py --folder ~/research --extensions pdf,md

# Retrieve more context per question
python research.py --folder ~/papers --top-k 8

# Use a stronger model for complex synthesis
python research.py --folder ~/papers \
  --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

---

## Supported File Types

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text-based (not scanned) |
| Markdown | `.md` | Full text |
| Plain text | `.txt` | Full text |
| RST | `.rst` | Full text |

---

## How it works

```
Folder of documents
    → load each file (pypdf for PDFs, direct read for MD/TXT/RST)
    → word-level chunking with filename + position metadata
    → single TF-IDF index across all documents
    → per question: cosine similarity retrieval of top-k chunks (any doc)
    → chunks + source filenames injected into LLM context
    → MLX streams the answer with source citations
```

---

## Supported Models

| Model | Size | Speed (M3 Pro) | Best for |
|-------|------|----------------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s | Default — fast Q&A |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s | Better cross-doc synthesis |
| `mlx-community/Llama-3-8B-Instruct-4bit` | 4.9 GB | 28 tok/s | Best quality |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

Your documents are indexed locally and never transmitted. Designed for sensitive research: unpublished papers, proprietary analysis, confidential reports, internal strategy docs.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
