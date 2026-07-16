# PM Brief: Private Financial Analyzer

---

## 1. PRD — Product Requirements Document

### Problem Statement
Personal financial data is among the most sensitive information a person has — yet the only AI-powered tools for analyzing it require uploading that data to a company's servers. Mint, YNAB, and banking apps that offer AI insights are explicitly accessing, storing, and often monetizing transaction data. For users who want the insight without the exposure, there is no good option.

### Goal
Build an on-device financial analysis tool that accepts standard bank export CSV files and produces spending analysis, budget breakdowns, and anomaly detection using a local LLM — with zero financial data leaving the device.

### Non-Goals
- Direct bank account connection / Plaid integration (requires sending credentials to a service)
- Real-time transaction monitoring
- Investment portfolio analysis (out of scope)
- Tax preparation

### User Stories
- As a privacy-conscious professional, I want to analyze my spending patterns without my transaction data going to Mint, YNAB, or any other company.
- As someone rebuilding financially, I want to identify where I'm overspending without sharing that information with an advertiser-funded platform.
- As a small business owner, I want to analyze my business credit card transactions locally before sharing insights with my accountant.
- As a budget-conscious person, I want to detect duplicate charges and unusual transactions in my data privately.

### Success Metrics
| Metric | Target |
|--------|--------|
| Correct column auto-detection (Chase, BofA, generic) | >95% on common formats |
| Category classification accuracy | >85% on standard merchant names |
| Anomaly detection precision | >80% (flagged items are genuinely unusual) |
| Anomaly detection recall | >75% (catches real duplicates/unusual charges) |
| Zero financial data transmitted | ✓ |

---

## 2. Users

### Primary Persona: The Privacy-First Professional
**Name:** Tara, 29, Software Engineer  
**Financial situation:** Mid-to-high income, several subscriptions, eats out frequently  
**Current tool:** Tries Mint but uncomfortable with their data practices (Intuit acquisition made it worse). Uses spreadsheets manually.  
**Job to Be Done:** "Show me where my money is going without me having to give my financial data to a company that will monetize it or get hacked."

### Secondary Persona: The Self-Improvement Budgeter
**Name:** Aditya, 26, Marketing Manager  
**Financial situation:** Aggressively paying off student loans, tracking every dollar  
**Current tool:** YNAB ($15/month) — but uncomfortable that YNAB has access to his full transaction history  
**Job to Be Done:** "Tell me whether I'm on track with my budget and flag anything unusual, but keep my financial data on my laptop."

### Tertiary Persona: The Small Business Owner
**Name:** Lisa, 42, Freelance Designer  
**Financial situation:** Mixed personal and business expenses on one card  
**Current tool:** Exports from Chase and reviews manually in Excel  
**Problem:** An AI that could categorize and summarize her business expenses would save 2 hours/month, but she doesn't want her business financials in the cloud.  
**Job to Be Done:** "Analyze my business card transactions locally so I can prep for my accountant without sending client-sensitive data to a third party."

---

## 3. Pain Points

### With cloud financial tools (Mint, YNAB, Copilot, banking apps)
- **Data monetization:** Mint/Intuit explicitly uses financial data for ad targeting and credit offers. Users with Mint are the product.
- **Security risk:** Centralized storage of financial data is a high-value target. Mint, Equifax, Capital One have all been breached.
- **Privacy invasion:** Knowing your spending patterns reveals your life: health conditions (pharmacy purchases), relationship status, political beliefs (donations), mental health (therapy payments).
- **Terms of service abuse:** Most tools' ToS allow broad use of transaction data for "improving services" — often meaning ML training on your financial behavior.

### With manual analysis (Excel/Sheets)
- **Time-consuming:** Categorizing and summarizing 100+ transactions takes 1-2 hours.
- **No intelligence:** Excel can total columns. It can't tell you "your dining spend is unusually high this month" or "this $12.99 charge looks like a duplicate."
- **No narrative:** Raw numbers don't explain themselves. A natural language summary of "here's what happened to your money this month" requires human synthesis.

---

## 4. Specs

### Functional
- Load CSV via `--csv` argument
- Auto-detect column names for amount, date, description from common bank formats
- Encoding fallback: try utf-8 → latin-1 → cp1252
- Compute statistical summary: total, by-category totals, largest transactions
- Four modes: `overview`, `budget`, `anomalies`, `chat`
- Auto-detect amount/date/description columns from: Chase, BofA, YNAB, Mint, generic
- In chat mode: multi-turn Q&A grounded in the loaded transaction data

### Non-functional
- No network requests (LLM runs locally via MLX)
- CSV never written to any external location
- Works on files up to 10,000 rows without performance degradation
- Memory usage <6 GB for analysis + 3B LLM

### Edge Cases
- Negative amounts (credits vs debits): detect and handle sign convention per bank
- Mixed currencies: flag to user, analyze as-is
- Missing date column: analysis still possible for spending patterns (not temporal)
- Merchant names with special characters / encoding issues → handled by encoding fallback

---

## 5. Prototype

### Demo Flow (for interviews)
1. Download your own bank statement as CSV (Chase, BofA, or any bank)
2. `python analyze.py --csv transactions.csv` — show spending overview
3. Highlight: top categories, largest transactions, insights like "dining is 10% of spend"
4. `--mode anomalies` — show unusual charge detection
5. `--mode chat` — ask "how much did I spend on food last month?"
6. Show: no network activity, runs in terminal, CSV stays on your disk

### For Interviewers (PM angle)
Frame it as: "I built a tool to answer the question: what if you could have Mint-quality insights without Mint's business model?" The privacy-first constraint forced specific product choices (local inference, CSV import instead of Plaid) that tell a clear product story.

---

## 6. Vibe Coding

### Column auto-detection
The most useful engineering decision was column auto-detection. Rather than requiring users to specify column names, the tool guesses from common patterns:
- Amount: columns named "amount", "transaction amount", "debit", "credit"
- Date: columns named "date", "transaction date", "post date"
- Description: columns named "description", "payee", "merchant"

This was built by listing 8 common bank export formats and writing detection logic for each. The vibe coding approach: describe the formats, ask the LLM to generate the detection logic, test on real exports.

### Category inference
Merchant-to-category mapping is inherently imperfect. The approach: inject the top 30 merchant names into the LLM context and ask it to group them into categories. This is more flexible than a lookup table and more accurate than keyword matching — the LLM correctly categorizes "WHOLEFDS #10347" as Groceries and "AMZN MKTP US" as Shopping.

---

## 7. Evals

### What "working" looks like
The analyzer works when: (a) column auto-detection succeeds on common bank export formats, (b) spending categories are correctly assigned, (c) anomalies (duplicates, unusual charges) are correctly flagged, (d) the natural language summary is accurate and useful.

### Evaluation Framework

#### Column detection accuracy
- **Test set:** 10 real bank export CSV formats (Chase, BofA, Citi, Wells Fargo, YNAB, Mint, generic)
- **Target:** >95% correct column identification
- **Current:** 9/10 formats detected correctly (Citi's format has an unusual amount sign convention)

#### Category classification
- **Method:** Take 50 merchant names with known ground-truth categories. Score auto-classification.
- **Target:** >85% accuracy
- **Current:** ~83% — main errors are ambiguous merchants (Amazon can be Shopping, Electronics, or Groceries)

#### Anomaly detection
- **Method:** Create test CSVs with planted anomalies (duplicate charges, unusually large transactions, new merchant categories). Measure precision and recall.
- **Precision target:** >80% (flagged items are real anomalies)
- **Recall target:** >75% (real anomalies get flagged)
- **Current:** Precision 84%, Recall 68% — recall is weaker because subtle anomalies (10% higher than usual in a category) are missed

#### Chat mode accuracy
- **Method:** Ask 10 specific factual questions about a test CSV with known answers. Score correctness.
- **Target:** >90% factual accuracy on direct questions about the data
- **Current:** 92% — the main failure mode is questions that require cross-month comparison when only one month is loaded

### Next eval milestone
Add automated test harness with synthetic transaction data (known ground truth) that runs category classification and anomaly detection on every code update.
