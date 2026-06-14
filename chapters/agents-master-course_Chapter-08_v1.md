# Chapter 8 — Five Traits Together + Eval Harness

**Trait focus:** All five composed. Inline eval harness (gap #3 from research).
**Persona:** The Architect (see personas §8).
**Prerequisites:** Chapters 2–7 complete.
**Code:** `code/chapter_08_integration.py`, `code/shared/eval_harness.py`.

> **Tutor instruction.** Adopt The Architect. The most important non-obvious lesson: **30% of build time goes to evals.** Without them, every prompt change is vibes.

---

## PHASE 1 — CALIBRATION

> **Ask Ram:** "You've tweaked your agent's system prompt and it 'feels better.' Without running anything: how confident are you that it's actually better, and what would make you certain?"

(Looking for: awareness that subjective improvement is unreliable for non-deterministic systems; only an eval harness with fixed inputs and a scoring rubric produces real signal. If Ram says "I'd test it a few times," Branch A. If he names regression suites / golden tasks / trajectory grading, Branch B.)

## PHASE 2 — ADAPT

- **Branch A (shallow):** Explain the eval-harness mental model. Non-deterministic systems can't be unit-tested the way functions can. Instead, you maintain a set of *task instances* (input, expected behavior, scoring function) and run the agent against the full set after every change. Score moves up or down. That's your signal. Two flavors: outcome evals (final output correct?) and trajectory evals (did the agent take a reasonable path?).
- **Branch B (strong):** Skip to design choices: outcome vs trajectory, deterministic scoring vs LLM-judge scoring, eval-set freshness (how do you avoid overfitting to your eval set), and the inflection point where you need 10 vs 100 vs 1000 cases.
- **Branch C (reinforce hook_recovery_design):** Confirm Ch 7 takeaway first.

## PHASE 3 — CODE

> **Tell Ram:** "Two files this chapter. `chapter_08_integration.py` is a real single-agent system — perceive, reason, act, iterate, with a goal. The task: 'find and fix all TODO comments in this directory.' `shared/eval_harness.py` is the reusable scaffold."

Architecture walkthrough before he runs:
1. **Goal predicate:** every TODO in the directory either fixed or deferred with a comment.
2. **Tools:** `list_files`, `read_file` (perception); `propose_fix`, `write_file` (action).
3. **Loop:** `ClaudeSDKClient`, max 20 turns.
4. **Hooks:** PreToolUse sandbox check; PostToolUse log to a trace file.

Then the eval harness:
1. Five fixture directories with known-good "before" states.
2. Each fixture has a `golden.json` describing the expected outcome.
3. The harness runs the agent against each fixture in a fresh sandbox copy.
4. Scoring function compares the post-run directory state to `golden.json`.

> **Predict before running:** "Which of the 5 fixtures do you think will fail and why?"

(Watch Ram reason about edge cases — file with no TODOs, file where the TODO is in a string literal, etc. This is architecture practice.)

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Your agent scores 4/5 on the eval set. You tweak the system prompt to fix the failing case and it now scores 5/5. What's the one thing you forgot to do?"

(Expected: re-run the OTHER 4 cases. A prompt change can regress passing cases. Real eval discipline: every change → full eval run. Bonus: add the formerly-failing case PERMANENTLY to the eval set as a regression test. The set should grow over time.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=eval_regression_discipline`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Evals are the unlock for iteration. 30% of build time. Every fix becomes a regression test. Without this, you're vibing — not engineering.]`

---

## Architect's Reflection

This chapter is the inflection point of the course. Everything before was primitive. Everything after assumes you have an evaluation discipline.

Three design choices the harness made for you, that you'd own in production:

1. **Outcome vs trajectory scoring.**
   - **Outcome:** the final state matches the golden. Cheap. Misses cases where the agent got lucky.
   - **Trajectory:** the *steps* match an acceptable pattern. Expensive. Catches "wrong reasoning, right answer" failures.
   - **Production rule:** outcome for fast feedback, trajectory for promotion gates.

2. **Deterministic vs LLM-judge scoring.**
   - **Deterministic:** Python compares strings/diffs/schemas. Fast, free, no variance.
   - **LLM-judge:** another Claude call grades the output against a rubric. Expensive, variable, catches semantic correctness.
   - **Production rule:** deterministic where possible; LLM-judge for genuinely fuzzy outputs (text quality, code style, summary completeness).

3. **Eval-set hygiene.**
   - Eval set grows on every shipped bugfix.
   - Eval set is checked into the repo. It IS the spec.
   - Beware overfitting: keep a separate **held-out set** that you score against monthly, not every commit.

Why this matters for Chapters 9–12: the verifier loop (Ch 9), the error recovery (Ch 10), the two-agent contract (Ch 11), and the orchestrator (Ch 12) all need this same harness shape. You'll extend `eval_harness.py` in each one.

## Exit Check

You can take any agent and define a 5-task eval set: each task has an input, a deterministic or LLM-judge scoring function, and a golden expected state. You can also explain when to add a task as a regression test vs hold it out for periodic checks.
