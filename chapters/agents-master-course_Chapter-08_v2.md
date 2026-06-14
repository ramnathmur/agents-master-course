# Chapter 8 — Five Traits Together + Eval Harness  [v2]

**Trait focus:** All five composed. Eval harness.
**Persona:** The Architect (personas v2, §8).
**Voice opener:** *"Five traits in one runnable file, scored by an eval set you wrote yourself. Spend a third of your build time here — it pays back over the next four chapters."*
**Prerequisites:** Chapters 2–7 complete.
**Code:** `code/chapter_08_integration.py` (v2 — now a REAL TODO-fixing agent with all five traits), `code/shared/eval_harness.py` (v2 — adds trajectory + LLM-judge).

> **Revision v1 → v2:** the code now actually composes all five traits (R1). The reflection is now an action checklist (R7). Branch C expanded (R5).

---

## PHASE 1 — CALIBRATION

Open with the Voice sample, then:

> **Ask Ram:** "You've tweaked your agent's system prompt and it 'feels better.' Without running anything: how confident are you that it's actually better, and what would make you certain?"

## PHASE 2 — ADAPT

- **Branch A (shallow):** Walk through the eval-harness mental model. Non-deterministic systems can't be unit-tested; you maintain task instances and run the agent against the full set after every change.
- **Branch B (strong):** Skip to design choices — outcome vs trajectory, deterministic vs LLM-judge, eval-set freshness, overfitting risk.
- **Branch C (reinforce `hook_recovery_design` from Ch 7):** "In Chapter 7 your weak signal was hook recovery design — what happens when a hook denies and the agent loops on the same deny? Evals are how you catch that failure mode systematically. A regression test that exercises the deny-loop case turns 'I think my hook works' into 'the eval set proves it.' Hooks without evals are intuition."

## PHASE 3 — CODE

> **Tell Ram:** "Two files. `chapter_08_integration.py` (v2) is now a REAL agent: list/read tools (perceive), plan tool (reason), write tool with sandbox hook (act), iteration loop (iterate), 'all TODOs resolved' predicate (goal). `shared/eval_harness.py` (v2) scores it against 3 fixture directories (clean, one_todo, multi_todo)."

Predict before running: which fixture is most likely to fail and why? Then run.

After scoring: tweak the system prompt (e.g., remove the "ALWAYS list_python_files first" rule). Re-run. Watch the score change. That delta is real engineering.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Your agent scores 2/3 on the eval set. You tweak the prompt to fix the failing case and it now scores 3/3. What's the one thing you forgot to do?"

Expected: re-run the OTHER 2 cases. Prompt changes can regress passing cases. Real eval discipline: every change → full eval run. Promote the formerly-failing case to a permanent regression test.

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=eval_regression_discipline`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Evals are the unlock for iteration. 30% of build time. Every fix becomes a regression test. Without this, you're vibing — not engineering.]`

---

## Architect's Reflection (action checklist form)

Before shipping any agent change, walk this list:

1. **Outcome vs trajectory** — am I scoring the final state, the path taken, or both? Use outcome for fast feedback, trajectory for promotion gates.
2. **Deterministic vs LLM-judge** — Python comparison where possible; LLM-judge only for genuinely fuzzy outputs.
3. **Eval-set hygiene** — is my eval set checked into the repo? Does it grow on every shipped bugfix? Do I keep a held-out set for periodic checks?
4. **Regression discipline** — did I re-run ALL cases after this change, not just the formerly-failing one?
5. **Failure attribution** — when a case fails, can I tell whether it's the prompt, the tool, or the goal predicate that's wrong?

## Exit Check

Take any agent and define a 5-task eval set: each task has an input, a scoring function (deterministic OR trajectory OR LLM-judge), and an expected output or trajectory. You can also explain when to add a task as a regression test vs hold it out.
