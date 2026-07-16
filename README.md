<p align="center">
  <img src="docs/banner.png" width="900px" alt="Awesome On-Device AI">
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/shreelaxmi-ganesh/">
    <img src="https://img.shields.io/badge/Follow%20on%20LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
  </a>
  <a href="https://twitter.com/shreelaxmi_ai">
    <img src="https://img.shields.io/badge/Follow%20on%20𝕏-000000?style=for-the-badge&logo=x&logoColor=white" alt="X / Twitter">
  </a>
</p>

<hr/>

<div align="center">

# 🔒 Awesome On-Device AI

<p><strong>50+ local AI apps you can actually run — no API keys, no cloud, no data leaving your machine.</strong><br/>
Local LLMs · Private RAG · On-Device Voice AI · Local Agents · Edge Fine-tuning · Cross-Platform Inference</p>

<p>
<strong>Every app runs on your hardware. Your data never leaves your device.</strong><br/>
<strong>Works with MLX · Whisper · LiteRT-LM · Ollama · llama.cpp</strong>
</p>

<p>
<a href="https://github.com/shreelaxmi-11/awesome-on-device-ai/stargazers"><img src="https://img.shields.io/github/stars/shreelaxmi-11/awesome-on-device-ai?style=for-the-badge&logo=github&color=FFD700" alt="Stars"></a>
<a href="https://github.com/shreelaxmi-11/awesome-on-device-ai/network/members"><img src="https://img.shields.io/github/forks/shreelaxmi-11/awesome-on-device-ai?style=for-the-badge&logo=github&color=4FC3F7" alt="Forks"></a>
<a href="https://github.com/shreelaxmi-11/awesome-on-device-ai/graphs/contributors"><img src="https://img.shields.io/github/contributors/shreelaxmi-11/awesome-on-device-ai?style=for-the-badge&color=22C55E" alt="Contributors"></a>
<a href="LICENSE"><img src="https://img.shields.io/github/license/shreelaxmi-11/awesome-on-device-ai?style=for-the-badge&color=8B5CF6" alt="License"></a>
<img src="https://img.shields.io/github/last-commit/shreelaxmi-11/awesome-on-device-ai?style=for-the-badge&color=F97316" alt="Last Commit">
</p>

<p>
<a href="#-quick-start"><kbd> &nbsp; 🚀 Quick Start &nbsp; </kbd></a>
<a href="#-featured-this-month"><kbd> &nbsp; 🔥 Featured &nbsp; </kbd></a>
<a href="#-all-apps"><kbd> &nbsp; 📂 Browse Apps &nbsp; </kbd></a>
</p>

</div>

---

## 💡 Why this exists

Every "AI app" tutorial on the internet sends your data to OpenAI, Anthropic, or Google.

**Awesome On-Device AI is a cookbook of local-first templates** — apps that run entirely on your machine using open models. No API key. No usage bill. No data leaving your device. Clone, install, run.

- 🔒 **Privacy by default** — your files, voice, and conversations stay on your hardware
- 🛠️ **Hand-built, not curated** — every template is original, tested end-to-end before it ships
- ⚡ **Runs in 3 commands** — clone → pip install → python run.py
- 🧠 **Covers the full on-device stack** — MLX, Whisper, LiteRT-LM, Ollama, llama.cpp, local RAG, local agents, on-device fine-tuning
- 🍎 **Apple Silicon optimized** — MLX templates use the full 150 GB/s unified memory bandwidth on M-series chips
- 🌐 **Cross-platform options** — LiteRT-LM templates run on macOS, Linux, Windows, and Android
- 📜 **Apache-2.0** — fork it, ship it, build products. No paywall, no signup, no telemetry.

> ⭐ **If this saves you time, [star the repo](https://github.com/shreelaxmi-11/awesome-on-device-ai/stargazers) — that's how the next developer discovers it.**

---

## 🚀 Quick Start

Run your first local AI app in **30 seconds**:

```bash
git clone https://github.com/shreelaxmi-11/awesome-on-device-ai.git
cd awesome-on-device-ai/starter_apps/local_pdf_chat
pip install -r requirements.txt
python chat.py --pdf your_document.pdf
```

No API key. No internet. Your PDF, your machine, your answers.

**Requirements:** Python 3.9+ · Apple Silicon Mac (M1/M2/M3/M4) for MLX apps · 8GB+ unified memory recommended

---

## 🔥 Featured This Month

| App | What it does | Stack |
|-----|-------------|-------|
| [📄 Local PDF Chat](starter_apps/local_pdf_chat/) | Chat with any PDF entirely on-device — contracts, research papers, medical docs | MLX · local RAG |
| [🎙️ Voice Notes Summarizer](voice_ai/voice_notes_summarizer/) | Record yourself talking, get a private local summary — never uploaded anywhere | Whisper · MLX |
| [🔍 MLX vs LiteRT-LM Benchmark](benchmarks/mlx_vs_litert_lm/) | Same model, same hardware, two runtimes — measured on M3 Pro with real numbers | MLX · LiteRT-LM |
| [💬 Local AI Chat](starter_apps/local_ai_chat/) | ChatGPT-style chat that runs on your Mac — Llama, Qwen, Mistral, Phi | MLX |
| [📊 On-Device AI Hardware Benchmarks](benchmarks/mlx_hardware_benchmark/) | Real tok/s, memory, TTFT numbers across 4 models on Apple M3 Pro | MLX 0.32.0 |

---

## 📑 Table of Contents

<details open>
<summary><strong>10 categories · Click to expand</strong></summary>

- [🌱 Starter Local AI Apps](#-starter-local-ai-apps)
- [🎙️ Local Voice AI](#️-local-voice-ai)
- [📚 Local RAG Apps](#-local-rag-apps)
- [💬 Chat with X (Local)](#-chat-with-x-local)
- [🤖 Local AI Agents](#-local-ai-agents)
- [🧠 Local AI with Memory](#-local-ai-with-memory)
- [🔧 On-Device Fine-tuning](#-on-device-fine-tuning)
- [🔒 Privacy-First Apps](#-privacy-first-apps)
- [📊 Edge AI Benchmarks](#-edge-ai-benchmarks)
- [🌐 Cross-Platform Edge AI](#-cross-platform-edge-ai)

</details>

---

## 📂 All Apps

### 🌱 Starter Local AI Apps
*Single-file apps that run with no API key — the best place to start.*

- [💬 Local AI Chat](starter_apps/local_ai_chat/) — ChatGPT-style terminal chat using Llama 3.2 3B on MLX. Streams tokens, no internet needed.
- [📄 Local PDF Chat](starter_apps/local_pdf_chat/) — Ask questions about any PDF locally. Chunks the doc, retrieves relevant sections, answers with a local LLM.
- [✍️ Local Writing Assistant](starter_apps/local_writing_assistant/) — Draft emails, blog posts, and messages locally. Paste bullet points, get a polished draft.
- [🔍 Local Code Explainer](starter_apps/local_code_explainer/) — Paste any code snippet, get a plain-English explanation. Runs entirely on-device.

---

### 🎙️ Local Voice AI
*Speech-in, text-out — using Whisper on-device. No audio ever leaves your machine.*

- [🎙️ Voice Notes Summarizer](voice_ai/voice_notes_summarizer/) — Record a voice note or drop an audio file. Whisper transcribes it locally, a local LLM summarizes it.
- [📝 Local Meeting Transcriber](voice_ai/local_meeting_transcriber/) — Transcribe recorded meetings entirely on-device. Outputs timestamped transcript + action items.
- [📔 Private Voice Journal](voice_ai/private_voice_journal/) — Speak daily. Whisper transcribes. Local LLM tracks weekly patterns. Your most private thoughts stay private.

---

### 📚 Local RAG Apps
*Retrieval-augmented generation — all on your machine.*

- [📄 Local PDF RAG](local_rag/local_pdf_rag/) — Full RAG pipeline: PDF → chunks → local embeddings → vector search → local LLM answer.
- [💻 Local Code RAG](local_rag/local_code_rag/) — Index your codebase locally and chat with it. Ask "where is the auth logic?" and get an answer.
- [🔬 Private Research Assistant](local_rag/private_research_assistant/) — Drop a folder of papers or docs. Build a local knowledge base. Ask questions across all of them.

---

### 💬 Chat with X (Local)
*Turn any data source into a local chat interface.*

- [📄 Chat with PDF (Local)](chat_with_x/chat_with_pdf/) — Load any PDF and chat with it. Works offline. Ideal for contracts, reports, textbooks.
- [💻 Chat with Code (Local)](chat_with_x/chat_with_code/) — Index a GitHub repo or local folder and ask questions about the codebase.
- [📊 Chat with CSV (Local)](chat_with_x/chat_with_csv/) — Load any CSV file and ask questions in plain English. Local data analysis with no cloud.
- [📓 Chat with Notion Export (Local)](chat_with_x/chat_with_notion/) — Export your Notion workspace and chat with your own notes privately.

---

### 🤖 Local AI Agents
*Agents that reason and act — entirely on your machine.*

- [🔍 Local Research Agent](local_agents/local_research_agent/) — Give it a topic. It searches local docs, reasons across them, and drafts a structured summary.
- [📧 Private Email Drafting Agent](local_agents/private_email_agent/) — Paste bullet points or context. Local agent drafts a professional email. Nothing goes to the cloud.
- [📋 Local Task Planner](local_agents/local_task_planner/) — Describe a goal. Local agent breaks it into tasks, estimates effort, and outputs a structured plan.

---

### 🧠 Local AI with Memory
*Agents and apps that remember across sessions — stored locally.*

- [🧠 Local AI with Persistent Memory](memory_apps/local_ai_memory/) — Chat interface that remembers your preferences, past conversations, and context — saved locally as JSON.
- [📚 Personal Knowledge Base](memory_apps/personal_knowledge_base/) — Feed it your notes, documents, and ideas over time. It builds a private local knowledge graph you can query.

---

### 🔧 On-Device Fine-tuning
*Adapt open models to your data — training stays on your machine.*

- [🎯 LoRA Fine-tuning on Personal Data](finetuning/lora_on_personal_data/) — Fine-tune Llama 3.2 or Mistral on your own writing using MLX LoRA. Creates a model that sounds like you.
- [🔨 Custom Adapter Builder](finetuning/custom_adapter_builder/) — Pipeline to prepare data, run LoRA training, and export a reusable `.npz` adapter for any MLX-compatible model.

---

### 🔒 Privacy-First Apps
*Apps where privacy isn't a feature — it's the entire point.*

- [📋 Local Contract Analyzer](privacy_apps/local_contract_analyzer/) — Load any contract PDF. Local LLM flags unusual clauses, liability risks, and missing provisions in plain English. Your legal docs never leave your Mac.
- [💰 Private Financial Analyzer](privacy_apps/private_financial_analyzer/) — Load bank statement CSVs. Local LLM analyzes spending patterns, flags anomalies, and answers questions. Your financial data stays local.
- [🩺 Medical Document Explainer](privacy_apps/medical_doc_explainer/) — Load lab results or discharge summaries. Local LLM explains findings in plain English. Your medical records stay on your device.

---

### 📊 Edge AI Benchmarks
*Real performance numbers — measured on real hardware.*

- [⚡ On-Device AI Hardware Benchmarks](benchmarks/mlx_hardware_benchmark/) — Real tok/s, memory (GB), and TTFT across 4 models (Llama 3.2 3B, Phi-3.5 Mini, Mistral 7B, Llama 3 8B) at INT4 on M3 Pro.
- [🔬 MLX vs LiteRT-LM Runtime Comparison](benchmarks/mlx_vs_litert_lm/) — Same model (Qwen3-4B-Instruct-2507), same hardware (M3 Pro 18GB), two runtimes. Real measured numbers, PM-level analysis of when each wins.

---

### 🌐 Cross-Platform Edge AI
*On-device AI that runs beyond Apple Silicon.*

- [🌍 LiteRT-LM Desktop Python](cross_platform/litert_lm_desktop/) — Google's LiteRT-LM running via Python on macOS. Gemma 4 and Qwen3 models, GPU-accelerated.
- [⚖️ Cross-Runtime Inference Comparison](cross_platform/cross_runtime_comparison/) — Compare MLX, LiteRT-LM, and Ollama on the same hardware. Latency, memory, and quality tradeoffs explained for PMs.

---

## 🛠️ Hardware & Runtime Guide

| Runtime | Best for | Platforms | Install |
|---------|----------|-----------|---------|
| [MLX](https://github.com/ml-explore/mlx) | Apple Silicon (M1–M4) | macOS only | `pip install mlx-lm` |
| [LiteRT-LM](https://developers.google.com/edge/litert-lm) | Cross-platform (Android, iOS, Desktop) | macOS · Linux · Windows · Android | `pip install litert-lm-api` |
| [Whisper (mlx-whisper)](https://github.com/ml-explore/mlx-examples) | Local speech recognition | macOS (Apple Silicon) | `pip install mlx-whisper` |
| [Ollama](https://ollama.com) | Quickest local setup | macOS · Linux · Windows | [ollama.com](https://ollama.com) |
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | Maximum cross-platform | All platforms | [build from source](https://github.com/ggerganov/llama.cpp) |

---

## 📐 Recommended Models

| Model | Size (INT4) | Best for | Download |
|-------|------------|----------|----------|
| Llama 3.2 3B Instruct | ~1.7 GB | Chat, summarization, agents | [mlx-community](https://huggingface.co/mlx-community/Llama-3.2-3B-Instruct-4bit) |
| Phi-3.5 Mini Instruct | ~2.0 GB | Reasoning, coding, Q&A | [mlx-community](https://huggingface.co/mlx-community/Phi-3.5-mini-instruct-4bit) |
| Qwen3-4B-Instruct-2507 | ~2.5 GB | Multilingual, instruction following | [mlx-community](https://huggingface.co/mlx-community/Qwen3-4B-Instruct-2507-4bit) |
| Mistral 7B Instruct v0.3 | ~3.8 GB | Long context, complex tasks | [mlx-community](https://huggingface.co/mlx-community/Mistral-7B-Instruct-v0.3-4bit) |
| Whisper Large v3 | ~1.5 GB | Speech transcription | [mlx-community](https://huggingface.co/mlx-community/whisper-large-v3-mlx) |

---

## 🙏 Built by

<p>Created and maintained by <a href="https://www.linkedin.com/in/shreelaxmi-ganesh/"><strong>Shreelaxmi Ganesh</strong></a> — PM in on-device AI, ex-Samsung Research (Galaxy AI · Patent WO2025/063733 · File Cache Reclamation for GenAI on Mobile NPUs).</p>

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=shreelaxmi-11/awesome-on-device-ai&type=Date)](https://star-history.com/#shreelaxmi-11/awesome-on-device-ai&Date)

> 🔒 **Every app in this repo runs locally. Your data stays yours.**

---

## 📜 License

Apache-2.0. See [LICENSE](LICENSE). Fork it, ship it, build products on it.
