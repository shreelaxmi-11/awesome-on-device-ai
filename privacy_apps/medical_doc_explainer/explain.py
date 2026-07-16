#!/usr/bin/env python3
"""
Medical Document Explainer — Awesome On-Device AI
Load any medical document — lab results, discharge summaries, pathology reports —
and get a plain-English explanation. Local LLM only. Your records never leave your Mac.

Usage:
    python explain.py --pdf lab_results.pdf
    python explain.py --pdf discharge_summary.pdf --mode chat
    python explain.py --text "WBC: 11.2 K/uL (H), RBC: 4.1 M/uL..."
"""

import argparse
import re
import sys
from pathlib import Path

import numpy as np
from pypdf import PdfReader
from mlx_lm import load, stream_generate
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule

console = Console()

DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
MAX_TOKENS    = 800
CHUNK_SIZE    = 400
TOP_K         = 5

DISCLAIMER = (
    "[bold yellow]⚠ Not medical advice.[/bold yellow] "
    "This tool explains medical terminology — it cannot diagnose or treat. "
    "Always discuss your results with your healthcare provider."
)

MODES = {
    "explain": {
        "label": "Plain-English Explanation",
        "system": (
            "You are a medical literacy assistant who explains medical documents to patients. "
            "Use clear, plain English that a non-medical person can understand. "
            "Explain medical terms when you use them. "
            "Do NOT diagnose, recommend treatments, or interpret results as normal/abnormal — "
            "that is the doctor's role. Focus on helping the patient understand what the words mean."
        ),
        "prompt": (
            "Explain the following medical document in plain English:\n\n"
            "1. What type of document is this?\n"
            "2. What does it measure or describe?\n"
            "3. Explain any medical terms, abbreviations, or values in plain language\n"
            "4. What questions might the patient want to ask their doctor?\n\n"
            "Remind the reader that you are explaining terminology, not providing medical advice.\n\n"
            "DOCUMENT:\n{context}"
        ),
    },
    "labs": {
        "label": "Lab Results Explainer",
        "system": (
            "You are a medical literacy assistant specializing in explaining laboratory results. "
            "Explain what each test measures in plain English. "
            "Do NOT interpret whether values are concerning — only explain what the test is and what it measures. "
            "The patient's doctor will interpret the clinical significance."
        ),
        "prompt": (
            "Explain each lab test and value in this report in plain English:\n\n"
            "For each test:\n"
            "- What does it measure?\n"
            "- What does the value mean in plain language?\n"
            "- What is the unit of measurement?\n\n"
            "Do not say whether values are 'good' or 'bad' — only explain what they measure.\n\n"
            "LAB REPORT:\n{context}"
        ),
    },
    "chat": {
        "label": "Q&A Chat",
        "system": (
            "You are a medical literacy assistant. You help patients understand medical terminology "
            "and documents. You explain what words and tests mean in plain language. "
            "You do NOT provide diagnoses, treatment recommendations, or clinical interpretations. "
            "Always remind users to discuss questions with their healthcare provider."
        ),
        "prompt": "{question}\n\nMEDICAL DOCUMENT CONTEXT:\n{context}",
    },
}


# ── PDF loading (same TF-IDF approach as local_pdf_chat) ──────────────────────

def load_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"[Page {i+1}]\n{text.strip()}")
    full = "\n\n".join(pages)
    if not full.strip():
        console.print("[red]Could not extract text. PDF may be scanned/image-based.[/red]")
        sys.exit(1)
    return full


def chunk_text(text: str) -> list[str]:
    words = text.split()
    chunks, step = [], CHUNK_SIZE - 60
    for i in range(0, len(words), step):
        c = " ".join(words[i:i + CHUNK_SIZE])
        if c.strip():
            chunks.append(c)
    return chunks


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())


def build_tfidf(chunks: list[str]):
    tokenized = [_tokenize(c) for c in chunks]
    vocab = sorted({w for doc in tokenized for w in doc})
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    n, V = len(chunks), len(vocab)
    tf = np.zeros((n, V), dtype=np.float32)
    for di, doc in enumerate(tokenized):
        for w in doc:
            tf[di, vocab_idx[w]] += 1
        if tf[di].sum() > 0:
            tf[di] /= tf[di].sum()
    df = (tf > 0).sum(axis=0).astype(np.float32)
    idf = np.log((n + 1) / (df + 1)) + 1
    tfidf = tf * idf
    norms = np.linalg.norm(tfidf, axis=1, keepdims=True) + 1e-9
    tfidf /= norms
    return tfidf, vocab_idx, idf


def retrieve(query: str, chunks, tfidf_matrix, vocab_idx, idf, top_k=TOP_K) -> list[str]:
    V = tfidf_matrix.shape[1]
    q_tokens = _tokenize(query)
    q_vec = np.zeros(V, dtype=np.float32)
    for w in q_tokens:
        if w in vocab_idx:
            q_vec[vocab_idx[w]] += 1
    if q_vec.sum() > 0:
        q_vec /= q_vec.sum()
    q_vec *= idf
    norm = np.linalg.norm(q_vec) + 1e-9
    q_vec /= norm
    scores = tfidf_matrix @ q_vec
    top_idx = np.argsort(scores)[::-1][:top_k]
    return [chunks[i] for i in top_idx if scores[i] > 0]


def run_explanation(model, tokenizer, mode_key: str, context: str, question: str = "") -> str:
    mode = MODES[mode_key]
    if mode_key == "chat":
        user_content = mode["prompt"].format(question=question, context=context)
    else:
        user_content = mode["prompt"].format(context=context)

    messages = [
        {"role": "system", "content": mode["system"]},
        {"role": "user",   "content": user_content},
    ]
    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        prompt = f"SYSTEM: {mode['system']}\nUSER: {user_content}\nASSISTANT:"

    console.rule(f"[bold]{mode['label']}[/bold]")
    console.print()

    result = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
        token = chunk.text if hasattr(chunk, "text") else chunk
        print(token, end="", flush=True)
        result += token
    print("\n")
    return result.strip()


def main():
    parser = argparse.ArgumentParser(description="Explain medical documents in plain English.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--pdf",  help="Path to PDF medical document")
    source.add_argument("--text", help="Paste medical text directly")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--mode",  default="explain", choices=list(MODES.keys()))
    args = parser.parse_args()

    console.print(Panel.fit(
        f"[bold cyan]🩺 Medical Document Explainer[/bold cyan]\n"
        f"{DISCLAIMER}\n"
        "[dim]Runtime:[/dim] MLX (Apple Silicon) · No internet · No API key",
        border_style="cyan"
    ))

    # Load text
    if args.pdf:
        pdf_path = Path(args.pdf)
        if not pdf_path.exists():
            console.print(f"[red]File not found: {pdf_path}[/red]")
            sys.exit(1)
        with console.status("[cyan]Reading document...[/cyan]"):
            raw_text = load_pdf(str(pdf_path))
            chunks   = chunk_text(raw_text)
        console.print(f"[green]✓[/green] Loaded {len(chunks)} chunks from {len(PdfReader(str(pdf_path)).pages)} pages\n")
    else:
        raw_text = args.text
        chunks   = chunk_text(raw_text)

    # Load model
    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    if args.mode == "chat":
        with console.status("[cyan]Building search index...[/cyan]"):
            tfidf_matrix, vocab_idx, idf = build_tfidf(chunks)

        console.print("[dim]Ask questions about your medical document. Type [bold]exit[/bold] to quit.[/dim]\n")
        while True:
            try:
                q = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not q or q.lower() in {"exit", "quit"}:
                break
            relevant = retrieve(q, chunks, tfidf_matrix, vocab_idx, idf)
            context  = "\n\n---\n\n".join(relevant) if relevant else "\n\n".join(chunks[:TOP_K])
            run_explanation(model, tokenizer, "chat", context, question=q)
    else:
        # Use the whole document (take top chunks covering key terms)
        if len(chunks) <= TOP_K * 2:
            context = "\n\n---\n\n".join(chunks)
        else:
            tfidf_matrix, vocab_idx, idf = build_tfidf(chunks)
            key_queries = ["diagnosis result findings measurement laboratory", "medication prescription treatment"]
            seen, top_chunks = set(), []
            for q in key_queries:
                for c in retrieve(q, chunks, tfidf_matrix, vocab_idx, idf, top_k=5):
                    if c not in seen:
                        seen.add(c)
                        top_chunks.append(c)
            context = "\n\n---\n\n".join(top_chunks) if top_chunks else "\n\n".join(chunks[:TOP_K])

        run_explanation(model, tokenizer, args.mode, context)

    console.print("[dim]Nothing was sent to any server.[/dim]")


if __name__ == "__main__":
    main()
