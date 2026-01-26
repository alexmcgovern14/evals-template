#!/usr/bin/env python3
"""
Evaluation runner for this repo.
Runs eval criteria from an Evals.json file against executions JSONL input/output pairs.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Any
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_evals(evals_path: str) -> List[Dict]:
    """Load evaluation criteria from Evals.json"""
    with open(evals_path, 'r') as f:
        return json.load(f)


def load_executions(executions_path: str) -> List[Dict]:
    """Load input-output pairs from merged JSONL file"""
    executions = []
    with open(executions_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                executions.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping line {line_num} due to JSON error: {e}")
                print(f"  First 100 chars: {line[:100]}")
                continue
    return executions


def replace_template_variables(template: str, item_input: str, item_output: str) -> str:
    """Replace template variables like {{item.input}} and {{item.output}}"""
    # Replace {{item.input}} with the actual input
    template = template.replace("{{item.input}}", item_input)
    # Replace {{item.output}} with the actual output
    template = template.replace("{{item.output}}", item_output)
    return template


def run_eval(eval_criteria: Dict, execution: Dict) -> Dict:
    """Run a single evaluation criterion against one execution"""
    
    # Extract input and output
    item_input = execution.get("llm-input", "")
    item_output = execution.get("llm-output", "")
    
    # Build messages for the API call
    messages = []
    for msg in eval_criteria["input"]:
        content = replace_template_variables(msg["content"], item_input, item_output)
        messages.append({
            "role": msg["role"] if msg["role"] != "developer" else "system",
            "content": content
        })
    
    # Make API call
    try:
        response = client.chat.completions.create(
            model=eval_criteria["model"],
            messages=messages,
            temperature=0
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse result based on eval type
        # For score_model, try to extract integer or JSON
        if eval_criteria["type"] == "score_model":
            # Check if response is JSON (for evals that request JSON output)
            try:
                result_json = json.loads(result_text)
                if isinstance(result_json, dict) and "result" in result_json:
                    score = result_json["result"]
                    explanation = result_json.get("explanation", "")
                else:
                    score = result_json
                    explanation = ""
            except json.JSONDecodeError:
                # Try to extract integer from text
                match = re.search(r'\b(\d+)\b', result_text)
                if match:
                    score = int(match.group(1))
                    explanation = result_text
                else:
                    score = None
                    explanation = result_text
            
            return {
                "eval_name": eval_criteria["name"],
                "score": score,
                "explanation": explanation,
                "pass_threshold": eval_criteria["pass_threshold"],
                "passed": score >= eval_criteria["pass_threshold"] if score is not None else None,
                "range": eval_criteria["range"]
            }
    
    except Exception as e:
        return {
            "eval_name": eval_criteria["name"],
            "score": None,
            "explanation": f"Error: {str(e)}",
            "pass_threshold": eval_criteria["pass_threshold"],
            "passed": None,
            "range": eval_criteria["range"]
        }


def load_existing_results(output_path: Path) -> List[Dict]:
    results = []
    if not output_path.exists():
        return results
    with output_path.open("r") as handle:
        for line_num, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping existing result line {line_num} due to JSON error: {e}")
                continue
    return results


def run_evaluations(
    evals_path: Path,
    executions_path: Path,
    output_path: Path,
    resume: bool = False,
) -> List[Dict]:
    """Run all evaluation criteria against executions and write results."""
    
    # Load data
    print("Loading evaluation criteria...")
    evals = load_evals(evals_path)
    print(f"Loaded {len(evals)} evaluation criteria")
    
    print("\nLoading executions...")
    executions = load_executions(executions_path)
    print(f"Loaded {len(executions)} executions")
    
    print("\nRunning evaluations...")
    print("=" * 80)
    
    # Run evaluations with incremental saving
    results: List[Dict[str, Any]] = []
    completed_ids = set()
    if resume and output_path.exists():
        results = load_existing_results(output_path)
        completed_ids = {
            result.get("execution_id")
            for result in results
            if result.get("execution_id") is not None
        }
        if completed_ids:
            print(f"\nResuming: {len(completed_ids)} executions already completed.")
    total_evals = len(executions) * len(evals)
    current = len(completed_ids) * len(evals)
    
    # Open output file for incremental writes
    output_mode = "a" if resume and output_path.exists() else "w"
    with open(output_path, output_mode) as output_file:
        for idx, execution in enumerate(executions, 1):
            if idx in completed_ids:
                continue
            print(f"\nExecution {idx}/{len(executions)}")
            
            result = {
                "execution_id": idx,
                "input": execution.get("llm-input"),
                "output": execution.get("llm-output"),
                "evals": []
            }
            
            for eval_criteria in evals:
                current += 1
                # Less verbose - print progress once per execution (after all criteria).
                if len(evals) and current % len(evals) == 0:
                    print(f"  Progress: {current}/{total_evals} API calls ({current*100//total_evals}%)")
                
                eval_result = run_eval(eval_criteria, execution)
                result["evals"].append(eval_result)
            
            results.append(result)
            
            # Write result immediately after each execution completes
            output_file.write(json.dumps(result) + '\n')
            output_file.flush()
    
    # Results already saved incrementally
    print("\n" + "=" * 80)
    print(f"\nResults saved incrementally to {output_path}")
    
    # Print summary statistics
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    
    for eval_criteria in evals:
        eval_name = eval_criteria["name"]
        scores = [
            e["score"]
            for r in results
            for e in r.get("evals", [])
            if e.get("eval_name") == eval_name and e.get("score") is not None
        ]
        
        if scores:
            avg_score = sum(scores) / len(scores)
            passed_count = sum(
                1
                for r in results
                for e in r.get("evals", [])
                if e.get("eval_name") == eval_name and e.get("passed")
            )
            total_count = len(results)
            pass_rate = (passed_count / total_count) * 100
            
            print(f"\n{eval_name}:")
            print(f"  Average Score: {avg_score:.2f}/{eval_criteria['range'][1]}")
            print(f"  Pass Rate: {pass_rate:.1f}% ({passed_count}/{total_count})")
            print(f"  Pass Threshold: {eval_criteria['pass_threshold']}")
    
    print("\n" + "=" * 80)
    print(f"✓ Complete! Results saved to: {output_path}")
    print("=" * 80)

    return results


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Run evals against execution data.")
    base_dir = Path(__file__).parent.parent
    parser.add_argument(
        "--evals-path",
        default=str(base_dir / "prompts" / "Evals.json"),
        help="Path to Evals.json",
    )
    parser.add_argument(
        "--executions-path",
        default=str(base_dir / "data" / "merged_executions.jsonl"),
        help="Path to merged executions JSONL",
    )
    parser.add_argument(
        "--output-path",
        default=str(base_dir / "outputs" / "eval_results.jsonl"),
        help="Path to write eval results JSONL",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume by skipping executions already present in the output file.",
    )
    args = parser.parse_args()

    evals_path = Path(args.evals_path)
    executions_path = Path(args.executions_path)
    output_path = Path(args.output_path)

    run_evaluations(evals_path, executions_path, output_path, resume=args.resume)


if __name__ == "__main__":
    main()
