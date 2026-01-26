#!/usr/bin/env python3
"""
Generate a meta-analysis report for a completed eval run.
Produces clustered, prioritised issues per criterion with concrete examples.
"""

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from openai import OpenAI
from dotenv import load_dotenv


SEVERITY_WEIGHTS = {
    "High": 3,
    "Medium": 2,
    "Low": 1,
}

PLACEHOLDER_VALUES = {
    "short, specific",
    "what is happening",
    "tbd",
    "n/a",
    "none",
    "unknown",
}

NO_EXPLANATION = "No explanation provided by judge."


def find_run_file(run_dir: Path, run_id: str, suffix: str) -> Optional[Path]:
    preferred = run_dir / f"{run_id}_{suffix}"
    if preferred.exists():
        return preferred
    matches = list(run_dir.glob(f"*_{suffix}"))
    return matches[0] if matches else None


def load_jsonl(path: Path) -> List[Dict]:
    results = []
    with path.open("r") as handle:
        for line in handle:
            if line.strip():
                results.append(json.loads(line))
    return results


def compute_stats(results: List[Dict]) -> Dict[str, Dict[str, float]]:
    if not results:
        return {}
    stats = {}
    criteria = [e["eval_name"] for e in results[0].get("evals", [])]
    for name in criteria:
        scores = []
        passed = 0
        total = 0
        for result in results:
            for eval_result in result.get("evals", []):
                if eval_result.get("eval_name") == name:
                    score = eval_result.get("score")
                    if score is not None:
                        scores.append(score)
                    if eval_result.get("passed"):
                        passed += 1
                    total += 1
        avg = sum(scores) / len(scores) if scores else 0
        pass_rate = (passed / total) if total else 0
        stats[name] = {
            "avg_score": avg,
            "pass_rate": pass_rate,
            "failures": total - passed,
            "total": total,
        }
    return stats


def stats_table(stats: Dict[str, Dict[str, float]]) -> str:
    if not stats:
        return ""
    header = "| Criterion | Avg Score | Pass Rate | Failures |"
    sep = "|---|---|---|---|"
    lines = [header, sep]
    for name, values in stats.items():
        lines.append(
            f"| {name} | {values['avg_score']:.2f} | {values['pass_rate']*100:.1f}% | {values['failures']} |"
        )
    return "\n".join(lines)


def load_evals_map(evals_path: Path) -> Dict[str, Dict]:
    with evals_path.open("r") as handle:
        evals = json.load(handle)
    return {item.get("name"): item for item in evals}


def collect_entries(results: List[Dict]) -> Dict[str, List[Dict]]:
    entries: Dict[str, List[Dict]] = {}
    for result in results:
        for eval_result in result.get("evals", []):
            entry = {
                "execution_id": result.get("execution_id"),
                "score": eval_result.get("score"),
                "pass_threshold": eval_result.get("pass_threshold"),
                "passed": eval_result.get("passed"),
                "explanation": eval_result.get("explanation", ""),
                "output": result.get("output"),
                "input": result.get("input"),
            }
            entries.setdefault(eval_result.get("eval_name"), []).append(entry)
    return entries


def identify_near_fails(entries: List[Dict], pass_threshold: int) -> List[Dict]:
    passing = [e for e in entries if e.get("passed") is True and e.get("score") is not None]
    if not passing:
        return []
    near_fails = [e for e in passing if e.get("score", 0) == pass_threshold]
    return near_fails


def build_failure_payload(entries: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    failures = [e for e in entries if e.get("passed") is False]
    pass_threshold = entries[0].get("pass_threshold", 0) if entries else 0
    near_fails = identify_near_fails(entries, pass_threshold)
    near_fails = sorted(near_fails, key=lambda e: e.get("score", 0))[:3]

    def normalize(item: Dict) -> Dict:
        return {
            "execution_id": item.get("execution_id"),
            "score": item.get("score"),
            "pass_threshold": item.get("pass_threshold"),
            "passed": item.get("passed"),
            "explanation": item.get("explanation", ""),
            "output": item.get("output", ""),
            "input": item.get("input"),
        }

    return [normalize(e) for e in failures], [normalize(e) for e in near_fails]


def extract_json(text: str) -> Dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def build_cluster_prompt(
    criterion_name: str,
    criterion_def: Dict,
    failures: List[Dict],
    near_fails: List[Dict],
    feature_context: str,
    system_prompt: str,
    explanations_available: bool,
) -> str:
    criterion_json = json.dumps(criterion_def, indent=2)
    failures_json = json.dumps(failures, indent=2)
    near_fails_json = json.dumps(near_fails, indent=2)
    failure_ids = [f.get("execution_id") for f in failures]

    explanation_note = (
        "Explanations are available. Use them as primary evidence."
        if explanations_available
        else f"No judge explanations are available. Use \"{NO_EXPLANATION}\" for explanation_anchor and explanation_excerpt."
    )

    return f"""
You are producing a structured meta-analysis for a single evaluation criterion.

Use the feature context and prompt rules to judge why issues matter, not just what the judge said.
Judge explanations are the primary evidence; scores only provide pass/fail context.
{explanation_note}

## Feature context
{feature_context}

## System prompt (generation)
{system_prompt}

## Eval criterion definition (Evals.json entry)
{criterion_json}

## Failures (must be clustered)
{failures_json}

## Failure IDs (must all be assigned exactly once)
{failure_ids}

## Near-fails (optional evidence)
{near_fails_json}

Required output: JSON only, with this schema:
{{
  "criterion": "{criterion_name}",
  "failures": {len(failures)},
  "clusters": [
    {{
      "cluster_name": "short, specific",
      "severity": "High|Medium|Low",
      "root_cause": "prompt|data|eval|model|mixed",
      "pattern": "what is happening, grounded in judge explanations",
      "explanation_anchor": "quote or summary of the judge explanation pattern that defines this cluster",
      "why_it_matters": "tie explicitly to the product intent described in feature_context.md",
      "failure_execution_ids": [12, 15],
      "examples": [
        {{
          "execution_id": 12,
          "example_type": "failure|near_fail",
          "output_full": "full output text",
          "explanation_excerpt": "quote or paraphrase from judge explanation (or: \"No explanation provided by judge.\")",
          "issue_note": "1-2 sentence explanation of the issue"
        }}
      ],
      "recommendation": {{
        "type": "prompt|data|eval|model",
        "action": "specific change, ideally exact prompt/eval text",
        "risk": "possible side effect or trade-off"
      }}
    }}
  ],
  "no_issue_note": "only if failures == 0"
}}

Rules:
- Cluster ALL failures (each failure belongs to exactly one cluster).
- Use exactly 3 examples per cluster when possible. If fewer than 3 failures exist, use near-fails to reach 3; otherwise use as many as exist.
- Rank clusters by priority: severity first, then prevalence, then product risk.
- Do not invent data not present in failures/near-fails.
- Do NOT use placeholder text like "short, specific" or "what is happening".
- Focus on judge explanations more than scores; scores are for pass/fail context only.
- Output examples must include the FULL output text (not excerpts).
- If a judge explanation is missing/empty, set explanation_excerpt to: "No explanation provided by judge."
""".strip()


def is_placeholder(value: str) -> bool:
    return value.strip().lower() in PLACEHOLDER_VALUES


def validate_cluster_payload(
    payload: Dict,
    failure_ids: List[int],
    near_fail_ids: List[int],
    max_examples: int,
    explanation_map: Dict[int, bool],
) -> List[str]:
    errors = []
    clusters = payload.get("clusters", [])
    if failure_ids and not clusters:
        errors.append("No clusters provided for failures.")
    covered_failures = []
    for cluster in clusters:
        name = str(cluster.get("cluster_name", "")).strip()
        pattern = str(cluster.get("pattern", "")).strip()
        why = str(cluster.get("why_it_matters", "")).strip()
        explanation_anchor = str(cluster.get("explanation_anchor", "")).strip()
        severity = cluster.get("severity")
        examples = cluster.get("examples", [])
        failure_execution_ids = cluster.get("failure_execution_ids", [])

        if not name or is_placeholder(name):
            errors.append("Cluster name is missing or placeholder.")
        if not pattern or is_placeholder(pattern):
            errors.append("Cluster pattern is missing or placeholder.")
        if not explanation_anchor:
            errors.append("explanation_anchor is missing.")
        if not why:
            errors.append("why_it_matters is missing.")
        if severity not in SEVERITY_WEIGHTS:
            errors.append("Severity must be High, Medium, or Low.")
        if not failure_execution_ids:
            errors.append("Cluster failure_execution_ids missing.")
        else:
            for exec_id in failure_execution_ids:
                if exec_id not in failure_ids:
                    errors.append("Cluster failure_execution_ids includes unknown ID.")
            covered_failures.extend(failure_execution_ids)
        for example in examples:
            output_full = str(example.get("output_full", "")).strip()
            explanation_excerpt = str(example.get("explanation_excerpt", "")).strip()
            note = str(example.get("issue_note", "")).strip()
            example_type = str(example.get("example_type", "")).strip()
            exec_id = example.get("execution_id")
            if not output_full or is_placeholder(output_full):
                errors.append("Example output_full is missing or placeholder.")
            has_explanation = explanation_map.get(exec_id, False)
            if has_explanation:
                if not explanation_excerpt or is_placeholder(explanation_excerpt) or explanation_excerpt == NO_EXPLANATION:
                    errors.append("Example explanation_excerpt must use judge explanation.")
            else:
                if explanation_excerpt != NO_EXPLANATION:
                    errors.append("Example explanation_excerpt must be NO_EXPLANATION when missing.")
        explanation_available = any(explanation_map.values())
        if explanation_available:
            if is_placeholder(explanation_anchor) or explanation_anchor == NO_EXPLANATION:
                errors.append("explanation_anchor must use judge explanations.")
        else:
            if explanation_anchor != NO_EXPLANATION:
                errors.append("explanation_anchor must be NO_EXPLANATION when missing.")
            if not note or is_placeholder(note):
                errors.append("Example issue_note is missing or placeholder.")
            if example_type not in {"failure", "near_fail"}:
                errors.append("Example example_type must be failure or near_fail.")
            if example_type == "failure" and exec_id not in failure_ids:
                errors.append("Example marked failure but exec_id not in failures.")
            if example_type == "near_fail" and exec_id not in near_fail_ids:
                errors.append("Example marked near_fail but exec_id not in near-fails.")
    if failure_ids:
        missing = set(failure_ids) - set(covered_failures)
        if missing:
            errors.append("Not all failures are assigned to a cluster.")
        duplicates = [x for x in covered_failures if covered_failures.count(x) > 1]
        if duplicates:
            errors.append("Failures assigned to multiple clusters.")
    return errors


def build_repair_prompt(original_prompt: str, payload: Dict, errors: List[str]) -> str:
    error_text = "\n".join(f"- {err}" for err in errors)
    return f"""
Your previous JSON did not meet requirements. Fix it.

Errors:
{error_text}

Original instructions:
{original_prompt}

Your previous JSON:
{json.dumps(payload, indent=2)}

Return corrected JSON only. Do not add extra text.
""".strip()


def request_cluster_json(
    client: OpenAI,
    model: str,
    prompt: str,
    failure_ids: List[int],
    near_fail_ids: List[int],
    max_examples: int,
    explanation_map: Dict[int, bool],
) -> Dict:
    attempt = 0
    payload = None
    current_prompt = prompt
    explanations_available = any(explanation_map.values())
    while attempt < 3:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Return only JSON. No markdown."},
                {"role": "user", "content": current_prompt},
            ],
            temperature=0,
        )
        content = response.choices[0].message.content.strip()
        payload = extract_json(content)
        if payload.get("clusters"):
            for cluster in payload.get("clusters", []):
                if not explanations_available:
                    cluster["explanation_anchor"] = NO_EXPLANATION
                for example in cluster.get("examples", []):
                    exec_id = example.get("execution_id")
                    if exec_id in explanation_map and not explanation_map[exec_id]:
                        example["explanation_excerpt"] = NO_EXPLANATION
        errors = validate_cluster_payload(
            payload, failure_ids, near_fail_ids, max_examples, explanation_map
        )
        if not errors:
            return payload
        current_prompt = build_repair_prompt(prompt, payload, errors)
        attempt += 1

    raise ValueError(f"Meta-analysis JSON validation failed: {errors}")


def rank_all_clusters(cluster_sets: Dict[str, Dict]) -> List[Dict]:
    ranked = []
    for criterion, payload in cluster_sets.items():
        for cluster in payload.get("clusters", []):
            severity = cluster.get("severity", "Low")
            prevalence = cluster.get("prevalence_count", 0)
            score = SEVERITY_WEIGHTS.get(severity, 1) * prevalence
            ranked.append({
                "criterion": criterion,
                "cluster": cluster,
                "priority_score": score,
            })
    ranked.sort(key=lambda item: item["priority_score"], reverse=True)
    return ranked


def apply_cluster_metrics(
    payload: Dict, failure_ids: List[int]
) -> Dict:
    total_failures = len(failure_ids)
    clusters = payload.get("clusters", [])
    for cluster in clusters:
        cluster_failures = cluster.get("failure_execution_ids", [])
        prevalence_count = len(cluster_failures)
        prevalence_pct = (prevalence_count / total_failures * 100) if total_failures else 0
        cluster["prevalence_count"] = prevalence_count
        cluster["prevalence_pct"] = round(prevalence_pct, 1)

    clusters.sort(
        key=lambda c: (
            SEVERITY_WEIGHTS.get(c.get("severity", "Low"), 1),
            c.get("prevalence_count", 0),
        ),
        reverse=True,
    )
    for idx, cluster in enumerate(clusters, start=1):
        cluster["priority_rank"] = idx
    payload["clusters"] = clusters
    return payload


def ensure_cluster_examples(
    payload: Dict,
    failures: List[Dict],
    near_fails: List[Dict],
    target_count: int = 3,
) -> Dict:
    failure_map = {item["execution_id"]: item for item in failures}
    near_fail_map = {item["execution_id"]: item for item in near_fails}

    for cluster in payload.get("clusters", []):
        examples = cluster.get("examples", [])
        used_ids = {example.get("execution_id") for example in examples}
        needed = max(0, target_count - len(examples))

        failure_ids = cluster.get("failure_execution_ids", [])
        for exec_id in failure_ids:
            if needed <= 0:
                break
            if exec_id in used_ids or exec_id not in failure_map:
                continue
            entry = failure_map[exec_id]
            examples.append({
                "execution_id": exec_id,
                "example_type": "failure",
                "output_full": entry.get("output", ""),
                "explanation_excerpt": entry.get("explanation") or NO_EXPLANATION,
                "issue_note": "Supplemental example aligned with this cluster; see output and explanation.",
            })
            used_ids.add(exec_id)
            needed -= 1

        if needed > 0:
            for exec_id, entry in near_fail_map.items():
                if needed <= 0:
                    break
                if exec_id in used_ids:
                    continue
                examples.append({
                    "execution_id": exec_id,
                    "example_type": "near_fail",
                    "output_full": entry.get("output", ""),
                    "explanation_excerpt": entry.get("explanation") or NO_EXPLANATION,
                    "issue_note": "Supplemental example aligned with this cluster; see output and explanation.",
                })
                used_ids.add(exec_id)
                needed -= 1

        cluster["examples"] = examples
    return payload


def render_markdown(
    run_id: str,
    stats: Dict[str, Dict[str, float]],
    cluster_sets: Dict[str, Dict],
) -> str:
    generated = datetime.now(timezone.utc).date().isoformat()
    total_execs = next(iter(stats.values()))["total"] if stats else 0
    table = stats_table(stats)

    ranked = rank_all_clusters(cluster_sets)
    top_issues = ranked[:5]

    lines = [
        "# Meta-Analysis Report",
        f"*Generated: {generated}*  ",
        f"*Eval Run: {total_execs} executions*",
        "",
        "## Executive Summary",
    ]
    if not top_issues:
        lines.append("- No failures detected across criteria.")
    else:
        for item in top_issues:
            cluster = item["cluster"]
            lines.append(
                f"- **{cluster.get('cluster_name')}** ({item['criterion']}): "
                f"{cluster.get('prevalence_count')} failures, "
                f"severity {cluster.get('severity')}"
            )

    lines.extend(["", "## Overall Statistics", table, ""])
    lines.append("## Criterion Analysis")

    for criterion, payload in cluster_sets.items():
        criterion_stats = stats.get(criterion, {})
        pass_rate = criterion_stats.get("pass_rate", 0) * 100
        avg_score = criterion_stats.get("avg_score", 0)
        failures = criterion_stats.get("failures", 0)

        lines.append(f"### {criterion}")
        lines.append(
            f"**Pass Rate**: {pass_rate:.1f}% | **Avg Score**: {avg_score:.2f} | **Failures**: {failures}"
        )

        if failures == 0:
            no_issue = payload.get("no_issue_note", "No issues found for this criterion.")
            lines.append("")
            lines.append(no_issue)
            lines.append("")
            continue

        clusters = payload.get("clusters", [])
        for cluster in clusters:
            lines.append("")
            lines.append(
                f"#### {cluster.get('priority_rank')}. {cluster.get('cluster_name')} "
                f"({cluster.get('prevalence_pct', 0)}% of failures)"
            )
            lines.append(f"- **Severity**: {cluster.get('severity')}")
            lines.append(f"- **Root Cause**: {cluster.get('root_cause')}")
            lines.append(f"- **Pattern**: {cluster.get('pattern')}")
            lines.append(f"- **Explanation Signal**: {cluster.get('explanation_anchor')}")
            lines.append(f"- **Why It Matters**: {cluster.get('why_it_matters')}")
            lines.append("- **Examples**:")
            for example in cluster.get("examples", []):
                lines.append(
                    f"  - Exec #{example.get('execution_id')} ({example.get('example_type')})"
                )
                lines.append("    - Output:")
                lines.append("      ```")
                lines.append(str(example.get("output_full", "")))
                lines.append("      ```")
                lines.append(
                    f"    - Explanation: {example.get('explanation_excerpt')}"
                )
                lines.append(f"    - Issue: {example.get('issue_note')}")
            if (
                not any(ex.get("example_type") == "near_fail" for ex in cluster.get("examples", []))
                and payload.get("near_fail_available") is False
            ):
                lines.append("- **Near-fail evidence**: None available (no borderline passes).")
            recommendation = cluster.get("recommendation", {})
            lines.append(
                f"- **Recommendation**: {recommendation.get('action')}"
            )
            lines.append(
                f"- **Risk**: {recommendation.get('risk')}"
            )
        lines.append("")

    return "\n".join(lines)


def generate_report(
    run_dir: Path,
    run_id: str,
    output_path: Path,
    model: str,
) -> None:
    base_dir = Path(__file__).parent.parent

    slim_path = find_run_file(run_dir, run_id, "eval_results_slim.jsonl")
    if not slim_path:
        raise FileNotFoundError("Slim eval results not found for run.")

    system_prompt_path = find_run_file(run_dir, run_id, "system_prompt.md") or (
        base_dir / "prompts" / "system_prompt.md"
    )
    evals_path = find_run_file(run_dir, run_id, "Evals.json") or (
        base_dir / "prompts" / "Evals.json"
    )

    feature_context = (base_dir / "context" / "feature_context.md").read_text()
    system_prompt = system_prompt_path.read_text()

    results = load_jsonl(slim_path)
    stats = compute_stats(results)
    entries = collect_entries(results)
    evals_map = load_evals_map(evals_path)

    load_dotenv()
    client = OpenAI()

    cluster_sets = {}
    for criterion_name, criterion_entries in entries.items():
        failures, near_fails = build_failure_payload(criterion_entries)
        explanations_available = any(
            entry.get("explanation") for entry in failures + near_fails
        )
        criterion_def = evals_map.get(criterion_name, {})
        prompt = build_cluster_prompt(
            criterion_name,
            criterion_def,
            failures,
            near_fails,
            feature_context,
            system_prompt,
            explanations_available,
        )
        if not failures:
            cluster_sets[criterion_name] = {
                "criterion": criterion_name,
                "failures": 0,
                "clusters": [],
                "no_issue_note": "No failures detected for this criterion.",
            }
            continue
        max_examples = min(3, len(failures) + len(near_fails))
        failure_ids = [f["execution_id"] for f in failures]
        near_fail_ids = [n["execution_id"] for n in near_fails]
        explanation_map = {
            entry["execution_id"]: bool(entry.get("explanation"))
            for entry in failures + near_fails
        }
        payload = request_cluster_json(
            client,
            model,
            prompt,
            failure_ids,
            near_fail_ids,
            max_examples,
            explanation_map,
        )
        payload = apply_cluster_metrics(payload, failure_ids)
        payload = ensure_cluster_examples(payload, failures, near_fails)
        payload["near_fail_available"] = bool(near_fails)
        cluster_sets[criterion_name] = payload

    report = render_markdown(run_id, stats, cluster_sets)
    output_path.write_text(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate meta-analysis report.")
    parser.add_argument("--run-dir", required=True, help="Run directory path.")
    parser.add_argument("--run-id", required=True, help="Run ID (two digits).")
    parser.add_argument(
        "--output-path",
        required=True,
        help="Path to write the meta-analysis report markdown.",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Model to use for meta-analysis generation.",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    output_path = Path(args.output_path)

    generate_report(run_dir, args.run_id, output_path, args.model)
    print(f"Meta-analysis report saved to {output_path}")


if __name__ == "__main__":
    main()
