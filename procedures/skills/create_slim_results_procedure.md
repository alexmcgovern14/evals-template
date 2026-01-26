# Create Slim Results Procedure

## Purpose

After running evaluations, create a slimmed-down results file for fast meta-analysis and dashboard loading.

The slim file keeps the full generated output and all eval scores/explanations, while applying a conservative, best-effort prune to the input payload (only when it contains very large fields).

---

## What The Slim File Contains

Each JSONL line contains:
- `execution_id`
- `output`
- `evals` (scores, pass/fail, thresholds, explanations)
- `input` (parsed JSON when possible, with light pruning)

The pruning rules are intentionally generic (template-friendly):
- Drop known-huge keys (configured in `scripts/create_slim_results.py` as `DEFAULT_EXCLUDED_KEYS`)
- Replace very long lists (length > `MAX_LIST_ITEMS`) with a placeholder: `{"omitted": true, "items": N}`

---

## When To Run

- `scripts/new_run.py` already generates `<RUN_ID>_eval_results_slim.jsonl` automatically after evals finish.
- Run this manually only if you want to regenerate slim results from a full results file.

---

## Command

Option A (by run id):

```bash
python3 scripts/create_slim_results.py --run-id 01
```

Option B (explicit paths):

```bash
python3 scripts/create_slim_results.py \
  --input outputs/runs/<RUN_ID>/<RUN_ID>_eval_results.jsonl \
  --output outputs/runs/<RUN_ID>/<RUN_ID>_eval_results_slim.jsonl
```

---

## Validation

Line counts should match:

```bash
wc -l outputs/runs/<RUN_ID>/<RUN_ID>_eval_results.jsonl \
  outputs/runs/<RUN_ID>/<RUN_ID>_eval_results_slim.jsonl
```

---

## Customisation (Recommended)

If your domain inputs have very large fields (e.g. transcripts, documents, timelines), update:
- `DEFAULT_EXCLUDED_KEYS` (keys to drop entirely)
- `MAX_LIST_ITEMS` (max list length before truncation)

Keep this procedure file in sync with `scripts/create_slim_results.py` so template users can rely on it.

