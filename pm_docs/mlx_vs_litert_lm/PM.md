# PM Brief: MLX vs LiteRT-LM Runtime Benchmark

---

## 1. PRD — Product Requirements Document

### Problem Statement
Product managers building on-device AI face a foundational question with no good public answer: which runtime should we use? MLX, LiteRT-LM, Ollama, and llama.cpp all claim to run LLMs locally, but their real performance characteristics on Apple Silicon — the dominant developer hardware — are not independently measured and published in a format that's useful for product decisions.

### Goal
Run a controlled, reproducible benchmark of MLX vs LiteRT-LM on the same hardware, same model, same prompt — and publish the results with enough context for a PM or engineer to make an informed runtime choice.

### Non-Goals
- Benchmarking on non-Apple hardware (Windows GPU, Linux CUDA)
- Model quality evaluation (only speed and memory)
- Benchmark of all possible models (one representative 4B model)
- Android/mobile benchmarking

### User Stories
- As a PM scoping an on-device AI feature, I want to know the expected latency and memory footprint before committing to a runtime choice.
- As an engineer evaluating MLX vs LiteRT-LM, I want independent benchmark data rather than each vendor's own claims.
- As a developer building for cross-platform, I want to understand the performance cost of LiteRT-LM's portability vs MLX's Apple-specific optimization.
- As a startup CTO, I want to know if the 16× decode speed difference matters for my use case, or if LiteRT-LM's cross-platform support justifies the trade-off.

### Success Metrics
| Metric | Target |
|--------|--------|
| Benchmark is reproducible by others | ✓ (open source, documented) |
| Numbers are measured, not synthetic | ✓ (real hardware, real timing) |
| Results include confidence intervals | ✓ (5 trials each, report mean + std) |
| Coverage: TTFT, prefill, decode, memory | ✓ (all four measured) |
| Published as a real GitHub artifact | ✓ |

---

## 2. Users

### Primary Persona: The Technical PM
**Name:** Shreelaxmi, 24, PM Candidate targeting Google/Apple AI roles  
**Context:** Building a portfolio demonstrating on-device AI depth. Needs to show, not just state, that she understands runtime trade-offs.  
**Job to Be Done:** "Have real measured data that I can cite in interviews when asked 'how does MLX compare to LiteRT-LM?'"

### Secondary Persona: The Startup Engineer
**Name:** Ben, 29, Full-Stack Engineer at a small startup  
**Context:** Building an on-device AI feature for a Mac app. Needs to choose between MLX (faster, Apple only) and LiteRT-LM (slower, cross-platform).  
**Job to Be Done:** "Give me real numbers so I can justify the runtime choice to my team and know what latency to promise users."

### Tertiary Persona: The Developer Advocate / Writer
**Name:** Anika, 32, Technical Writer / ML Engineer  
**Context:** Writing about on-device AI options. Needs independent benchmarks to cite that aren't from the runtime vendors themselves.  
**Job to Be Done:** "Find independent, reproducible benchmark data for MLX vs LiteRT-LM that I can reference without reproducing myself."

---

## 3. Pain Points

### With vendor-published benchmarks
- **Conflict of interest:** Every runtime publishes benchmarks where they look favorable. Selection of test cases, models, and metrics is inherently biased.
- **Opaque methodology:** "We tested on our internal hardware" with no reproduction instructions is not useful for engineers making real decisions.
- **Cherry-picked metrics:** MLX focuses on decode speed (their strength). LiteRT-LM focuses on cross-platform reach (their strength). Neither publishes a head-to-head on the other's metric.

### With "just try both" approach
- **Time cost:** Setting up both runtimes, finding the same model in both formats, writing comparable measurement code takes 4-8 hours for a non-expert.
- **Methodology inconsistency:** Ad-hoc timing approaches (wall clock, `time.time()`) produce unreliable results. Need proper warmup, multiple trials, and measurement of the right thing (TTFT vs decode speed vs prefill vs memory).

---

## 4. Specs

### Functional
- `mlx_benchmark.py`: benchmark MLX runtime — measures TTFT, prefill tok/s, generation tok/s, peak memory
- `litert_benchmark.py`: benchmark LiteRT-LM (GPU and CPU backends) — same metrics
- 5 trials per measurement, first trial used as warmup, report mean + std of trials 2-5
- Fixed prompt (~256 tokens, same for both), fixed output length (128 tokens)
- Resource.getrusage for peak memory measurement
- Results printed as a rich table

### Non-functional
- Scripts are self-contained — download and run in one command
- Reproduce on any Apple Silicon Mac
- Results match published numbers in README (no post-hoc editing)

### Edge Cases
- LiteRT-LM GPU+MTP mode: Qwen3-4B-Instruct-2507 not converted with MTP support → flag in results, don't present as runtime failure
- Model download required on first run: handled gracefully, not counted in timing
- Memory measurement accuracy: `resource.getrusage` measures peak RSS, which includes model loading overhead

---

## 5. Prototype

### Demo Flow (for interviews)
This is a benchmark, not a user-facing app — the "prototype" is the data itself.

**The PM interview angle:**
1. "I ran a real head-to-head benchmark of MLX vs LiteRT-LM on M3 Pro. The results surprised me."
2. Present the table: 44.62 vs 2.81 tok/s — 16× decode speed gap
3. "But prefill speed is almost identical: 615 vs 548 tok/s."
4. Explain *why*: MLX's Metal kernels for matrix-vector multiplication (the autoregressive decode bottleneck) are Apple Silicon-specific. LiteRT-LM uses a generic GPU abstraction.
5. "Here's when each runtime is the right choice..." — deliver the framework, not just the data.

### What to Emphasize
- You ran these experiments yourself on real hardware
- You understand *why* the gap exists (not just that it exists)
- You can articulate the trade-off in product terms: "Use MLX for speed-sensitive Mac-only features; use LiteRT-LM when you need the same code on Android."

---

## 6. Vibe Coding

### Async streaming for LiteRT-LM
LiteRT-LM's Python API is async — `conversation.send_message_async()` returns an async generator. This required wrapping benchmark calls in `asyncio.run()`. Vibe coding caught this on first test run and the fix was one iteration.

### Memory measurement
`resource.getrusage(RUSAGE_SELF).ru_maxrss` returns bytes on Linux, kilobytes on macOS (yes, really — it's a macOS quirk). The benchmark handles this with platform detection. Discovered during cross-machine testing.

### Warmup strategy
First trial always runs substantially slower due to Metal shader compilation and memory allocation. Using trial 1 as warmup and averaging trials 2-5 produces numbers representative of real-world warm-path performance.

### LiteRT-LM MTP failure
The Qwen3-4B model wasn't converted with Multi-Token Prediction support, so GPU+MTP failed with `embedding_lookup != nullptr`. This is a model-level constraint, not a runtime bug. Documenting this accurately was a judgment call — it would have been easy to omit it, but real benchmarks include failures.

---

## 7. Evals

### What "working" looks like
The benchmark works when: (a) numbers are consistent across multiple runs (low variance), (b) numbers are plausible given known hardware specs, (c) the measurement methodology is reproducible by others.

### Reproducibility Check
| Metric | Run 1 | Run 2 | Run 3 | Std Dev |
|--------|-------|-------|-------|---------|
| MLX Gen (tok/s) | 44.1 | 45.2 | 44.5 | ±0.56 |
| LiteRT GPU Gen (tok/s) | 2.78 | 2.83 | 2.84 | ±0.03 |
| MLX TTFT (ms) | 14 | 17 | 16 | ±1.5 |
| LiteRT GPU TTFT (ms) | 538 | 544 | 541 | ±3.1 |

Low variance confirms measurement methodology is sound.

### Sanity checks
- MLX decode speed should be bandwidth-limited: Llama 3.2 3B INT4 = ~1.7 GB model, M3 Pro has ~200 GB/s bandwidth → theoretical ~117 tok/s. Measured 44 tok/s is plausible (overhead from attention, sampling, etc.).
- LiteRT-LM TTFT of 541ms vs MLX 16ms: 33× gap is expected — LiteRT-LM compiles Metal shaders on first inference; subsequent runs are faster but still much slower than MLX's pre-optimized kernels.

### What the numbers actually mean for product decisions
- For **interactive chat**: MLX wins clearly. 44 tok/s feels instant. 2.8 tok/s is noticeably slow for conversational use.
- For **batch processing** (not real-time): LiteRT-LM is viable — 2.8 tok/s still processes a 128-token response in ~45 seconds.
- For **prefill-heavy use** (long context, short output): Gap narrows — prefill is 12% faster with MLX, not 16×.
- For **cross-platform**: LiteRT-LM is the only option. MLX doesn't exist on Android or Windows.

### Next benchmark milestone
Add llama.cpp (CPU-only) and Ollama to the comparison table. Measure across M1, M2, and M3 chips to produce a hardware × runtime matrix.
