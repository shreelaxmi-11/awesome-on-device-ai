#!/usr/bin/env python3
"""
Local PDF RAG — Awesome On-Device AI
Full RAG pipeline: PDF → chunks → TF-IDF index → retrieve → local LLM answer.
Single-shot Q&A mode (for batch questions) vs chat mode (interactive).
No API key. No vector database. No cloud.

Usage:
    python rag.py --pdf document.pdf --question "What is the main finding?"
    python rag.py --pdf report.pdf --chat
    python rag.py --pdf paper.pdf --questions questions.txt
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

console = Console()

DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
CHUNK_SIZE    = 400
TOP_K         = 5
MAX_TOKENS    = 512


def load_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"[Page {i+1}]\n{text.strip()}")
    return "\n\n".join(pages)


def chunk_text(text: str) -> list[str]:
    words = text.split()
    chunks, step = [], CHUNK_SIZE - 50
    for i in range(0, len(words), step):
        c = " ".join(words[i:i + CHUNK_SIZE])
        if c.strip():
            chunks.append(c)
    return chunks


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())


def build_index(chunks: list[str]):
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
    return tfidf / norms, vocab_idx, idf


def retrieve(query: str, chunks, matrix, vocab_idx, idf) -> list[str]:
    V = matrix.shape[1]
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
    scores = matrix @ q_vec
    top_idx = np.argsort(scores)[::-1][:TOP_K]
    return [chunks[i] for i in top_idx if scores[i] > 0]


def answer(model, tokenizer, question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    system  = (
        "You are a helpful assistant that answers questions about a document. "
        "Use only the provided excerpts. If the answer isn't there, say so."
    )
    messages = [
        {"role": "system", "content": system + f"\n\nDOCUMENT EXCERPTS:\n{context}"},
        {"role": "user",   "content": question},
    ]
    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        prompt = f"SYSTEM: {system}\nEXCERPTS:\n{context}\nUSER: {question}\nASSISTANT:"

    result = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
        token = chunk.text if hasattr(chunk, "text") else chunk
        print(token, end="", flush=True)
        result += token
    print("\n")
    return result.strip()


def main():
    parser = argparse.ArgumentParser(description="Local PDF RAG pipeline.")
    parser.add_argument("--pdf",       required=True)
    parser.add_argument("--question",  help="Single question to answer")
    parser.add_argument("--questions", help="File with one question per line")
    parser.add_argument("--chat",      action="store_true", help="Interactive chat mode")
    parser.add_argument("--model",     default=DEFAULT_MODEL)
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        console.print(f"[red]File not found: {pdf_path}[/red]")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold cyan]📚 Local PDF RAG[/bold cyan]\n"
        f"[dim]File:[/dim] {pdf_path.name} · [dim]Model:[/dim] {args.model.split('/')[-1]}\n"
        "[dim]Runtime:[/dim] MLX · No internet · No API key",
        border_style="cyan"
    ))

    with console.status("[cyan]Loading and indexing PDF...[/cyan]"):
        text   = load_pdf(str(pdf_path))
        chunks = chunk_text(text)
        matrix, vocab_idx, idf = build_index(chunks)
    console.print(f"[green]✓[/green] Indexed {len(chunks)} chunks\n")

    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    if args.question:
        relevant = retrieve(args.question, chunks, matrix, vocab_idx, idf)
        console.print(f"[bold green]Answer[/bold green]")
        answer(model, tokenizer, args.question, relevant)

    elif args.questions:
        questions = [l.strip() for l in Path(args.questions).read_text().splitlines() if l.strip()]
        for q in questions:
            console.print(f"\n[bold cyan]Q:[/bold cyan] {q}")
            relevant = retrieve(q, chunks, matrix, vocab_idx, idf)
            answer(model, tokenizer, q, relevant)

    else:
        console.print("[dim]Ask questions about your document. Type [bold]exit[/bold] to quit.[/dim]\n")
        while True:
            try:
                q = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not q or q.lower() in {"exit", "quit"}:
                break
            relevant = retrieve(q, chunks, matrix, vocab_idx, idf)
            if not relevant:
                console.print("[yellow]No relevant content found.[/yellow]\n")
                continue
            console.print("\n[bold green]Assistant[/bold green]")
            answer(model, tokenizer, q, relevant)


if __name__ == "__main__":
    main()
