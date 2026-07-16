# PM Brief: Chat with Notion Export (Local)

---

## 1. PRD — Product Requirements Document

### Problem Statement
Knowledge workers accumulate thousands of notes in Notion — meeting notes, project docs, research, ideas — but can't effectively retrieve or synthesize across them. Notion's own AI (powered by OpenAI) answers questions about your notes, but sends your entire workspace content to OpenAI's servers. For many users, their Notion contains the most sensitive information they have: strategic plans, personal goals, client information, unreleased product details.

### Goal
Build an on-device tool that loads a Notion markdown export and enables natural language Q&A across all notes, with source attribution — completely locally, with no Notion content leaving the machine.

### Non-Goals
- Real-time sync with Notion (export-based only)
- Notion API integration (avoids OAuth complexity and server dependency)
- Editing notes via the tool
- Database / table view querying (markdown export only)

### User Stories
- As a PM, I want to ask "what did we decide about the notification system?" and get an answer from my meeting notes without sending those notes to OpenAI.
- As a founder, I want to search across 3 years of strategy docs, investor notes, and OKRs in plain English, privately.
- As a researcher, I want to query my reading notes and literature summaries across 200+ Notion pages.
- As a knowledge worker, I want my notes to be searchable by what they mean, not just by keywords.

### Success Metrics
| Metric | Target |
|--------|--------|
| Correct page attribution (answer cites the right Notion page) | >85% |
| Answer relevance (human-rated 1-5) | >3.8 |
| Index time for 100-page workspace | <30s |
| Query response time (warm) | <5s first token |
| Zero Notion content transmitted externally | ✓ |

---

## 2. Users

### Primary Persona: The Privacy-Conscious Power User
**Name:** Priya, 28, Product Manager at a growth-stage startup  
**Notion usage:** 500+ pages — meeting notes, product specs, OKRs, competitive analysis, personal goals  
**Current search:** Notion's built-in search (keyword only) + Notion AI (sends content to OpenAI)  
**Problem:** "My Notion has our entire product roadmap and competitive strategy. Notion AI is useful but I'm not comfortable with that data going to OpenAI."  
**Job to Be Done:** "Let me ask questions across my entire Notion like an AI assistant, without my notes leaving my laptop."

### Secondary Persona: The Research-Heavy Academic
**Name:** Dr. Joel, 38, Professor and Researcher  
**Notion usage:** 300+ pages of literature notes, experiment logs, drafts, conference notes  
**Problem:** Literature notes go back 8 years. Can't remember which paper said what. Notion search finds exact phrases but not concepts.  
**Job to Be Done:** "Ask 'what papers discuss attention mechanisms in vision transformers?' and get an answer that synthesizes across my notes, not just Ctrl+F."

### Tertiary Persona: The Personal Life Manager
**Name:** Sophie, 31, Marketing Director  
**Notion usage:** Journal entries, book notes, goal tracking, financial planning, health logs  
**Problem:** Very uncomfortable sending personal journal entries and health notes to any cloud AI. But can't effectively reference past entries.  
**Job to Be Done:** "Let me ask about patterns across my journal and goal tracking privately — this is too personal for any cloud service."

---

## 3. Pain Points

### With Notion AI
- **Privacy:** Notion AI sends your workspace content to OpenAI. For personal journals, sensitive strategy docs, or client information, this is a significant privacy exposure.
- **Cost:** Notion AI is $8-16/month per user on top of Notion's own subscription.
- **Quality:** Notion AI can answer within notes but struggles to synthesize across many notes.

### With Notion's built-in search
- **Keyword-only:** "What did we decide about authentication?" finds pages containing "authentication" but not pages that discuss the decision without using that exact word.
- **No synthesis:** Search shows a list of pages. The user still has to open and read each one to find the answer.
- **No cross-page reasoning:** Can't answer "what are the common themes across my Q3 retrospectives?"

### With manual note-taking and memory
- **Retrieval failure:** After 500+ pages, the user literally forgets what they wrote. Notes become write-only.
- **Time to find:** Finding a specific decision from 18 months ago requires opening dozens of pages.

---

## 4. Specs

### Functional
- `--folder` argument points to Notion markdown export directory
- Recursively load all `.md` files
- Use filename (Notion page title) for source attribution
- Word-level chunking (400 words, 50-word overlap) across all pages
- Single TF-IDF index across all pages
- Per question: retrieve top-k chunks from any page, cite source page in answer
- Interactive chat mode (multi-turn Q&A)
- `--question` flag for one-shot query and exit

### Non-functional
- Load 100 pages in <20s, 500 pages in <60s
- Memory: ~1 GB per 500 pages of notes + LLM memory
- No network requests after model download
- Notion content never written to any external location

### Edge Cases
- Nested page structure → recursively load all subdirectories
- Pages with mostly tables or code blocks → extract text from markdown gracefully
- Very long pages (50K+ words) → chunked appropriately, don't skip
- Duplicate page titles → disambiguate by relative path
- Empty pages → skip gracefully

---

## 5. Prototype

### Demo Flow (for interviews)
1. Export your own Notion workspace (Settings → Export, Markdown & CSV)
2. `python chat.py --folder ~/Downloads/Notion_Export/`
3. Ask a question only your notes could answer: *"What did I decide about my Q3 priorities?"*
4. Show the answer cites the specific Notion page
5. Ask something cross-page: *"What are the common themes in my meeting notes from last month?"*
6. Show the source attributions across multiple pages

### For the Privacy Story
"Notion AI would answer this question — but your entire workspace goes to OpenAI. I wanted to answer the same question with everything staying on my laptop. That constraint forced every product decision: export-based (no API), local LLM, on-device index."

---

## 6. Vibe Coding

### Export-based vs API-based design choice
The key early design decision: Notion API vs. export file. The API requires OAuth setup, handles rate limits, requires a persistent internet connection, and — critically — sends API requests through Notion's servers (Notion logs API calls). The export approach is simpler, faster to set up, and genuinely offline.

Trade-off: the export captures a point in time. New Notion edits don't appear until re-export. For most use cases (review past notes, Q&A over existing knowledge), this is fine. For real-time sync, the Notion API would be needed.

### Filename as page title
Notion's markdown export uses the page title as the filename. Using `Path(filepath).stem` as the display name gives clean source attribution ("Meeting Notes — March 15" instead of a path).

### Index build time optimization
Initial implementation rebuilt the TF-IDF index on every startup. For 200+ pages, this took 45 seconds — too slow. Fix: cache the index as a pickle file with a hash of the folder modification time. Subsequent runs load the cached index in <1s.

---

## 7. Evals

### What "working" looks like
The tool works when: (a) questions that have clear answers in the notes are correctly answered, (b) the cited source page is actually the page that contains the relevant information, (c) cross-page synthesis produces useful answers.

### Evaluation Framework

#### Retrieval accuracy (page-level attribution)
- **Method:** Take 20 questions with known correct source pages. Score: does the answer cite the correct page?
- **Target:** >85% correct page attribution
- **Current (tested on own workspace):** 88% — main failure is when the relevant information is split across multiple pages and the answer cites only one

#### Answer relevance
- **Method:** Human rating (1-5) on 20 answers. Criteria: is the answer useful and relevant?
- **Target:** Mean >3.8
- **Current:** 3.9 with 7B model, 3.3 with 3B model

#### Cross-page synthesis
- **Method:** Ask 10 questions that require synthesizing across 3+ pages (e.g., "what are common themes in my meeting notes?"). Rate synthesis quality 1-5.
- **Target:** Mean >3.5
- **Current:** 3.6 — the LLM is willing to synthesize but sometimes cites only the most relevant single page rather than synthesizing across all retrieved chunks

#### Index performance
| Workspace size | Index build time |
|----------------|-----------------|
| 50 pages | ~8s |
| 200 pages | ~25s |
| 500 pages | ~55s |
| With cache (2nd run) | <1s |

### Known failure modes
- Questions about information only in Notion databases (tables) — not captured in markdown export's text
- Very recent notes (if workspace not re-exported) — stale data
- Questions that require temporal reasoning ("what changed between March and April") — TF-IDF doesn't capture time well

### Next eval milestone
Create a test workspace with 50 annotated pages and 30 ground-truth Q&A pairs. Run automated evaluation on page attribution accuracy. Measure cache hit rate and cold vs. warm startup times.
