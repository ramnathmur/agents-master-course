# Chapter 10 — Error Recovery, Re-Planning, and Human-in-the-Loop  [v2]

**Trait focus:** Goal-orientation under failure.
**Persona:** The Incident Commander (personas v2, §10).
**Voice opener:** *"Three failure responses, three seams. Premature retry is the rookie mistake. When in doubt, stop the loop and ask a person."*
**Prerequisites:** Chapter 9 complete.
**Code:** `code/chapter_10_recovery.py` (v2 — `Dispatcher` class now actually routes; retry/re-plan/escalate all fire in a single deliberate-failure scenario).

> **Revision v1 → v2:** dispatcher code is now wired end-to-end (R2). Branch C expanded (R5).

---

## PHASE 1 — CALIBRATION

Open with the Voice sample, then:

> **Ask Ram:** "Your agent's tool call fails with a 500 error. Three correct responses, depending on context. Name them."

## PHASE 2 — ADAPT

- **Branch A (shallow):** Three failure responses — retry (transient), re-plan (structural), escalate (policy). Each has a budget.
- **Branch B (strong):** Skip to the seam design: where in your code architecture do retry / re-plan / escalate live? Where's the dispatcher?
- **Branch C (reinforce `critic_calibration` from Ch 9):** "In Chapter 9 your weak signal was critic calibration — testing the critic against known-bad outputs. Failure dispatchers have an analogous discipline: test them against KNOWN failures of each class. Inject a transient → see retry fire. Inject a structural → see re-plan. Inject a policy block → see escalate. Without that test, your dispatcher's branches are theoretical, just like an untested critic's accepts are theoretical."

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_10_recovery.py` (v2). The `Dispatcher` class implements RETRY_CAP=3 and REPLAN_CAP=2 with promotion. The outer loop intercepts tool results via the `capture_result` PostToolUse hook, calls `classify_failure()`, and routes accordingly."

Run the scripted scenario (transient failure). Watch the dispatcher retry 3 times, then promote to structural (re-plan), then potentially escalate. The `dispatcher.history` list at the end is your audit trail.

Then modify the scenario: change the first call's mode to `structural`. Watch re-plan fire immediately, no retries.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Your dispatcher retries a transient failure 3 times and it's still failing. The 4th attempt is the same call, same input. What's the bug — and what's the fix?"

Expected: classification is too permissive. After K retries the failure is no longer transient — it's structural. The dispatcher should *promote* on retry exhaustion. (That's why `v2` calls `self.decide("structural")` recursively after RETRY_CAP.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=failure_classification_promotion`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Classification is not static. After K retries, transient promotes to structural. The escalation gate is where deployable agents differ from demo agents.]`

---

## Architect's Reflection (action checklist form)

For every tool surface you ship:

1. **Failure taxonomy** — have I listed the failure classes (network, rate limit, deny, schema, ambiguous, hallucinated)? Each maps to retry / re-plan / escalate.
2. **Budgets** — retry cap, re-plan cap. After re-plan exhaustion → escalate.
3. **Promotion rule** — does K retries on the same call → reclassify as structural? Without this, you loop.
4. **Re-plan context shape** — when I trigger re-plan, do I feed the failure as a structured `<previous_attempt>` block, not just "try again"?
5. **Escalation message** — is it a self-contained ticket (what was tried, what failed, what's needed)? The human shouldn't have to dig.

## Exit Check

Take any tool surface. Design (a) the failure taxonomy, (b) the dispatcher rules (which class routes where), (c) promotion rules, (d) HITL approval gates for irreversible actions.
