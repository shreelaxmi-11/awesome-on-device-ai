# PM Brief: Local AI Memory

---

## 1. PRD — Product Requirements Document

### Problem Statement
Every conversation with a local LLM starts from zero. The model has no idea who you are, what you're working on, what you've discussed before, or what your preferences are. This forces users to re-explain context in every session — the opposite of how human relationships and effective assistants work.

### Goal
Build an on-device memory layer that extracts and persists facts about the user across sessions, injecting them into every conversation — without any data leaving the device.

### Non-Goals
- Syncing memory across devices
- Multi-user memory profiles
- Memory editing via a GUI (CLI only for now)
- Summarization of full past conversations (just facts/entities)

### User Stories
- As a product manager, I want the AI to remember my role, my product, and my company's context, so I don't have to re-explain it every session.
- As a developer, I want the AI to remember my preferred tech stack, so it defaults to that without prompting.
- As a student, I want the AI to remember what topics I'm studying, so it can connect new information to what I already know.
- As a user, I want to see what the AI has remembered about me and delete any fact I don't want stored.

### Success Metrics
| Metric | Target |
|--------|--------|
| Fact extraction precision (correct facts saved) | >85% |
| Fact extraction recall (facts in conversation that get saved) | >70% |
| Memory injection latency added per turn | <500ms |
| User can view / delete memory | ✓ (via /memory, /forget) |
| Zero facts transmitted externally | ✓ (verified) |

---

## 2. Users

### Primary Persona: The Power User Who's Tired of Re-explaining
**Name:** Alex, 29, Product Manager at a startup  
**Usage pattern:** Uses local AI daily for writing, planning, and brainstorming. Starts every session by typing "I'm a PM at a B2B SaaS company building an analytics product for finance teams..."  
**Frustration:** "I've explained my context probably 200 times to AI assistants. It's exhausting."  
**Job to Be Done:** "Remember who I am so I can get useful help from the first message, not the fifth."

### Secondary Persona: The Specialized Professional
**Name:** Dr. Aisha, 38, Research Scientist  
**Usage pattern:** Uses local AI to think through research problems. Her context (research area, methodology preferences, key papers she's read) is highly specific and takes 3-4 paragraphs to explain.  
**Job to Be Done:** "When I ask a question, have the context of my research automatically in scope."

### Tertiary Persona: The Privacy-Conscious Developer
**Name:** Marcus, 25, Backend Engineer  
**Reason for local AI:** Doesn't trust cloud services with his codebase and development context.  
**Job to Be Done:** "Let the AI learn my preferences (Python over JS, FastAPI over Flask, opinionated about testing) without me sending that profile to any company."

---

## 3. Pain Points

### With cloud AI memory (ChatGPT Memory, Claude Projects)
- **Privacy:** Your personal facts — job, family, health, preferences, concerns — are stored on a company's server. Used for model training (in most cases by default). Unavoidable data collection.
- **Opacity:** Users can't fully audit what has been remembered. Partial views, hard to delete selectively.
- **Lock-in:** Memory is tied to one platform. If you switch from ChatGPT to Claude, you lose your memory.
- **Terms of service risk:** For professionals, sharing work context with a cloud AI may violate NDA or employer policy.

### With local AI (no memory)
- **Every session starts cold:** The model has no idea who you are.
- **Context re-injection is tedious:** Users paste system prompts, copy-paste background into every session.
- **No learning:** Despite hours of conversation, the AI gains nothing about the user's preferences or situation.

---

## 4. Specs

### Functional
- Load memory from `~/.local_ai_memory.json` on startup
- Inject all stored facts into the system prompt before every turn
- After each AI response: run a second LLM pass to extract new facts from the conversation turn
- Store new facts as JSON array, deduplicating near-identical facts
- In-chat commands: `/memory` (show facts), `/forget` (clear all)
- `--memory-file` flag to use a custom location (support multiple profiles)
- `--show-memory` flag to print memory on startup
- `--clear-memory` flag to wipe and start fresh

### Non-functional
- Memory extraction adds <500ms per turn (asynchronous where possible)
- Memory file is human-readable JSON (user can edit directly)
- Max memory size: 50 facts (older facts cycle out when limit hit)
- No network requests — fact extraction uses the same local model

### Edge Cases
- First run with no memory file: create file silently, start chatting
- Contradictory facts: "User works at Google" then "User left Google" → newer fact replaces older
- Very long conversations: memory stays bounded at 50 facts regardless of session length
- User mentions sensitive info they don't want saved: `/forget` clears everything (granular delete is future work)

---

## 5. Prototype

### Demo Flow (for interviews)
**Session 1:**
1. `python chat.py` — fresh start
2. Tell the AI: *"I'm a PM at a fintech startup working on a payments product"*
3. Show the `🧠 Remembered:` indicator appear
4. Type `/memory` — show the stored fact

**Session 2 (new terminal window / restart):**
1. `python chat.py` again
2. Immediately ask: *"What should I prioritize on my roadmap this quarter?"*
3. AI's first response uses the context from last session without re-explaining
4. Highlight: the AI knows you're in fintech payments without you saying it

### What to Emphasize
- The second session demo is the "wow moment" — the AI remembers across a full restart
- Show the JSON file directly: `cat ~/.local_ai_memory.json` — it's readable and deletable
- Privacy punchline: "This is what memory looks like when you own it"

---

## 6. Vibe Coding

### Architecture decisions made through iteration
The memory extraction step — using a second LLM call to parse facts from each turn — was the hardest part to get right. Early attempts used regex and keyword matching (brittle). The right approach was asking the LLM itself to return a JSON array of facts: clean, robust, generalizable.

### Prompt engineering for fact extraction
The system prompt for the fact extractor needed to be very specific:
- "Return ONLY a JSON array of strings. Each string is a factual statement about the user."
- "If no new facts are mentioned, return an empty array []."
- "Do not include opinions, questions, or conversational filler."

Getting the LLM to return valid JSON reliably required 3 iterations. The final approach wraps extraction in a try/except and falls back to no-op if JSON parsing fails — the conversation continues even if memory extraction glitches.

### What surprised me
The memory injection (adding stored facts to the system prompt) had almost zero latency impact. The expensive step was fact extraction, not injection. Moving extraction to after the AI response (instead of blocking the next turn) was the key UX fix.

---

## 7. Evals

### What "working" looks like
Memory works when: (a) relevant facts from conversation are extracted and saved, (b) saved facts appear in subsequent sessions, (c) the AI's responses reflect awareness of the stored context.

### Evaluation Framework

#### Fact extraction precision
- **Method:** Have 10 conversations with known ground-truth facts ("I'm 28, I work at Apple, I use Python"). After each conversation, count how many facts were correctly extracted vs. incorrectly extracted.
- **Target:** >85% precision (few false facts stored)
- **Current:** ~88% on factual statements; drops to ~70% on implicit facts ("I'm exhausted from this project" → should NOT store as a permanent fact)

#### Recall
- **Method:** Count what fraction of explicitly stated facts get captured.
- **Target:** >70%
- **Current:** ~74% — main miss is facts stated as subordinate clauses ("My manager, who's been at the company for 10 years, wants me to...")

#### Context utilization
- **Method:** Start a session with memory loaded. Ask 5 questions that should use the memory context. Rate each answer: did it use the context appropriately?
- **Target:** >80% of answers appropriately use stored context

#### Known failure modes
- Storing transient facts: "I'm tired today" should not persist
- Memory file corruption if process killed mid-write → mitigated with atomic writes
- Facts about other people stored as facts about the user: "My colleague loves Python" → incorrectly stored as "User loves Python"

### Next eval milestone
Build a test dataset of 20 conversations with annotated ground-truth facts. Run extraction automatically and report precision/recall per model size (3B vs 7B).
