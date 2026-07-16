# 🔬 Private Research Assistant

Drop a folder of papers, docs, or notes. Ask questions across all of them. Local multi-document RAG — no API key, no cloud, your research stays private.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/local_rag/private_research_assistant
pip install -r requirements.txt

# Chat with a folder of PDFs and markdown files
python research.py --folder ~/papers/

# Ask a single question
python research.py --folder ~/docs --question "What are the main findings?"

# Specific file types only
python research.py --folder ~/research --extensions pdf,md
```

---

## Supported File Types

PDF · Markdown · TXT · RST

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
