#!/usr/bin/env python3
"""
Create a slimmed-down version of eval results for meta-analysis.
Extracts only essential fields for efficient review.
"""

import argparse
import json
from pathlib import Path


DEFAULT_EXCLUDED_KEYS = {
    # Commonly huge fields in some domains; safe defaults for a template.
    "incidents",
    "fullIncidents",
    "commentaries",
    "tweets",
    "playerLists",
}

MAX_LIST_ITEMS = 200


def slim_input_payload(input_data):
    """Best-effort slimming of input payload while preserving useful context."""
    if not isinstance(input_data, dict):
        return input_data

    slimmed = {}
    for key, value in input_data.items():
        if key in DEFAULT_EXCLUDED_KEYS:
            continue
        if isinstance(value, list) and len(value) > MAX_LIST_ITEMS:
            # Keep a lightweight placeholder so analysts know something was omitted.
            slimmed[key] = {"omitted": True, "items": len(value)}
            continue
        slimmed[key] = value
    return slimmed


def extract_slim_data(full_results_path: str, output_path: str):
    """
    Extract slimmed-down eval results containing:
    - Output (generated summary)
    - Eval scores and explanations
    - Input data (optionally slimmed to remove very large fields)
    """
    
    slim_results = []
    
    with open(full_results_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                result = json.loads(line)
                
                raw_input = result.get("input")
                if isinstance(raw_input, str):
                    try:
                        input_data = json.loads(raw_input)
                    except json.JSONDecodeError:
                        input_data = {"raw_input": raw_input}
                elif isinstance(raw_input, dict):
                    input_data = raw_input
                else:
                    input_data = {"raw_input": raw_input}

                slim_input = slim_input_payload(input_data)
                
                # Ensure explanations are preserved
                # (Some may be empty strings if model didn't provide them)
                slim_evals = []
                for eval_result in result['evals']:
                    slim_evals.append({
                        'eval_name': eval_result['eval_name'],
                        'score': eval_result['score'],
                        'explanation': eval_result.get('explanation', ''),  # Preserve explanations
                        'pass_threshold': eval_result['pass_threshold'],
                        'passed': eval_result['passed'],
                        'range': eval_result['range']
                    })
                
                # Create slim result entry
                slim_result = {
                    'execution_id': result['execution_id'],
                    'output': result['output'],
                    'input': slim_input,
                    'evals': slim_evals
                }
                
                slim_results.append(slim_result)
                
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping line {line_num} due to JSON error: {e}")
                continue
    
    # Write slim results
    with open(output_path, 'w') as f:
        for result in slim_results:
            f.write(json.dumps(result) + '\n')
    
    return len(slim_results)


def resolve_paths(args: argparse.Namespace, base_dir: Path) -> tuple[Path, Path]:
    if args.run_id:
        run_id = str(args.run_id).zfill(2)
        run_dir = base_dir / "outputs" / "runs" / run_id
        input_path = run_dir / f"{run_id}_eval_results.jsonl"
        output_path = run_dir / f"{run_id}_eval_results_slim.jsonl"
        return input_path, output_path
    input_path = Path(args.input) if args.input else base_dir / "outputs" / "eval_results.jsonl"
    output_path = Path(args.output) if args.output else base_dir / "outputs" / "eval_results_slim.jsonl"
    return input_path, output_path


def main():
    base_dir = Path(__file__).parent.parent

    parser = argparse.ArgumentParser(description="Create slim eval results for meta-analysis.")
    parser.add_argument("--run-id", help="Run ID to process (e.g. 01).")
    parser.add_argument("--input", help="Path to full eval results JSONL.")
    parser.add_argument("--output", help="Path to write slim eval results JSONL.")
    args = parser.parse_args()

    full_results, slim_results = resolve_paths(args, base_dir)
    
    print("Creating slimmed-down eval results...")
    print(f"Input:  {full_results}")
    print(f"Output: {slim_results}")
    
    count = extract_slim_data(str(full_results), str(slim_results))
    
    # Calculate size reduction
    full_size = full_results.stat().st_size / (1024 * 1024)  # MB
    slim_size = slim_results.stat().st_size / (1024 * 1024)  # MB
    reduction = ((full_size - slim_size) / full_size) * 100
    
    print(f"\n✓ Processed {count} executions")
    print(f"  Full file:  {full_size:.2f} MB")
    print(f"  Slim file:  {slim_size:.2f} MB")
    print(f"  Reduction:  {reduction:.1f}%")
    print(f"\nSlim file ready for meta-analysis at:")
    print(f"  {slim_results}")


if __name__ == "__main__":
    main()
