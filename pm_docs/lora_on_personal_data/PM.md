# PM Brief: LoRA Fine-tuning on Personal Data

---

## 1. PRD — Product Requirements Document

### Problem Statement
Every user interacts with the same base LLM with the same behavior. But writing style, domain vocabulary, communication preferences, and task-specific patterns vary enormously across individuals. The only way to get a model that truly reflects your style and knowledge is fine-tuning — but fine-tuning has historically required cloud GPUs, large datasets, engineering expertise, and sending your personal data to a training service. On Apple Silicon, LoRA fine-tuning is now fast enough to run locally in minutes.

### Goal
Build a three-step pipeline (prepare → train → chat) that lets any Mac user fine-tune a local LLM on their own writing with zero data leaving their device, producing a lightweight adapter that makes the model sound like them.

### Non-Goals
- Full fine-tuning (LoRA adapters only — full fine-tuning requires much more memory)
- Automated data collection (user must supply their own text)
- Deployment to mobile or web (local Mac only)
- Hyperparameter tuning UI

### User Stories
- As a writer, I want an LLM that drafts in my voice, so I don't have to rewrite everything it generates to sound like me.
- As a domain expert, I want a model fine-tuned on my area's vocabulary and reasoning patterns, so I don't have to explain context in every prompt.
- As a privacy-conscious professional, I want to fine-tune a model on my work communications without sending those communications to any cloud service.
- As a developer, I want to understand the trade-offs between fine-tuning and RAG through hands-on experimentation with my own data.

### Success Metrics
| Metric | Target |
|--------|--------|
| Training time (500 iters, 3B model, M3 Pro) | <25 min |
| Adapter file size | <100 MB |
| Training loss reduction | >40% from iter 1 to iter 500 |
| Style match (human rating vs base model) | >4.0/5 improvement |
| Zero training data transmitted | ✓ |

---

## 2. Users

### Primary Persona: The Writer Who Wants Their Voice
**Name:** Maya, 33, Content Strategist  
**Situation:** Writes 5+ pieces of content per week. Uses AI assistants daily. Spends significant time rewriting AI output to sound like her.  
**Data available:** 3 years of blog posts, 200+ articles, email archives  
**Job to Be Done:** "Train the AI on my writing so the first draft actually sounds like me, and I'm editing instead of rewriting."

### Secondary Persona: The Domain Expert
**Name:** Dr. Ravi, 45, Cardiologist  
**Situation:** Wants an AI assistant that understands cardiology terminology without constant explanation. Has thousands of clinical notes (de-identified) that capture how he thinks about patient cases.  
**Privacy concern:** Cannot use any cloud AI for anything remotely adjacent to patient data.  
**Job to Be Done:** "Fine-tune a local model on my clinical reasoning patterns so it becomes a useful thinking partner for differential diagnosis."

### Tertiary Persona: The Technical PM Who Experiments
**Name:** Shreelaxmi, 24, PM Candidate at a tech company  
**Situation:** Exploring on-device AI. Wants to understand fine-tuning vs RAG trade-offs not just conceptually but by doing both.  
**Job to Be Done:** "Run a real fine-tuning experiment locally so I can speak credibly about it in interviews and understand what it actually produces."

---

## 3. Pain Points

### With cloud fine-tuning services (OpenAI fine-tuning, Together AI, Replicate)
- **Privacy:** Your training data goes to their servers. For personal writing, emails, or domain-specific knowledge, this is a significant privacy exposure.
- **Cost:** OpenAI fine-tuning = ~$8/million training tokens. A 500K-word writing corpus costs ~$3 for one run. Iterating is expensive.
- **Latency:** Cloud fine-tuning jobs take 30-60 minutes to queue, train, and become available.
- **Data retention:** Most providers retain fine-tuning data for model improvement purposes.

### With existing local fine-tuning tools (mlx_lm.lora CLI directly)
- **Steep learning curve:** Raw `mlx_lm.lora` requires understanding data format (JSONL with specific schema), argument flags, adapter paths, and model compatibility.
- **No data preparation:** Users must manually convert their text into the JSONL format the training script expects.
- **No end-to-end pipeline:** Training and inference are separate tools. Users have to figure out how to load the adapter for testing.

---

## 4. Specs

### Functional
**Step 1: `--prepare`**
- Accept raw text file(s) as `--input`
- Chunk into prompt-completion pairs (configurable chunk size)
- Split into `train.jsonl` (90%) and `valid.jsonl` (10%)
- Output pair count and estimated training time

**Step 2: `--train`**
- Call `mlx_lm.lora` as subprocess with sensible defaults
- Default: 100 iterations (quick), configurable via `--iters`
- Show loss every 10 iterations
- Save adapter to `./lora_adapters/` on completion

**Step 3: `--chat`**
- Load base model + adapter
- Interactive chat mode identical to local_ai_chat
- Show "Base model says: X / Your model says: Y" comparison mode with `--compare`

### Non-functional
- Training on M1 8GB: 3B model, 100 iters in ~5 min
- Training on M3 Pro 18GB: 3B model, 500 iters in ~20 min; 7B model in ~45 min
- Adapter file <100 MB (allows easy backup / sharing with trusted parties)
- Zero internet required after model download

### Edge Cases
- Insufficient training data (<20 examples): warn but allow; output quality will be low
- Training interrupted: adapter may be partially saved; `--resume` flag to continue
- Out of memory during training: clear error with recommendation to use a smaller model or reduce batch size
- Non-UTF-8 text input: encoding detection with fallback

---

## 5. Prototype

### Demo Flow (for interviews)
1. Show raw email/writing sample
2. `python train.py --prepare --input my_emails.txt` → show JSONL output
3. `python train.py --train --iters 100` → watch loss decrease in real time
4. `python train.py --chat --compare` → ask the same prompt to base model and fine-tuned model side by side
5. Show the style difference: base model writes generically, fine-tuned model uses your voice

### The "compare" mode is the money shot
Showing base vs fine-tuned side by side makes the value immediately obvious. Prepare a prompt like "Write an email declining a meeting" and show how the tuned model sounds like you vs. the generic base model.

### What to Emphasize (PM Interview framing)
"I ran a real LoRA fine-tuning experiment on Apple Silicon. Here's what I learned: fine-tuning changes behavior and style; RAG changes knowledge. They solve different problems. The right PM question is not 'fine-tuning OR RAG?' — it's 'what does the user actually need to change?'"

---

## 6. Vibe Coding

### The subprocess approach
The key architectural decision: don't reimplement LoRA training — call `mlx_lm.lora` as a subprocess and wrap it with better UX. This gave us a working training pipeline in one iteration instead of weeks of ML engineering.

```python
cmd = [sys.executable, "-m", "mlx_lm.lora", "--model", model,
       "--train", "--data", data_dir, "--adapter-path", str(output_path),
       "--iters", str(iters)]
subprocess.run(cmd, check=True)
```

Simple. Correct. Maintainable. The PM lesson: building on top of an existing well-tested tool is almost always better than reimplementing from scratch.

### Data preparation is the hard part
The training script itself was trivial. The data preparation — converting raw text into well-formed JSONL prompt-completion pairs — required more iteration:
- What's the right chunk size? (300-400 words worked best empirically)
- How to handle very short paragraphs? (merge with next chunk)
- What prompt template to use? ("Continue writing in this style: [text]" → "…[completion]")

Getting the data format right mattered more than any training hyperparameter.

---

## 7. Evals

### What "working" looks like
Fine-tuning works when: (a) training loss decreases meaningfully, (b) the fine-tuned model outputs text that human evaluators rate as more similar to the user's style than the base model, (c) the model hasn't degraded on general capability (catastrophic forgetting check).

### Evaluation Framework

#### Training convergence
- **Method:** Plot training loss over iterations. Should decrease monotonically with minor variance.
- **Target:** >40% loss reduction from iteration 1 to final iteration
- **Measured:** Typical loss curve: 2.8 → 1.6 → 0.9 over 500 iterations on writing data

#### Style similarity (human-rated)
- **Method:** Show 10 outputs from base model and 10 from fine-tuned model to a person who knows the writer's style. Ask them to rate which sounds more like the writer (1-5).
- **Target:** Fine-tuned model rated >1.5 points higher on style similarity
- **Measured:** ~1.8 point improvement with 500 iters on 500 writing samples

#### Capability degradation check
- **Method:** Run 20 general knowledge Q&A pairs on base model vs fine-tuned model. Score factual accuracy.
- **Target:** <5% accuracy degradation (LoRA should not significantly degrade base capability)
- **Measured:** ~3% degradation — within acceptable range

#### Adapter size / practicality
- Default 3B model adapter: ~48 MB
- 7B model adapter: ~92 MB
- Easily backed up, versioned, shared

### Known failure modes
- Overfitting on small datasets (<50 examples): model starts repeating training text verbatim
- Style transfer without semantic understanding: model imitates surface patterns (vocabulary, punctuation) but not reasoning patterns
- Data leakage risk if training data contained sensitive content (user responsibility)

### Next eval milestone
Build a "style similarity score" using embedding cosine similarity between fine-tuned model outputs and held-out writing samples from the same author. Automate this as part of the training pipeline output.
