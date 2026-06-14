# Chapter 6 — Reason: Deliberate Planning + Tool Design  [v2]

**Trait focus:** Reasoning isolated. Schema as grammar.
**Persona:** The Planner (personas v2, §6).
**Voice opener:** *"Schema is grammar. Loose grammar, loose thought. Required fields are how you compress reasoning quality into the contract."*
**Prerequisites:** Chapter 5 complete.
**Code:** `code/chapter_06_reason.py` (v2 — `make_plan_tight` now validates the full inner shape).

> **Revision v1 → v2:** calibration question reframed to land on the schema seam Chapter 5 sets up (R8); code-side schema is now genuinely tight (R4).

---

## PHASE 1 — CALIBRATION

Open with the Voice sample, then:

> **Ask Ram (revised v2):** "In Chapter 5 you engineered the tool's *description* — the prose the model reads to decide WHETHER to use the tool. Now you're engineering the tool's *schema* — the structure the model fills in when it DOES use the tool. Description is vocabulary; schema is grammar. Tell me: if I want the model to plan-before-acting, do I put the plan-instruction in the description, in the schema, or in the system prompt? Pick one. Defend it."

## PHASE 2 — ADAPT

- **Branch A (shallow):** Three places reasoning can be encoded — system prompt instruction, chain-of-thought scratchpad, or a structured plan tool whose SCHEMA forces the plan shape. The schema is contract; the others are suggestion.
- **Branch B (strong):** Skip to "loose schema → loose reasoning." Required fields + enums + per-field descriptions are compressed reasoning quality.
- **Branch C (reinforce `tool_description_ergonomics` from Ch 5):** "In Chapter 5 your weak signal was tool description ergonomics. In this chapter the partner discipline is schema ergonomics. The same four-question rule applies, scaled to fields: every field needs a description AND a tight type AND a required/optional declaration."

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_06_reason.py`. Two tools — `make_plan_sloppy` (accepts `plan: str`) and `make_plan_tight` (requires `steps: list[Step]` where each Step has action as an enum, target and expected_outcome as non-empty strings, ALL validated server-side). Predict: which one will produce an executable plan?"

Run the same task ("plan a 3-day trip to Goa") through both. Then watch what happens if you feed the tight tool a malformed step — it rejects with a structured error message the agent can fix.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Your tight schema requires `expected_outcome` per step. Why does that field matter for the agent's *reasoning*, even before any execution?"

Expected: it forces the agent to predict success per step → goal predicate baked into the plan → Ch 2's discipline composed into Ch 6's structure.

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=schema_as_grammar`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Schema is the agent's grammar. Required fields compress reasoning quality into the contract. Every field has a teaching reason, not just a data reason.]`

---

## Architect's Reflection (action checklist form)

For every tool you ship, verify:

1. **Required fields are required** — no `Optional[T] = None` fields without a server-side default.
2. **Enums over strings** — for any field with a finite value set, use an enum. 100x reliability gain.
3. **Field-level descriptions** — every field's `description` answers "HOW to fill this," not just "WHAT shape."
4. **Server-side validation** — the tool body re-checks the schema. The model WILL produce malformed inputs occasionally; the tool's rejection becomes a teaching signal.

## Exit Check

Take any agent task. Design the tool surface: for each tool, deliver (a) the four-question description (Ch 5) and (b) the tight schema with enums + required fields + per-field descriptions (Ch 6). You can also identify when to skip the tool entirely and use structured output from the model directly.
