#!/usr/bin/env python3
"""
Local AI Memory — Awesome On-Device AI
A chatbot that remembers things across sessions. Facts, preferences, and
context are stored locally in a JSON file. No API key. No cloud.

Usage:
    python chat.py                        # start chatting (loads memory)
    python chat.py --show-memory          # print what the AI remembers about you
    python chat.py --clear-memory         # wipe all memory
    python chat.py --memory-file ~/my_memory.json  # use a custom memory file
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from mlx_lm import load, stream_generate
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table

console = Console()

DEFAULT_MODEL       = "mlx-community/Llama-3.2-3B-Instruct-4bit"
DEFAULT_MEMORY_FILE = Path.home() / ".local_ai_memory.json"
MAX_TOKENS          = 1024
MAX_HISTORY         = 20


# ── Memory management ──────────────────────────────────────────────────────────

def load_memory(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            console.print(f"[yellow]Warning: memory file corrupted, starting fresh.[/yellow]")
    return {"facts": [], "created": datetime.now().isoformat(), "sessions": 0}


def save_memory(memory: dict, path: Path):
    path.write_text(json.dumps(memory, indent=2))


def memory_to_text(memory: dict) -> str:
    if not memory["facts"]:
        return "No facts stored yet."
    lines = []
    for fact in memory["facts"]:
        ts = fact.get("timestamp", "")[:10]
        lines.append(f"- [{ts}] {fact['fact']}")
    return "\n".join(lines)


def extract_and_store_facts(response: str, query: str, memory: dict, model, tokenizer) -> list[str]:
    """Ask the LLM to extract memorable facts from the conversation turn."""
    extract_prompt_content = (
        "Extract any personal facts, preferences, or important information the user shared "
        "in this conversation turn. Format as a JSON array of short fact strings. "
        "Only include facts about the USER, not general knowledge. "
        "If there are no new facts, return [].\n\n"
        f"User said: {query}\n"
        f"Assistant replied: {response[:300]}\n\n"
        "Return ONLY a valid JSON array, nothing else. Example: "
        '[\"User prefers Python over JavaScript\", \"User works at Acme Corp\"]'
    )

    messages = [
        {"role": "system",  "content": "You extract facts from conversations. Respond with valid JSON only."},
        {"role": "user",    "content": extract_prompt_content},
    ]

    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        prompt = f"USER: {extract_prompt_content}\nASSISTANT:"

    raw = ""
    for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=200):
        token = chunk.text if hasattr(chunk, "text") else chunk
        raw += token

    # Parse JSON from response
    try:
        # Find JSON array in the response
        start = raw.find("[")
        end   = raw.rfind("]") + 1
        if start >= 0 and end > start:
            facts = json.loads(raw[start:end])
            if isinstance(facts, list):
                new_facts = []
                for f in facts:
                    if isinstance(f, str) and f.strip():
                        entry = {"fact": f.strip(), "timestamp": datetime.now().isoformat()}
                        memory["facts"].append(entry)
                        new_facts.append(f.strip())
                return new_facts
    except (json.JSONDecodeError, ValueError):
        pass
    return []


def build_system_prompt(memory: dict) -> str:
    memory_text = memory_to_text(memory)
    sessions    = memory["sessions"]
    created     = memory.get("created", "")[:10]

    return (
        "You are a helpful AI assistant with persistent memory. "
        "You remember facts about the user across conversations.\n\n"
        f"WHAT YOU KNOW ABOUT THE USER (from {sessions} previous sessions since {created}):\n"
        f"{memory_text}\n\n"
        "Use this context naturally when relevant — don't recite it, just apply it. "
        "When the user shares new personal information, acknowledge it. "
        "Be helpful, warm, and concise."
    )


def show_memory_table(memory: dict):
    if not memory["facts"]:
        console.print("[dim]No facts stored yet. Start chatting and I'll remember things about you.[/dim]")
        return
    table = Table(title="What I Remember", show_header=True, header_style="bold cyan")
    table.add_column("Date", style="dim", width=12)
    table.add_column("Fact")
    for fact in memory["facts"]:
        ts = fact.get("timestamp", "")[:10]
        table.add_row(ts, fact["fact"])
    console.print(table)
    console.print(f"\n[dim]{len(memory['facts'])} facts · {memory['sessions']} sessions[/dim]")


def main():
    parser = argparse.ArgumentParser(description="Local AI chatbot with persistent memory.")
    parser.add_argument("--model",       default=DEFAULT_MODEL, help="MLX model repo")
    parser.add_argument("--memory-file", default=str(DEFAULT_MEMORY_FILE),
                        help="Path to memory JSON file")
    parser.add_argument("--show-memory", action="store_true", help="Show stored memory and exit")
    parser.add_argument("--clear-memory", action="store_true", help="Clear all memory and exit")
    args = parser.parse_args()

    memory_path = Path(args.memory_file)
    memory      = load_memory(memory_path)

    if args.show_memory:
        show_memory_table(memory)
        return

    if args.clear_memory:
        count = len(memory["facts"])
        memory["facts"] = []
        save_memory(memory, memory_path)
        console.print(f"[green]✓[/green] Cleared {count} facts from memory.")
        return

    # Increment session counter
    memory["sessions"] = memory.get("sessions", 0) + 1
    save_memory(memory, memory_path)

    console.print(Panel.fit(
        f"[bold cyan]🧠 Local AI Memory[/bold cyan]\n"
        f"[dim]Sessions:[/dim] {memory['sessions']} · "
        f"[dim]Facts stored:[/dim] {len(memory['facts'])} · "
        f"[dim]Model:[/dim] {args.model.split('/')[-1]}\n"
        "[dim]Runtime:[/dim] MLX · No internet · No API key\n"
        "[dim]Memory file:[/dim] " + str(memory_path),
        border_style="cyan"
    ))

    with console.status(f"[cyan]Loading {args.model.split('/')[-1]}...[/cyan]"):
        model, tokenizer = load(args.model)
    console.print(f"[green]✓[/green] Model loaded\n")

    if memory["facts"]:
        console.print(f"[dim]I remember {len(memory['facts'])} things about you from previous sessions.[/dim]\n")

    console.print("[dim]Commands: [bold]exit[/bold] to quit · [bold]/memory[/bold] to see what I remember · [bold]/forget[/bold] to clear memory[/dim]\n")

    history: list[dict] = []
    system_prompt = build_system_prompt(memory)

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye. Memory saved.[/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "q"}:
            console.print("[dim]Goodbye. Memory saved.[/dim]")
            break
        if user_input.lower() == "/memory":
            show_memory_table(memory)
            continue
        if user_input.lower() == "/forget":
            memory["facts"] = []
            save_memory(memory, memory_path)
            system_prompt = build_system_prompt(memory)
            console.print("[dim]Memory cleared.[/dim]\n")
            continue

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-MAX_HISTORY:])
        messages.append({"role": "user", "content": user_input})

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

        history.append({"role": "user",      "content": user_input})
        history.append({"role": "assistant", "content": response_text.strip()})

        # Extract and save any new facts
        new_facts = extract_and_store_facts(response_text, user_input, memory, model, tokenizer)
        if new_facts:
            save_memory(memory, memory_path)
            system_prompt = build_system_prompt(memory)  # refresh system prompt
            for f in new_facts:
                console.print(f"[dim]🧠 Remembered: {f}[/dim]")
            console.print()


if __name__ == "__main__":
    main()
