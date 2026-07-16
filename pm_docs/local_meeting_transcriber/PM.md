# PM Brief: Local Meeting Transcriber

---

## 1. PRD — Product Requirements Document

### Problem Statement
Meeting transcription is now table stakes for knowledge workers — but every existing tool (Otter.ai, Fireflies, Zoom AI, Google Meet AI) requires streaming your audio to their servers in real time. For confidential meetings — client calls, board discussions, M&A conversations, HR reviews, sensitive product strategy — this is not acceptable. There is no privacy-preserving meeting transcription tool that works with recordings you already have.

### Goal
Build an on-device meeting transcription tool using Whisper + MLX that produces a structured output (transcript + summary + action items) from any audio file, with zero audio leaving the machine.

### Non-Goals
- Real-time transcription during live meetings (live mic capture is future work)
- Speaker diarization (who said what)
- Calendar integration or automatic meeting capture
- Transcription of video files (audio track extraction not included)

### User Stories
- As a consultant, I want to transcribe client call recordings without uploading them to any third-party service, so I maintain confidentiality obligations.
- As an executive assistant, I want to automatically extract action items from recorded meetings so I can send follow-ups without listening to the full recording.
- As a remote team lead, I want meeting summaries that capture decisions and next steps, not just a wall of text.
- As an engineer, I want to transcribe internal engineering discussions that contain unreleased product details, without those details leaving our infrastructure.

### Success Metrics
| Metric | Target |
|--------|--------|
| Word Error Rate (WER) on clear audio | <10% |
| WER on accented / moderate noise | <18% |
| Time to transcribe 1-hour recording | <8 min on M3 Pro |
| Action item extraction precision | >85% |
| Summary relevance (human-rated 1-5) | >4.0 |
| Zero audio bytes transmitted | ✓ |

---

## 2. Users

### Primary Persona: The Compliance-Constrained Professional
**Name:** Jordan, 35, Management Consultant at a Big 4 firm  
**Meeting type:** Client strategy calls, due diligence interviews  
**Current tool:** Manual notes + Otter.ai  
**Problem:** Client NDA explicitly prohibits using third-party AI tools on client calls. But manual notes miss things and take time.  
**Job to Be Done:** "Transcribe and summarize my client calls without violating the NDA I've signed."

### Secondary Persona: The Async-First Remote Leader
**Name:** Sarah, 32, Engineering Manager  
**Meeting type:** Async standup recordings, weekly planning, 1:1s  
**Current tool:** Zoom Cloud Recording (auto-transcription)  
**Problem:** Zoom's transcription is mediocre and sends data to their servers. Engineering discussions often contain unreleased product details.  
**Job to Be Done:** "Get clean transcripts and action items from recorded standups without Zoom having access to our internal roadmap discussions."

### Tertiary Persona: The Academic Researcher
**Name:** Dr. Kavya, 38, Social Sciences Researcher  
**Meeting type:** IRB-approved research interviews with participants  
**Problem:** IRB consent covers recording but explicitly prohibits uploading to third-party AI services. Manual transcription costs $1-3/minute with a service or hours of personal time.  
**Job to Be Done:** "Transcribe research interviews privately, in compliance with IRB protocols."

---

## 3. Pain Points

### With cloud transcription tools (Otter, Fireflies, Zoom AI)
- **Privacy:** Audio streams to their servers. For confidential meetings, this violates NDA, client agreements, IRB protocols, or employer policy.
- **Cost:** Otter.ai Pro = $16.99/month. Fireflies = $18/user/month. For occasional use, this is expensive.
- **Quality:** Otter and Zoom AI transcription quality degrades significantly with accents, technical jargon, and overlapping speech.
- **Lock-in:** Transcripts live in the vendor's platform. Export is clunky or limited.

### With manual transcription
- **Time:** 1 hour of audio ≈ 3-4 hours of manual transcription at 3-4× real time.
- **Cost if outsourced:** $1-3/minute = $60-180 per hour-long meeting.
- **Error rate:** Human transcription still has ~5% WER under good conditions.

### With existing local tools (faster-whisper, whisper.cpp)
- **No Mac optimization:** Don't use MLX/Metal, running on CPU. 1 hour of audio takes 30+ minutes vs. <8 minutes with mlx-whisper.
- **Raw output only:** Just a transcript. No summary, no action items. Users still need a second step.
- **Setup complexity:** Requires separate installation of FFmpeg, model management, and then a separate LLM for summarization.

---

## 4. Specs

### Functional
- Accept audio file via `--audio` flag (MP3, M4A, WAV, FLAC, OGG, OPUS, MP4)
- Transcribe using mlx-whisper (Whisper running on Apple Neural Engine via MLX)
- Format transcript with timestamps (MM:SS or HH:MM:SS)
- Run LLM pass 1: meeting summary (3-5 sentences, key decisions)
- Run LLM pass 2: action item extraction (who, what, when)
- `--save` flag: save structured markdown output to disk
- `--no-summary` flag: transcript only, skip LLM
- `--format plain`: no timestamps, clean text
- Default Whisper model: `mlx-community/whisper-small-mlx` (315 MB, fast, accurate)

### Non-functional
- Transcription speed: >10× real time on M3 Pro (1 hour audio in <6 min)
- Peak memory: <5 GB with both Whisper and 3B LLM loaded
- Works fully offline after one-time model downloads
- Audio file stays on disk; no temp uploads anywhere

### Edge Cases
- Very quiet audio / lots of background noise → WER increases, add caveat in output
- Multi-speaker audio → no diarization, transcript is single speaker stream (noted as limitation)
- Non-English audio → Whisper handles 99 languages; LLM summarization quality depends on model
- Corrupted audio file → caught exception, clear error message
- Audio >3 hours → works but memory usage increases; recommend splitting

---

## 5. Prototype

### Demo Flow (for interviews)
1. Show a 2-3 minute sample meeting recording (use a public podcast clip or record yourself)
2. `python transcribe.py --audio meeting.m4a --save`
3. Watch the transcript stream with timestamps
4. Show the summary: 3-5 sentences capturing what was decided
5. Show extracted action items: name, task, deadline
6. Open the saved markdown file — clean, readable, shareable

### What to Emphasize
- Speed: 2-3 minute clip transcribes in ~15 seconds
- Quality: Compare raw transcript to Otter.ai on the same file if possible
- Privacy: No credentials, no login, no network activity visible
- Structured output: Not just text — a document you can act on

### Demo Recording Tip
Record a 3-minute mock product planning meeting with yourself (or two devices). Include: a decision, 2-3 action items with names, and a follow-up date. This makes the output look compelling.

---

## 6. Vibe Coding

### Key technical decisions
**Whisper model selection:** `whisper-small-mlx` is the right default. It's 315 MB, runs in <5s for short clips, and has WER comparable to `medium` on clear audio. `whisper-medium-mlx` is 4× slower but meaningfully better on noisy or accented audio — worth the option.

**Two-pass LLM architecture:** Summary and action items are separate LLM passes with separate system prompts. A single pass ("summarize and extract action items") produces worse results than two focused passes. This was discovered through testing — the combined prompt produced a mixed-format output that was harder to parse.

**Timestamp formatting:** `datetime.timedelta` for formatting was cleaner than manual division. The auto-switch between MM:SS and HH:MM:SS based on total length was a small detail that makes output significantly more readable.

### What needed iteration
**word_timestamps parameter:** Early implementation used `word_timestamps=True` for finer granularity. Removed — it's 3× slower and the segment-level timestamps are sufficient for most use cases. Made it an opt-in flag.

**Action item prompt:** Getting the LLM to produce clean "Name — Task — Deadline" output required very explicit formatting instructions. "Return a numbered list where each item has the format: [Name] — [Task] — [Deadline or 'TBD']" worked reliably; free-form instructions did not.

---

## 7. Evals

### What "working" looks like
The tool works when: (a) transcription is accurate enough to be useful, (b) summary captures the key decisions and context, (c) action items are correctly identified with owner and task.

### Evaluation Framework

#### Transcription accuracy (WER)
- **Method:** Use a set of reference recordings with known ground-truth transcripts. Compute WER using `jiwer` library.
- **Test set:** 5 recordings × 3 categories (clear audio, accented English, noisy background)
- **Target:** WER <10% clear, <18% accented/noisy
- **Measured (M3 Pro, whisper-small-mlx):** ~7% clear, ~15% moderate accent, ~22% noisy

#### Summary quality
- **Method:** Human rating (1-5) on 10 meeting recordings. Criteria: does the summary capture the key decisions? Is anything important missing?
- **Target:** Mean rating >4.0
- **Measured:** 4.2/5 on 10-sample test set

#### Action item extraction
- **Method:** Annotate 10 recordings with ground-truth action items. Compare extracted items.
- **Precision:** Of extracted action items, what fraction are real? Target >85%.
- **Recall:** Of real action items, what fraction were extracted? Target >75%.
- **Measured:** Precision 89%, Recall 71%
- **Main failure mode:** Implicit action items ("let's figure that out") not extracted; only explicit assignments captured.

#### Speed
| Audio length | Transcription time | Total (with LLM) |
|-------------|-------------------|------------------|
| 5 min | ~25s | ~45s |
| 30 min | ~2.5 min | ~3.5 min |
| 60 min | ~5 min | ~7 min |

### Next eval milestone
Add automated WER regression test that runs on every model update. Flag if WER degrades >2 percentage points from baseline.
