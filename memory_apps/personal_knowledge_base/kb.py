#!/usr/bin/env python3
"""
Personal Knowledge Base — Awesome On-Device AI
Add notes, ideas, and documents over time. Build a private local knowledge base
you can query with natural language. Stored as plain JSON + markdown on disk.
No API key. No cloud. No telemetry.

Usage:
    python kb.py add "The key to good prompts is specificity and examples"
    python kb.py add --file notes.md --tag "prompting"
    python kb.py search "what do I know about prompting?"
    python kb.py chat
    python kb.py list
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
from mlx_lm import load, stream_generate
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

DEFAULT_MODEL  = "mlx-community/Llama-3.2-3B-Instruct-4bit"
DEFAULT_KB_DIR = Path.home() / ".personal_knowledge_base"
MAX_TOKENS     = 700
CHUNK_SIZE     = 200


def load_kb(kb_dir: Path) -> list[dict]:
    index_path = kb_dir / "index.json"
    if index_path.exists():
        return json.loads(index_path.read_text())
    return []


def save_kb(kb_dir: Path, entries: list[dict]):
    kb_dir.mkdir(parents=True, exist_ok=True)
    (kb_dir / "index.json").write_text(json.dumps(entries, indent=2))


def add_entry(kb_dir: Path, entries: list[dict], text: str, tags: list[str], source: str = "") -> dict:
    entry = {
        "id":        len(entries) + 1,
        "text":      text.strip(),
        "tags":      tags,
        "source":    source,
        "created":   datetime.now().isoformat(),
        "words":     len(text.split()),
    }
    entries.append(entry)
    save_kb(kb_dir, entries)
    return entry


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())


def build_index(entries: list[dict]):
    if not entries:
        return None, None, None
    corpus    = [e["text"] + " " + " ".join(e.get("tags", [])) for e in entries]
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


def retrieve(query: str, entries, matrix, vocab_idx, idf, top_k=5) -> list[dict]:
    if matrix is None:
        return []
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
    top_idx = np.argsort(scores)[::-1][:top_k]
    return [entries[i] for i in top_idx if scores[i] > 0.05]


def chat_with_kb(model, tokenizer, entries, matrix, vocab_idx, idf):
    system = (
        "You are a personal knowledge assistant with access to the user's private notes. "
        "Answer questions using only the provided knowledge base excerpts. "
        "Be helpful, concise, and reference specific notes when relevant."
    )
    console.print("[dim]Ask questions about your knowledge base. Type [bold]exit[/bold] to quit.[/dim]\n")

    while True:
        try:
            q = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not q or q.lower() in {"exit", "quit"}:
            break

        relevant = retrieve(q, entries, matrix, vocab_idx, idf)
        if not relevant:
            console.print("[yellow]Nothing relevant found in your knowledge base.[/yellow]\n")
            continue

        context = "\n\n---\n\n".join(
            f"[Note #{e['id']} · {e['created'][:10]}]\n{e['text']}"
            for e in relevant
        )
        messages = [
            {"role": "system", "content": system + f"\n\nKNOWLEDGE BASE:\n{context}"},
            {"role": "user",   "content": q},
        ]
        if hasattr(tokenizer, "apply_chat_template"):
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            prompt = f"SYSTEM: {system}\nKB:\n{context}\nUSER: {q}\nASSISTANT:"

        console.print("\n[bold green]Assistant[/bold green]")
        result = ""
        for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
            token = chunk.text if hasattr(chunk, "text") else chunk
            print(token, end="", flush=True)
            result += token
        print("\n")


def main():
    parser = argparse.ArgumentParser(description="Personal local knowledge base.")
    subparsers = parser.add_subparsers(dest="command")

    # add
    add_p = subparsers.add_parser("add", help="Add a note to the knowledge base")
    add_p.add_argument("text",   nargs="?", help="Note text")
    add_p.add_argument("--file", help="Add a markdown or text file")
    add_p.add_argument("--tag",  action="append", default=[], dest="tags", help="Add tags")

    # search
    search_p = subparsers.add_parser("search", help="Search the knowledge base")
    search_p.add_argument("query", help="Search query")

    # chat
    subparsers.add_parser("chat", help="Chat with your knowledge base")

    # list
    subparsers.add_parser("list", help="List all entries")

    parser.add_argument("--model",   default=DEFAULT_MODEL)
    parser.add_argument("--kb-dir",  default=str(DEFAULT_KB_DIR))
    args = parser.parse_args()

    kb_dir  = Path(args.kb_dir)
    entries = load_kb(kb_dir)

    if args.command == "add":
        if args.file:
            text = Path(args.file).read_text()
            source = args.file
        elif args.text:
            text = args.text
            source = "manual"
        else:
            console.print("[dim]Enter your note (Ctrl+D or blank line×2 to finish):[/dim]\n")
            lines, blank = [], 0
            while True:
                try:
                    line = input()
                except EOFError:
                    break
                if line == "":
                    blank += 1
                    if blank >= 2:
                        break
                else:
                    blank = 0
                    lines.append(line)
            text   = "\n".join(lines).strip()
            source = "manual"

        if not text:
            console.print("[red]No text provided.[/red]")
            sys.exit(1)

        entry = add_entry(kb_dir, entries, text, args.tags, source)
        console.print(f"[green]✓[/green] Added note #{entry['id']} ({entry['words']} words)"
                      + (f" · tags: {', '.join(args.tags)}" if args.tags else ""))

    elif args.command == "list":
        if not entries:
            console.print("[dim]No entries yet. Use `python kb.py add` to add notes.[/dim]")
            return
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#",    width=4)
        table.add_column("Date", width=12)
        table.add_column("Tags", width=20)
        table.add_column("Preview")
        for e in entries:
            preview = e["text"][:60].replace("\n", " ")
            if len(e["text"]) > 60:
                preview += "..."
            table.add_row(str(e["id"]), e["created"][:10], ", ".join(e.get("tags", [])), preview)
        console.print(table)
        console.print(f"\n[dim]{len(entries)} entries · {sum(e['words'] for e in entries):,} total words[/dim]")

    elif args.command == "search":
        if not entries:
            console.print("[dim]Knowledge base is empty.[/dim]")
            return
        matrix, vocab_idx, idf = build_index(entries)
        results = retrieve(args.query, entries, matrix, vocab_idx, idf)
        if not results:
            console.print("[yellow]No relevant entries found.[/yellow]")
            return
        for e in results:
            console.print(Panel(
                e["text"][:300] + ("..." if len(e["text"]) > 300 else ""),
                title=f"#{e['id']} · {e['created'][:10]}" +
                      (f" · {', '.join(e['tags'])}" if e.get("tags") else ""),
                border_style="cyan"
            ))

    elif args.command == "chat":
        if not entries:
            console.print("[dim]Knowledge base is empty. Add notes first.[/dim]")
            return
        matrix, vocab_idx, idf = build_index(entries)
        with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
            model, tokenizer = load(args.model)
        chat_with_kb(model, tokenizer, entries, matrix, vocab_idx, idf)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
