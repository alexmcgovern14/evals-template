#!/usr/bin/env python3
"""
Create a new numbered eval run folder, snapshot inputs, and run evaluations.
"""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
from typing import Dict, List, Optional

from run_evals import run_evaluations
from create_slim_results import extract_slim_data


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def next_run_id(runs_dir: Path) -> str:
    existing = []
    if runs_dir.exists():
        for entry in runs_dir.iterdir():
            if entry.is_dir() and entry.name.isdigit():
                existing.append(int(entry.name))
    next_num = max(existing, default=0) + 1
    return f"{next_num:02d}"


def parse_eval_models(evals_path: Path) -> List[Dict[str, str]]:
    with evals_path.open("r") as handle:
        evals = json.load(handle)
    models = []
    for item in evals:
        model_name = item.get("model", "")
        eval_name = item.get("name", "")
        if model_name:
            models.append({"eval_name": eval_name, "model": model_name})
    return models


def summarize_results(results: List[Dict]) -> Dict[str, Dict[str, float]]:
    summary = {}
    if not results:
        return summary
    eval_names = [e["eval_name"] for e in results[0].get("evals", [])]
    for eval_name in eval_names:
        scores = []
        passed = 0
        total = 0
        for result in results:
            for eval_result in result.get("evals", []):
                if eval_result.get("eval_name") == eval_name:
                    score = eval_result.get("score")
                    if score is not None:
                        scores.append(score)
                    if eval_result.get("passed"):
                        passed += 1
                    total += 1
        avg_score = sum(scores) / len(scores) if scores else 0
        pass_rate = (passed / total) if total else 0
        summary[eval_name] = {"avg_score": avg_score, "pass_rate": pass_rate}
    return summary


def write_manifest(
    manifest_path: Path,
    run_id: str,
    executions_path: Path,
    system_prompt_path: Path,
    user_prompt_path: Path,
    evals_path: Path,
    results: List[Dict],
    started_at: str,
    finished_at: str,
    source_executions_path: str,
) -> None:
    manifest = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "inputs": {
            "executions": {
                "path": str(executions_path),
                "sha256": sha256_file(executions_path),
                "count": len(results),
                "source_path": source_executions_path,
            },
            "prompts": {
                "system": {
                    "path": str(system_prompt_path),
                    "sha256": sha256_file(system_prompt_path),
                },
                "user": {
                    "path": str(user_prompt_path),
                    "sha256": sha256_file(user_prompt_path),
                },
            },
            "evals": {
                "path": str(evals_path),
                "sha256": sha256_file(evals_path),
                "models": parse_eval_models(evals_path),
            },
        },
        "summary": summarize_results(results),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a new eval run folder and execute evaluations."
    )
    base_dir = Path(__file__).parent.parent
    parser.add_argument(
        "--executions-path",
        required=True,
        help="Path to the incoming executions JSONL file.",
    )
    parser.add_argument(
        "--system-prompt-path",
        default=str(base_dir / "prompts" / "system_prompt.md"),
        help="Path to the system prompt file used for generation.",
    )
    parser.add_argument(
        "--user-prompt-path",
        default=str(base_dir / "prompts" / "user_prompt.md"),
        help="Path to the user prompt file used for generation.",
    )
    parser.add_argument(
        "--evals-path",
        default=str(base_dir / "prompts" / "Evals.json"),
        help="Path to the eval criteria JSON file.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional run ID (two digits). If not provided, auto-increment.",
    )
    args = parser.parse_args()

    executions_path = Path(args.executions_path)
    if not executions_path.exists():
        raise FileNotFoundError(f"Executions file not found: {executions_path}")

    runs_dir = base_dir / "outputs" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    run_id = args.run_id or next_run_id(runs_dir)
    if not run_id.isdigit():
        raise ValueError("run-id must be numeric")
    if len(run_id) < 2:
        run_id = run_id.zfill(2)

    run_dir = runs_dir / run_id
    if run_dir.exists():
        raise FileExistsError(f"Run folder already exists: {run_dir}")
    run_dir.mkdir()

    prefix = f"{run_id}_"
    run_executions = run_dir / f"{prefix}executions.jsonl"
    run_system_prompt = run_dir / f"{prefix}system_prompt.md"
    run_user_prompt = run_dir / f"{prefix}user_prompt.md"
    run_evals = run_dir / f"{prefix}Evals.json"
    run_results = run_dir / f"{prefix}eval_results.jsonl"
    run_slim_results = run_dir / f"{prefix}eval_results_slim.jsonl"
    run_manifest = run_dir / f"{prefix}run_manifest.json"

    source_executions_path = str(executions_path)
    shutil.move(str(executions_path), run_executions)

    system_prompt_path = Path(args.system_prompt_path)
    user_prompt_path = Path(args.user_prompt_path)
    evals_path = Path(args.evals_path)

    shutil.copy2(system_prompt_path, run_system_prompt)
    shutil.copy2(user_prompt_path, run_user_prompt)
    shutil.copy2(evals_path, run_evals)

    started_at = datetime.now(timezone.utc).isoformat()
    results = run_evaluations(run_evals, run_executions, run_results)
    extract_slim_data(str(run_results), str(run_slim_results))
    finished_at = datetime.now(timezone.utc).isoformat()

    write_manifest(
        run_manifest,
        run_id,
        run_executions,
        run_system_prompt,
        run_user_prompt,
        run_evals,
        results,
        started_at,
        finished_at,
        source_executions_path,
    )


    print(f"\nRun complete: {run_dir}")
    print(f"Results: {run_results}")
    print(f"Slim results: {run_slim_results}")
    print(f"Manifest: {run_manifest}")


if __name__ == "__main__":
    main()
