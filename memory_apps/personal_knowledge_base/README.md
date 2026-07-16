# 📚 Personal Knowledge Base

Add notes and ideas over time. Build a private local knowledge base you can query with natural language. Stored as plain JSON on disk. No cloud, no API key.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://python.org)
[![MLX](https://img.shields.io/badge/Runtime-MLX-orange?style=flat-square)](https://github.com/ml-explore/mlx)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=flat-square)](#)

---

## Quick Start

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/memory_apps/personal_knowledge_base
pip install -r requirements.txt

# Add a note
python kb.py add "The key to good prompts is specificity and examples"

# Add a file
python kb.py add --file notes.md --tag "prompting"

# Search
python kb.py search "what do I know about prompting?"

# Chat with your KB
python kb.py chat

# List all entries
python kb.py list
```

KB stored at `~/.personal_knowledge_base/`.

---

## Part of [Awesome On-Device AI](../../README.md)

> 🔒 Every app in this collection runs locally. Your data stays yours.
