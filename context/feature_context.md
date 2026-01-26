# Project Context — Weekly Portfolio Briefing (Fintech App)

# Product overview: Fintech App
This product is a consumer fintech app that helps users **track and understand** their long-term investment portfolio.

The product prioritises:
- Trust and numerical accuracy over creativity
- Clear, scannable explanations over market commentary
- Consistent behaviour across millions of users and portfolios

This is not a trading terminal or an advisory product. It is a **portfolio visibility and understanding** product.

---

# Feature overview: Weekly Portfolio Briefing

### What the Weekly Portfolio Briefing is
The **Weekly Portfolio Briefing** is an AI-generated, weekly summary that explains:
- How the user’s portfolio performed over the last week
- Which holdings drove that performance (positive and negative)
- What *provided* market context and *provided* news helps explain that movement

Its core user question is:

> “What moved my portfolio this week, and why?”

The briefing complements existing app surfaces such as:
- Portfolio chart and holdings list
- Performance breakdown by holding
- News tab

It does not replace them.

---

## What the Weekly Portfolio Briefing does
The feature:
- Summarises weekly portfolio performance using **authoritative input numbers**
- Highlights top contributors and detractors using **contribution_pct**
- Uses the provided market context (benchmark, rates, volatility) to frame broad conditions
- Uses the provided news digests (short article summaries) to explain movement **only when linked** to relevant holdings

The output is:
- Deterministic in structure (easy to scan and evaluate)
- Neutral and explanatory (no opinionated market takes)
- Grounded strictly in provided inputs

---

## What the Weekly Portfolio Briefing does NOT do
The briefing must NOT:
- Provide financial advice (no buy/sell/hold, no rebalancing suggestions)
- Make forward-looking predictions or probability statements
- Introduce facts not present in the input (no external macro events, earnings, “breaking news”, etc.)
- Attribute an article’s content to a holding that is not listed in that article’s linked_holdings
- Use fear/urgency language (“act now”, “panic”, “you should move to cash”)
- Mention specific news sources, publishers, or real-world brands

When data is insufficient, omission is preferred over inference.

---

# Goals of the feature

### User goals
- Understand performance drivers without manual analysis
- Feel confident that the explanation is accurate and grounded
- Quickly identify what mattered most (prioritisation)

### Product goals
- Increase weekly engagement and retention
- Reduce confusion and support tickets (“Why did my portfolio move?”)
- Build trust in the app’s analytics layer

### System goals
- High reliability and low hallucination risk
- Outputs that are easy to evaluate deterministically
- Consistent formatting for dashboard comparison at scale

---

# How the system works (conceptual)
The Weekly Portfolio Briefing is generated from structured inputs, including:
- Portfolio summary (starting/ending values, portfolio return)
- Holdings list including weight, weekly return, and contribution
- Market context (benchmark return, volatility proxy, rate moves)
- News digest items consisting of a **2–3 sentence summary** and explicit **linked_holdings**

The model operates under strict prompt constraints that:
- Treat all numbers as authoritative
- Enforce fixed output sections and ordering
- Restrict narrative claims to what can be grounded in the provided fields

Design principle:
> Constrain the model to **explain the provided data**, not to “reason about markets”.

---

# Why this context matters for evals
Evaluations are measuring:
- Numerical fidelity and correct prioritisation
- Grounded use of news digests (no hallucinated causes)
- Appropriate tone and compliance (explanatory, not advisory)
- Deterministic output formatting

This file exists so that every eval run and judge model understands the product intent, not just the surface task of “writing a briefing”.

---

# Current focus: news grounding and linkage

### Why this data exists
The news digest exists to provide **bounded explanatory context** without requiring live browsing.

Each news item:
- Contains a short summary (2–3 sentences)
- Is explicitly linked to one or more holdings via linked_holdings
- Includes a confidence label to guide how strongly it should be used

### How it should be used
- Prefer using news items linked to the **top contributors** first
- Prefer higher-confidence items over lower-confidence items
- If a top contributor has no linked news, explain using market context or acknowledge lack of specific news context

### Constraints
- Do not invent additional “articles” or facts
- Do not apply an article to an unlinked holding
- Do not overstate causality: describe news as contextual explanation, not definitive proof
