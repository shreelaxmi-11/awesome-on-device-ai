# 📋 Local Task Planner

Describe a goal — the local LLM breaks it into phases, tasks, effort estimates, and risks. Structured planning output, fully on-device.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Platform](https://img.shields.io/badge/Platform-Apple%20Silicon-black?style=flat-square)](https://developer.apple.com/documentation/apple-silicon)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## What it does

Describe what you're trying to accomplish. The local LLM generates a structured plan with phases, tasks, effort estimates, risks, and a definition of done — without your ideas going to a cloud service.

```
$ python plan.py "Launch a product beta in 6 weeks"

📋 Project Plan: Launch a product beta in 6 weeks

Phase 1 — Foundation (Week 1-2)
  ✦ Define beta scope and success metrics (2 days)
  ✦ Identify and recruit 20-30 beta users (3 days)
  ✦ Set up feedback collection system (1 day)
  ✦ Create beta onboarding checklist (1 day)

Phase 2 — Preparation (Week 3-4)
  ✦ Stabilize core user flows — no P0 bugs (5 days)
  ✦ Write beta documentation and FAQ (2 days)
  ✦ Configure monitoring and alerting (1 day)
  ✦ Internal dry run with 5 friendly users (2 days)

Phase 3 — Launch (Week 5-6)
  ✦ Soft launch to first cohort of 10 users (day 1)
  ✦ Daily check-ins for first week (ongoing)
  ✦ Roll out to full 30-user cohort (week 6)
  ✦ Synthesize feedback, draft learnings doc (2 days)

Key Risks
  ⚠ Scope creep on "stable core flows" — need hard cutoff on what's in scope
  ⚠ Recruiting delay — start outreach in week 1, not week 2
  ⚠ Feedback overload — use structured template, not freeform

Definition of Done
  30 users onboarded, 3 feedback sessions completed, retention >60% at 2 weeks
```

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/local_agents/local_task_planner
pip install -r requirements.txt

# Plan from a goal
python plan.py "Launch a product beta in 6 weeks"

# Interactive mode
python plan.py --interactive

# Save the plan to a file
python plan.py "Write a research paper on edge AI" --output plan.md
```

---

## Usage

```bash
# One-shot plan
python plan.py "Migrate our backend to Kubernetes"

# With timeline context
python plan.py "Redesign our onboarding flow" --context "We have 2 engineers, 6 weeks"

# More detailed plan with a stronger model
python plan.py "Build an internal analytics dashboard" \
  --model mlx-community/Mistral-7B-Instruct-v0.3-4bit

# Save to markdown
python plan.py "Prepare for a Series A raise" --output fundraising_plan.md
```

---

## How it works

```
Your goal description (+ optional context)
    → structured planning prompt with explicit sections required
    → local LLM generates: phases → tasks → estimates → risks → definition of done
    → streams to terminal
    → optionally saved as markdown with --output
```

---

## Supported Models

| Model | Size | Speed (M3 Pro) | Best for |
|-------|------|----------------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7 GB | 61 tok/s | Default — fast plans |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit` | 3.8 GB | 29 tok/s | More thorough planning |
| `mlx-community/Llama-3-8B-Instruct-4bit` | 4.9 GB | 28 tok/s | Best quality |

---

## Requirements

- macOS with Apple Silicon (M1, M2, M3, or M4)
- Python 3.9+
- 8 GB unified memory minimum

---

## Privacy

Your project ideas and plans never leave your machine. No API key, no cloud, no telemetry.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
