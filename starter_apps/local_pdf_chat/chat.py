#!/usr/bin/env python3
"""
Local PDF Chat — Awesome On-Device AI
Chat with any PDF entirely on-device. No API key. No internet. No data leaving your machine.

Usage:
    python chat.py --pdf your_document.pdf
    python chat.py --pdf contract.pdf --model mlx-community/Llama-3.2-3B-Instruct-4bit
"""

import argparse
import sys
import re
from pathlib import Path

import numpy as np
from pypdf import PdfReader
from mlx_lm import load, generate, stream_generate
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich import print as rprint

console = Console()

# ── Default model ──────────────────────────────────────────────────────────────
DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
CHUNK_SIZE    = 400    # words per chunk
TOP_K         = 4      # chunks to retrieve per query
MAX_TOKENS    = 512    # max tokens in model response


# ── PDF loading ─────────────────────────────────────────────────────────────────

def load_pdf(path: str) -> str:
    """Extract all text from a PDF file."""
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"[Page {i+1}]\n{text.strip()}")
    full_text = "\n\n".join(pages)
    if not full_text.strip():
        console.print("[red]Could not extract text from this PDF. It may be scanned or image-based.[/red]")
        sys.exit(1)
    return full_text


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """Split text into overlapping word-level chunks."""
    words = text.split()
    chunks = []
    step = chunk_size - 50  # 50-word overlap between chunks
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


# ── Retrieval (TF-IDF cosine similarity, no external dependencies) ──────────────

def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())


def _build_tfidf(chunks: list[str]):
    """Build a minimal TF-IDF index over the chunks."""
    from math import log

    tokenized = [_tokenize(c) for c in chunks]
    vocab = sorted({w for doc in tokenized for w in doc})
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    n = len(chunks)
    V = len(vocab)

    # Term frequency matrix
    tf = np.zeros((n, V), dtype=np.float32)
    for di, doc in enumerate(tokenized):
        for w in doc:
            tf[di, vocab_idx[w]] += 1
        if tf[di].sum() > 0:
            tf[di] /= tf[di].sum()

    # IDF
    df = (tf > 0).sum(axis=0).astype(np.float32)
    idf = np.log((n + 1) / (df + 1)) + 1

    tfidf = tf * idf

    # L2-normalise rows
    norms = np.linalg.norm(tfidf, axis=1, keepdims=True) + 1e-9
    tfidf /= norms

    return tfidf, vocab_idx, idf


def retrieve(query: str, chunks: list[str], tfidf_matrix, vocab_idx, idf,
             top_k: int = TOP_K) -> list[str]:
    """Return the top-k most relevant chunks for the query."""
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
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [chunks[i] for i in top_indices if scores[i] > 0]


# ── Prompt building ─────────────────────────────────────────────────────────────

def build_prompt(query: str, context_chunks: list[str], history: list[dict]) -> list[dict]:
    """Build the MLX chat message list."""
    context = "\n\n---\n\n".join(context_chunks)

    system = (
        "You are a helpful assistant that answers questions about a document. "
        "Use only the document excerpts provided below. "
        "If the answer is not in the excerpts, say so honestly. "
        "Be concise and accurate.\n\n"
        f"DOCUMENT EXCERPTS:\n{context}"
    )

    messages = [{"role": "system", "content": system}]
    messages.extend(history[-6:])  # keep last 3 exchanges for context
    messages.append({"role": "user", "content": query})
    return messages


# ── Main chat loop ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Chat with any PDF locally using MLX.")
    parser.add_argument("--pdf",   required=True, help="Path to the PDF file")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="MLX model repo on HuggingFace")
    parser.add_argument("--top-k", type=int, default=TOP_K, help="Chunks to retrieve per query")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        console.print(f"[red]File not found: {pdf_path}[/red]")
        sys.exit(1)

    # ── Header ──
    console.print(Panel.fit(
        f"[bold cyan]🔒 Local PDF Chat[/bold cyan]\n"
        f"[dim]PDF:[/dim] {pdf_path.name}\n"
        f"[dim]Model:[/dim] {args.model}\n"
        f"[dim]Runtime:[/dim] MLX (Apple Silicon) · No internet · No API key",
        border_style="cyan"
    ))

    # ── Load PDF ──
    with console.status("[cyan]Reading PDF...[/cyan]"):
        text = load_pdf(str(pdf_path))
        chunks = chunk_text(text)
    console.print(f"[green]✓[/green] Loaded {len(chunks)} chunks from {len(PdfReader(str(pdf_path)).pages)} pages\n")

    # ── Build index ──
    with console.status("[cyan]Building search index...[/cyan]"):
        tfidf_matrix, vocab_idx, idf = _build_tfidf(chunks)
    console.print(f"[green]✓[/green] Search index ready ({len(vocab_idx):,} terms)\n")

    # ── Load model ──
    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    console.print("[dim]Type your question and press Enter. Type [bold]exit[/bold] to quit.[/dim]\n")

    history = []

    while True:
        try:
            query = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not query:
            continue
        if query.lower() in {"exit", "quit", "q"}:
            console.print("[dim]Goodbye.[/dim]")
            break

        # Retrieve relevant chunks
        relevant = retrieve(query, chunks, tfidf_matrix, vocab_idx, idf, top_k=args.top_k)
        if not relevant:
            console.print("[yellow]No relevant content found in the document for this query.[/yellow]\n")
            continue

        # Build messages
        messages = build_prompt(query, relevant, history)

        # Apply chat template
        if hasattr(tokenizer, "apply_chat_template"):
            prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            prompt = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
            prompt += "\nASSISTANT:"

        # Stream response
        console.print("\n[bold green]Assistant[/bold green]")
        response_text = ""
        for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
            token = chunk.text if hasattr(chunk, "text") else chunk
            print(token, end="", flush=True)
            response_text += token
        print("\n")

        # Update history
        history.append({"role": "user",      "content": query})
        history.append({"role": "assistant", "content": response_text.strip()})


if __name__ == "__main__":
    main()
