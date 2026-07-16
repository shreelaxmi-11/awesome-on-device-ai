# PM Brief: Local Code RAG

---

## 1. PRD — Product Requirements Document

### Problem Statement
Developers working on large, unfamiliar, or legacy codebases spend significant time on code navigation — understanding where logic lives, how components connect, and what a function actually does. Existing AI code tools (GitHub Copilot, Cursor) require uploading source code to cloud servers, which is prohibited for most proprietary codebases. There is no good on-device alternative that works with any codebase in any language.

### Goal
Build an on-device RAG system that indexes any local codebase and answers natural-language questions about it — grounded in the actual source code, with file and line number attribution, zero code leaving the machine.

### Non-Goals
- Code generation / autocomplete (this is Q&A only)
- Real-time indexing as files change (batch index only)
- Execution or testing of code
- Version control integration (Git blame, history)

### User Stories
- As a new engineer, I want to ask "where is the authentication logic?" and get a direct answer with file locations, instead of spending 30 minutes grepping.
- As an engineer working on a proprietary codebase, I want AI-powered code understanding without uploading the source code to GitHub Copilot.
- As a tech lead, I want to quickly understand what a new hire's PR is doing at a high level by asking natural language questions.
- As a developer inheriting legacy code, I want to understand architectural patterns without reading every file.

### Success Metrics
| Metric | Target |
|--------|--------|
| Correct file attribution (answer cites right file) | >85% |
| Correct conceptual answer (grounded in actual code) | >80% |
| Index build time for 10K-line codebase | <30s |
| Query response time (warm) | <5s first token |
| Zero source code transmitted externally | ✓ |

---

## 2. Users

### Primary Persona: The New Team Member
**Name:** Preethi, 24, Junior Software Engineer  
**Context:** Just joined a company with a 200K-line Python codebase. No documentation. Senior engineers are busy.  
**Current approach:** `grep -r`, reading files one by one, asking Slack  
**Problem:** Grep finds strings, not concepts. "Where is the payment processing logic?" requires reading dozens of files.  
**Job to Be Done:** "Help me navigate an unfamiliar codebase like I have a senior engineer sitting next to me who can answer 'where is X?' questions."

### Secondary Persona: The Security-Constrained Developer
**Name:** David, 31, Backend Engineer at a defense contractor  
**Context:** Works on classified or export-controlled software. Copilot and Cursor are explicitly prohibited by company policy.  
**Current approach:** Manual code reading, internal wikis (often outdated)  
**Job to Be Done:** "Give me AI-powered code understanding without sending a single line of our source code to Microsoft, GitHub, or any external server."

### Tertiary Persona: The Open Source Contributor
**Name:** Sam, 27, Senior Developer  
**Context:** Contributes to large open-source projects. Needs to understand a new project's codebase before submitting a PR.  
**Job to Be Done:** "Let me ask questions about this project's codebase in plain English before I start writing code, so I don't repeat existing patterns or break conventions."

---

## 3. Pain Points

### With cloud code AI tools (Copilot, Cursor, Codeium)
- **Privacy/policy violation:** Source code is uploaded to external servers. Prohibited for most enterprise codebases. Violations lead to IP exposure, security incidents, and termination.
- **Context window limits:** Large codebases don't fit in context. Tools use their own retrieval, which users can't inspect or tune.
- **Cost:** GitHub Copilot = $10-19/month per user. For a 100-person engineering team, that's $12K-$23K/year.
- **Always-on telemetry:** Code completions and queries are logged. Even "privacy mode" still sends code for processing.

### With grep / manual exploration
- **Conceptual queries fail:** `grep -r "auth"` finds 847 matches. It cannot answer "explain the authentication flow."
- **Time cost:** Understanding how a 50K-line codebase works takes days for a new engineer.
- **Documentation lag:** READMEs and wikis go stale. The code is the truth, but it's hard to read.

---

## 4. Specs

### Functional
- `--repo` argument points to any local directory
- Recursively scan for code files (default: .py, .js, .ts, .tsx, .jsx, .go, .rs, .java, .swift, .kt, .cpp, .c, .rb, .sh)
- Skip: `.git`, `node_modules`, `__pycache__`, `.venv`, `dist`, `build`, `*.lock` files, binary files
- Skip files >100KB (likely generated or data files)
- Code-aware tokenization: split on camelCase, snake_case, file paths (better TF-IDF for identifiers)
- Chunk by function/class boundaries where detectable; fall back to line-count chunks
- Each chunk stores: file path, start line, end line
- Show file + line range in every answer
- `--extensions` flag to restrict to specific file types

### Non-functional
- Index 10K lines in <10s, 100K lines in <60s
- Memory scales with codebase size; 100K lines ≈ ~2 GB index + LLM memory
- No network requests after model download
- Source code never written to any external location

### Edge Cases
- Binary files accidentally included → detect by null bytes, skip
- Minified JS/CSS → skip files >50KB single line
- Very large monorepos (>1M lines) → streaming index with progress indicator; recommend `--extensions` to narrow scope
- Non-UTF-8 source files → try UTF-8 → fall back to latin-1

---

## 5. Prototype

### Demo Flow (for interviews)
1. Clone any medium-sized open source project (`git clone https://github.com/fastapi/fastapi`)
2. `python chat.py --repo ./fastapi`
3. Ask: *"Where is the routing logic?"* — show answer with file paths and line numbers
4. Ask: *"How does FastAPI handle dependency injection?"* — show conceptual explanation grounded in actual source
5. Ask: *"What happens when a request comes in? Walk me through the flow."* — show multi-file synthesis

### What to Emphasize
- File + line attribution: answers aren't vague, they tell you exactly where to look
- Conceptual queries: "how does X work" produces a comprehensible explanation, not just file paths
- Privacy: demo on a proprietary-seeming directory name to illustrate the use case

---

## 6. Vibe Coding

### Code-aware tokenization
Standard TF-IDF tokenizes on whitespace. Code has compound identifiers: `processPaymentRequest`, `auth_middleware`, `handleUserLogin`. Standard tokenization treats these as single tokens, missing the semantic components.

The solution: a custom tokenizer that splits on camelCase and snake_case before TF-IDF indexing. "processPaymentRequest" becomes ["process", "payment", "request"] — much better for queries like "where is payment processing?"

This was the key technical insight that made code RAG significantly better than naive document RAG. Built through one iteration: naive TF-IDF → test with real code queries → identify failure mode → add code-aware tokenizer.

### Chunking strategy
For code, fixed-size word chunks lose function/class context (a chunk might start mid-function). The better approach: attempt to chunk at function/class boundaries using simple regex heuristics. Falls back to line-count chunks for files that don't match patterns. This improved answer quality on architectural questions noticeably.

---

## 7. Evals

### What "working" looks like
The tool works when: (a) it correctly identifies which files contain relevant code, (b) it produces a conceptually accurate explanation of how the code works, (c) the cited line numbers are genuinely relevant.

### Evaluation Framework

#### Retrieval accuracy (file-level)
- **Method:** On a known codebase, ask 20 questions with known correct file locations. Score: does the answer cite the correct file?
- **Target:** >85% correct file attribution
- **Current (FastAPI repo):** 88% correct file, 71% correct line range

#### Conceptual accuracy
- **Method:** Have a developer who knows the codebase rate the conceptual accuracy of 15 answers on a 1-5 scale.
- **Target:** Mean >3.8
- **Current:** 3.9 with 7B model, 3.2 with 3B model — this is the strongest argument for a larger model for code understanding

#### Index build performance
| Codebase | Lines | Index time |
|----------|-------|------------|
| Small project | 5K | ~4s |
| FastAPI | ~25K | ~15s |
| Large monorepo | 200K | ~90s |

#### Known failure modes
- Questions requiring understanding of runtime behavior (not in source code)
- Cross-language codebases where language-specific patterns aren't handled
- Generated code files (migrations, protobuf) polluting results — mitigate with `--extensions`

### Next eval milestone
Build a ground-truth Q&A set for 3 well-known open source projects. Automate file-attribution accuracy testing to run on every PR.
