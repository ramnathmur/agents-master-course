# Chapter 6 — Reason: Deliberate Planning + Tool Design

**Trait focus:** Reasoning isolated. Inline tool-design ergonomics (gap #1 from research).
**Persona:** The Planner (see personas §6).
**Prerequisites:** Chapter 5 complete.
**Code:** `code/chapter_06_reason.py`.

> **Tutor instruction.** Adopt The Planner. Force the contrast: a sloppy schema vs a tight one. Schema IS the agent's grammar.

---

## PHASE 1 — CALIBRATION

> **Ask Ram:** "If I want Claude to plan before acting, where do I put the plan? In the system prompt instructions? In a tool schema? In the conversation structure? Pick one and defend it."

(Listen for awareness that all three are options. The strongest answer: a structured-output tool whose schema enforces the plan shape. If Ram only says "system prompt," Branch A. If he names structured output / tool-as-contract, Branch B.)

## PHASE 2 — ADAPT

- **Branch A (shallow):** Walk through three places reasoning can be encoded: (a) system prompt instructions ("think step by step before acting"), (b) chain-of-thought scratchpad in the response, (c) a structured plan tool the model must call before action tools. Compare reliability — system prompt is suggestion; schema is contract.
- **Branch B (strong):** Skip to schema-as-grammar. Frame: "The JSON Schema for your tool's input is the agent's grammar for reasoning about that tool. Loose schema → loose reasoning. Required fields with crisp descriptions are compressed reasoning quality."
- **Branch C (reinforce tool_description_ergonomics):** Confirm Ram's takeaway from Ch 5 first.

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_06_reason.py` to IntelliJ. It defines TWO tools — `make_plan_sloppy` and `make_plan_tight`. Same intent, different schemas. Predict: which one produces a plan you could actually execute?"

(Expected: `make_plan_tight`. Sloppy schema accepts a single `plan: str` field. Tight schema requires `steps: list[Step]` where each Step has `action: enum`, `target: str`, `expected_outcome: str`. The tight schema enforces structure the agent must respect.)

Run the same task ("plan a trip to Goa for 3 days") through both. Compare:
- Sloppy plan: probably one paragraph of prose.
- Tight plan: a structured list of 3+ steps with explicit fields.

Then run a *second* call that takes the plan as input and executes step 1. Notice: the tight plan is executable; the sloppy plan requires more re-parsing.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Your tight schema requires `expected_outcome` per step. Why does that field matter for the *agent's reasoning*, even before any execution happens?"

(Expected answer: it forces the agent to predict, per step, what success looks like. That prediction is a goal predicate baked into the plan. When you execute step N, you have a built-in success criterion. This is goal-orientation (Ch 2) composed into reasoning (Ch 6). The architect's discipline: every schema field has a *teaching reason*, not just a *data reason*.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=schema_as_grammar`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Schema is the agent's grammar. Required fields compress reasoning quality into the contract. Every field should have a teaching reason, not just a data reason.]`

---

## Architect's Reflection

Tool design separates engineers who ship from engineers who debug forever. Three patterns:

1. **The plan-before-act tool.** Define a `propose_plan` tool whose schema is the plan structure. Configure the system prompt: "Always call `propose_plan` before any action tool." This forces deliberate reasoning as a step in the conversation. The plan is now in the transcript, inspectable, critiquable.

2. **Self-documenting fields.** Every field in your schema has a `description` that tells the model HOW to fill it, not just WHAT shape. `"target": str` is a shape. `"target": str (description: "The specific file or URL the action will affect. Must be a fully-qualified path.")` is a contract.

3. **Enums over strings whenever possible.** `action: enum["read", "write", "execute"]` is 100x more reliable than `action: str`. Enums constrain the model's output to a finite space the rest of your code can switch on. This is the cheapest reliability gain available.

Anti-pattern: massive optional-field schemas. A tool with 12 optional fields creates decision fatigue for the agent. Every optional field is a question the model has to answer (or skip, badly). Make every field required if possible. If genuinely optional, default it server-side.

## Exit Check

You can take any agent task and design the tool surface — for each tool: (a) one-sentence description with input/output/when-NOT, (b) JSON schema with required fields, enums where applicable, and field-level descriptions. You can also identify whether to use a tool at all, or just structured output from the model.
