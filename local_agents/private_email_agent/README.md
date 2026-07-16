# 📧 Private Email Drafting Agent

Paste bullet points — get a professional email. Six types, five tones. No API key, no cloud, your email content stays on your machine.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Give it bullet points of what you want to say. Choose your email type and tone. Get a complete, ready-to-send email with subject line — without your draft going to any cloud service.

```
$ python draft.py --type followup --tone friendly

Enter bullet points (blank line to finish):
> Following up on last Tuesday's demo call
> They seemed interested but haven't heard back in 5 days
> Want to keep it light, not pushy
> Ask if they need any additional info
>

Subject: Quick follow-up — our demo call

Hi [Name],

Hope you had a good week! Just wanted to follow up on our demo call
last Tuesday — it was great walking you through how everything works.

If you have questions or would like to see anything in more detail,
I'm happy to set up another quick call. Otherwise, I'm here whenever
you're ready to take next steps.

No pressure at all — just wanted to stay in touch!

Best,
[Your name]
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/local_agents/private_email_agent
pip install -r requirements.txt
python draft.py
```

---

## Usage

```bash
# Interactive (default: professional new email)
python draft.py

# Follow-up email, friendly tone
python draft.py --type followup --tone friendly

# Formal decline
python draft.py --type decline --tone formal

# Reply to an existing email
python draft.py --type reply --context "Hi, we'd like to schedule a call..."

# Assertive request
python draft.py --type request --tone assertive

# Save the draft
python draft.py --output draft.txt

# Use a stronger model
python draft.py --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

---

## Email Types & Tones

**Types:** `new` · `followup` · `reply` · `decline` · `request` · `intro`

**Tones:** `professional` · `friendly` · `formal` · `assertive` · `concise`

---

## How it works

```
Your bullet points + email type + tone
    → type/tone-specific system prompt constructed
    → bullet points injected into user message
    → MLX generates subject line + full email body
    → streams to terminal
    → optionally saved to --output file
```

---

## Supported Models

| Model | Size | Speed (M3 Pro) | Best for |
|-------|------|----------------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s | Default — fast drafts |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s | Nuanced tone matching |
| `mlx-community/Llama-3-8B-Instruct-4bit` | 4.9 GB | 28 tok/s | Best quality |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

Your email content never leaves your machine. Especially important when drafting emails that contain deal details, internal strategy, compensation information, or sensitive negotiations.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
