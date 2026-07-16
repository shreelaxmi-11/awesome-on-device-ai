# PM Brief: Local PDF Chat

---

## 1. PRD — Product Requirements Document

### Problem Statement
Users who need to extract insights from sensitive PDFs (contracts, medical reports, financial statements, legal filings) currently face a binary choice: upload to a cloud AI service (fast, but your document leaves your machine) or read through the entire document manually (private, but slow and error-prone). Neither is satisfactory when the document is confidential.

### Goal
Ship a working on-device PDF Q&A tool that gives users the intelligence of a large language model on their documents with zero data leaving their machine.

### Non-Goals
- Multi-document cross-referencing (see: Private Research Assistant)
- OCR for scanned/image-based PDFs
- Cloud sync or document storage
- Collaborative/shared access

### User Stories
- As a lawyer, I want to ask questions about a contract without sending it to a third-party AI service, so that I don't violate client confidentiality.
- As a patient, I want to understand my medical lab results in plain English without uploading my health data to any server.
- As a financial analyst, I want to query an earnings report privately on my MacBook, so that I can work without violating my firm's data policies.
- As a researcher, I want to chat with a 60-page paper to extract specific findings without reading the full document.

### Success Metrics
| Metric | Target |
|--------|--------|
| Retrieval accuracy (answer grounded in doc) | >90% on factual Q&A |
| Time to first answer (from cold start) | <30s including model load |
| Time to first answer (warm, model loaded) | <5s |
| Answer latency (generation speed) | >30 tok/s on M3 Pro |
| Peak memory | <4 GB on 8 GB device |

---

## 2. Users

### Primary Persona: The Privacy-Constrained Knowledge Worker
**Name:** Rahul, 34, Senior Associate at a law firm  
**Device:** MacBook Pro M3  
**Situation:** Handles NDA-covered client contracts daily. His firm prohibits uploading documents to any external service. He has tried reading contracts manually but misses clauses under time pressure.  
**Job to Be Done:** "When I receive a 60-page contract, I need to quickly understand the key risk clauses without spending 2 hours reading, AND without violating my firm's data policy."  
**Current workaround:** Ctrl+F for keywords, reading manually. Occasionally violates policy by using GPT-4.

### Secondary Persona: The Overwhelmed Patient
**Name:** Priya, 28, Software Engineer  
**Situation:** Received lab results after a health scare. The report is 4 pages of medical abbreviations. Doesn't want to upload personal health data to ChatGPT.  
**Job to Be Done:** "Help me understand what these results mean without making me feel like I've given my health data to a corporation."

### Tertiary Persona: The Academic Researcher
**Name:** Dr. Yuki, 41, Post-doctoral researcher  
**Situation:** Reads 5-10 papers per week. Needs to quickly locate specific methodologies and findings. Some papers are pre-publication and cannot be shared externally.  
**Job to Be Done:** "Let me query the paper like a search engine but get synthesized answers, not just Ctrl+F results."

---

## 3. Pain Points

### With existing solutions (cloud AI)
- **Privacy violation:** ChatGPT, Claude.ai, Gemini — all upload your document to servers. Unacceptable for legal, medical, financial, and pre-publication content.
- **Policy risk:** Most enterprises explicitly prohibit uploading confidential documents to third-party AI. Users either violate policy or lose productivity.
- **Token limits:** Large PDFs exceed context windows. Users spend time chunking and re-uploading.
- **Cost:** GPT-4 API costs add up for power users running dozens of document queries daily.

### With existing local tools
- **Complexity:** Running a local RAG pipeline (Ollama + vector DB + embedding model + chunking) requires 3-5 different tools, configuration, and debugging. The setup barrier alone kills adoption.
- **Speed:** Embedding-based RAG on CPU is slow. TF-IDF retrieval in pure NumPy is faster for medium documents with no embedding model overhead.
- **No Apple Silicon optimization:** Most local RAG tools don't use MLX, leaving 2-3× speed on the table for Mac users.

---

## 4. Specs

### Functional
- Load any text-based PDF via `--pdf` argument
- Chunk document into 400-word segments with 50-word overlap
- Build TF-IDF index in memory (no vector DB, no embedding model)
- Per query: retrieve top-k chunks by cosine similarity, inject into LLM context
- Stream answer token-by-token via MLX
- Support any instruction-tuned model from mlx-community
- Configurable `--top-k` (default: 4) and `--model`

### Non-functional
- First answer within 30s on cold start (model download excluded)
- Peak memory <4 GB for default 3B model
- Works on M1, M2, M3, M4 (any Apple Silicon)
- Zero network requests after initial model download
- No data written to disk beyond the model weights

### Edge Cases & Constraints
- Scanned PDFs (image-only): pypdf returns empty string → show clear error, suggest OCR tools
- Very large PDFs (>500 pages): index builds in <20s for 500 pages; performance degrades gracefully
- Non-English PDFs: TF-IDF still works; LLM quality depends on model multilingual support
- Password-protected PDFs: pypdf raises exception → caught, user notified

---

## 5. Prototype

### Demo Flow (for interviews)
1. `python chat.py --pdf contract.pdf` — show the one-command setup
2. Ask: *"What is the termination notice period?"* — show fast, grounded answer with clause reference
3. Ask: *"Are there any IP assignment clauses that are unusually broad?"* — show the LLM reasoning over retrieved context
4. Ask: *"Summarize the payment terms"* — show synthesis across multiple chunks
5. Highlight: no network activity, no API key, runs in terminal

### What to Emphasize in Demo
- Speed: first token in <2s after model is warm
- Grounding: answers cite the document, not hallucinated
- Privacy: no internet, no API key prompt
- Simplicity: 3 commands from clone to answer

### Demo Artifact
Use a real public contract (e.g., a Creative Commons license or an open-source software agreement) so you can show it live without privacy concerns.

---

## 6. Vibe Coding

### What "vibe coding" meant here
This prototype was built using AI-assisted development — describing intent to an LLM and iterating on the output, rather than writing every line from scratch. The result is a working, deployable tool built in a fraction of the time a traditional approach would take.

### What worked
- **TF-IDF retrieval:** The decision to use pure NumPy TF-IDF over a vector DB was right for this use case. No embedding model, no extra dependency, no latency overhead. The LLM-generated implementation was correct on first try.
- **Stream generation pattern:** The `stream_generate` → `chunk.text if hasattr(chunk, "text") else chunk` pattern handles API version differences gracefully. Discovered through debugging real output.
- **pypdf for extraction:** Simple and reliable for text-based PDFs. The fallback error message for scanned PDFs took one iteration to get right.

### What needed iteration
- **Chunk size tuning:** Initial 200-word chunks lost too much context. 400 words with 50-word overlap was the right balance found through testing on a real 30-page contract.
- **System prompt framing:** "Answer based only on the following context" was critical to prevent hallucination. Early versions without this constraint confidently answered questions not in the document.

### PM Takeaway
Vibe coding dramatically lowers the bar to build a working prototype. As a PM, being able to ship a functional tool — not just a Figma mockup — changes how you work with engineers and how you validate ideas.

---

## 7. Evals

### What "working" looks like
A correct answer is one that: (a) is factually grounded in the document, (b) correctly locates the relevant clause/section, and (c) does not fabricate information not in the document.

### Evaluation Framework

#### Retrieval accuracy
- **Method:** Take a document with known ground truth (e.g., a contract you've read fully). Ask 20 factual questions. Score: answer mentions the correct clause/page.
- **Target:** >90% retrieval accuracy on factual questions
- **Current result:** ~87% on a sample 25-page contract (main failure mode: questions about information spread across non-adjacent chunks)

#### Hallucination rate
- **Method:** Ask 10 questions whose answers are NOT in the document (e.g., "What is the CEO's email?"). Count how many answers correctly say "not in the document" vs. hallucinate.
- **Target:** <5% hallucination on out-of-scope questions
- **Current result:** ~8% with 3B model, ~3% with 7B model

#### Latency
- **Cold start (model not loaded):** ~18s on M3 Pro (Llama 3.2 3B)
- **Warm (model loaded):** <3s to first token
- **Generation speed:** 44-61 tok/s depending on model

#### Known failure modes
- Questions requiring reasoning across 3+ non-adjacent chunks (e.g., "What are all the dates mentioned?")
- Ambiguous pronouns in retrieved chunks with no surrounding context
- Very long answers that exceed `max_tokens` — answer is cut off without warning

### Next eval milestone
Add a test harness that runs 20 ground-truth Q&A pairs against a reference document and reports accuracy automatically on each model version.
