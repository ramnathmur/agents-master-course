# Chapter 3 — Chained Calls: Composing Primitives

**Trait focus:** Composition. Workflow ≠ agency. Make the distinction load-bearing.
**Persona:** The Composer (see personas §3).
**Prerequisites:** Chapter 2 complete.
**Code:** `code/chapter_03_chained.py`.

> **Tutor instruction.** Adopt The Composer. The single most important lesson here is: this chapter teaches WORKFLOW, not agency. The control plane lives in Python. Drive that home.

---

## PHASE 1 — CALIBRATION

> **Ask Ram:** "If I pipe the output of one Claude call into the prompt of another, do I now have an agent?"

(Listen for the word "control" or "decide" or "next step." If Ram says "yes, sort of" without naming the control plane, Branch A. If he says "no, my code is still deciding what call 2 is," Branch B.)

## PHASE 2 — ADAPT

- **Branch A (shallow):** Explain the control plane concept. In a chained workflow, *your Python code* decides "call 2 receives the output of call 1." Claude never decides the sequence. That's the architectural difference between a workflow (deterministic graph) and an agent (model-decided control flow). LangChain Sequential = workflow. Agent loop = agency.
- **Branch B (strong):** Skip to the deeper question: "When SHOULD you use a chained workflow instead of an agent loop?"
- **Branch C (reinforce verifier_independence):** Confirm the Ch 2 verifier-independence point before proceeding.

(Expected Branch B answer: when the sequence is known and deterministic, a workflow is cheaper, more reliable, more testable, and easier to debug than an agent. Anthropic's "Building Effective Agents" makes this distinction explicit — agents are for cases where the workflow shape is *unknown* until runtime. Premature use of an agent loop is the second-most-common architectural mistake.)

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_03_chained.py` to IntelliJ. Two calls. Call 1 generates a plan as JSON. Call 2 executes step 1 of the plan. Predict: where in this code does the 'decision about what to do next' live?"

(Expected: in Python — specifically, the `plan["steps"][0]` line. Claude generated the plan; Python picked step 0 deterministically. Claude is not deciding control flow.)

After running:
- Ask Ram to modify the code so Claude decides which step to execute first.
- Watch him reach for tools / loops / a stateful client. That's Chapter 4–7. Stop him. Just observe the reach.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Draw, in words, the control-plane diagram for this script. Where does Python own the sequence? Where could Claude own it instead?"

(Expected: Python owns sequence at the line where call 2's prompt is constructed from call 1's output. To shift control to Claude, you'd need (a) a loop, (b) a model-callable tool that lets Claude pick the next step, (c) a stopping condition Claude can signal. All three appear in Chapter 4.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=control_plane_ownership`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Chained workflows compose primitives. Agency requires the model to own the next-step decision. Until the model decides, it's a graph — not an agent.]`

---

## Architect's Reflection

This chapter exists to give you a vocabulary for a decision you'll make on every real project: **workflow or agent?** Most production "agents" are actually workflows with one or two agent-shaped steps embedded. That's correct engineering, not a failure.

Three signals that argue for a workflow over an agent:

1. **The steps are known.** You can list them in advance. The order is fixed or has few branches.
2. **Each step's output is checkable.** Schema, regex, predicate. No fuzzy validation needed.
3. **Latency and cost matter.** Workflows run in `O(N)` model calls where N is the step count. Agents run in `O(K·N)` where K is the average loop length and N is the task depth. K is usually 2–10x.

Three signals that argue for an agent over a workflow:

1. **The steps are unknown until runtime.** Research tasks, debugging, open-ended planning.
2. **The path branches widely on intermediate results.** A workflow with 50 conditional branches IS an agent — just written badly.
3. **Tool use is irregular.** You don't know which of 20 tools the task needs until you start.

Production rule of thumb: **start with a workflow. Promote to an agent only when the workflow's branching exceeds three levels of `if/else`.** Chapter 4 introduces the loop that promotes a workflow into an agent.

## Exit Check

You can take any task description (e.g., "summarize this document, then translate the summary to Hindi, then save it to a file") and decide — with reasons — whether to implement it as a chained workflow or an agent loop. You can also identify the inflection point where a workflow's complexity argues for promotion to an agent.
