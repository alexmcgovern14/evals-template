# Eval methodology context

After 1000s of evals developing a number of production AI features, this is the most effective methodology I’ve landed on.

It combines the **LLM-as-a-judge efficiency** needed to validate consistent output, with the ability for the human to zoom in and out on the source data to fully understand the source data and problems — whilst maintaining full project context for AI throughout.

Based in an AI-powered IDE repo of files — Cursor.

Benefit of IDE is that i find chatgpt etc wont handle such massive files and context as well as this hub of information and files (not exectly sure what to call the set up/knowledge base!)

Then we can talk to the model to suggest improcements and negotiate on changes > update prompt file > run evals again and loop until happy.

Critical: evaluate at scale and retain ability to dive into the detail yourself.

Note: The repo includes procedure files under `procedures/skills/` (e.g., new run + meta-analysis). These are IDE-agnostic playbooks and can be wrapped into skills/slash commands in whatever IDE the user prefers.

---

## Why do evaluations?

LLMs are probabilistic. Provide the same prompt and input data twice and you’ll get different outputs. When building products, it’s critical that you can trust the output of the model.

Consistency can only be validated at scale, and is achieved through refined prompt engineering, input data, system design, observability, guardrails and all of our other levers.

Evals are the measure of success, verifying that the output meets expectations across a vast number of runs. They should be run not just before shipping, but each time you make a change: new model, new data input, prompt change.

- Evals can be human, always start here, I read someone call it a vibe check and that’s spot on.
- Scale is achieved through LLM as a judge, using another model to check the work of the first model. That’s what this post focuses on.

---

## Vibe check

Before using AI as a judge, firstly, vibe check. Read through output and get to a point where you’re approximately happy.

Consistent errors don’t need the scale of AI-as-a-judge evals to fix — handle those yourself first.

---

## Set up

I set up a folder for Cursor, or Codex, or Claude Code with the following files:

- Prompt (markdown) — can become a prompt changelog  
- Context (markdown)  
- Eval criteria, start wit 3–5, (json)  
- Execution data (JSONL) which contains input-output pairs, let’s say there’s 200.

Therefore Cursor has a full understanding of what we're trying to achieve with the project overall, the current prompt, what the evals are and the execution data.

---

## Define your eval criteria

Do not use generic eval prompts and scorers which lack context — evals must be specific to measuring the task you’re evaluating.

Remember, each evaluation run is independent and only knows what you tell it.

Your project context means the agent understands the overall concept, but maybe not the finer detail of what good/bad looks like, you might not be 100% clear either at this stage. This can take a few loops.

There’s nothing wrong with adding more evals as you go.

Talk through with the LLM output and what you like/dislike and define ~5 primary criteria. More or fewer depending on the complexity of your task.

---

## Evals with explanation output

Without this specification you just get scores, which don't tell you **WHY** something was marked up or down. This information is critical to understand problems with the prompt and then engineer it.

The prompts for the eval criteria will always be guided like:
- 1–2 = X  
- 3–4 = Y  
- 5–6 = Z  

This means that each evaluation will keep scoring consistent rather than each call handling the prompt/scoring differently.

It's important to give guidance here as need to trust the scores.

The next step is for the agent to run the evals, usually by taking the eval criteria and creating scripts to run them through API calls for each row of JSONL.

---

## Eval your eval

Your scores are now dependent on two probabilistic things:
- Primary prompt
- Eval criteria

Just as you’ll prompt engineer your primary prompt after not being perfect the first time, you’ll probably not get your evals perfect the first time either.

Something will be analysed incorrectly — maybe the rules weren’t tight enough, maybe logic was missed, maybe you didn’t think of something and realise it after seeing the eval pass it.

Treat the first run as evaluating your evals, not evaluating the output.

Go back to the agent and discuss what was missed and tighten up the prompts.

Often you find that the evals score things up/down for reasons you didnt intend, so it's important at this stage to validate that the evals are looking at the right things, not missing anything important, and thus scores and explanations can be trusted.

Update the evals in `prompts/Evals.json` (or ask the model to do it for you).

Loop again if needed.

Now the eval criteria are accurately measuring the input-output pairs according to your expectations.

---

## Evaluating eval results: meta analysis

The output now is:
- 200 executions  
- x 5 criteria  
- All with scores and explanations  

The scale is necessary to catch problems, but that's inefficient to read everything and identify common issues, especially as a first pass.

But you know what’s perfect for chunking, analysing text, pattern matching and clustering? **AI**.

Second layer of analysis is for another LLM to review the evaluation output: maintaining feature context once again, with clear visibility on prompt, evals and goals.

The LLM is tasked with reviewing:
- All outputs and judge explanations (not just failures)
- Scores (secondary context)
- Input-output pairs
- Prompt and context

…to cluster results.

Maybe:
- 50% of the 1s have the same issue
- 20% of the 2s have another issue

Those are big things to focus on.

The LLM is able to review the three sources of truth and identify where the problems could be:
- Missing data in some runs
- Prompt ambiguity
- Inconsistent interpretation

The report must cite **specific examples for each cluster**.

This combines:
- Scale of identifying problems
- Human ability to inspect source data

---

## Dashboard for deepdiving

Reading through jsonl/json isn't the smoothest experience when zooming in on outputs and eval scores/explanations, so work with the agent to build a dashboard which formats the data in an easily consumable way when deep-diving output and evals. 

Recommendation: 
One row per output 
Columns: ID | Output | Eval1 | Eval 2 |
- Eval columns contain scores and explanations
- Eval columns can be minimised for dialling in on specific ones
- Ability to pop up a focused view where you can see the full input data 

---

## Prompt engineering

Now that you’ve got the primary clusters to work on, identified at scale and validated with human eye, it’s time to make changes to the prompt.

As always, the Agent has context, understanding everything including:
- Evals meta analysis
- Prompt
- Input-output pairs

Perfectly placing it as a partner to prompt engineer with.

Go back and forth with the agent on how to solve the clusters through modifying the prompt, whilst not creating unintended issues.

Often LLMs like to dial in on a problem and create a heavy set of rules for what might be a small part of the primary prompt’s task.

In my experience the best-performing prompts are a little loose:
- They guide the model
- They set hard rules for a list of critical items

Too many extensive sections with hard rules for every edge case creates contradictions and confusion.

Update the new prompt in the prompt file.

---

## Loop

Run the evals again  
→ meta analysis  
→ get into the detail  
→ prompt engineer  
→ loop
