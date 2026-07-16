#!/usr/bin/env python3
"""
Chat with CSV — Awesome On-Device AI
Ask questions about any CSV file in plain English. Local LLM answers using
the actual data. No API key. No cloud. Your data never leaves your machine.

Usage:
    python chat.py --csv sales_data.csv
    python chat.py --csv employees.csv --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
"""

import argparse
import io
import sys
from pathlib import Path

import pandas as pd
from mlx_lm import load, stream_generate
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
MAX_TOKENS    = 800
MAX_ROWS_IN_CONTEXT = 200   # rows to include in prompt (larger CSVs get a sample)


def load_csv(path: str) -> pd.DataFrame:
    """Load CSV with encoding fallback."""
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            df = pd.read_csv(path, encoding=enc)
            return df
        except UnicodeDecodeError:
            continue
    console.print("[red]Could not read the CSV file — try converting it to UTF-8 first.[/red]")
    sys.exit(1)


def describe_dataframe(df: pd.DataFrame) -> str:
    """Build a rich text description of the dataframe for the LLM."""
    buf = io.StringIO()

    buf.write(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n\n")

    # Column info
    buf.write("Columns:\n")
    for col in df.columns:
        dtype = str(df[col].dtype)
        n_unique = df[col].nunique()
        n_null = df[col].isna().sum()
        sample_vals = df[col].dropna().head(3).tolist()
        buf.write(f"  - {col} ({dtype}): {n_unique} unique values, {n_null} nulls. "
                  f"Sample: {sample_vals}\n")

    # Numeric stats
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        buf.write("\nNumeric summary:\n")
        buf.write(df[numeric_cols].describe().to_string())
        buf.write("\n")

    return buf.getvalue()


def get_data_context(df: pd.DataFrame) -> str:
    """Return the data as a CSV string, sampling if too large."""
    if len(df) <= MAX_ROWS_IN_CONTEXT:
        return df.to_csv(index=False)
    else:
        sample = df.sample(MAX_ROWS_IN_CONTEXT, random_state=42)
        return (
            f"[Note: CSV has {len(df)} rows; showing a random sample of {MAX_ROWS_IN_CONTEXT}]\n"
            + sample.to_csv(index=False)
        )


def build_system_prompt(df: pd.DataFrame, filename: str) -> str:
    description = describe_dataframe(df)
    data_context = get_data_context(df)

    return (
        f"You are a data analyst assistant. You have been given a CSV file called '{filename}'.\n\n"
        "DATASET DESCRIPTION:\n"
        f"{description}\n\n"
        "FULL DATA (or representative sample):\n"
        f"{data_context}\n\n"
        "Answer questions about this data accurately and concisely. "
        "When computing statistics, use the actual numbers from the data. "
        "If a question requires computation you cannot do precisely, give your best estimate "
        "and say so. If the question cannot be answered from this data, say so clearly."
    )


def show_preview(df: pd.DataFrame):
    """Show a rich table preview of the first 5 rows."""
    table = Table(show_header=True, header_style="bold cyan", max_width=120)
    for col in df.columns:
        table.add_column(str(col), no_wrap=True)
    for _, row in df.head(5).iterrows():
        table.add_row(*[str(v) for v in row.values])
    console.print(table)
    if len(df) > 5:
        console.print(f"[dim]... {len(df) - 5} more rows[/dim]\n")


def main():
    parser = argparse.ArgumentParser(description="Chat with any CSV file using a local LLM.")
    parser.add_argument("--csv",   required=True, help="Path to the CSV file")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="MLX model repo")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        console.print(f"[red]File not found: {csv_path}[/red]")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold cyan]📊 Chat with CSV[/bold cyan]\n"
        f"[dim]File:[/dim] {csv_path.name} · "
        f"[dim]Model:[/dim] {args.model.split('/')[-1]}\n"
        "[dim]Runtime:[/dim] MLX (Apple Silicon) · No internet · No API key",
        border_style="cyan"
    ))

    # Load data
    with console.status("[cyan]Loading CSV...[/cyan]"):
        df = load_csv(str(csv_path))
    console.print(f"[green]✓[/green] Loaded [bold]{len(df):,} rows × {len(df.columns)} columns[/bold]\n")
    show_preview(df)

    # Load model
    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    system_prompt = build_system_prompt(df, csv_path.name)
    history: list[dict] = []

    console.print("[dim]Ask questions about your data. Type [bold]exit[/bold] to quit.[/dim]\n")
    console.print("[dim]Example questions:[/dim]")
    console.print("[dim]  • What is the average value of [column]?[/dim]")
    console.print("[dim]  • Which row has the highest [column]?[/dim]")
    console.print("[dim]  • How many unique values are there in [column]?[/dim]\n")

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

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-6:])
        messages.append({"role": "user", "content": query})

        if hasattr(tokenizer, "apply_chat_template"):
            prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            prompt = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
            prompt += "\nASSISTANT:"

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
