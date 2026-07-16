# 📊 Chat with CSV

Ask questions about any CSV file in plain English. A local LLM reads your data and answers — no API key, no uploads, no cloud.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Load any CSV — sales data, survey results, financial records, experiment logs — and ask questions in plain English. The LLM reads your actual data and answers with real numbers from it.

```
You: What is the average order value?
Assistant: The average order value is $847.32, with a median of $612.50.
           The range is $12.00 to $9,840.00.

You: Which product category has the highest revenue?
Assistant: Electronics leads with $2.4M in total revenue (34% of total),
           followed by Home & Garden at $1.8M (26%)...

You: Are there any outliers in the transaction amounts?
Assistant: Yes — 3 transactions stand out: $9,840 (row 142), $8,200 (row 891),
           and $7,650 (row 203). These are 4–5x the mean of $1,920...
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/chat_with_x/chat_with_csv
pip install -r requirements.txt
python chat.py --csv your_data.csv
```

---

## Usage

```bash
# Chat with any CSV
python chat.py --csv sales.csv

# Use a stronger model for complex analysis
python chat.py --csv financials.csv --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

---

## What can you ask?

- "What is the average / median / max of [column]?"
- "Which rows have [column] greater than X?"
- "How many unique values are in [column]?"
- "What's the correlation between [column A] and [column B]?"
- "Summarize this dataset in plain English."
- "Are there any missing values? Which columns?"
- "Which [category] has the highest [metric]?"
- "Find outliers in [column]."

---

## How it works

```
CSV → pandas (schema + stats summary + raw data)
    → context injected into LLM system prompt
    → your question → local LLM (MLX)
    → answer grounded in your actual data
```

Large CSVs (>200 rows) are sampled. The model also receives a full statistical summary (mean, std, min, max, unique counts) so it can answer statistical questions accurately even from a sample.

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

Your CSV data never leaves your machine. Especially useful for sensitive datasets: customer records, financial data, HR data, experimental results, proprietary business data.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
