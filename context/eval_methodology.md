Below is the overall methodology and approach for running evals.

**Title: AI-native guide to evals: methodology for building reliable AI features**
**Subheading: Repeatable template and approach for building consistent GenAI output, through Claude Code/Cursor/Codex** 

After hundreds of evals developing a number of production AI features, this is the most effective methodology I have landed on for **building reliable GenAI features where outputs consistently and measurably meet expectations.** 

**The primary goal is to efficiently evaluate at scale** whilst retaining the **ability to zoom in and inspect the detail**. Working at small scale loses statistical significance, and _only_ zooming out takes you too far away from the detail to effectively understand and implement change — both are critical.

Therefore the methodology is a **fast, repeatable evaluation loop with two layers of analysis: evals and meta analysis, leveraging the power of AI to analyse eval outputs at scale.** 

**Based in an AI-powered IDE repository** — Cursor, Claude Code, Codex, etc, your choice — enabling **repeatability and controlled variability across runs**, easier handling of massive files and, importantly, **maintaining complete context for your agent**. It also makes spinning up a custom dashboard to observe your results *very* easy. **Each run is versioned and produces an auditable and comparable bundle of artefacts** acting as a changelog and results.

> Repository notes: **The accompanying GitHub repository contains a repeatable eval template and dashboard for following this methodology** https://github.com/alexmcgovern14/evals-template 

*Insert workflow diagram here*


## Why do evaluations?
LLMs are probabilistic. Provide the same prompt and input data five times and you’ll get five different outputs. When building AI products, it’s **critical that you can trust the output of the model**. 

Consistency can only be validated at scale, and is achieved through system design, prompt engineering, refining input data, observability, guardrails and more. These leverage points constrain the distribution of outputs, and evals are the measures of success.

**Evals verify that the output meets expectations across a vast number of runs**. They should be run not just before moving to production, but each time you make a change: new model, new data input, prompt change, and are a critical part of the overall system.

- Evals can be human, always start here, no need to use 100 LLM calls to discover something blindingly obvious. 
- Scale is achieved through LLM as a judge, using another model to check the work of the first model. That’s what this process focuses on. 


## 1. Vibe check

I read someone call early human observations *vibe checks* and that’s spot on. Obvious errors don’t need the scale of AI-as-a-judge evals to discover — read through outputs and resolve repeated issues first.


## 2. IDE setup: providing context

Providing full context of the feature, what you're trying to achieve and system design enables the AI agent to ground all of its answers in the source of truth. The template repo contains the following primary files:

- `feature_context.md`: what the product and feature are, goals, constraints, what 'good' looks like
- `system_prompt.md`: generation system prompt you’re evaluating
- `user_prompt.md`: in this example, the input schema
- `Evals.json`: eval criteria 
- `sample_executions.jsonl` — sample input-output pairs (what gets evaluated)

Separating these makes prompt, context, evals and data independently versionable and auditable.

## 3. Define eval criteria

Feature context means the agent understands the overall concept, but probably not the finer detail of what good/bad looks like — you might not be 100% clear either at this stage. This can take a few loops. There’s nothing wrong with discovering as you go, and sometimes seeing great output is a lightbulb moment to dial in on.

**Talk through the output with the LLM, what you like/dislike and what your primary expectations are, with the goal of defining 3-5 primary criteria.**

### What makes a good eval?

- **Scoring guidelines:** When using a model scorer (returning a number rating), it's important to guide the model with a system like 0-1 = X, 2-3 = Y, 4-5 = Z. Since each run is independent, not doing so runs the risk of variability in how the model handles each run. 
- **Explanations:** Scores alone don't tell you **why** something was marked up or down. Explanations give critical detail on the nuance of each output and are critical to understanding problems at scale through meta analysis (step 6).
- **Context:** Each evaluation run is independent and only knows what you tell it, so providing context in the eval system prompt goes a long way.
- **Specificity:** evals must be specific to measuring the task you’re evaluating. Do not use generic eval prompts and scorers which lack context. 
- **Non-overlapping metrics:** Each eval criterion should measure an independent aspect of quality.

> `Evals.json` provides strong examples of these requirements


## 4. Run evals 
The next step is for the agent to run the evals, applying eval prompts to each input-output pair via API calls.

> Repository notes: 
To run evals with repeatability: repository includes procedure files under `procedures/skills/` (e.g., new run + meta analysis). These are IDE-agnostic playbooks and provide instruction to the agent, or can be wrapped into skills/slash commands in whatever IDE the user prefers. 

Each eval run is versioned as a numbered folder, e.g. `outputs/runs/01/`. The folder contains the executions file plus logs of the prompts and eval criteria used for that run, alongside the eval results, run manifest (timestamps/hashes/models) and later meta analysis. This makes results reproducible and comparable across prompt/model changes.


## 5. Eval your eval
Your eval results are now dependent on two probabilistic things: primary system prompt and eval criteria. Just as you’ll prompt engineer your primary prompt after not being perfect the first time, **you’ll probably not get your evals perfect the first time either**. Do not act on the evals results until you trust the eval rubric.

Something will be analysed incorrectly vs. expectations — often you'll find that evals score things up/down for reasons you didn't intend, maybe the rules weren’t tight enough, maybe logic was missed, maybe you didn’t think of a requirement.

Treat the first run as evaluating your evals, not evaluating the output. Go back to the agent and discuss what was missed and tighten up the eval prompts.

It's important at this stage to validate that the evals are looking at the right things, not missing anything important, and therefore scores and explanations can be trusted. Discuss with the agent and update `Evals.json` (or ask the model to do it for you). 

**Loop again if needed.**

Now the eval criteria are accurately measuring the input-output pairs according to your expectations.

## 6. Dashboard: viewing eval results

Reading through JSON isn't the smoothest experience, so work with the agent to spin up a dashboard to format the data in an easily consumable way.

Repository includes a lightweight HTML dashboard which allows switching between runs, viewing outputs and eval results, as well as accessing the meta analysis, input data, evals and prompts used on that run — per versioning structure below.

*Insert dashboard screenshot here*

> Repository notes: lightweight dashboard built to run on localhost, you'll just need to ask the IDE agent to map your schema and adapt the dash if necessary.

### Versioning runs

Each run is versioned in `outputs/` folder, maintaining a log of artefacts and variables used.

**This makes results reproducible and changes attributable: when scores move, you can see exactly what changed.**

Each run (eg. `outputs/runs/01/`) contains: 
- Input data used: `01_executions.jsonl` 
- Generation prompts: `01_system_prompt.md`, `01_user_prompt.md`
- Eval rubric: `01_evals.json`
- Eval results: `01_eval_results.jsonl`
- Run manifest: model(s), temperature, timestamp, git commit etc. `01_run_manifest.json`
- Meta analysis report: `01_meta_analysis_report.md`

## 7. Meta analysis: zoom out and in 

A reminder of the primary goal: **efficiently evaluate at scale (zoom out)** whilst retaining the ability to zoom in and inspect the detail. 

You can start smaller to save burning tokens, but output must be validated at scale to be a representative sample. 

Let's say there's 200 executions x 5 criteria, all with scores and explanations. Reading 1000 rows to pattern match and prioritise issues is inefficient, and you *probably* won't do a great job of it. You know what’s great at chunking, analysing, pattern matching and clustering text..? 

The second layer of analysis is for another model to analyse the four primary factors to **identify, cluster and prioritise issues in output:**
**1. Eval output:** with scores and explanations  
**2. Input-output pairs:** to understand if an output issue is due to input data 
**3. System prompt:** likely cause of issues, to be engineered
**4. Eval criteria:** to detect rubric flaws causing false positives or false negatives

Maybe 50% of runs have the one issue, and 20% have another problem, those are big things to focus on! Maybe the good scores have something in common which to dial in on too.

The report must:
- **Cite specific examples for each cluster:** This means we combine the scale of identifying problems at scale with the ability for the human to read the source data and understand the problem 
- **List clusters in priority order** to prioritise where you focus
- **Suggest changes** to resolve issues

> GitHub repo: `01_meta_analysis_report.md.` provides a sample of report.
`meta_analysis_procedure.md` and skills file instruct IDE agent on this step.





## 8. Prompt engineering

Now that you have the primary clusters to work on, identified at scale and validated with human eye, it’s time to make changes to the prompt.

As always, the Agent has context, understanding everything including the evals, meta analysis, the prompt and the input-output pairs. Perfectly placing it as a partner to prompt engineer with. 

Go back and forth with the agent on how to solve the clusters through modifying the prompt, whilst not creating unintended issues. 

Often LLMs like to dial in on a problem and create a heavy set of rules for what might be a small part of the primary prompt’s task. The best-performing prompts are, in my view, a little loose, they guide the model and only set hard rules for a small list of critical items. Too many extensive sections with hard rules for every edge case creates contradictions and confusion. 

Update the new prompt in the `system_prompt.md` (or, once again, ask the agent to do it for you)

## 9. Iteration: loop

Run the evals again → meta analysis → review the dashboard → prompt engineer → loop.

## Conclusion

Evals are a fundamental building block of good AI infrastructure. Without them your output shape, structure, data reliability, tone of voice or factual fidelity will break in production. 

After a little bit of set up, having a repeatable, auditable process with comprehensive context makes each iteration easier and easier. 