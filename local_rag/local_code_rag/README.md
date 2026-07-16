# 💻 Local Code RAG

Index any codebase and ask questions about it in plain English. No API key, no cloud — your source code stays on your machine.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Point it at any codebase and ask questions in plain English. Supports Python, JS, TS, Go, Rust, Java, Swift, and more.

The LLM reads relevant chunks of your code and answers questions grounded in what it actually found — with file names and line numbers.

**Example questions:**
- "Where is the authentication logic?"
- "How does the data pipeline work?"
- "What does the `process_payment` function do?"
- "Where are database queries made?"
- "Explain the caching strategy used here."

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/local_rag/local_code_rag
pip install -r requirements.txt

# Index and chat with any repo
python chat.py --repo /path/to/your/project
```

---

## Usage

```bash
# Chat with a repo
python chat.py --repo ~/my-project

# Index only specific file types
python chat.py --repo ~/my-project --extensions py,yaml,md

# Use a code-focused model (recommended)
python chat.py --repo ~/my-project --model mlx-community/Phi-3.5-mini-instruct-4bit

# Larger model for complex codebases
python chat.py --repo ~/my-project --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

---

## How it works

```
Repository
    → file scanner (skips node_modules, .git, binaries, large files)
    → word-level chunking with file path + line number metadata
    → TF-IDF index (code-aware tokenization: camelCase, snake_case, paths)
    → per query: cosine similarity retrieval of top-k chunks
    → chunks + file references injected into LLM context
    → MLX streams the answer
```

No embedding model required. The TF-IDF approach works well for code because function names and identifiers are highly distinctive keywords.

---

## Supported Languages

Python · JavaScript · TypeScript · TSX/JSX · Go · Rust · Java · C/C++ · Swift · Kotlin · Ruby · Shell · YAML · JSON · TOML · Markdown

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

Your source code is indexed locally and never transmitted. Critical for proprietary codebases, internal tools, or any code you can't upload to a third-party AI service.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
