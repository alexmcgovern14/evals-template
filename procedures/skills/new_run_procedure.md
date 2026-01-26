# New Eval Run Procedure (Numbered Runs)

This repo is for evaluating pre-generated LLM outputs. Generation happens elsewhere; you bring a fresh executions JSONL file (input-output pairs) into this repo, then run evals + meta-analysis here.

## 1) Prepare inputs

- Put your new executions file somewhere in this repo (example: `data/incoming/executions.jsonl`).
- If your executions JSONL uses different keys/structure, have the IDE agent add a small adapter or update `scripts/run_evals.py` so the eval runner can map your fields into the expected input/output shape.
- Confirm `prompts/system_prompt.md` and `prompts/user_prompt.md` match the prompts used to generate the executions file.
- Assume `prompts/Evals.json` is unchanged unless you explicitly want to update eval criteria.

## 2) Create a new run folder + run evals

Run:

```bash
python3 scripts/new_run.py --executions-path data/incoming/executions.jsonl
```

What happens:
- A new numbered run folder is created under `outputs/runs/` (e.g. `01`, `02`, `03`).
- The executions file is moved into that run folder.
- Snapshots are written into the run folder:
  - `<RUN_ID>_system_prompt.md`
  - `<RUN_ID>_user_prompt.md`
  - `<RUN_ID>_Evals.json`
  - `<RUN_ID>_run_manifest.json` (hashes + models + timestamps + counts)
- Eval outputs are written into the run folder:
  - `<RUN_ID>_eval_results.jsonl`
  - `<RUN_ID>_eval_results_slim.jsonl`

## 3) Meta-analysis (Chat-Driven)

After evals finish, generate meta-analysis in chat by following:
- `procedures/skills/meta_analysis_procedure.md`

Save the report into the same run folder using the run ID prefix:
- `<RUN_ID>_meta_analysis_report.md`

## 4) Review

Start the dashboard and select the run:
- pick the run in the “Eval run” selector
- open the meta-analysis link for that run

## 5) If The Eval Run Was Interrupted

If the eval process was interrupted, resume it by re-running evals and skipping completed executions:

```bash
python3 scripts/run_evals.py \
  --evals-path outputs/runs/<RUN_ID>/<RUN_ID>_Evals.json \
  --executions-path outputs/runs/<RUN_ID>/<RUN_ID>_executions.jsonl \
  --output-path outputs/runs/<RUN_ID>/<RUN_ID>_eval_results.jsonl \
  --resume
```
