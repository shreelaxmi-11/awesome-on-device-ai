# 🩺 Medical Document Explainer

Load lab results or discharge summaries — get a plain-English explanation of what the medical terms mean. Runs entirely on-device. Your medical records never leave your Mac.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

> **⚠ Not medical advice.** This tool explains terminology — it cannot diagnose or treat. Always discuss your results with your healthcare provider.

---

## What it does

Medical documents are full of abbreviations and clinical language that's hard to understand. This tool reads them locally and explains what the words mean in plain English.

```
$ python explain.py --pdf lab_results.pdf --mode labs

🩺 Lab Results Explained

WBC  11.2 K/uL  (H)
  WBC = White Blood Cell count — how many infection-fighting cells are in
  your blood per microliter. K/uL means thousands per microliter.
  "(H)" means your result is above the lab's reference range (4.5–11.0).
  Mildly elevated WBC can result from stress, mild infection, or exercise.
  Your doctor will look at this alongside other markers to interpret it.

Neutrophils  78%  (H)
  Neutrophils are your body's first responders to bacterial infections —
  the most common type of white blood cell. The typical range is 45–70%.
  At 78%, yours is slightly elevated, consistent with the elevated WBC.
  Often seen transiently during stress, illness, or steroid use.

Lymphocytes  15%  (L)
  Lymphocytes fight viral infections. A low percentage can occur when
  neutrophils are proportionally higher, which is the case here.
  This is called "relative lymphopenia" and is often not clinically
  significant on its own.
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/privacy_apps/medical_doc_explainer
pip install -r requirements.txt

# Explain a lab report PDF
python explain.py --pdf lab_results.pdf

# Explain specific lab values (text mode)
python explain.py --text "WBC: 11.2 K/uL (H), RBC: 4.1..." --mode labs

# Ask questions about your document
python explain.py --pdf discharge_summary.pdf --mode chat
```

---

## Modes

| Mode | What it does |
|------|-------------|
| `explain` | Plain-English explanation of the entire document |
| `labs` | Per-test breakdown: what each value measures, reference range context |
| `chat` | Ask specific questions: "What does 'mild cardiomegaly' mean?" |

---

## How it works

```
Medical PDF
    → pypdf text extraction
    → word-level chunking (400 words, 50-word overlap)
    → TF-IDF index built in memory
    → for explain/labs: top relevant chunks fed to LLM with medical context prompt
    → for chat: per-question retrieval of most relevant sections
    → MLX streams the plain-English explanation
```

---

## Supported Models

| Model | Size | Speed (M3 Pro) | Best for |
|-------|------|----------------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s | Quick explanations |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s | More thorough explanations |
| `mlx-community/Llama-3-8B-Instruct-4bit` | 4.9 GB | 28 tok/s | Complex documents |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum
- Text-based PDF (not a scanned image)

---

## Privacy

Medical records are among the most sensitive documents there are. This tool was designed so they never leave your device. No cloud OCR, no cloud AI, no uploads of any kind.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
