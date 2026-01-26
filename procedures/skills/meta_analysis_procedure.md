# Meta-Analysis Procedure (Chat Prompt)

Use this file as the single, repeatable prompt for the chat model to generate a meta-analysis report for one eval run.

The report must:
- cluster issues (and also note strengths to preserve)
- rank clusters by priority
- cite specific examples (with full outputs)
- focus on judge explanations more than scores
- keep the feature context in mind (product intent, constraints, what "good" means)
- review all outputs and judge explanations, not just failures or near-fails

---

## Inputs (Run-Scoped)

You are generating a report for: `RUN_ID = <RUN_ID>`

Before you start, ensure these exist:
- `outputs/runs/<RUN_ID>/<RUN_ID>_eval_results.jsonl` (full results)
- `outputs/runs/<RUN_ID>/<RUN_ID>_eval_results_slim.jsonl` (slim results)
- `outputs/runs/<RUN_ID>/<RUN_ID>_system_prompt.md`
- `outputs/runs/<RUN_ID>/<RUN_ID>_user_prompt.md`
- `outputs/runs/<RUN_ID>/<RUN_ID>_Evals.json`
- `outputs/runs/<RUN_ID>/<RUN_ID>_run_manifest.json`

If `RUN_ID` is not provided, ask the user which run to analyze (or default to the latest run folder in `outputs/runs/`).

---

## Step 1: Load Context (Read These Files First)

### Product & Methodology Context
- `context/feature_context.md`
- `context/eval_methodology.md`

### Prompts & Eval Criteria (Use The Run Snapshots)
- `outputs/runs/<RUN_ID>/<RUN_ID>_system_prompt.md`
- `outputs/runs/<RUN_ID>/<RUN_ID>_user_prompt.md`
- `outputs/runs/<RUN_ID>/<RUN_ID>_Evals.json`

### Run Metadata
- `outputs/runs/<RUN_ID>/<RUN_ID>_run_manifest.json`

### Results Data
- `outputs/runs/<RUN_ID>/<RUN_ID>_eval_results_slim.jsonl` (primary analysis input; use for clustering)
- `outputs/runs/<RUN_ID>/<RUN_ID>_eval_results.jsonl` (source of truth; use to validate top clusters)

Keep this context in mind throughout. Clusters must be described in terms of product impact, not just judge language.

---

## Step 2: Compute Overall Stats

Using the run manifest + results:

### A) Run Summary
- Run id
- Started/finished timestamps (UTC)
- Total executions
- Judge models used (from `<RUN_ID>_run_manifest.json`)

### B) Criterion Score Table
For each eval criterion:
- Avg score
- Pass rate
- Failures count

Format as:

```text
| Criterion | Avg Score | Pass Rate | Failures |
|---|---:|---:|---:|
| ... | ... | ... | ... |
```

### C) Priority Signal
Rank criteria by failures count (descending) and call out the top 1–3 that deserve attention first.

---

## Step 3: Per-Criterion Clustering (Explanations First)

For each criterion in `<RUN_ID>_Evals.json`, do the following using the slim results file.

### A) Build Evidence Sets
Use all executions and their explanations as the primary evidence set. Then derive subsets:
- Failures: `score < pass_threshold`
- Near-fails: `score == pass_threshold` (borderline passes)
- Strong passes: pick 3–5 of the highest-scoring executions for this criterion

Scores are secondary. Judge explanations are the primary evidence.

### B) Identify Patterns (Grounded In Context)
Look for repeated patterns across all explanations (passes + fails), and interpret them in terms of:
- Product intent and constraints (from `context/feature_context.md`)
- What the generation prompt is trying to enforce
- What the eval criterion is actually measuring

Typical root-cause categories:
- Prompt: missing/ambiguous/conflicting instruction
- Data: missing fields, inconsistent schemas, edge cases
- Eval: criterion definition misaligned or too loose/tight
- Model: consistent misinterpretation despite clear prompt
- Mixed: a combination

### C) Form 1–5 Issue Clusters (Ranked)
Cluster issues surfaced across the full set of outputs (including passes) into 1–5 clusters, ranked by priority:
1) Severity (product risk), then
2) Prevalence (how common), then
3) Likelihood of successful remediation (confidence)

For each cluster, include:
- Cluster name (short, specific)
- Severity: High / Medium / Low
- Root cause: prompt / data / eval / model / mixed
- Pattern (what is happening, grounded in judge explanations)
- Explanation signal (what the judge repeatedly says)
- Insight narrative (3–6 sentences) that explains the cluster in depth: what’s happening, why it’s happening, how it shows up in the outputs, and why a user would care. This should stand on its own so the user doesn’t need to read every eval.
- Why it matters (tie explicitly to product context)
- Prevalence (N executions; X% of failures for this criterion)
- Examples: exactly 3 examples when possible

Example selection rules:
- Prefer failures and near-fails first
- If a pattern is primarily visible in passes, include passed examples explicitly
- If there are fewer than 3 relevant examples, use as many as exist (do not invent)

Each example MUST include the full output text (no excerpts).

### D) Also Capture Strengths To Preserve (Not Just Failures)
From the strong-pass set, note 1–3 patterns that are working well for this criterion (based on judge explanations), so remediation does not accidentally break them.
Include 1–2 example execution IDs (no need to paste outputs here unless it materially clarifies the pattern).

---

## Step 4: Validate Top Clusters With Full Results

After you have:
- per-criterion clusters, and
- an overall priority ordering,

re-load the highest-priority clusters (top ~3–5 clusters overall) using the FULL results file:
- `outputs/runs/<RUN_ID>/<RUN_ID>_eval_results.jsonl`

For each validated cluster:
- Confirm the slim input did not omit a critical field needed to diagnose the root cause
- Adjust root cause / recommendation if full context changes the conclusion
- Keep report structure stable (this is a verification pass, not a rewrite)

---

## Step 5: Cross-Criterion Patterns

Identify:
- Systemic issues appearing across multiple criteria
- Cascade effects (one issue causes multiple failures)
- Data dependencies (failures concentrated in specific input conditions)

Keep this section concrete: cite criteria + a few execution IDs to support each claim.

---

## Step 6: Remediation Plan (Prevent Cascading Side Effects)

Translate the top clusters into actions, grouped by lever:
- Prompt edits (exact text changes, plus the risk/trade-off)
- Data fixes (schema changes, required fields, edge-case handling)
- Eval updates (tighten/loosen criteria or add a missing eval)
- Model changes (if relevant)

For each action, include:
- What it fixes (clusters)
- What it might break (strengths-to-preserve signals)
- How to validate (what to re-run / what to sanity-check in the dashboard)

---

## Step 7: Write The Report

Save to:

`outputs/runs/<RUN_ID>/<RUN_ID>_meta_analysis_report.md`

Use this structure:

```markdown
# Meta-analysis report
*Generated: YYYY-MM-DD HH:MM (UTC)*
*Run: <RUN_ID>*

## Executive summary (ranked)
- ...

## Run metadata
- ...

## Overall statistics
| Criterion | Avg Score | Pass Rate | Failures |
|---|---:|---:|---:|
| ... | ... | ... | ... |

## Top clusters (cross-criterion)
1. **[Cluster name]** (Severity: High) — affects: [criteria...]
   - Pattern: ...
   - Why it matters: ...
   - Examples: Exec #X, #Y, #Z
   - Recommendation: ...

## Criterion breakdowns

### [Criterion name]
**Pass rate**: X% | **Avg score**: Y/Z | **Failures**: N

#### Issue clusters (ranked)

##### Cluster 1: [Name]
- Root cause: prompt/data/eval/model/mixed
- Severity: High/Medium/Low
- Pattern: ...
- Explanation signal: ...
- Why it matters: ...
- Prevalence: N (X% of failures)
- Examples (full outputs):

**Exec #X (failure/near-fail)**
**Output:**
```
[Full output]
```
**Judge explanation:** [Full explanation text]
**Issue:** [Plain-language issue note]

**Exec #Y ...**
...

#### Strengths to preserve
- ...

## Cross-criterion patterns
- ...

## Remediation plan (ranked)
1. ...

## Appendix: Notes / edge cases
- ...
```

---

## Report Quality Checklist (Must Pass)

- Every cluster is grounded in judge explanations (not vibes).
- Clusters are explicitly ranked by priority (severity first).
- Examples include full outputs (no excerpts) and include the judge explanation text.
- Strengths-to-preserve are noted so fixes don’t cause regressions.
- The report is saved to: `outputs/runs/<RUN_ID>/<RUN_ID>_meta_analysis_report.md`
