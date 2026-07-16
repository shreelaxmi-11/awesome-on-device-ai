# 🩺 Medical Document Explainer

Load lab results or discharge summaries — get a plain-English explanation of what the medical terms mean. Runs entirely on-device. Your medical records never leave your Mac.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

> **⚠ Not medical advice.** This tool explains terminology — it cannot diagnose or treat. Always discuss your results with your healthcare provider.

---

## What it does

Medical documents are full of abbreviations and clinical language that's hard to understand. This tool reads them locally and explains what the words mean in plain English.

```
Lab result: WBC 11.2 K/uL (H), Neutrophils 78% (H), Lymphocytes 15% (L)

Explanation:
WBC stands for White Blood Cell count — it measures how many infection-fighting
cells are in your blood per microliter. K/uL means thousands per microliter.
The "(H)" means your result is above the lab's reference range...

Neutrophils are the most common type of white blood cell — they're your body's
first responders to bacterial infections. At 78%, yours is slightly above the
typical reference range (45-70%)...
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/privacy_apps/medical_doc_explainer
pip install -r requirements.txt

# Explain a lab report PDF
python explain.py --pdf lab_results.pdf

# Explain lab results (text mode)
python explain.py --text "WBC: 11.2 K/uL (H), RBC: 4.1..." --mode labs

# Ask questions about your document
python explain.py --pdf discharge_summary.pdf --mode chat
```

---

## Modes

| Mode | What it does |
|------|-------------|
| `explain` | Plain-English explanation of the whole document |
| `labs` | Per-test explanation of what each lab value measures |
| `chat` | Ask specific questions about your document |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum
- Text-based PDF (not scanned)

---

## Privacy

Medical records are among the most sensitive documents there are. This tool was designed so they never leave your device. No cloud OCR, no cloud AI, no uploads.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
