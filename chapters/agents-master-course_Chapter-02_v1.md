# Chapter 2 — LLM Call + Goal: The Goal-Orientation Trait

**Trait focus:** Goal. Isolated. No iteration yet.
**Persona:** The Strategist (see personas §2).
**Prerequisites:** Chapter 1 complete.
**Code:** `code/chapter_02_goal.py`, `code/shared/goal_predicates.py`.

> **Tutor instruction.** Adopt The Strategist. Be decisive. Push Ram on the verifier — most learners under-engineer it.

---

## PHASE 1 — CALIBRATION

> **Ask Ram:** "If I tell Claude 'extract the city name from this sentence,' how do I know — programmatically, not by eyeballing — whether it succeeded?"

(Looking for: a checkable predicate. If Ram says "look at the output," that's Branch A. If he says "regex / schema / set membership," Branch B.)

## PHASE 2 — ADAPT

- **Branch A (shallow):** Explain goal-orientation has two halves — (a) the goal stated to the model in the prompt, (b) the verifier in your code that decides if the goal was met. Most beginners do (a) and skip (b). Both are required.
- **Branch B (strong):** Frame the deeper question: "Where does the goal predicate LIVE architecturally? In the prompt? In Python? In a schema? Pick one, defend it."
- **Branch C (reinforce trait_absence_naming):** Ask Ram to name what trait Chapter 1 lacked that Chapter 2 adds. Confirm before proceeding.

## PHASE 3 — CODE

Two files this time:
- `code/shared/goal_predicates.py` — reusable predicate helpers. You'll import from this in Ch 4, 8, 9, 10.
- `code/chapter_02_goal.py` — uses one predicate against a single `query()` call.

> **Tell Ram:** "Before running — predict: under what input will the predicate return False? Construct an example in your head."

(Expected: an input where Claude either hallucinates a city not in the sentence, or returns "no city" framed as prose instead of structured output.)

Run with two inputs:
- "I flew to Mumbai last week." → predicate should return True
- "I love long walks." → predicate should return False

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Move the goal predicate INTO the system prompt — i.e., tell Claude to self-check. What goes wrong, architecturally?"

(Expected answer: self-checking by the same model in the same call is self-confirmation bias. The verifier must be either deterministic Python OR a separately-prompted call with different context. Anything else is the model grading its own homework. This previews Chapter 9.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=verifier_independence`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Goal-orientation is a two-part contract: the goal in the prompt, the verifier in your code. Models confidently produce off-target output. The verifier is the architect's contract with reality.]`
> Generate your session brief: `python code/shared/session_brief.py --after 2`. Open the .html in your browser.

---

## Architect's Reflection

The pattern you've established in this chapter is portable across every future chapter:

```
result = call_the_model(prompt)
if goal_predicate(result):    # this is YOUR code, not Claude's
    success
else:
    miss — but no retry yet (that's Chapter 4)
```

Three properties of good goal predicates:

1. **Cheap to evaluate.** A predicate that needs another LLM call is expensive and adds latency. Prefer regex, schema validation, set membership, or deterministic checks where possible.
2. **Independent of the model.** If the predicate's logic is "ask Claude if Claude succeeded," you have no signal. The predicate must be a *different judge* — Python, schema, or a separately-prompted call.
3. **Structured input from the model.** If you want a tight predicate, demand structured output (JSON, single token, fixed format). Sloppy output ↔ sloppy predicate. This previews Chapter 6 (tool schemas as grammar).

Why this matters for the rest of the course: Chapter 4 adds iteration. An iteration loop without a clean goal predicate is an infinite loop. The predicate decides when to stop.

## Exit Check

You can write a goal predicate for three different tasks — (1) "extract a city name," (2) "summarize in ≤30 words," (3) "return a JSON object with these three fields." For each, state whether the predicate is deterministic, schema-based, or LLM-judged, and why.
