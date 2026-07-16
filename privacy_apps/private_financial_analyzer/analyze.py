#!/usr/bin/env python3
"""
Private Financial Analyzer — Awesome On-Device AI
Load your bank statements or transaction CSVs — get spending analysis,
category breakdowns, and budgeting insights. No API key. No cloud.
Your financial data never leaves your machine.

Usage:
    python analyze.py --csv transactions.csv
    python analyze.py --csv bank_export.csv --mode budget
    python analyze.py --csv spending.csv --mode chat
"""

import argparse
import io
import sys
from pathlib import Path

import pandas as pd
import numpy as np
from mlx_lm import load, stream_generate
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.rule import Rule

console = Console()

DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
MAX_TOKENS    = 1024

# ── Analysis modes ─────────────────────────────────────────────────────────────
MODES = {
    "overview": {
        "label": "Spending Overview",
        "emoji": "📊",
        "prompt": (
            "Analyze this financial data and provide:\n\n"
            "1. **Total spending** for the period\n"
            "2. **Top spending categories** (by amount and %, with amounts)\n"
            "3. **Largest individual transactions** (top 5)\n"
            "4. **Spending trends** — any notable patterns over time?\n"
            "5. **Quick insights** — 2-3 observations about spending behavior\n\n"
            "DATA:\n{data}"
        ),
        "system": "You are a personal finance analyst. Be specific with dollar amounts and percentages.",
    },
    "budget": {
        "label": "Budget Analysis",
        "emoji": "💰",
        "prompt": (
            "Analyze this spending data from a budgeting perspective:\n\n"
            "1. **Fixed vs variable expenses** — categorize and total each\n"
            "2. **Recurring payments** — identify subscriptions or regular bills\n"
            "3. **Discretionary spending** — what's optional vs necessary?\n"
            "4. **Where to cut** — top 3 specific areas with potential savings\n"
            "5. **50/30/20 breakdown** — how does spending align with needs/wants/savings?\n\n"
            "DATA:\n{data}"
        ),
        "system": (
            "You are a certified financial planner helping someone understand their spending. "
            "Be specific, practical, and non-judgmental. Give actionable recommendations."
        ),
    },
    "anomalies": {
        "label": "Unusual Transactions",
        "emoji": "🔍",
        "prompt": (
            "Review this financial data and identify:\n\n"
            "1. **Unusually large transactions** — above normal for their category\n"
            "2. **Duplicate or suspicious charges** — same amount/merchant repeated\n"
            "3. **Unexpected categories** — things that don't fit normal patterns\n"
            "4. **Weekend/unusual-hour charges** — if timestamps available\n"
            "5. **Summary** — anything that looks like it needs attention\n\n"
            "DATA:\n{data}"
        ),
        "system": (
            "You are a financial auditor reviewing transaction data for anomalies. "
            "Be thorough and flag anything unusual. Be specific about which transactions concern you."
        ),
    },
    "chat": {
        "label": "Q&A Chat",
        "emoji": "💬",
        "prompt": "{question}\n\nFINANCIAL DATA:\n{data}",
        "system": (
            "You are a personal finance analyst. Answer questions about the transaction data accurately. "
            "Use specific numbers from the data. If you can't answer from the data, say so."
        ),
    },
}


# ── Data loading & processing ──────────────────────────────────────────────────

COMMON_AMOUNT_COLS = ["amount", "Amount", "AMOUNT", "debit", "Debit", "credit", "Credit",
                      "transaction_amount", "Transaction Amount", "value", "Value"]
COMMON_DATE_COLS   = ["date", "Date", "DATE", "transaction_date", "Transaction Date",
                      "posted_date", "Posted Date", "datetime"]
COMMON_DESC_COLS   = ["description", "Description", "DESC", "merchant", "Merchant",
                      "payee", "Payee", "name", "Name", "memo", "Memo"]


def detect_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def load_transactions(path: str) -> tuple[pd.DataFrame, dict]:
    """Load a transaction CSV and detect column types."""
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            df = pd.read_csv(path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        console.print("[red]Could not read the CSV file.[/red]")
        sys.exit(1)

    cols = {
        "amount": detect_column(df, COMMON_AMOUNT_COLS),
        "date":   detect_column(df, COMMON_DATE_COLS),
        "desc":   detect_column(df, COMMON_DESC_COLS),
    }

    # Try to parse amount column
    if cols["amount"]:
        df[cols["amount"]] = (
            df[cols["amount"]]
            .astype(str)
            .str.replace(r"[$,()]", "", regex=True)
            .str.strip()
        )
        df[cols["amount"]] = pd.to_numeric(df[cols["amount"]], errors="coerce")

    # Try to parse date column
    if cols["date"]:
        df[cols["date"]] = pd.to_datetime(df[cols["date"]], errors="coerce", infer_datetime_format=True)

    return df, cols


def compute_summary(df: pd.DataFrame, cols: dict) -> str:
    """Compute a text summary of the financial data to feed to the LLM."""
    buf = io.StringIO()
    n_rows = len(df)
    buf.write(f"Transactions: {n_rows}\n")
    buf.write(f"Columns: {', '.join(df.columns.tolist())}\n\n")

    if cols["date"] and pd.api.types.is_datetime64_any_dtype(df[cols["date"]]):
        valid_dates = df[cols["date"]].dropna()
        if len(valid_dates) > 0:
            buf.write(f"Date range: {valid_dates.min().date()} to {valid_dates.max().date()}\n")

    if cols["amount"]:
        amounts = df[cols["amount"]].dropna()
        # Treat negatives as spending (bank exports often use negative for debits)
        spending = amounts[amounts < 0].abs() if (amounts < 0).any() else amounts[amounts > 0]
        income   = amounts[amounts > 0] if (amounts < 0).any() else pd.Series([], dtype=float)

        buf.write(f"\nTotal spending: ${spending.sum():,.2f}\n")
        buf.write(f"Number of expense transactions: {len(spending)}\n")
        buf.write(f"Average transaction: ${spending.mean():,.2f}\n")
        buf.write(f"Largest transaction: ${spending.max():,.2f}\n")
        if len(income) > 0:
            buf.write(f"Total income/credits: ${income.sum():,.2f}\n")

    # Full data (capped at 300 rows)
    sample = df if len(df) <= 300 else df.sample(300, random_state=42)
    buf.write(f"\nFull data ({len(sample)} rows{' — sampled' if len(df) > 300 else ''}):\n")
    buf.write(sample.to_csv(index=False))

    return buf.getvalue()


def show_preview(df: pd.DataFrame):
    table = Table(show_header=True, header_style="bold cyan", max_width=120)
    for col in df.columns[:6]:  # show max 6 columns
        table.add_column(str(col), no_wrap=True)
    for _, row in df.head(5).iterrows():
        table.add_row(*[str(v)[:30] for v in list(row.values)[:6]])
    console.print(table)
    if len(df) > 5:
        console.print(f"[dim]... {len(df) - 5} more rows[/dim]\n")


def run_analysis(model, tokenizer, mode_key: str, data_summary: str, question: str = "") -> str:
    mode = MODES[mode_key]

    if mode_key == "chat":
        user_content = mode["prompt"].format(question=question, data=data_summary)
    else:
        user_content = mode["prompt"].format(data=data_summary)

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
    parser = argparse.ArgumentParser(description="Analyze financial CSV data using a local LLM.")
    parser.add_argument("--csv",   required=True, help="Path to transaction CSV")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--mode",
        default="overview",
        choices=list(MODES.keys()),
        help="Analysis mode: overview, budget, anomalies, chat"
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        console.print(f"[red]File not found: {csv_path}[/red]")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold cyan]💳 Private Financial Analyzer[/bold cyan]\n"
        f"[dim]File:[/dim] {csv_path.name} · "
        f"[dim]Mode:[/dim] {MODES[args.mode]['label']}\n"
        "[dim]Runtime:[/dim] MLX (Apple Silicon) · No internet · No API key\n"
        "[bold yellow]Your financial data stays on your machine.[/bold yellow]",
        border_style="cyan"
    ))

    # Load data
    with console.status("[cyan]Loading transactions...[/cyan]"):
        df, cols = load_transactions(str(csv_path))
    console.print(f"[green]✓[/green] Loaded [bold]{len(df):,} transactions[/bold]\n")
    show_preview(df)

    # Compute summary
    with console.status("[cyan]Preparing financial summary...[/cyan]"):
        data_summary = compute_summary(df, cols)

    # Load model
    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    if args.mode == "chat":
        console.print("[dim]Ask questions about your transactions. Type [bold]exit[/bold] to quit.[/dim]\n")
        while True:
            try:
                q = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not q or q.lower() in {"exit", "quit", "q"}:
                break
            run_analysis(model, tokenizer, "chat", data_summary, question=q)
    else:
        run_analysis(model, tokenizer, args.mode, data_summary)

    console.print("[dim]Nothing was sent to any server.[/dim]")


if __name__ == "__main__":
    main()
