# 💳 Private Financial Analyzer

Load your bank statement or transaction CSV — get spending analysis, budget breakdown, and anomaly detection. Runs entirely on-device. Your financial data never leaves your machine.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Export your transactions from your bank (most banks let you download as CSV), then load them here for private AI-powered analysis.

```
💳 Spending Overview

Total spending this period: $4,832.14 across 87 transactions

Top Categories:
  1. Rent / Housing:     $2,200.00 (45.5%)
  2. Groceries:          $612.40   (12.7%)
  3. Dining:             $489.22   (10.1%)
  4. Transport:          $218.90   (4.5%)
  5. Subscriptions:      $187.00   (3.9%)

Largest transactions:
  • $2,200 — ACH Transfer / Rent (Mar 1)
  • $412 — Apple One / Annual (Mar 3)
  • $208 — Whole Foods (Mar 15)

Insight: Dining spend is 10% of income — industry benchmark is 5-8%.
         You have 6 active streaming subscriptions totalling $89/month.
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/privacy_apps/private_financial_analyzer
pip install -r requirements.txt

# Spending overview
python analyze.py --csv transactions.csv

# Budget breakdown
python analyze.py --csv bank_export.csv --mode budget

# Detect unusual charges
python analyze.py --csv spending.csv --mode anomalies

# Ask specific questions
python analyze.py --csv transactions.csv --mode chat
```

---

## Analysis Modes

| Mode | What it does |
|------|-------------|
| `overview` | Total spend, top categories, largest transactions, trends |
| `budget` | Fixed vs variable, recurring payments, 50/30/20 breakdown |
| `anomalies` | Unusual charges, duplicate transactions, suspicious patterns |
| `chat` | Ask specific questions: "How much did I spend on food in March?" |

---

## CSV Format

Works with any CSV that has amount, date, and description columns. Automatically detects column names from popular bank exports (Chase, Bank of America, YNAB, Mint, etc.).

**Example formats that work:**
- Chase: `Transaction Date, Post Date, Description, Category, Type, Amount, Memo`
- Bank of America: `Date, Description, Amount, Running Bal.`
- Generic: `date, description, amount`

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

Your financial data is loaded locally and never transmitted anywhere. This is exactly the kind of sensitive data you should NOT upload to a cloud AI service — run it here instead.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
