#!/bin/bash
# Progress monitoring script for evaluation run

# Get script directory and go to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

RUN_ID="$1"

if [ -z "$RUN_ID" ]; then
    if [ -d "outputs/runs" ]; then
        RUN_DIR=$(ls -1d outputs/runs/[0-9][0-9] 2>/dev/null | sort | tail -n 1)
        RUN_ID=$(basename "$RUN_DIR")
    fi
fi

if [ -n "$RUN_ID" ]; then
    RESULTS_FILE="outputs/runs/${RUN_ID}/${RUN_ID}_eval_results.jsonl"
    EXECUTIONS_FILE="outputs/runs/${RUN_ID}/${RUN_ID}_executions.jsonl"
    EVALS_FILE="outputs/runs/${RUN_ID}/${RUN_ID}_Evals.json"
else
    RESULTS_FILE="outputs/eval_results.jsonl"
    EXECUTIONS_FILE="data/merged_executions.jsonl"
    EVALS_FILE="prompts/Evals.json"
fi

if [ ! -f "$RESULTS_FILE" ]; then
    echo "❌ Results file not found. Evaluation may not have started."
    exit 1
fi

COMPLETED=$(wc -l < "$RESULTS_FILE")
if [ -f "$EXECUTIONS_FILE" ]; then
    TOTAL=$(wc -l < "$EXECUTIONS_FILE")
else
    TOTAL=$COMPLETED
fi
PERCENT=$((COMPLETED * 100 / TOTAL))

echo "================================"
echo "Evaluation Progress"
echo "================================"
echo "Completed: $COMPLETED / $TOTAL executions"
echo "Progress:  $PERCENT%"
echo "Remaining: $((TOTAL - COMPLETED)) executions"
echo ""

if [ $COMPLETED -eq $TOTAL ]; then
    echo "✅ Evaluation complete!"
    echo ""
    echo "View results:"
    echo "  cat $RESULTS_FILE | jq '.evals[] | {name: .eval_name, score: .score, passed: .passed}'"
else
    if command -v python3 >/dev/null 2>&1; then
        EVALS_COUNT=$(python3 - <<PY
import json
from pathlib import Path
path = Path("$EVALS_FILE")
if path.exists():
    print(len(json.loads(path.read_text())))
else:
    print(7)
PY
)
    else
        EVALS_COUNT=7
    fi
    TOTAL_API_CALLS=$((TOTAL * EVALS_COUNT))
    COMPLETED_API_CALLS=$((COMPLETED * EVALS_COUNT))
    echo "API Calls: $COMPLETED_API_CALLS / $TOTAL_API_CALLS"
    
    # Estimate time remaining
    if [ $COMPLETED -gt 0 ]; then
        EST_MINS=$((((TOTAL - COMPLETED) * 20) / 60))
        echo "Est. time remaining: ~${EST_MINS} minutes"
    fi
fi

echo "================================"
