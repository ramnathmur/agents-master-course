# Chapter 9 — Deeper Integration: Verifier / Critic Loop  [v2]

**Trait focus:** All five + actor/judge separation.
**Persona:** The Reviewer (personas v2, §9).
**Voice opener:** *"Don't ask the model 'is your answer correct?' — that's confirmation, not verification. Give me a structurally different judge."*
**Prerequisites:** Chapter 8 complete with eval harness working.
**Code:** `code/chapter_09_verifier.py`.

> **Revision v1 → v2:** Branch C expanded (R5).

---

## PHASE 1 — CALIBRATION

Open with the Voice sample, then:

> **Ask Ram:** "Your Ch 8 agent produces an answer. You ask the *same* agent in the *same* conversation 'is your answer correct?' What's the architectural problem with that as a verifier?"

## PHASE 2 — ADAPT

- **Branch A (shallow):** Self-confirmation bias. The verifier must differ from the actor along at least one of: different prompt, different context, different model.
- **Branch B (strong):** "Should the critic see the actor's chain of thought, or only the final output? Pick one. Defend it." (Most production critics see output only.)
- **Branch C (reinforce `eval_regression_discipline` from Ch 8):** "In Chapter 8 your weak signal was eval regression discipline — re-running the full suite after every change. The critic loop EXTENDS that discipline at runtime, per call. Every output gets graded by a structurally separate judge before commit. Same idea, different timing: evals are pre-deploy, critics are per-request. Both prevent silent regressions."

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_09_verifier.py`. The wrapper calls the actor (Ch 8 style), then runs a SEPARATE `query()` with the adversarial critic system prompt and fresh context. The critic returns `{accept, confidence, critique}`. Block commit if accept=False or confidence<0.7."

Predict: what does the critic need to see to catch a plausible-but-wrong actor output?

Force a failure: give the actor a task where its first answer is plausible but subtly wrong. Watch the critic catch what the goal predicate missed.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Your critic accepts 99% of actor outputs. Two interpretations. What are they, and how do you tell them apart?"

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=critic_calibration`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Actor and judge must be structurally different. Verify the critic with known-bad inputs before trusting its accept signals.]`

> Generate your session brief: `python code/shared/session_brief.py --after 9`. Open the .html in your browser.

---

## Architect's Reflection (action checklist form)

For every critic loop you ship:

1. **Adversarial framing** — does the critic's system prompt prime skepticism? ("Find what's wrong" not "Is this good?")
2. **Calibration set** — do I have 5 known-good + 5 known-bad outputs that I score the critic against? Did the critic accept all 5 good and reject all 5 bad?
3. **Separation discipline** — is the critic in a fresh context, with a different system prompt, ideally a different model tier?
4. **Cost gate** — am I running the critic on every output (2x cost), or only on high-stakes ones?
5. **Verification ≠ re-planning** — does my critic say "this is wrong" without saying "here's how to fix it"? Fixing is Chapter 10's surface.

## Exit Check

Take any agent output and design (a) the critic's adversarial system prompt, (b) the critic's calibration set (5 good + 5 bad), (c) the decision gate (threshold, what happens on reject).
