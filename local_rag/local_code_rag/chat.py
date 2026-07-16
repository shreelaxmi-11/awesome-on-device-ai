#!/usr/bin/env python3
"""
Local Code RAG — Awesome On-Device AI
Index any codebase and ask questions about it in plain English.
No API key. No cloud. Your source code never leaves your machine.

Usage:
    python chat.py --repo /path/to/your/project
    python chat.py --repo . --extensions py,js,ts
    python chat.py --repo ~/my-project --model mlx-community/Phi-3.5-mini-instruct-4bit
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
from rich.syntax import Syntax

console = Console()

DEFAULT_MODEL      = "mlx-community/Phi-3.5-mini-instruct-4bit"  # code-focused
DEFAULT_EXTENSIONS = ["py", "js", "ts", "tsx", "jsx", "go", "rs", "java", "cpp", "c", "h",
                      "rb", "swift", "kt", "sh", "yaml", "yml", "json", "toml", "md"]
MAX_FILE_SIZE_KB   = 100     # skip very large files
CHUNK_SIZE         = 300     # words per chunk
TOP_K              = 6
MAX_TOKENS         = 1024

# Files/dirs to skip
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "env", ".env",
             "dist", "build", ".next", ".nuxt", "target", "vendor", ".idea", ".vscode"}
SKIP_FILES = {"package-lock.json", "yarn.lock", "Pipfile.lock", "poetry.lock"}


def collect_files(repo_path: Path, extensions: list[str]) -> list[Path]:
    """Recursively collect all code files in the repo."""
    files = []
    ext_set = {f".{e.lower()}" for e in extensions}

    for p in repo_path.rglob("*"):
        # Skip hidden dirs and known noise dirs
        if any(part.startswith(".") or part in SKIP_DIRS for part in p.parts):
            continue
        if p.name in SKIP_FILES:
            continue
        if not p.is_file():
            continue
        if p.suffix.lower() not in ext_set:
            continue
        if p.stat().st_size > MAX_FILE_SIZE_KB * 1024:
            continue
        files.append(p)

    return sorted(files)


def file_to_chunks(file_path: Path, repo_root: Path) -> list[dict]:
    """Split a file into chunks with metadata."""
    try:
        content = file_path.read_text(errors="replace")
    except Exception:
        return []

    rel_path = str(file_path.relative_to(repo_root))
    words = content.split()

    if not words:
        return []

    chunks = []
    step = max(1, CHUNK_SIZE - 50)
    for i in range(0, len(words), step):
        chunk_words = words[i:i + CHUNK_SIZE]
        chunk_text  = " ".join(chunk_words)
        # Compute which lines this chunk covers (approximate)
        char_offset = len(" ".join(words[:i]))
        line_start  = content[:char_offset].count("\n") + 1
        chunks.append({
            "text":     f"# File: {rel_path} (around line {line_start})\n\n{chunk_text}",
            "file":     rel_path,
            "line":     line_start,
        })

    return chunks


def _tokenize(text: str) -> list[str]:
    # Include camelCase/snake_case splitting for code identifiers
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)  # camelCase → camel Case
    text = re.sub(r"[_\-./]", " ", text)               # snake_case, paths
    return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())


def build_tfidf(chunks: list[dict]):
    corpus = [c["text"] for c in chunks]
    tokenized = [_tokenize(c) for c in corpus]
    vocab = sorted({w for doc in tokenized for w in doc})
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    n, V = len(corpus), len(vocab)

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


def retrieve(query: str, chunks: list[dict], tfidf_matrix, vocab_idx, idf) -> list[dict]:
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
    top_idx = np.argsort(scores)[::-1][:TOP_K]
    return [chunks[i] for i in top_idx if scores[i] > 0]


def main():
    parser = argparse.ArgumentParser(description="Chat with your codebase using a local LLM.")
    parser.add_argument("--repo",       required=True, help="Path to the code repository")
    parser.add_argument("--model",      default=DEFAULT_MODEL, help="MLX model repo")
    parser.add_argument(
        "--extensions",
        default=",".join(DEFAULT_EXTENSIONS),
        help="Comma-separated file extensions to index"
    )
    args = parser.parse_args()

    repo_path = Path(args.repo).expanduser().resolve()
    if not repo_path.exists():
        console.print(f"[red]Path not found: {repo_path}[/red]")
        sys.exit(1)

    extensions = [e.strip().lstrip(".") for e in args.extensions.split(",")]

    console.print(Panel.fit(
        f"[bold cyan]💻 Local Code RAG[/bold cyan]\n"
        f"[dim]Repo:[/dim] {repo_path.name} · "
        f"[dim]Model:[/dim] {args.model.split('/')[-1]}\n"
        "[dim]Runtime:[/dim] MLX (Apple Silicon) · No internet · No API key",
        border_style="cyan"
    ))

    # Collect and index files
    with console.status("[cyan]Scanning repository...[/cyan]"):
        files = collect_files(repo_path, extensions)
    console.print(f"[green]✓[/green] Found [bold]{len(files)}[/bold] files\n")

    if not files:
        console.print("[yellow]No matching files found. Check --extensions.[/yellow]")
        sys.exit(0)

    with console.status("[cyan]Chunking files...[/cyan]"):
        all_chunks = []
        for f in files:
            all_chunks.extend(file_to_chunks(f, repo_path))
    console.print(f"[green]✓[/green] Indexed [bold]{len(all_chunks)}[/bold] chunks from {len(files)} files\n")

    with console.status("[cyan]Building search index...[/cyan]"):
        tfidf_matrix, vocab_idx, idf = build_tfidf(all_chunks)
    console.print(f"[green]✓[/green] Search index ready\n")

    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    system = (
        f"You are a senior software engineer who has read and understands the entire codebase at '{repo_path.name}'. "
        "Answer questions about the code using only the excerpts provided. "
        "When referencing code, mention the file name and approximate line number. "
        "Be precise, technical, and helpful."
    )

    console.print("[dim]Ask questions about your codebase. Type [bold]exit[/bold] to quit.[/dim]")
    console.print("[dim]Examples:[/dim]")
    console.print("[dim]  • Where is the authentication logic?[/dim]")
    console.print("[dim]  • How does the data pipeline work?[/dim]")
    console.print("[dim]  • What does the process_user function do?[/dim]\n")

    history: list[dict] = []

    while True:
        try:
            query = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not query:
            continue
        if query.lower() in {"exit", "quit", "q"}:
            break

        relevant = retrieve(query, all_chunks, tfidf_matrix, vocab_idx, idf)
        if not relevant:
            console.print("[yellow]No relevant code found for that query.[/yellow]\n")
            continue

        context = "\n\n---\n\n".join(c["text"] for c in relevant)
        sources = list({c["file"] for c in relevant})

        messages = [
            {"role": "system", "content": system + f"\n\nCODE EXCERPTS:\n{context}"}
        ]
        messages.extend(history[-6:])
        messages.append({"role": "user", "content": query})

        if hasattr(tokenizer, "apply_chat_template"):
            prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            prompt = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
            prompt += "\nASSISTANT:"

        console.print(f"\n[dim]Sources: {', '.join(sources[:4])}[/dim]")
        console.print("\n[bold green]Assistant[/bold green]")
        response_text = ""
        for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS):
            token = chunk.text if hasattr(chunk, "text") else chunk
            print(token, end="", flush=True)
            response_text += token
        print("\n")

        history.append({"role": "user",      "content": query})
        history.append({"role": "assistant", "content": response_text.strip()})


if __name__ == "__main__":
    main()
