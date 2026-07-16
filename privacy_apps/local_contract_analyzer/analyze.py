#!/usr/bin/env python3
"""
Local Contract Analyzer — Awesome On-Device AI
Upload any contract PDF — get a plain-English analysis of key terms,
obligations, risks, and red flags. Runs entirely on your machine.
No API key. No cloud. Your contract never leaves your device.

Usage:
    python analyze.py --pdf contract.pdf
    python analyze.py --pdf nda.pdf --mode summary
    python analyze.py --pdf employment.pdf --mode risks
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
CHUNK_SIZE    = 500   # words
MAX_TOKENS    = 1024
TOP_K         = 5


# ── Analysis modes ─────────────────────────────────────────────────────────────
MODES = {
    "full": {
        "label": "Full Analysis",
        "emoji": "📋",
        "system": (
            "You are an expert contract analyst with legal training. "
            "Analyze contracts clearly for non-lawyers. Be precise but accessible. "
            "Do NOT provide legal advice — flag issues for the reader to verify with counsel."
        ),
        "prompt": (
            "Analyze the following contract excerpts and provide:\n\n"
            "1. **Contract Type & Parties** — What kind of contract is this? Who are the parties?\n"
            "2. **Key Terms** — The most important clauses (payment, duration, deliverables, IP)\n"
            "3. **Obligations** — What does each party have to do?\n"
            "4. **Termination** — How and when can this be ended? Notice period?\n"
            "5. **Liability & Indemnification** — Who is responsible for what?\n"
            "6. **Red Flags** — Any unusual, one-sided, or potentially unfair clauses?\n"
            "7. **Questions to Ask Counsel** — 2-3 things you'd want a lawyer to review\n\n"
            "CONTRACT EXCERPTS:\n{context}"
        ),
    },
    "summary": {
        "label": "Plain-English Summary",
        "emoji": "📝",
        "system": (
            "You are a contract analyst who explains legal documents in plain English. "
            "Be clear, concise, and avoid jargon."
        ),
        "prompt": (
            "Summarize this contract in plain English in 5-7 bullet points. "
            "Cover: what it is, who it's between, what each party gets, key obligations, "
            "how long it lasts, and how it ends.\n\n"
            "CONTRACT EXCERPTS:\n{context}"
        ),
    },
    "risks": {
        "label": "Risk Analysis",
        "emoji": "⚠️",
        "system": (
            "You are a risk-focused contract analyst. Identify clauses that could be "
            "harmful, one-sided, or create unexpected obligations. Be specific."
        ),
        "prompt": (
            "Identify and explain all risky, unusual, or one-sided clauses in this contract. "
            "For each risk:\n"
            "- Quote the relevant clause\n"
            "- Explain why it's risky\n"
            "- Suggest what a fairer version would look like\n\n"
            "CONTRACT EXCERPTS:\n{context}"
        ),
    },
    "chat": {
        "label": "Q&A Chat",
        "emoji": "💬",
        "system": (
            "You are a contract analyst assistant. Answer questions about the contract "
            "accurately using only the excerpts provided. "
            "If the answer isn't in the excerpts, say so. "
            "Do not provide legal advice — note that the user should consult counsel for important decisions."
        ),
        "prompt": "{question}\n\nCONTRACT EXCERPTS:\n{context}",
    },
}


# ── PDF loading + retrieval (TF-IDF, same as pdf_chat) ──────────────────────────

def load_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"[Page {i+1}]\n{text.strip()}")
    full = "\n\n".join(pages)
    if not full.strip():
        console.print("[red]Could not extract text. The PDF may be scanned/image-based.[/red]")
        sys.exit(1)
    return full


def chunk_text(text: str) -> list[str]:
    words = text.split()
    chunks, step = [], CHUNK_SIZE - 80
    for i in range(0, len(words), step):
        c = " ".join(words[i:i + CHUNK_SIZE])
        if c.strip():
            chunks.append(c)
    return chunks


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())


def build_tfidf(chunks: list[str]):
    from math import log
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


# ── Analysis ───────────────────────────────────────────────────────────────────

def run_analysis(model, tokenizer, mode_key: str, context: str, question: str = "") -> str:
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
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        prompt = f"SYSTEM: {mode['system']}\nUSER: {user_content}\nASSISTANT:"

    console.rule(f"[bold]{mode['emoji']} {mode['label']}[/bold]")
    console.print()

    result = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
        token = chunk.text if hasattr(chunk, "text") else chunk
        print(token, end="", flush=True)
        result += token
    print("\n")
    return result.strip()


def main():
    parser = argparse.ArgumentParser(description="Analyze contracts locally using a local LLM.")
    parser.add_argument("--pdf",   required=True, help="Path to the contract PDF")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="MLX model repo")
    parser.add_argument(
        "--mode",
        default="full",
        choices=list(MODES.keys()),
        help="Analysis mode: full, summary, risks, chat"
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        console.print(f"[red]File not found: {pdf_path}[/red]")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold cyan]📋 Local Contract Analyzer[/bold cyan]\n"
        f"[dim]File:[/dim] {pdf_path.name} · "
        f"[dim]Mode:[/dim] {MODES[args.mode]['label']}\n"
        "[dim]Runtime:[/dim] MLX (Apple Silicon) · No internet · No API key\n"
        "[bold yellow]Note: Not legal advice. Consult a lawyer for important decisions.[/bold yellow]",
        border_style="cyan"
    ))

    # Load PDF
    with console.status("[cyan]Reading contract...[/cyan]"):
        text = load_pdf(str(pdf_path))
        chunks = chunk_text(text)
    console.print(f"[green]✓[/green] Loaded {len(chunks)} chunks from {len(PdfReader(str(pdf_path)).pages)} pages\n")

    # Build index
    with console.status("[cyan]Building search index...[/cyan]"):
        tfidf_matrix, vocab_idx, idf = build_tfidf(chunks)

    # Load model
    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    if args.mode == "chat":
        # Q&A chat loop
        console.print("[dim]Ask questions about your contract. Type [bold]exit[/bold] to quit.[/dim]\n")
        history: list[dict] = []
        while True:
            try:
                q = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
            except (KeyboardInterrupt, EOFError):
                console.print("\n[dim]Goodbye.[/dim]")
                break
            if not q:
                continue
            if q.lower() in {"exit", "quit", "q"}:
                break

            relevant = retrieve(q, chunks, tfidf_matrix, vocab_idx, idf)
            context = "\n\n---\n\n".join(relevant) if relevant else "\n\n".join(chunks[:TOP_K])
            run_analysis(model, tokenizer, "chat", context, question=q)
    else:
        # For full analysis / summary / risks — use the whole doc (top chunks for key terms)
        # Query with broad terms to pull the most important sections
        key_queries = [
            "payment fees compensation",
            "termination notice cancellation",
            "liability indemnification damages",
            "intellectual property ownership rights",
            "obligations responsibilities duties",
            "confidentiality non-disclosure",
            "governing law jurisdiction dispute",
        ]
        seen, all_chunks = set(), []
        for q in key_queries:
            for c in retrieve(q, chunks, tfidf_matrix, vocab_idx, idf, top_k=2):
                if c not in seen:
                    seen.add(c)
                    all_chunks.append(c)
            if len(all_chunks) >= 12:
                break

        context = "\n\n---\n\n".join(all_chunks)
        run_analysis(model, tokenizer, args.mode, context)

    console.print("[dim]Nothing was sent to any server.[/dim]")


if __name__ == "__main__":
    main()
