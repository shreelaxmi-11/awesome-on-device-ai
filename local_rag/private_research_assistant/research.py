#!/usr/bin/env python3
"""
Private Research Assistant — Awesome On-Device AI
Drop a folder of papers, docs, or notes. Ask questions across all of them.
Local multi-document RAG — no API key, no cloud, your research stays private.

Usage:
    python research.py --folder ~/papers/
    python research.py --folder ./docs --extensions pdf,md,txt
    python research.py --folder ~/research --question "What methods are used?"
"""

import argparse
import re
import sys
from pathlib import Path

import numpy as np
from mlx_lm import load, stream_generate
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
CHUNK_SIZE    = 400
TOP_K         = 6
MAX_TOKENS    = 800
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def load_file(path: Path) -> str | None:
    if path.stat().st_size > MAX_FILE_SIZE:
        return None
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            pages = [p.extract_text() or "" for p in reader.pages]
            return "\n\n".join(pages)
        except Exception:
            return None
    else:
        for enc in ("utf-8", "latin-1"):
            try:
                return path.read_text(encoding=enc)
            except UnicodeDecodeError:
                continue
    return None


def collect_documents(folder: Path, extensions: list[str]) -> list[dict]:
    ext_set = {f".{e.lstrip('.')}" for e in extensions}
    docs = []
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix.lower() in ext_set:
            text = load_file(p)
            if text and text.strip():
                docs.append({"path": p, "name": p.name, "text": text.strip()})
    return docs


def chunk_documents(docs: list[dict]) -> list[dict]:
    all_chunks = []
    for doc in docs:
        words = doc["text"].split()
        step  = CHUNK_SIZE - 60
        for i in range(0, len(words), step):
            chunk_text = " ".join(words[i:i + CHUNK_SIZE])
            if chunk_text.strip():
                all_chunks.append({
                    "text":     f"[Source: {doc['name']}]\n\n{chunk_text}",
                    "source":   doc["name"],
                    "chunk_id": len(all_chunks),
                })
    return all_chunks


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())


def build_index(chunks: list[dict]):
    corpus    = [c["text"] for c in chunks]
    tokenized = [_tokenize(c) for c in corpus]
    vocab     = sorted({w for doc in tokenized for w in doc})
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    n, V = len(corpus), len(vocab)
    tf = np.zeros((n, V), dtype=np.float32)
    for di, doc in enumerate(tokenized):
        for w in doc:
            tf[di, vocab_idx[w]] += 1
        if tf[di].sum() > 0:
            tf[di] /= tf[di].sum()
    df  = (tf > 0).sum(axis=0).astype(np.float32)
    idf = np.log((n + 1) / (df + 1)) + 1
    tfidf = tf * idf
    norms = np.linalg.norm(tfidf, axis=1, keepdims=True) + 1e-9
    return tfidf / norms, vocab_idx, idf


def retrieve(query: str, chunks, matrix, vocab_idx, idf) -> list[dict]:
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


def answer(model, tokenizer, question: str, relevant: list[dict]) -> str:
    context = "\n\n---\n\n".join(c["text"] for c in relevant)
    sources = list({c["source"] for c in relevant})

    system = (
        "You are a research assistant with access to a private document collection. "
        "Answer questions using only the provided document excerpts. "
        "When citing information, mention which document it came from. "
        "If the answer spans multiple documents, synthesize the information clearly."
    )
    messages = [
        {"role": "system", "content": system + f"\n\nDOCUMENT EXCERPTS:\n{context}"},
        {"role": "user",   "content": question},
    ]
    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        prompt = f"SYSTEM: {system}\nEXCERPTS:\n{context}\nUSER: {question}\nASSISTANT:"

    console.print(f"[dim]Sources: {', '.join(sources[:4])}[/dim]")
    console.print("\n[bold green]Assistant[/bold green]")
    result = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
        token = chunk.text if hasattr(chunk, "text") else chunk
        print(token, end="", flush=True)
        result += token
    print("\n")
    return result.strip()


def main():
    parser = argparse.ArgumentParser(description="Multi-document local RAG research assistant.")
    parser.add_argument("--folder",     required=True, help="Folder containing research documents")
    parser.add_argument("--extensions", default="pdf,md,txt,rst",
                        help="Comma-separated file extensions to index")
    parser.add_argument("--model",      default=DEFAULT_MODEL)
    parser.add_argument("--question",   help="Single question to answer")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.exists():
        console.print(f"[red]Folder not found: {folder}[/red]")
        sys.exit(1)

    extensions = [e.strip() for e in args.extensions.split(",")]

    console.print(Panel.fit(
        f"[bold cyan]🔬 Private Research Assistant[/bold cyan]\n"
        f"[dim]Folder:[/dim] {folder.name} · [dim]Model:[/dim] {args.model.split('/')[-1]}\n"
        "[dim]Runtime:[/dim] MLX · No internet · No API key",
        border_style="cyan"
    ))

    with console.status("[cyan]Scanning documents...[/cyan]"):
        docs = collect_documents(folder, extensions)
    if not docs:
        console.print(f"[yellow]No files found with extensions: {args.extensions}[/yellow]")
        sys.exit(0)
    console.print(f"[green]✓[/green] Found [bold]{len(docs)}[/bold] documents\n")

    # Show document list
    table = Table(show_header=True, header_style="bold cyan", max_width=80)
    table.add_column("Document")
    table.add_column("Words", justify="right")
    for d in docs[:10]:
        table.add_row(d["name"], f"{len(d['text'].split()):,}")
    if len(docs) > 10:
        table.add_row(f"... {len(docs)-10} more", "")
    console.print(table)
    console.print()

    with console.status("[cyan]Chunking and indexing...[/cyan]"):
        chunks = chunk_documents(docs)
        matrix, vocab_idx, idf = build_index(chunks)
    console.print(f"[green]✓[/green] Indexed [bold]{len(chunks)}[/bold] chunks\n")

    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    if args.question:
        relevant = retrieve(args.question, chunks, matrix, vocab_idx, idf)
        answer(model, tokenizer, args.question, relevant)
    else:
        console.print("[dim]Ask questions across your document collection. Type [bold]exit[/bold] to quit.[/dim]\n")
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
            answer(model, tokenizer, q, relevant)


if __name__ == "__main__":
    main()
