#!/usr/bin/env python3
"""
Chat with Notion Export — Awesome On-Device AI
Export your Notion workspace and chat with your own notes privately.
Loads all markdown files from a Notion export folder, indexes them,
lets you ask questions across your entire knowledge base.
No API key. No cloud. Your notes stay on your machine.

Usage:
    # Export from Notion: Settings → Export → Markdown & CSV
    python chat.py --folder ~/Downloads/Notion_export/
    python chat.py --folder ~/notion --question "What are my meeting notes from last week?"
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

console = Console()

DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
CHUNK_SIZE    = 350
TOP_K         = 6
MAX_TOKENS    = 700


def load_notion_export(folder: Path) -> list[dict]:
    """Load all markdown files from Notion export."""
    docs = []
    for p in folder.rglob("*.md"):
        try:
            text = p.read_text(encoding="utf-8").strip()
            if text:
                # Use the filename as the page title (Notion export format)
                title = p.stem.replace("-", " ").replace("_", " ")
                docs.append({"title": title, "path": str(p.relative_to(folder)), "text": text})
        except UnicodeDecodeError:
            continue
    return docs


def chunk_documents(docs: list[dict]) -> list[dict]:
    all_chunks = []
    for doc in docs:
        words = doc["text"].split()
        step  = CHUNK_SIZE - 50
        for i in range(0, len(words), step):
            chunk_text = " ".join(words[i:i + CHUNK_SIZE])
            if chunk_text.strip():
                all_chunks.append({
                    "text":   f"[Page: {doc['title']}]\n\n{chunk_text}",
                    "source": doc["title"],
                    "path":   doc["path"],
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


def answer_question(model, tokenizer, question: str, relevant: list[dict]) -> str:
    context = "\n\n---\n\n".join(c["text"] for c in relevant)
    sources = list({c["source"] for c in relevant})

    system = (
        "You are a personal assistant with access to the user's Notion notes. "
        "Answer questions using only the provided note excerpts. "
        "Mention which Notion page the information came from when relevant. "
        "If the answer isn't in the notes, say so."
    )
    messages = [
        {"role": "system", "content": system + f"\n\nNOTION EXCERPTS:\n{context}"},
        {"role": "user",   "content": question},
    ]
    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        prompt = f"SYSTEM: {system}\nEXCERPTS:\n{context}\nUSER: {question}\nASSISTANT:"

    console.print(f"[dim]Sources: {', '.join(sources[:3])}[/dim]")
    console.print("\n[bold green]Assistant[/bold green]")
    result = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
        token = chunk.text if hasattr(chunk, "text") else chunk
        print(token, end="", flush=True)
        result += token
    print("\n")
    return result.strip()


def main():
    parser = argparse.ArgumentParser(description="Chat with your Notion export locally.")
    parser.add_argument("--folder",   required=True, help="Path to Notion export folder")
    parser.add_argument("--model",    default=DEFAULT_MODEL)
    parser.add_argument("--question", help="Single question to answer")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.exists():
        console.print(f"[red]Folder not found: {folder}[/red]")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold cyan]📓 Chat with Notion Export[/bold cyan]\n"
        f"[dim]Folder:[/dim] {folder.name}\n"
        "[dim]Runtime:[/dim] MLX · No internet · No API key",
        border_style="cyan"
    ))

    with console.status("[cyan]Loading Notion export...[/cyan]"):
        docs = load_notion_export(folder)
    if not docs:
        console.print("[yellow]No markdown files found. Export from Notion as Markdown & CSV.[/yellow]")
        sys.exit(0)
    console.print(f"[green]✓[/green] Loaded [bold]{len(docs)}[/bold] Notion pages\n")

    with console.status("[cyan]Indexing...[/cyan]"):
        chunks = chunk_documents(docs)
        matrix, vocab_idx, idf = build_index(chunks)
    console.print(f"[green]✓[/green] Indexed {len(chunks)} chunks\n")

    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    if args.question:
        relevant = retrieve(args.question, chunks, matrix, vocab_idx, idf)
        answer_question(model, tokenizer, args.question, relevant)
    else:
        console.print("[dim]Ask questions about your Notion workspace. Type [bold]exit[/bold] to quit.[/dim]\n")
        while True:
            try:
                q = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not q or q.lower() in {"exit", "quit"}:
                break
            relevant = retrieve(q, chunks, matrix, vocab_idx, idf)
            if not relevant:
                console.print("[yellow]Nothing found in your notes for that query.[/yellow]\n")
                continue
            answer_question(model, tokenizer, q, relevant)


if __name__ == "__main__":
    main()
