# PM Brief: Local Contract Analyzer

---

## 1. PRD — Product Requirements Document

### Problem Statement
Contracts are everywhere — employment offers, NDAs, freelance agreements, rental leases, SaaS subscriptions — but most people sign them without understanding what they've agreed to. The only alternatives are: pay a lawyer ($300-500/hour), use a cloud AI tool (uploads your confidential contract to an external server), or read it yourself and hope you catch everything. None of these work for everyday contract review.

### Goal
Build an on-device contract analysis tool that reads any contract PDF and surfaces key terms, obligations, red flags, and unusual clauses — in plain English, locally, with no document leaving the device.

### Non-Goals
- Legal advice or recommendations (tool explains, not advises)
- e-signature or contract management
- Multi-party contract comparison
- Negotiation tracking

### User Stories
- As a freelancer, I want to understand an NDA before signing it without paying a lawyer or uploading it to ChatGPT.
- As an employee, I want to understand my employment contract's non-compete and IP clauses before my first day.
- As a startup founder, I want to quickly scan vendor contracts for unusual liability or IP terms without sending them externally.
- As a tenant, I want to understand my lease agreement in plain English, especially the clauses I usually ignore.

### Success Metrics
| Metric | Target |
|--------|--------|
| Key term extraction (compensation, duration, termination, IP, liability) | >90% recall |
| Red flag identification (unusual/one-sided clauses) | >80% precision |
| User comprehension improvement vs. reading alone | >30% on test questions |
| Time to first insight from file load | <20s |
| Zero bytes of contract transmitted externally | ✓ |

---

## 2. Users

### Primary Persona: The Unrepresented Individual
**Name:** Kenji, 27, Junior Designer  
**Situation:** Received an offer letter with a broad IP clause and 12-month non-compete. Can't afford a lawyer. Uncomfortable uploading his future employer's offer to ChatGPT.  
**Job to Be Done:** "Tell me if there's anything in this offer letter I should push back on before I sign it."

### Secondary Persona: The Time-Pressed Founder
**Name:** Amara, 34, Co-founder of a seed-stage startup  
**Situation:** Reviews 10-15 vendor contracts per year. Most are standard but some have unusual terms. Can't send them to an external AI — they contain business-sensitive commercial terms.  
**Job to Be Done:** "Scan this contract in 2 minutes and tell me if anything's unusual. I'll send the flagged clauses to our lawyer, not the whole document."

### Tertiary Persona: The Freelance Professional
**Name:** Carlos, 31, Freelance Software Developer  
**Situation:** Gets 4-5 contracts per year from clients. All have different IP and payment terms. Gets burned occasionally by clauses he missed.  
**Job to Be Done:** "Before I sign any contract, give me a clear picture of what I'm agreeing to — especially IP ownership and payment terms."

---

## 3. Pain Points

### With lawyers
- **Cost:** $300-500/hour for basic contract review. For a $5K freelance contract, a 1-hour review is 10% of the revenue.
- **Time:** Lawyer availability means 3-5 business days for a review, often when the client wants a same-day signature.
- **Overkill for standard contracts:** Most contracts are templates. Paying lawyer rates to read a standard NDA is inefficient.

### With cloud AI (ChatGPT, Claude)
- **Privacy violation:** Uploading an employment contract or business agreement to a cloud service exposes confidential terms, compensation data, and proprietary information.
- **No specialization:** General-purpose AI gives generic summaries. A contract-aware prompt gives meaningfully better output.
- **No structure:** Raw chat output requires the user to synthesize the analysis themselves.

### With reading the contract yourself
- **Time:** A 20-page contract takes 45-90 minutes to read carefully.
- **Expertise gap:** Legal language is intentionally precise and often non-intuitive. "Consequential damages" and "indemnification" have specific meanings most people don't know.
- **Coverage gap:** Under time pressure, people skim and miss important clauses.

---

## 4. Specs

### Functional
- Load contract PDF via `--pdf` argument
- Four modes: `full` (complete analysis), `summary` (5-7 bullet overview), `risks` (red flags only), `chat` (Q&A)
- `full` mode output structure: type/parties → key terms → obligations → liability → red flags → questions to ask counsel
- TF-IDF retrieval for `chat` mode (per-question chunk retrieval)
- `full` and `risks` modes use top-k retrieval focused on risk-relevant clauses
- Legal disclaimer displayed on every output

### Non-functional
- Works on text-based PDFs (not scanned/image)
- Peak memory <6 GB (supports 7B models on 16 GB devices)
- Legal disclaimer: non-removable, displayed before every output
- No data written to external location

### Edge Cases
- Multi-part contracts with exhibits → all text extracted and indexed together
- Contracts in non-English languages → Whisper handles 99 languages; disclaimer updated to note translation quality
- Password-protected PDFs → caught exception, user notified
- Scanned/image PDFs → pypdf returns empty string → error with OCR tool suggestion
- Very long contracts (100+ pages) → index handles any length; chunking ensures coverage

---

## 5. Prototype

### Demo Flow (for interviews)
Use a Creative Commons license or any freely available standard contract (e.g., GitHub's terms of service or a public standard NDA template).

1. `python analyze.py --pdf standard_nda.pdf`
2. Show `full` mode output: parties, key terms, red flags highlighted
3. Switch to `python analyze.py --pdf nda.pdf --mode risks` — just the flags
4. Switch to `--mode chat`: ask "What are my obligations if I leave the company?"
5. Highlight: the tool correctly identifies unusual IP scope or non-compete language

### PM Interview Framing
"I built this to answer: what does contract review look like when the constraint is 'this document cannot leave my laptop'? The constraint forces a specific product: on-device LLM, PDF parsing, structured output. The constraint is the product."

---

## 6. Vibe Coding

### Prompt structure for risk detection
The hardest prompt to get right was risk flagging. Early prompts produced a list of all unusual-sounding clauses, including standard ones that merely sound intimidating. The fix: give the model explicit criteria.

"Flag ONLY clauses that are: (1) more one-sided than industry standard, (2) unusually broad in scope, (3) potentially waiving important rights, or (4) financially risky beyond normal. Do not flag standard clauses just because they use legal language."

This reduced false positives from ~40% to ~12%.

### Two-stage for `full` mode
Full mode runs two LLM passes: first pass extracts structured facts (parties, dates, amounts, durations), second pass does risk analysis on the full context. Combining into one pass produced worse output — the model tried to do too much at once and missed things.

### Legal disclaimer necessity
Early testing without a disclaimer produced responses where users (myself included) started making decisions based on LLM output without checking with a lawyer. The disclaimer isn't just legal cover — it's a necessary UX element that frames the tool correctly as an explanation aid, not legal advice.

---

## 7. Evals

### What "working" looks like
The analyzer works when: (a) key terms (compensation, duration, termination, IP, liability) are correctly extracted, (b) genuinely unusual clauses are flagged without excessive false positives, (c) the plain-English explanation is accurate.

### Evaluation Framework

#### Key term extraction
- **Method:** Take 10 contracts with known ground-truth terms (manually annotated). Score how many key terms the tool correctly identifies.
- **Target:** >90% recall on: compensation, duration, termination notice, IP assignment scope, liability cap
- **Measured:** 91% on 10-contract test set (main miss: IP clauses buried in schedule/exhibit appendices)

#### Risk flag precision
- **Method:** Have a lawyer review the same 10 contracts and annotate unusual clauses. Compare with tool output.
- **Precision target:** >80% (flagged items are genuinely unusual)
- **Recall target:** >70% (real red flags get caught)
- **Measured:** Precision 83%, Recall 68% — recall is harder because some risky clauses require industry knowledge to recognize

#### Explanation accuracy
- **Method:** For 20 specific contract clauses, compare tool explanation to lawyer explanation. Rate similarity 1-5.
- **Target:** Mean >3.5
- **Measured:** 3.7 with 7B model, 2.9 with 3B model — this is the clearest case for using a 7B model

#### Speed
- 10-page contract, 3B model: ~12s to full analysis
- 50-page contract, 3B model: ~35s to full analysis

### Known failure modes
- Jurisdiction-specific rules: tool may not know that a non-compete is unenforceable in California
- Exhibit/appendix references: "see Schedule A" — scope defined there may not be analyzed
- Calculated risk: some clauses look risky in isolation but are standard in the specific industry

### Next eval milestone
Partner with 1-2 lawyers to create a 20-contract gold standard evaluation set with annotated key terms and risk flags. Run automated precision/recall evaluation quarterly.
