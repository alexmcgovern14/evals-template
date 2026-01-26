# Meta-analysis report
*Generated: 2026-01-25 14:39 (UTC)*
*Run: 01*

## Executive summary (ranked)
- **Top contributors ordering errors** are the most consistent quantitative issue across outputs, producing misleading “what moved” ordering and cascading into narrative phrasing problems.
- **Summary insight depth is uneven** across many passes, with repetitive boilerplate and weak benchmark/market context linkage reducing the feature’s explanatory value.
- **Directional phrasing for negative contributors** is a recurring wording drift that creates minor grounding overreach and compliance risk.

## Run metadata
- Run id: 01
- Started: 2026-01-25T13:22:14.754645+00:00
- Finished: 2026-01-25T14:00:10.294262+00:00
- Total executions: 20
- Judge models: gpt-4o-mini (Numerical fidelity, Structure & formatting, News grounding & linkage, Tone, compliance & insight quality)

## Overall statistics
| Criterion | Avg Score | Pass Rate | Failures |
|---|---:|---:|---:|
| Numerical fidelity | 9.00 | 90.0% | 2 |
| Structure & formatting | 9.30 | 95.0% | 1 |
| News grounding & linkage | 9.20 | 100.0% | 0 |
| Tone, compliance & insight quality | 7.95 | 85.0% | 3 |

Priority signal (by failures): Tone, compliance & insight quality (3) → Numerical fidelity (2) → Structure & formatting (1).

## Top clusters (cross-criterion)
1. **Top contributors misordered by absolute contribution** (Severity: High) — affects: Numerical fidelity, Structure & formatting
   - Pattern: TOP CONTRIBUTORS list is not sorted by absolute contribution, which flips the story of the week.
   - Why it matters: Users rely on this ordering to understand drivers; misordering undermines trust and contradicts the deterministic format.
   - Examples: Exec #7, Exec #6, Exec #20
   - Recommendation: Enforce absolute sorting in prompt and/or upstream data; add sign-aware language rules for the summary insight.
2. **Directional phrasing conflicts with negative contributors** (Severity: Medium) — affects: News grounding & linkage, Tone, compliance & insight quality
   - Pattern: Phrases like “led the move” or “moved in the opposite direction” are used when the holding is a negative contributor, implying positive causality or advisory tone.
   - Why it matters: This erodes grounding precision and risks compliance tone for a non-advisory product.
   - Examples: Exec #7, Exec #15, Exec #4
   - Recommendation: Require “largest detractor / biggest drag” phrasing for negative contributors and avoid causality language.
3. **Summary insight is shallow or repetitive** (Severity: Medium) — affects: Tone, compliance & insight quality
   - Pattern: Insight paragraph repeats sector boilerplate and underuses benchmark/market context, even in passes.
   - Why it matters: The summary insight is the primary value-add; shallow insights reduce user understanding and engagement.
   - Examples: Exec #16, Exec #18, Exec #2
   - Recommendation: Add explicit requirements for benchmark comparison + one market-context linkage + one news linkage when available.

## Criterion breakdowns

### Numerical fidelity
**Pass rate**: 90% | **Avg score**: 9.00/10 | **Failures**: 2

#### Issue clusters (ranked)

##### Cluster 1: Top contributors not sorted by absolute contribution
- Root cause: prompt
- Severity: High
- Pattern: Ordering mistakes in TOP CONTRIBUTORS, especially with mixed sign contributions.
- Explanation signal: “ordering … incorrect,” “negative contribution listed as top contributor.”
- Insight narrative: The model often produces the correct values but fails to rank by absolute contribution, which reshapes the perceived drivers of the week. This appears even in passes (scores 8–9), suggesting a prompt clarity issue rather than random error. Because the product’s core question is “what moved my portfolio,” incorrect ordering is a high-severity risk. The pattern is concentrated in cases with mixed positive and negative contributors, where the model seems to default to a different ordering heuristic. Users would likely misinterpret the main drivers when the largest detractor is labeled as the top contributor.
- Why it matters: Incorrect ordering breaks deterministic output and misstates the most important holdings.
- Prevalence: 9 executions; 100% of failures for this criterion
- Examples (full outputs):

**Exec #7 (failure)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-06-22 to 2026-06-28

PERFORMANCE
- Portfolio change: +0.58%
- Starting value: $159,166.00
- Ending value: $160,089.16
- Benchmark change: +0.48%

TOP CONTRIBUTORS
1. Stock S (STK_S): -0.65%
2. Stock Q (STK_Q): +0.62%
3. Stock V (STK_V): +0.51%

MARKET CONTEXT
- Average volatility index: 16.2
- Interest rate change: 25 bps

SUMMARY INSIGHT
The portfolio outperformed the benchmark this week, with Stock S leading the move after industrials names gained as pricing momentum strengthened and cost pressures eased. Stock Q moved in the opposite direction, aligned with real estate performance was mixed, with defensives holding up while growth-oriented names slipped. Market conditions were steady with volatility at 16.2, and rates moved up. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing contains some numerical errors, particularly in the ordering of the top contributors by absolute contribution. Stock S, which had a negative contribution, is incorrectly listed as the top contributor. Additionally, the contributions of Stock N and Stock V are not in the correct order based on their absolute contributions. The other numerical values, including portfolio change, starting and ending values, and benchmark change, are accurate.
**Issue:** Ordering is not by absolute contribution.

**Exec #6 (near-fail)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-06-15 to 2026-06-21

PERFORMANCE
- Portfolio change: +0.26%
- Starting value: $100,021.00
- Ending value: $100,281.05
- Benchmark change: +1.03%

TOP CONTRIBUTORS
1. Stock U (STK_U): -1.21%
2. Stock R (STK_R): +0.90%
3. ETF Y (ETF_Y): +0.85%

MARKET CONTEXT
- Average volatility index: 21.2
- Interest rate change: 10 bps

SUMMARY INSIGHT
The portfolio underperformed the benchmark this week, with Stock U leading the move after consumer performance was mixed, with defensives holding up while growth-oriented names slipped. Stock R moved in the opposite direction, aligned with investors rotated into materials names as risk appetite stabilised and valuations looked more balanced. Market conditions were steady with volatility at 21.2, and rates moved up. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing is mostly correct with minor issues. The portfolio change, starting and ending values, and benchmark change all match the input data accurately. However, the ordering of the top contributors is incorrect; Stock R and ETF Y should be listed before Stock U based on their absolute contributions. This slight misordering affects the overall score.
**Issue:** Ordering is not by absolute contribution.

**Exec #20 (near-fail)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-09-21 to 2026-09-27

PERFORMANCE
- Portfolio change: +0.10%
- Starting value: $143,920.00
- Ending value: $144,063.92
- Benchmark change: +0.41%

TOP CONTRIBUTORS
1. Stock Q (STK_Q): +1.25%
2. Stock P (STK_P): -0.68%
3. Stock N (STK_N): -0.37%

MARKET CONTEXT
- Average volatility index: 25.6
- Interest rate change: 0 bps

SUMMARY INSIGHT
The portfolio underperformed the benchmark this week, with Stock Q leading the move after energy names gained as pricing momentum strengthened and cost pressures eased. Stock P moved in the opposite direction, aligned with healthcare stocks softened after guidance commentary pointed to slower near-term activity. Market conditions were steady with volatility at 25.6, and rates were unchanged. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing is mostly correct with minor issues. The portfolio change, starting and ending values, and benchmark change all match the input data accurately. However, the ordering of the top contributors is incorrect; Stock P should not be listed before Stock N based on their absolute contributions. This misordering affects the overall fidelity score.
**Issue:** Ordering is not by absolute contribution.

##### Cluster 2: Minor precision and completeness lapses in contributor list
- Root cause: prompt
- Severity: Medium
- Pattern: Rounding/precision commentary and occasional missing contributor mention appear alongside otherwise correct values.
- Explanation signal: “minor rounding issues,” “contribution percentage … not mentioned.”
- Insight narrative: A smaller set of outputs shows rounding commentary or missing contributor mentions in the TOP CONTRIBUTORS list. These are not large numerical errors, but they introduce ambiguity in the most visible section of the briefing. The issues often co-occur with ordering mistakes, suggesting a single prompt weakness around how to select and display the list. Even when the list looks numerically correct, missing a top contributor undermines the “biggest drivers” promise. Users may mistrust the system if an obvious contributor is absent from the ranked list.
- Why it matters: Small display errors reduce confidence in a trust-sensitive fintech summary.
- Prevalence: 3 executions; 50% of failures for this criterion (co-occurs with ordering issues)
- Examples (full outputs):

**Exec #12 (near-fail)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-07-27 to 2026-08-02

PERFORMANCE
- Portfolio change: +0.17%
- Starting value: $102,018.00
- Ending value: $102,191.43
- Benchmark change: +0.42%

TOP CONTRIBUTORS
1. ETF Y (ETF_Y): -0.96%
2. ETF W (ETF_W): +0.93%
3. Stock S (STK_S): +0.57%

MARKET CONTEXT
- Average volatility index: 25.9
- Interest rate change: -10 bps

SUMMARY INSIGHT
The portfolio underperformed the benchmark this week, with ETF Y leading the move after healthcare stocks softened after guidance commentary pointed to slower near-term activity. ETF W moved in the opposite direction, aligned with industrials shares were supported by steady demand trends and improved margins across the week. Market conditions were steady with volatility at 25.9, and rates moved lower. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing is mostly correct with minor rounding issues. The portfolio change, starting and ending values, and benchmark change all match the input data accurately. However, the ordering of the top contributors is incorrect; ETF W should be listed before Stock S based on absolute contribution values. This affects the overall fidelity score.
**Issue:** Minor rounding commentary and ordering error.

**Exec #14 (failure)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-08-10 to 2026-08-16

PERFORMANCE
- Portfolio change: +2.15%
- Starting value: $120,140.00
- Ending value: $122,723.01
- Benchmark change: +0.12%

TOP CONTRIBUTORS
1. Stock R (STK_R): +1.04%
2. Stock N (STK_N): +1.00%
3. Stock U (STK_U): +0.89%

MARKET CONTEXT
- Average volatility index: 18.4
- Interest rate change: 0 bps

SUMMARY INSIGHT
The portfolio outperformed the benchmark this week, with Stock R leading the move after financials stocks softened after guidance commentary pointed to slower near-term activity. Stock N moved in the opposite direction, aligned with energy stocks softened after guidance commentary pointed to slower near-term activity. Market conditions were steady with volatility at 18.4, and rates were unchanged. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing is mostly correct with minor rounding issues and one ordering error. The contribution of Stock N is incorrectly listed as +1.00% instead of the correct +1.00% (which is a rounding issue). Additionally, the ordering of the top contributors is incorrect; Stock U should be listed before Stock N based on absolute contribution values. All other numerical values match the input data accurately.
**Issue:** Minor rounding/precision commentary co-occurs with ordering.

**Exec #15 (near-fail)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-08-17 to 2026-08-23

PERFORMANCE
- Portfolio change: +0.21%
- Starting value: $138,146.00
- Ending value: $138,436.11
- Benchmark change: +0.54%

TOP CONTRIBUTORS
1. ETF Y (ETF_Y): -1.19%
2. ETF Z (ETF_Z): +0.68%
3. ETF X (ETF_X): +0.61%

MARKET CONTEXT
- Average volatility index: 19.0
- Interest rate change: 0 bps

SUMMARY INSIGHT
The portfolio underperformed the benchmark this week, with ETF Y leading the move after healthcare names gained as pricing momentum strengthened and cost pressures eased. ETF Z moved in the opposite direction, aligned with utilities names gained as pricing momentum strengthened and cost pressures eased. Market conditions were steady with volatility at 19.0, and rates were unchanged. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing is mostly correct with minor issues. The portfolio change, starting and ending values, and benchmark change all match the input data. However, the ordering of the top contributors is incorrect; ETF Z should be listed before ETF X based on their absolute contributions. Additionally, the contribution percentage for Stock T is not mentioned in the top contributors, which could lead to confusion. Overall, the numerical fidelity is high, but the ordering issue affects the score.
**Issue:** Missing contributor mention in the list.

#### Strengths to preserve
- Accurate transcription of portfolio and benchmark values without invented figures (Exec #1, Exec #2).
- Correct 2dp formatting and sign handling when ordering is correct (Exec #3, Exec #8).

### Structure & formatting
**Pass rate**: 95% | **Avg score**: 9.30/10 | **Failures**: 1

#### Issue clusters (ranked)

##### Cluster 1: TOP CONTRIBUTORS list selection/order inconsistencies
- Root cause: prompt
- Severity: Medium
- Pattern: The list sometimes excludes a positive contributor or presents ordering/selection that conflicts with the “top contributors” requirement.
- Explanation signal: “does not include Stock U,” “lists … in the wrong order,” “misleading as it had a negative contribution.”
- Insight narrative: Structural compliance is strong overall, but when it fails, the issue is almost always in the TOP CONTRIBUTORS list. The model sometimes treats “top contributors” as negative-only or applies an inconsistent ordering rule, which deviates from the deterministic format. This is a structural error because the list is a required section with specific expectations. The mis-selection appears in both near-fails and the one failure, indicating a systematic ambiguity rather than a one-off slip. If not fixed, this creates confusion for users who expect the list to contain the largest absolute contributors, regardless of sign.
- Why it matters: The list is a core structural element; errors here degrade trust and scan-ability.
- Prevalence: 6 executions; 100% of failures for this criterion
- Examples (full outputs):

**Exec #4 (near-fail)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-06-01 to 2026-06-07

PERFORMANCE
- Portfolio change: -2.15%
- Starting value: $73,278.00
- Ending value: $71,702.52
- Benchmark change: +0.68%

TOP CONTRIBUTORS
1. Stock P (STK_P): -1.11%
2. ETF Y (ETF_Y): -1.01%
3. Stock N (STK_N): -0.71%

MARKET CONTEXT
- Average volatility index: 21.0
- Interest rate change: -10 bps

SUMMARY INSIGHT
The portfolio underperformed the benchmark this week, with Stock P leading the move after investors rotated into energy names as risk appetite stabilised and valuations looked more balanced. ETF Y moved in the opposite direction, aligned with investors rotated into real estate names as risk appetite stabilised and valuations looked more balanced. Market conditions were steady with volatility at 21.0, and rates moved lower. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** ```json
{
  "result": 8,
  "explanation": "The briefing is mostly compliant with the required structure, containing all necessary sections in the correct order. However, there is a minor issue with the 'TOP CONTRIBUTORS' section, as it does not include Stock U, which had a positive contribution, and instead lists only the negative contributors. This oversight affects the completeness of the information presented."
}
```
**Issue:** A positive contributor is missing from the top list.

**Exec #6 (near-fail)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-06-15 to 2026-06-21

PERFORMANCE
- Portfolio change: +0.26%
- Starting value: $100,021.00
- Ending value: $100,281.05
- Benchmark change: +1.03%

TOP CONTRIBUTORS
1. Stock U (STK_U): -1.21%
2. Stock R (STK_R): +0.90%
3. ETF Y (ETF_Y): +0.85%

MARKET CONTEXT
- Average volatility index: 21.2
- Interest rate change: 10 bps

SUMMARY INSIGHT
The portfolio underperformed the benchmark this week, with Stock U leading the move after consumer performance was mixed, with defensives holding up while growth-oriented names slipped. Stock R moved in the opposite direction, aligned with investors rotated into materials names as risk appetite stabilised and valuations looked more balanced. Market conditions were steady with volatility at 21.2, and rates moved up. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing is mostly compliant with the required structure, but there are minor issues. The 'TOP CONTRIBUTORS' section lists the contributions in the wrong order, as it should reflect positive contributions first. Additionally, the 'MARKET CONTEXT' section uses 'Average volatility index' instead of 'Volatility index average', which is a slight deviation from the expected phrasing. Overall, the briefing is well-organized and clear, but these small discrepancies prevent a perfect score.
**Issue:** TOP CONTRIBUTORS ordering/selection is inconsistent with expectations.

**Exec #7 (failure)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-06-22 to 2026-06-28

PERFORMANCE
- Portfolio change: +0.58%
- Starting value: $159,166.00
- Ending value: $160,089.16
- Benchmark change: +0.48%

TOP CONTRIBUTORS
1. Stock S (STK_S): -0.65%
2. Stock Q (STK_Q): +0.62%
3. Stock V (STK_V): +0.51%

MARKET CONTEXT
- Average volatility index: 16.2
- Interest rate change: 25 bps

SUMMARY INSIGHT
The portfolio outperformed the benchmark this week, with Stock S leading the move after industrials names gained as pricing momentum strengthened and cost pressures eased. Stock Q moved in the opposite direction, aligned with real estate performance was mixed, with defensives holding up while growth-oriented names slipped. Market conditions were steady with volatility at 16.2, and rates moved up. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** ```json
{
  "result": 7,
  "explanation": "The briefing is mostly compliant with the required structure, but there are minor issues. The 'TOP CONTRIBUTORS' section lists Stock S first, which is misleading as it had a negative contribution. Additionally, the 'MARKET CONTEXT' section uses 'Average volatility index' instead of 'Volatility index average', which is a slight deviation in phrasing. Overall, the content is well-organized and informative, but these issues prevent a perfect score."
}
```
**Issue:** TOP CONTRIBUTORS list implies incorrect top contributor.

##### Cluster 2: Minor label/wording deviations within required sections
- Root cause: eval
- Severity: Low
- Pattern: Minor phrasing deviations (section labels or wording) despite correct section order and counts.
- Explanation signal: “phrasing … should be,” “repeats phrases unnecessarily.”
- Insight narrative: Several passes were scored down due to phrasing that is still consistent with the system prompt but not with the judge’s expected wording. The most frequent example is the Market Context label, which the system prompt explicitly defines as “Average volatility index,” but the judge prefers “Volatility index average.” This is not a user-facing issue, yet it creates score drag and noise in the structural signal. There are also minor wording issues in the SUMMARY INSIGHT that are more stylistic than structural. Tightening evaluator wording to match the prompt will improve signal quality without changing outputs.
- Why it matters: Evaluation drift creates false positives and obscures true structural issues.
- Prevalence: 5 executions; 100% of failures for this criterion (overlaps with Cluster 1)
- Examples (full outputs):

**Exec #10 (near-fail)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-07-13 to 2026-07-19

PERFORMANCE
- Portfolio change: -1.96%
- Starting value: $76,630.00
- Ending value: $75,128.05
- Benchmark change: +0.71%

TOP CONTRIBUTORS
1. Stock R (STK_R): -1.36%
2. Stock U (STK_U): -1.14%
3. Stock V (STK_V): +0.43%

MARKET CONTEXT
- Average volatility index: 17.6
- Interest rate change: 25 bps

SUMMARY INSIGHT
The portfolio underperformed the benchmark this week, with Stock R leading the move after investors rotated into materials names as risk appetite stabilised and valuations looked more balanced. Stock U moved in the opposite direction, aligned with real estate names gained as pricing momentum strengthened and cost pressures eased. Market conditions were steady with volatility at 17.6, and rates moved up. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing is mostly compliant with the required structure, containing all necessary sections in the correct order. However, there is a minor issue with the phrasing in the 'TOP CONTRIBUTORS' section, where the contributions should be presented as positive or negative percentages rather than as returns. This slight deviation affects the overall clarity but does not significantly impact structural compliance.
**Issue:** Judge expects specific contribution phrasing.

**Exec #15 (near-fail)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-08-17 to 2026-08-23

PERFORMANCE
- Portfolio change: +0.21%
- Starting value: $138,146.00
- Ending value: $138,436.11
- Benchmark change: +0.54%

TOP CONTRIBUTORS
1. ETF Y (ETF_Y): -1.19%
2. ETF Z (ETF_Z): +0.68%
3. ETF X (ETF_X): +0.61%

MARKET CONTEXT
- Average volatility index: 19.0
- Interest rate change: 0 bps

SUMMARY INSIGHT
The portfolio underperformed the benchmark this week, with ETF Y leading the move after healthcare names gained as pricing momentum strengthened and cost pressures eased. ETF Z moved in the opposite direction, aligned with utilities names gained as pricing momentum strengthened and cost pressures eased. Market conditions were steady with volatility at 19.0, and rates were unchanged. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** ```json
{
  "result": 8,
  "explanation": "The briefing is mostly compliant with the required structure, containing all necessary sections in the correct order. However, there is a minor issue with the phrasing in the 'SUMMARY INSIGHT' section, where it mentions ETF Z moving in the opposite direction, which could be misleading given its positive contribution. This could lead to slight confusion, but overall, the structure is well-maintained."
}
```
**Issue:** Summary phrasing flagged as structural by the evaluator.

**Exec #18 (pass)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-09-07 to 2026-09-13

PERFORMANCE
- Portfolio change: -0.64%
- Starting value: $80,561.00
- Ending value: $80,045.41
- Benchmark change: -0.67%

TOP CONTRIBUTORS
1. Stock V (STK_V): -1.01%
2. Stock U (STK_U): -0.75%
3. Stock R (STK_R): +0.58%

MARKET CONTEXT
- Average volatility index: 19.5
- Interest rate change: -10 bps

SUMMARY INSIGHT
The portfolio matched the benchmark this week, with Stock V leading the move after utilities performance was mixed, with defensives holding up while growth-oriented names slipped. Stock U moved in the opposite direction, aligned with technology performance was mixed, with defensives holding up while growth-oriented names slipped. Market conditions were steady with volatility at 19.5, and rates moved lower. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** ```json
{
  "result": 9,
  "explanation": "The briefing is mostly compliant with the required structure, containing all necessary sections in the correct order. However, there is a minor issue with the phrasing in the SUMMARY INSIGHT, where it repeats phrases unnecessarily, which could be streamlined for clarity. Overall, it adheres closely to the specified format."
}
```
**Issue:** Evaluator penalizes stylistic repetition as structural.

#### Strengths to preserve
- Section order and labels are consistently correct (Exec #1, Exec #2).
- SUMMARY INSIGHT remains a single paragraph with target length (Exec #3, Exec #5).

### News grounding & linkage
**Pass rate**: 100% | **Avg score**: 9.20/10 | **Failures**: 0

#### Issue clusters (ranked)

##### Cluster 1: Directional overreach for negative contributors
- Root cause: prompt
- Severity: Medium
- Pattern: Language implies positive causality (“led the move,” “moved in the opposite direction”) when the contributor is negative.
- Explanation signal: “minor overreach,” “led the move…negative contribution.”
- Insight narrative: The model generally links news correctly but occasionally uses directional phrasing that contradicts the sign of the contribution. This is a subtle but repeated phrasing issue across passes, not a hard grounding failure. Because the product forbids overstatement and ungrounded causality, this wording creates ambiguity about whether news was a tailwind or headwind. The issue becomes more visible when the top contributor is negative, as “leading the move” reads like a positive driver. Users could misread the causal relationship between news and performance.
- Why it matters: Precision in causal language is essential for trust and compliance in financial summaries.
- Prevalence: 10 executions; 0% of failures for this criterion
- Examples (full outputs):

**Exec #4 (pass)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-06-01 to 2026-06-07

PERFORMANCE
- Portfolio change: -2.15%
- Starting value: $73,278.00
- Ending value: $71,702.52
- Benchmark change: +0.68%

TOP CONTRIBUTORS
1. Stock P (STK_P): -1.11%
2. ETF Y (ETF_Y): -1.01%
3. Stock N (STK_N): -0.71%

MARKET CONTEXT
- Average volatility index: 21.0
- Interest rate change: -10 bps

SUMMARY INSIGHT
The portfolio underperformed the benchmark this week, with Stock P leading the move after investors rotated into energy names as risk appetite stabilised and valuations looked more balanced. ETF Y moved in the opposite direction, aligned with investors rotated into real estate names as risk appetite stabilised and valuations looked more balanced. Market conditions were steady with volatility at 21.0, and rates moved lower. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing is well-grounded in the provided news_digest, accurately reflecting the performance of the portfolio and linking it to relevant news articles. The mention of Stock P's performance aligns with the news about investors rotating into energy names, and the discussion of ETF Y corresponds with the news on real estate. However, the phrasing 'moved in the opposite direction' for ETF Y could imply a stronger negative correlation than supported by the news, which slightly overreaches. Overall, the linkage is strong and the insights are relevant.
**Issue:** Wording overstates directionality for a negative mover.

**Exec #7 (near-fail)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-06-22 to 2026-06-28

PERFORMANCE
- Portfolio change: +0.58%
- Starting value: $159,166.00
- Ending value: $160,089.16
- Benchmark change: +0.48%

TOP CONTRIBUTORS
1. Stock S (STK_S): -0.65%
2. Stock Q (STK_Q): +0.62%
3. Stock V (STK_V): +0.51%

MARKET CONTEXT
- Average volatility index: 16.2
- Interest rate change: 25 bps

SUMMARY INSIGHT
The portfolio outperformed the benchmark this week, with Stock S leading the move after industrials names gained as pricing momentum strengthened and cost pressures eased. Stock Q moved in the opposite direction, aligned with real estate performance was mixed, with defensives holding up while growth-oriented names slipped. Market conditions were steady with volatility at 16.2, and rates moved up. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing is well-grounded in the provided news_digest, accurately linking Stock S's performance to the industrials article and Stock Q's performance to the real estate article. However, there is a minor overreach in stating that Stock S 'led the move,' as it had a negative contribution. Overall, the connections to the news articles are strong, and the performance metrics are correctly reported.
**Issue:** “Led the move” conflicts with negative contribution.

**Exec #15 (near-fail)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-08-17 to 2026-08-23

PERFORMANCE
- Portfolio change: +0.21%
- Starting value: $138,146.00
- Ending value: $138,436.11
- Benchmark change: +0.54%

TOP CONTRIBUTORS
1. ETF Y (ETF_Y): -1.19%
2. ETF Z (ETF_Z): +0.68%
3. ETF X (ETF_X): +0.61%

MARKET CONTEXT
- Average volatility index: 19.0
- Interest rate change: 0 bps

SUMMARY INSIGHT
The portfolio underperformed the benchmark this week, with ETF Y leading the move after healthcare names gained as pricing momentum strengthened and cost pressures eased. ETF Z moved in the opposite direction, aligned with utilities names gained as pricing momentum strengthened and cost pressures eased. Market conditions were steady with volatility at 19.0, and rates were unchanged. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing is well-grounded in the provided news digest, accurately linking ETF Y and ETF Z to their respective news articles about healthcare and utilities. However, there is a minor overreach in stating that ETF Y 'led the move' when it actually had a negative contribution. The overall analysis is coherent and reflects the market context appropriately, but the phrasing could be more precise regarding the performance of ETF Y.
**Issue:** Overstates causality for a negative contributor.

##### Cluster 2: Linkage clarity gaps for specific holdings
- Root cause: prompt
- Severity: Low
- Pattern: The output references a holding’s performance without explicit linkage to the available news digest (or implies the wrong sentiment).
- Explanation signal: “lack of explicit linkage,” “slightly misleading sentiment.”
- Insight narrative: A smaller set of outputs show linkage that is technically grounded but not explicit enough for a strict evaluator. This includes cases where the model mentions a holding’s move without clearly tying it to a linked news item, or where sentiment in the summary diverges from the news tone. These are not hallucinations, but they blur the causal trail the user expects. The issue is concentrated in otherwise strong outputs, suggesting the model knows the correct article but does not always state the linkage precisely. Tightening the prompt to require explicit “linked news” phrasing would reduce this slippage.
- Why it matters: The feature’s credibility depends on transparent, source-linked explanations.
- Prevalence: 3 executions; 0% of failures for this criterion
- Examples (full outputs):

**Exec #2 (pass)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-04-06 to 2026-04-12

PERFORMANCE
- Portfolio change: -1.15%
- Starting value: $86,500.00
- Ending value: $85,503.25
- Benchmark change: +0.40%

TOP CONTRIBUTORS
1. Stock E (STK_E): -1.25%
2. ETF F (ETF_F): +0.32%
3. Stock G (STK_G): -0.18%

MARKET CONTEXT
- Average volatility index: 22.1
- Interest rate change: 25 bps

SUMMARY INSIGHT
The portfolio declined this week and underperformed the benchmark, driven mainly by Stock E, which accounted for the majority of the negative contribution; no holding-linked news was provided for that move, so the briefing should be read as performance-first rather than cause-first. Market conditions were choppier, with higher volatility and a rate increase pressuring bonds slightly, consistent with the small drag from fixed income. Consumer-related exposure was modestly negative amid mixed spending signals.
```
**Judge explanation:** The briefing is well-grounded in the provided news_digest, accurately reflecting the portfolio's performance and linking it to relevant market conditions. It correctly identifies Stock E as the main contributor to the negative return and mentions the mixed consumer spending signals related to Stock G, as well as the bond market context affecting ETF H. The only minor overreach is the lack of explicit linkage to the news for Stock E's performance, but overall, the analysis is coherent and aligns well with the news summaries.
**Issue:** Linkage to a specific holding is not explicit.

**Exec #10 (pass)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-07-13 to 2026-07-19

PERFORMANCE
- Portfolio change: -1.96%
- Starting value: $76,630.00
- Ending value: $75,128.05
- Benchmark change: +0.71%

TOP CONTRIBUTORS
1. Stock R (STK_R): -1.36%
2. Stock U (STK_U): -1.14%
3. Stock V (STK_V): +0.43%

MARKET CONTEXT
- Average volatility index: 17.6
- Interest rate change: 25 bps

SUMMARY INSIGHT
The portfolio underperformed the benchmark this week, with Stock R leading the move after investors rotated into materials names as risk appetite stabilised and valuations looked more balanced. Stock U moved in the opposite direction, aligned with real estate names gained as pricing momentum strengthened and cost pressures eased. Market conditions were steady with volatility at 17.6, and rates moved up. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing is well-grounded in the provided news_digest, accurately reflecting the performance of the portfolio and linking it to relevant news articles. The mention of Stock R's performance aligns with the news about investors rotating into materials, and Stock U's performance is correctly attributed to the positive sentiment in real estate. However, the statement regarding Stock V's performance could be slightly misleading as it suggests a positive sentiment while the news sentiment was negative, which is a minor overreach.
**Issue:** Sentiment alignment is unclear for one holding.

**Exec #16 (pass)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-08-24 to 2026-08-30

PERFORMANCE
- Portfolio change: +1.07%
- Starting value: $158,555.00
- Ending value: $160,251.54
- Benchmark change: -0.46%

TOP CONTRIBUTORS
1. ETF X (ETF_X): +1.12%
2. Stock T (STK_T): +0.83%
3. ETF Y (ETF_Y): -0.80%

MARKET CONTEXT
- Average volatility index: 15.9
- Interest rate change: -10 bps

SUMMARY INSIGHT
The portfolio outperformed the benchmark this week, with ETF X leading the move after technology performance was mixed, with defensives holding up while growth-oriented names slipped. Stock T moved in the opposite direction, aligned with communications performance was mixed, with defensives holding up while growth-oriented names slipped. Market conditions were steady with volatility at 15.9, and rates moved lower. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing is well-grounded in the provided news_digest, accurately linking ETF X and Stock T to their respective performance summaries. The insights regarding technology and communications performance align with the news articles, and the overall portfolio performance is correctly summarized. There is a minor overreach in stating that Stock T moved in the opposite direction without clarifying its contribution, but this does not significantly detract from the overall accuracy.
**Issue:** Linkage phrasing lacks contribution clarity.

#### Strengths to preserve
- No hallucinated articles or mismatched holding attribution across the run (Exec #1, Exec #11).
- Consistent preference for high-confidence news on top contributors (Exec #12, Exec #8).

### Tone, compliance & insight quality
**Pass rate**: 85% | **Avg score**: 7.95/10 | **Failures**: 3

#### Issue clusters (ranked)

##### Cluster 1: Insight depth and clarity are uneven (boilerplate + weak context linkage)
- Root cause: prompt
- Severity: Medium
- Pattern: The summary insight repeats boilerplate and underuses benchmark/market context, even in many passes.
- Explanation signal: “repetitive phrasing,” “lacks deeper analysis,” “minor lapses in clarity.”
- Insight narrative: Most outputs are compliant in tone but not consistently insightful. The summary insight often restates stock moves with generic sector language instead of interpreting what it means relative to the benchmark or market context. This shows up in passes and failures, suggesting the prompt leaves too much latitude for template-like phrasing. The result is a briefing that feels safe but not particularly helpful, especially for users seeking the “why” behind performance. Strengthening requirements for benchmark comparison and market-context linkage should improve this without adding advisory language.
- Why it matters: Insight quality is a core product goal; shallow summaries reduce trust and engagement.
- Prevalence: 17 executions; 100% of failures for this criterion
- Examples (full outputs):

**Exec #16 (failure)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-08-24 to 2026-08-30

PERFORMANCE
- Portfolio change: +1.07%
- Starting value: $158,555.00
- Ending value: $160,251.54
- Benchmark change: -0.46%

TOP CONTRIBUTORS
1. ETF X (ETF_X): +1.12%
2. Stock T (STK_T): +0.83%
3. ETF Y (ETF_Y): -0.80%

MARKET CONTEXT
- Average volatility index: 15.9
- Interest rate change: -10 bps

SUMMARY INSIGHT
The portfolio outperformed the benchmark this week, with ETF X leading the move after technology performance was mixed, with defensives holding up while growth-oriented names slipped. Stock T moved in the opposite direction, aligned with communications performance was mixed, with defensives holding up while growth-oriented names slipped. Market conditions were steady with volatility at 15.9, and rates moved lower. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing maintains a neutral tone and provides a clear overview of the portfolio's performance relative to the benchmark. However, the summary insight contains some repetitive phrasing and lacks deeper analysis of the drivers behind the performance, particularly in relation to sector dynamics and market context. While it avoids advisory language, the insight could benefit from a more nuanced interpretation of the market conditions and their implications.
**Issue:** Repetitive, low-insight summary.

**Exec #18 (failure)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-09-07 to 2026-09-13

PERFORMANCE
- Portfolio change: -0.64%
- Starting value: $80,561.00
- Ending value: $80,045.41
- Benchmark change: -0.67%

TOP CONTRIBUTORS
1. Stock V (STK_V): -1.01%
2. Stock U (STK_U): -0.75%
3. Stock R (STK_R): +0.58%

MARKET CONTEXT
- Average volatility index: 19.5
- Interest rate change: -10 bps

SUMMARY INSIGHT
The portfolio matched the benchmark this week, with Stock V leading the move after utilities performance was mixed, with defensives holding up while growth-oriented names slipped. Stock U moved in the opposite direction, aligned with technology performance was mixed, with defensives holding up while growth-oriented names slipped. Market conditions were steady with volatility at 19.5, and rates moved lower. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing maintains a neutral tone and provides a clear overview of the portfolio's performance relative to the benchmark. However, the summary insight contains some repetitive phrasing and lacks deeper analysis of the drivers behind the performance, particularly in relation to the broader market context. While it avoids advisory language, the insight could benefit from a more nuanced interpretation of the market dynamics affecting the portfolio.
**Issue:** Repetitive phrasing and thin interpretation.

**Exec #2 (near-fail)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-04-06 to 2026-04-12

PERFORMANCE
- Portfolio change: -1.15%
- Starting value: $86,500.00
- Ending value: $85,503.25
- Benchmark change: +0.40%

TOP CONTRIBUTORS
1. Stock E (STK_E): -1.25%
2. ETF F (ETF_F): +0.32%
3. Stock G (STK_G): -0.18%

MARKET CONTEXT
- Average volatility index: 22.1
- Interest rate change: 25 bps

SUMMARY INSIGHT
The portfolio declined this week and underperformed the benchmark, driven mainly by Stock E, which accounted for the majority of the negative contribution; no holding-linked news was provided for that move, so the briefing should be read as performance-first rather than cause-first. Market conditions were choppier, with higher volatility and a rate increase pressuring bonds slightly, consistent with the small drag from fixed income. Consumer-related exposure was modestly negative amid mixed spending signals.
```
**Judge explanation:** The briefing maintains a neutral tone and provides a clear overview of the portfolio's performance, aligning well with compliance standards. The summary insight effectively interprets the drivers behind the portfolio's decline and contextualizes it within the broader market conditions, although it could benefit from a more explicit comparison to the benchmark's performance. Overall, it offers strong insights with minor lapses in clarity regarding the implications of the market context.
**Issue:** Missing explicit benchmark/context linkage.

##### Cluster 2: Directional/advisory-leaning phrasing
- Root cause: prompt
- Severity: Medium
- Pattern: Phrases imply directional view or advice (e.g., “leading the move”) in a way that can be read as prescriptive.
- Explanation signal: “implies a directional view,” “could be interpreted as advisory.”
- Insight narrative: A small number of outputs use phrasing that reads like market commentary rather than neutral explanation. This is not widespread, but it appears in the lowest-scoring tone result and overlaps with negative-contribution cases. The language is subtle yet risky in a consumer fintech context that explicitly avoids advice. Tightening phrasing to sign-aware language would remove the compliance ambiguity without sacrificing clarity.
- Why it matters: Compliance and trust require strictly neutral, non-advisory language.
- Prevalence: 1 execution; 33% of failures for this criterion
- Examples (full outputs):

**Exec #7 (failure)**
**Output:**
```
WEEKLY PORTFOLIO SNAPSHOT
Period: 2026-06-22 to 2026-06-28

PERFORMANCE
- Portfolio change: +0.58%
- Starting value: $159,166.00
- Ending value: $160,089.16
- Benchmark change: +0.48%

TOP CONTRIBUTORS
1. Stock S (STK_S): -0.65%
2. Stock Q (STK_Q): +0.62%
3. Stock V (STK_V): +0.51%

MARKET CONTEXT
- Average volatility index: 16.2
- Interest rate change: 25 bps

SUMMARY INSIGHT
The portfolio outperformed the benchmark this week, with Stock S leading the move after industrials names gained as pricing momentum strengthened and cost pressures eased. Stock Q moved in the opposite direction, aligned with real estate performance was mixed, with defensives holding up while growth-oriented names slipped. Market conditions were steady with volatility at 16.2, and rates moved up. Overall, results were driven by stock-specific dynamics rather than a broad macro shift.
```
**Judge explanation:** The briefing provides a clear overview of the portfolio's performance and market context, but it contains some compliance issues, particularly in the summary insight where it implies a directional view on stocks. The language used could be interpreted as advisory, especially with phrases like 'leading the move' and 'aligned with real estate performance.' While the insight does offer some interpretation of market dynamics, it lacks depth in comparing the portfolio's performance to broader market trends, which could enhance its quality.
**Issue:** Directional phrasing creates compliance risk.

#### Strengths to preserve
- Neutral, non-advisory tone with explicit benchmark comparison (Exec #1, Exec #17).
- Clear explanatory summaries that tie market context to portfolio outcome (Exec #3).

## Cross-criterion patterns
- **Ordering errors cascade into narrative issues**: misordered TOP CONTRIBUTORS often leads to “leading the move” phrasing for negative contributors (Exec #7, Exec #6). Criteria impacted: Numerical fidelity, Structure & formatting, News grounding, Tone.
- **Phrasing drift shows up across criteria**: “moved in the opposite direction” appears in News and Tone, creating both grounding and compliance risk (Exec #4, Exec #15). Criteria impacted: News grounding, Tone.
- **Insight boilerplate reduces clarity**: repetitive sector phrasing appears in both Structure comments (wording) and Tone scores (clarity), indicating a need for stronger insight constraints (Exec #18, Exec #16).

## Remediation plan (ranked)
1. **Prompt edit: enforce absolute ordering and sign-aware wording**
   - Exact text change (add under “How to use numbers”):
     - “Sort TOP CONTRIBUTORS by absolute `contribution_pct` (largest magnitude first), regardless of sign. If the largest mover is negative, refer to it as the ‘largest detractor’ (not ‘leading the move’).”
   - Fixes: Numerical Cluster 1; Structure Cluster 1; News Cluster 1; Tone Cluster 2.
   - What it might break: Slightly more rigid phrasing in SUMMARY INSIGHT.
   - How to validate: Re-run evals; spot-check TOP CONTRIBUTORS ordering and negative-mover phrasing in dashboard.
2. **Prompt edit: require explicit benchmark + market context linkage in SUMMARY INSIGHT**
   - Exact text change (add under “SUMMARY INSIGHT” section):
     - “In the summary insight, include (a) a benchmark comparison clause, and (b) one explicit market-context linkage (volatility or rates). Avoid repeating generic sector boilerplate.”
   - Fixes: Tone Cluster 1; mitigates Structure Cluster 2 stylistic penalties.
   - What it might break: Risk of formulaic insights if over-constrained.
   - How to validate: Re-run evals; review Tone explanations for reduced “repetitive phrasing / clarity” comments.
3. **Prompt edit: make news linkage explicit and sign-aware**
   - Exact text change (add under “News digest rules”):
     - “When referencing news for a holding, explicitly state the linkage (e.g., ‘Linked news for X notes…’) and ensure wording matches contribution sign (headwind vs tailwind).”
   - Fixes: News Cluster 1 & 2.
   - What it might break: Slightly longer SUMMARY INSIGHT; watch word count 60–90 words.
   - How to validate: Re-run evals; spot-check for “overreach” phrasing in News explanations.
4. **Eval update: align Structure prompt wording with system prompt**
   - Exact text change (in Structure & formatting evaluator):
     - Replace references to “Volatility index average” with “Average volatility index” to match the system prompt label.
   - Fixes: Structure Cluster 2 evaluator drift.
   - What it might break: None; improves signal quality.
   - How to validate: Re-run evals and confirm Structure explanations no longer flag label phrasing.
5. **Data fix (optional): provide pre-sorted top_contributors list**
   - Fixes: Numerical Cluster 1; Structure Cluster 1.
   - What it might break: Adds dependency on upstream data quality.
   - How to validate: Compare input ordering to output; ensure the list is used verbatim.

## Appendix: Notes / edge cases
- Full results review confirms slim inputs did not omit critical fields for diagnosis.
- Structure evaluator penalizes label phrasing that matches the system prompt, indicating evaluator drift.
