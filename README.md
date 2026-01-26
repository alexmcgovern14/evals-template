# AI eval template (Weekly Portfolio Briefing example)

This repo is a **template for running evals on pre-generated LLM outputs**. It includes a fully synthetic example feature (Weekly Portfolio Briefing) plus a repeatable workflow for running evals, tracking runs, and reviewing results in a dashboard.

Generation happens **outside** this repo. You bring a JSONL file with input/output pairs, then run evals here.

## Quickstart

1) Install dependencies:
```bash
pip install -r requirements.txt
```

2) Add your API key:
```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

3) Try the included sample executions:
```bash
mkdir -p data/incoming
cp data/sample_executions.jsonl data/incoming/executions.jsonl
```

4) Run a new eval run:
```bash
python3 scripts/new_run.py --executions-path data/incoming/executions.jsonl
```

5) Open the dashboard:
```bash
python3 scripts/dashboard.py
# Visit http://localhost:5050
```

6) Generate meta-analysis (chat-driven):
- Follow `procedures/skills/meta_analysis_procedure.md`
- Save to `outputs/runs/<RUN_ID>/<RUN_ID>_meta_analysis_report.md`

## Execution File Format

Each line in the JSONL file must be:
```json
{"llm-input": "<JSON string>", "llm-output": "<model output string>"}
```

- `llm-input` is a **stringified JSON object** for the input
- `llm-output` is the model output (string)

If your executions use a different structure, that’s fine — ask the IDE agent to create a small adapter (or update `scripts/run_evals.py`) to map your fields into this expected shape. The agent should also update `prompts/user_prompt.md` to reflect your input schema.

## Primary Workflow (Numbered Runs)

Each run creates a new folder under `outputs/runs/<RUN_ID>/` with:
- `<RUN_ID>_executions.jsonl` (moved from incoming)
- `<RUN_ID>_system_prompt.md` / `<RUN_ID>_user_prompt.md`
- `<RUN_ID>_Evals.json`
- `<RUN_ID>_eval_results.jsonl`
- `<RUN_ID>_eval_results_slim.jsonl`
- `<RUN_ID>_run_manifest.json`
- `<RUN_ID>_meta_analysis_report.md` (chat-generated)

Full details live in:
- `procedures/skills/new_run_procedure.md`
- `procedures/skills/meta_analysis_procedure.md`

These procedure files can be wrapped into your IDE’s skill/slash-command system if it supports custom commands.

## Dashboard

The dashboard lets you:
- switch between eval runs
- search/filter by criteria and score
- open a full-screen modal with input, output, and evals
- view meta-analysis as a markdown overlay

Run it with:
```bash
python3 scripts/dashboard.py
```

## Optional Utilities

- Check progress for a run:
```bash
./scripts/check_progress.sh 02
```

- Resume an interrupted run:
```bash
python3 scripts/run_evals.py --executions-path outputs/runs/01/01_executions.jsonl \
  --output-path outputs/runs/01/01_eval_results.jsonl --resume
```

## Project Structure (Key Files)

```
context/                 Methodology + workflow docs
prompts/                 System prompt, user prompt, eval criteria
scripts/                 Run evals, dashboard, utilities
outputs/runs/             Per-run outputs (created by scripts)
data/incoming/            Drop new executions here
```

## Notes for Template Users

- Replace the Weekly Portfolio Briefing example prompts/evals with your own domain.
- Keep all metadata + run manifests so results are reproducible.
- This repo is eval-only; generation should happen elsewhere.
