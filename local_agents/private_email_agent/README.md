# 📧 Private Email Drafting Agent

Paste bullet points — get a professional email. Six types, five tones. No API key, no cloud, your email content stays on your machine.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Give it bullet points of what you want to say. Choose your tone. Get a complete, ready-to-send email with subject line.

```
Input:
• Following up on last Tuesday's demo call
• They seemed interested but haven't heard back in 5 days
• Want to keep it light, not pushy
• Ask if they need any additional info

Output (friendly follow-up):

Subject: Quick follow-up — [Company Name] demo

Hi [Name],

Hope you had a good week! Just wanted to follow up on our demo call
last Tuesday — it was great walking through how [product] could work
for your team.

If you have any questions or would like to see a specific feature in
more detail, I'm happy to set up another quick call. Otherwise, I'm
here whenever you're ready to take next steps.

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

# Reply to an email
python draft.py --type reply --context "Hi, we'd like to schedule a call..."

# Save the draft
python draft.py --output draft.txt
```

---

## Email Types & Tones

**Types:** `new` · `followup` · `reply` · `decline` · `request` · `intro`

**Tones:** `professional` · `friendly` · `formal` · `assertive` · `concise`

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
