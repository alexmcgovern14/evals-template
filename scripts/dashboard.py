#!/usr/bin/env python3
"""
Eval Results Dashboard
A sleek web interface for viewing evaluation results
"""

from flask import Flask, render_template, jsonify, request, abort, send_file
import json
from pathlib import Path
from typing import Dict, List, Optional
import re

app = Flask(__name__, 
            template_folder='../dashboard_templates',
            static_folder='../dashboard_static')

# Enable CORS for Cursor browser
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    return response

def find_run_file(run_dir: Path, run_id: str, suffix: str) -> Optional[Path]:
    preferred = run_dir / f"{run_id}_{suffix}"
    if preferred.exists():
        return preferred
    matches = list(run_dir.glob(f"*_{suffix}"))
    return matches[0] if matches else None


def list_runs() -> List[Dict[str, Optional[str]]]:
    base_dir = Path(__file__).parent.parent
    runs_dir = base_dir / "outputs" / "runs"
    runs = []
    if runs_dir.exists():
        for entry in runs_dir.iterdir():
            if entry.is_dir() and entry.name.isdigit():
                run_id = entry.name
                slim_path = find_run_file(entry, run_id, "eval_results_slim.jsonl")
                results_path = find_run_file(entry, run_id, "eval_results.jsonl")
                system_prompt_path = find_run_file(entry, run_id, "system_prompt.md")
                user_prompt_path = find_run_file(entry, run_id, "user_prompt.md")
                evals_path = find_run_file(entry, run_id, "Evals.json")
                meta_path = find_run_file(entry, run_id, "meta_analysis_report.md")
                results_filename = results_path.name if results_path else None
                runs.append({
                    "id": run_id,
                    "slim_path": str(slim_path) if slim_path else None,
                    "results_path": str(results_path) if results_path else None,
                    "results_filename": results_filename,
                    "system_prompt_path": str(system_prompt_path) if system_prompt_path else None,
                    "user_prompt_path": str(user_prompt_path) if user_prompt_path else None,
                    "evals_path": str(evals_path) if evals_path else None,
                    "meta_path": str(meta_path) if meta_path else None,
                })
    runs.sort(key=lambda item: int(item["id"]))
    return runs


def load_results(results_path: Path) -> List[Dict]:
    results = []
    with results_path.open('r') as handle:
        for line in handle:
            if line.strip():
                result = json.loads(line)
                input_data = result.get("input")
                if isinstance(input_data, str):
                    try:
                        result["input"] = json.loads(input_data)
                    except json.JSONDecodeError:
                        result["input"] = {"raw_input": input_data}
                if isinstance(result.get("input"), dict):
                    result["input_flat"] = flatten_scalar_fields(result["input"])
                else:
                    result["input_flat"] = {}
                results.append(result)
    return results


def is_scalar(value: object) -> bool:
    return isinstance(value, (str, int, float, bool))


def flatten_scalar_fields(
    data: Dict,
    prefix: str = "",
    depth: int = 0,
    max_depth: int = 3,
) -> Dict[str, object]:
    """Flatten nested dict scalars into dot-path keys; ignore lists to avoid huge fan-out."""
    if not isinstance(data, dict):
        return {}
    if depth >= max_depth:
        return {}
    flat: Dict[str, object] = {}
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if is_scalar(value):
            flat[path] = value
        elif isinstance(value, dict):
            flat.update(flatten_scalar_fields(value, path, depth + 1, max_depth))
        else:
            # Ignore lists/other structures for identifier columns.
            continue
    return flat

def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "field"


def collect_input_columns(results: List[Dict]) -> List[Dict[str, str]]:
    counts: Dict[str, int] = {}
    for result in results[:50]:
        input_flat = result.get("input_flat")
        if not isinstance(input_flat, dict):
            continue
        for key, value in input_flat.items():
            if value is None:
                continue
            counts[key] = counts.get(key, 0) + 1
    keys = sorted(counts.keys(), key=lambda k: (-counts[k], k))
    keys = keys[:4]
    columns = []
    used_ids = set()
    for key in keys:
        base = f"input-{slugify(str(key))}"
        column_id = base
        index = 2
        while column_id in used_ids:
            column_id = f"{base}-{index}"
            index += 1
        used_ids.add(column_id)
        columns.append({"key": key, "label": key, "column_id": column_id})
    return columns


def attach_identifier_values(results: List[Dict], columns: List[Dict[str, str]]) -> None:
    for result in results:
        input_flat = result.get("input_flat", {})
        values: List[str] = []
        if isinstance(input_flat, dict):
            for column in columns:
                value = input_flat.get(column["key"])
                if value is None:
                    continue
                values.append(str(value))
        result["identifier_values"] = values
        overview_title = None
        if isinstance(result.get("input"), dict):
            overview = result["input"].get("overview")
            if isinstance(overview, dict):
                overview_title = overview.get("title")
        result["overview_title"] = overview_title


def resolve_run(run_id: Optional[str]) -> Dict[str, Optional[str]]:
    runs = list_runs()
    if not runs:
        return {
            "id": None,
            "slim_path": None,
            "meta_path": None,
            "system_prompt_path": None,
            "user_prompt_path": None,
            "evals_path": None,
        }
    if run_id:
        match = next((run for run in runs if run["id"] == run_id), None)
        if match:
            return match
    return runs[-1]

@app.route('/')
def index():
    runs = list_runs()
    selected_run_id = request.args.get("run")
    active_run = resolve_run(selected_run_id)

    base_dir = Path(__file__).parent.parent
    fallback_path = base_dir / "outputs" / "eval_results_slim.jsonl"
    results_path = Path(active_run["slim_path"]) if active_run["slim_path"] else fallback_path
    results = load_results(results_path) if results_path.exists() else []

    eval_names = [e['eval_name'] for e in results[0]['evals']] if results else []
    input_columns = collect_input_columns(results)
    attach_identifier_values(results, input_columns)

    if input_columns:
        labels = ", ".join([col["label"] for col in input_columns])
        search_placeholder = f"🔍 Search output text or {labels}..."
    else:
        search_placeholder = "🔍 Search output text..."

    meta_analysis_url = None
    if active_run.get("id") and active_run.get("meta_path"):
        meta_analysis_url = f"/meta-analysis/{active_run['id']}"

    prompts_url = None
    if active_run.get("id") and active_run.get("system_prompt_path"):
        prompts_url = f"/prompts/{active_run['id']}"

    return render_template(
        'dashboard.html',
        results=results,
        eval_names=eval_names,
        total_count=len(results),
        runs=runs,
        active_run_id=active_run.get("id"),
        meta_analysis_url=meta_analysis_url,
        prompts_url=prompts_url,
        input_columns=input_columns,
        search_placeholder=search_placeholder,
    )

@app.route('/api/results')
def api_results():
    selected_run_id = request.args.get("run")
    active_run = resolve_run(selected_run_id)
    if not active_run.get("slim_path"):
        return jsonify([])
    return jsonify(load_results(Path(active_run["slim_path"])))


@app.route('/meta-analysis/<run_id>')
def meta_analysis(run_id: str):
    if not run_id.isdigit():
        abort(404)
    active_run = resolve_run(run_id)
    meta_path = active_run.get("meta_path")
    if not meta_path:
        abort(404)
    return send_file(meta_path, mimetype="text/markdown")


@app.route('/prompts/<run_id>')
def prompts(run_id: str):
    if not run_id.isdigit():
        abort(404)
    active_run = resolve_run(run_id)
    system_prompt_path = active_run.get("system_prompt_path")
    user_prompt_path = active_run.get("user_prompt_path")
    evals_path = active_run.get("evals_path")
    if not system_prompt_path or not user_prompt_path or not evals_path:
        abort(404)
    system_prompt = Path(system_prompt_path).read_text()
    user_prompt = Path(user_prompt_path).read_text()
    evals = json.loads(Path(evals_path).read_text())
    return jsonify({
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "evals": evals,
    })

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 Starting Eval Results Dashboard")
    print("="*80)
    print("\n📊 Dashboard URL: http://localhost:5050")
    print("\n💡 Press Ctrl+C to stop the server\n")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5050)
