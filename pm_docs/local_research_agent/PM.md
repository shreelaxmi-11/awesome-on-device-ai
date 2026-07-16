# PM Brief: Local Research Agent

---

## 1. PRD — Product Requirements Document

### Problem Statement
When a knowledge worker needs to research a topic — a technology landscape, a competitor, a policy question, a strategic decision — they have two options: do it themselves (slow, requires expertise in the domain) or ask a cloud AI (fast, but sends the topic to a third-party server). Neither is great for competitive analysis, internal strategy, or sensitive market research. And neither produces the structured, synthesized output that a PM or analyst actually needs to act on.

### Goal
Build an on-device research agent that autonomously decomposes any topic into sub-questions, answers each one with a full LLM pass, and synthesizes a structured report — all locally, with no external API.

### Non-Goals
- Web search or real-time information retrieval (knowledge cutoff of the base model applies)
- Citation of external sources (knowledge is from model weights, not fetched documents)
- Multi-agent collaboration
- GUI or web interface

### User Stories
- As a PM, I want to research the trade-offs between on-device AI and cloud AI and get a structured report in 10 minutes, so I can use it to brief my team.
- As a strategy analyst, I want to run competitive analysis on sensitive topics without those queries going to OpenAI's servers.
- As a researcher, I want to explore a new technical domain quickly and get a map of key concepts, players, and open questions.
- As a consultant, I want a structured starting point for any client topic that I can then enrich with my own expertise.

### Success Metrics
| Metric | Target |
|--------|--------|
| Report covers all major sub-themes of the topic | >80% coverage (human-rated) |
| Report factual accuracy (no hallucinations) | >90% verifiable claims |
| Time to complete quick (3 sub-Q) research | <5 min on M3 Pro |
| Time to complete deep (6 sub-Q) research | <12 min on M3 Pro |
| User rates synthesis as "useful starting point" | >85% on test set |

---

## 2. Users

### Primary Persona: The Strategic Thinker
**Name:** Neha, 31, Senior Product Manager at a tech company  
**Research use:** Technology landscape analysis, feature comparison, framework evaluation  
**Current approach:** Google + ChatGPT + manual synthesis in a doc  
**Problem:** ChatGPT research goes through OpenAI's servers. Competitive analysis topics are sensitive.  
**Job to Be Done:** "Give me a structured research brief on any topic in under 10 minutes that I can use as a starting point for my own thinking."

### Secondary Persona: The Time-Pressed Consultant
**Name:** Vikram, 38, Independent Strategy Consultant  
**Research use:** Client context preparation, industry overviews  
**Current approach:** Manual research + expensive research databases  
**Problem:** Can't use cloud AI for client-sensitive topics. Manual research for a new client domain takes 2-3 hours.  
**Job to Be Done:** "Get a 70% good enough research brief in 10 minutes so I can spend my time on the 30% that requires my expertise."

### Tertiary Persona: The Curious Generalist
**Name:** Leila, 24, MBA Student  
**Research use:** Exploring topics across business strategy, technology, economics  
**Current approach:** Wikipedia + articles + ChatGPT  
**Problem:** No single tool gives her a structured synthesis. ChatGPT outputs require heavy prompting to get structured output.  
**Job to Be Done:** "When I encounter a new topic, give me a structured map of what I need to understand — not just a wall of text."

---

## 3. Pain Points

### With cloud AI (ChatGPT, Perplexity, Claude)
- **Privacy of the query itself:** Searching for "our company's competitive response to [competitor's] new product" reveals internal strategy to the AI provider's servers. The topic being researched is often as sensitive as the content.
- **Shallow synthesis:** ChatGPT answers the surface question. It rarely proactively decomposes a topic into the sub-questions that give you real depth.
- **No structure by default:** Getting structured output requires careful prompting. Most users get a paragraph, not a report.
- **Hallucination with confidence:** Cloud AI hallucinates specific facts (statistics, dates, quotes) with the same confident tone as accurate information. No built-in signal for uncertainty.

### With manual research
- **Time-intensive:** 2-4 hours to build a comprehensive view of an unfamiliar topic.
- **Synthesis is the hard part:** Gathering information is easier than synthesizing it into a coherent framework. That's where time gets spent.
- **Coverage gaps:** Manual research is path-dependent — you find what you search for. A decompose-first approach finds angles you wouldn't have thought to search.

---

## 4. Specs

### Functional
- Accept topic as positional argument or via `--interactive`
- `--depth quick`: 3 sub-questions, ~5 min runtime
- `--depth deep`: 6 sub-questions, ~10 min runtime
- LLM pass 1: decompose topic into N focused sub-questions
- LLM pass 2-N: answer each sub-question (separate full LLM call per sub-question)
- LLM pass N+1: synthesize all answers into structured final report with: executive summary, key findings per sub-question, synthesis/implications, open questions
- `--output filename.md`: save report to disk
- `--model`: specify any mlx-community model

### Non-functional
- Each LLM pass is independent (no shared state between sub-question answers)
- Progress shown in terminal during multi-step processing
- Report saved as clean markdown (readable outside terminal)
- Works fully offline

### Edge Cases
- Ambiguous or extremely broad topics → decomposition step handles gracefully (may produce more generic sub-questions)
- Topics outside model knowledge cutoff → model may confidently assert outdated information; flagged in report header
- Very short topics ("AI") → decomposition produces high-level sub-questions; more specific topics produce better output
- Sub-question answers that contradict each other → synthesis step handles by noting the tension

---

## 5. Prototype

### Demo Flow (for interviews)
1. `python research.py "Trade-offs between RAG and fine-tuning for enterprise AI"` — pick a PM-relevant technical topic
2. Watch the 3-step process: decompose → research each sub-Q → synthesize
3. Show the final structured report with executive summary and findings
4. `--output rag_vs_finetuning.md` — show the saved markdown
5. Ask: "How long would this take manually?" Answer: 2-3 hours. This took 4 minutes.

### What to Emphasize
- The decompose step is the differentiator — it proactively generates angles you might not have thought to ask about
- The synthesis is PM-usable immediately (not raw notes)
- Topic-sensitive: demo with a topic that would be awkward to send to a cloud AI ("How is [our company] positioned vs [competitor]?")

---

## 6. Vibe Coding

### The agent pattern
The decompose → research → synthesize loop is one of the simplest and most powerful agent patterns. No tool use, no external APIs, no frameworks. Just sequential LLM calls where each output becomes the input for the next step. Vibe coding made the architecture obvious — describe the workflow, let the LLM implement it, test on a real topic.

### Prompt engineering for decomposition
The hardest prompt to get right was the decomposition step. Requirements:
- Sub-questions must be focused and non-overlapping
- They must together cover the topic comprehensively
- They must be answerable by an LLM (not requiring real-time data)

The winning format: "You are a research analyst. Break the following topic into exactly N focused sub-questions that together give a comprehensive view. Return ONLY a numbered list of questions. No preamble."

### What needed iteration
**Synthesis prompt:** Early synthesis prompts produced a list of summaries of each sub-answer. The right prompt produces genuine synthesis — drawing connections, identifying tensions, making implications explicit. The key instruction: "Do not just summarize each sub-answer. Find patterns, tensions, and implications across all of them."

**Progress display:** Long operations need user feedback. Adding "Researching sub-question 2/3..." with a spinner significantly improved perceived quality — users didn't think it had frozen.

---

## 7. Evals

### What "working" looks like
The agent works when the final report: (a) covers the major dimensions of the topic, (b) is factually accurate in its claims, (c) provides genuine synthesis rather than a list of summaries, and (d) is useful as a starting point without requiring significant cleanup.

### Evaluation Framework

#### Coverage
- **Method:** For 5 test topics, have a domain expert list the top 10 sub-themes they'd expect to see covered. Score how many appear in the report.
- **Target:** >8/10 sub-themes present for most topics
- **Current:** ~7.5/10 average across test set

#### Factual accuracy
- **Method:** Select 20 specific factual claims from 5 reports. Verify each against authoritative sources.
- **Target:** >90% accurate claims
- **Current:** ~88% — main error source is specific statistics (percentages, dates) stated with false precision

#### Synthesis quality (human-rated)
- **Scale:** 1 (just summaries) to 5 (genuine insights, novel connections)
- **Target:** Mean >3.5
- **Current:** 3.8 with 7B model, 3.1 with 3B model — this is the strongest argument for using a 7B model for research tasks

#### Speed
| Mode | Sub-questions | Time (M3 Pro, 3B) | Time (M3 Pro, 7B) |
|------|--------------|-------------------|-------------------|
| Quick | 3 | ~3.5 min | ~6 min |
| Deep | 6 | ~7 min | ~12 min |

### Known failure modes
- Circular synthesis: report says "as discussed above" referring to sub-answers not visible to the reader
- Over-confidence on contested facts: model presents contested claims as settled
- Repetition: if sub-questions overlap, answers repeat — mitigated by better decomposition prompt

### Next eval milestone
Build a 10-topic evaluation harness with human-annotated expected sub-themes. Measure coverage automatically by embedding similarity between expected and actual sub-questions.
