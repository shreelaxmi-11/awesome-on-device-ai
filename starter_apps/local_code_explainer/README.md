# 🔍 Local Code Explainer

Paste any code snippet — get a clear explanation, review, docstrings, or tests from a local LLM. No API key. No cloud. Your code stays on your machine.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Five modes for working with code entirely offline:

```
$ python explain.py --file app.py --mode review

👀 Code Review

Correctness
  Line 42: off-by-one error — range should be range(n-1), not range(n).
  Line 67: dict.get() called without a default — will return None silently
  on missing keys. If downstream code expects a string, this will crash later.

Performance
  The nested loop on lines 31-38 is O(n²). For n > 1000, this will be
  noticeably slow. Consider sorting and using a hash map — O(n log n).

Readability
  Function name `proc` is too vague — rename to `process_user_records`.
  The 40-line function at line 55 should be split into 2-3 smaller functions.

Security
  No issues found.
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/starter_apps/local_code_explainer
pip install -r requirements.txt

# Explain a file
python explain.py --file my_script.py

# Code review
python explain.py --file app.py --mode review

# Paste code interactively
python explain.py --mode explain
```

---

## Modes

| Mode | Command | What it does |
|------|---------|-------------|
| `explain` | `--mode explain` | Plain-English explanation of what the code does and why |
| `review` | `--mode review` | Senior engineer code review: bugs, performance, style, security |
| `docstring` | `--mode docstring` | Adds complete docstrings to every function and class |
| `optimize` | `--mode optimize` | Rewrites for performance and readability |
| `test` | `--mode test` | Generates unit tests covering happy path + edge cases |

---

## Usage

```bash
# Explain a file
python explain.py --file script.py

# Code review (paste interactively if no file)
python explain.py --mode review

# Generate docstrings and save output
python explain.py --file module.py --mode docstring --output module_documented.py

# Generate tests
python explain.py --file utils.py --mode test --output test_utils.py

# Use a stronger model for complex code
python explain.py --file complex.py --mode review \
  --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

---

## How it works

```
Code file or pasted snippet
    → optional: rich.Syntax preview in terminal (syntax-highlighted)
    → mode-specific system prompt (explain / review / docstring / ...)
    → full code injected into LLM context
    → MLX streams the response token by token
    → optionally saved to --output file
```

The entire file is passed to the LLM in context. For very large files (>500 lines), use `--lines start:end` to target a specific section.

---

## Supported Models

| Model | Size | Speed (M3 Pro) | Best for |
|-------|------|----------------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s | Quick explanations |
| `mlx-community/Phi-3.5-mini-instruct-4bit` | 2.0 GB | 51 tok/s | Code-focused reasoning |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s | Detailed reviews |
| `mlx-community/Llama-3-8B-Instruct-4bit` | 4.9 GB | 28 tok/s | Complex codebases |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

Your code never leaves your machine — especially important for proprietary or confidential source code. No API key, no uploads, no telemetry.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
