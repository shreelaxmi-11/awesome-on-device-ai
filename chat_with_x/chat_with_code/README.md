# 💻 Chat with Code (Local)

Index any GitHub repo or local folder and ask questions about the codebase in plain English. No API key. Your source code never leaves your machine.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Point it at any codebase and ask questions in plain English. Get answers grounded in the actual source code with file names and line numbers.

```
You: Where is the authentication logic?
Assistant: Authentication is handled in src/auth/middleware.py (lines 42-89).
           The main entry point is the `authenticate_request` function, which
           validates JWT tokens using the `python-jose` library...

You: How does the data pipeline work?
Assistant: The pipeline is defined in pipeline/runner.py. It follows a
           3-stage pattern: ingest (ingest.py), transform (transform.py),
           and load (loader.py). The orchestrator in runner.py calls these
           in sequence, passing a shared context object between stages...

You: What does process_payment do?
Assistant: process_payment (payments/processor.py, line 156) takes a
           PaymentRequest object, validates the amount and currency, calls
           the Stripe API wrapper in stripe_client.py, and returns a
           PaymentResult with status and transaction_id...
```

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
# Chat with a local repo
python chat.py --repo ~/my-project

# Index specific file types only
python chat.py --repo ~/my-project --extensions py,yaml,md

# Use a code-focused model
python chat.py --repo ~/my-project --model mlx-community/Phi-3.5-mini-instruct-4bit

# Larger model for complex codebases
python chat.py --repo ~/my-project --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

---

## How it works

```
Repository
    → file scanner (skips node_modules, .git, __pycache__, binaries, large files)
    → code-aware tokenization (splits camelCase, snake_case, file paths)
    → TF-IDF index with file path + line number metadata
    → per query: cosine similarity retrieval of top-k chunks
    → chunks + source references injected into LLM context
    → MLX streams the answer with file and line citations
```

Code-aware tokenization is the key differentiator: `processPaymentRequest` is indexed as ["process", "payment", "request"], making natural language queries much more effective than naive word-split TF-IDF.

---

## Supported Languages

Python · JavaScript · TypeScript · TSX/JSX · Go · Rust · Java · C/C++ · Swift · Kotlin · Ruby · Shell · YAML · JSON · TOML · Markdown

---

## Supported Models

| Model | Size | Speed (M3 Pro) | Best for |
|-------|------|----------------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s | Quick questions |
| `mlx-community/Phi-3.5-mini-instruct-4bit` | 2.0 GB | 51 tok/s | Code reasoning |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s | Complex codebases |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

Your source code is indexed locally and never transmitted. Critical for proprietary codebases, internal tools, or any code you can't upload to GitHub Copilot or Cursor.

---

## Full Implementation

The complete source code and documentation lives in [local_rag/local_code_rag](../../local_rag/local_code_rag/).

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
