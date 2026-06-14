# Chapter 10 — Error Recovery, Re-Planning, and Human-in-the-Loop

**Trait focus:** Goal-orientation under failure. Inline HITL (gap #4 from research).
**Persona:** The Incident Commander (see personas §10).
**Prerequisites:** Chapter 9 complete.
**Code:** `code/chapter_10_recovery.py`.

> **Tutor instruction.** Adopt The Incident Commander. The key lesson: three failure responses, three different architectural seams. Premature retry is the rookie mistake.

---

## PHASE 1 — CALIBRATION

> **Ask Ram:** "Your agent's tool call fails with a 500 error. Three correct responses, depending on context. Name them."

(Looking for: retry, re-plan, escalate. Plus the rule of thumb for choosing. If Ram says "retry with backoff," that's only one. Push: "What if the failure is the SAME on retry?" or "What if it's a permission denial, not a transient error?")

## PHASE 2 — ADAPT

- **Branch A (shallow):** Three failure responses:
  - **Retry** — same plan, same tool, same input. Appropriate ONLY for transient errors (network, rate limit, brief unavailability). Cap retries: 3 is a good default. After cap, escalate.
  - **Re-plan** — different approach. The current plan is wrong; generate a new one. Appropriate when the failure is structural (tool denied, schema mismatch, goal unreachable on this path).
  - **Escalate** — stop the agent, hand off to a human. Appropriate when both retry and re-plan have failed, when the failure has real-world consequences, or when policy requires human approval (financial, irreversible, ambiguous).
- **Branch B (strong):** Skip to the *seam* design: where in your code architecture do each of these three responses live? Where's the dispatcher that picks?
- **Branch C (reinforce critic_calibration):** Confirm Ch 9 takeaway first.

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_10_recovery.py` to IntelliJ. It extends Ch 8/9 with a recovery dispatcher. The agent's loop now wraps each tool call in a failure-handler that classifies the failure (transient/structural/policy) and routes to retry/re-plan/escalate. A `PreToolUse` hook can request human approval for high-stakes tool calls."

Architecture:
1. **Failure classifier:** Python function that inspects the tool result. Three classes:
   - Transient — exception types like timeout, rate-limit; HTTP 5xx.
   - Structural — schema mismatch, deny from validation hook, persistent 4xx.
   - Policy — `PreToolUse` returned `requires_approval`.
2. **Dispatcher:** routes by class. Retries (with backoff) for transient. Re-plans by injecting failure context into a fresh `query()` for structural. Pauses for input for policy.
3. **HITL gate:** a `PreToolUse` hook that prints the proposed tool call to stdout and waits for `y/n` on stdin.

> **Predict before running:** "I'll inject three deliberate failures. Which classification will the dispatcher use for each?"

Test cases injected:
- A `read_file` call to a path that returns a transient OS error (file locked) → retry.
- A `write_file` call with content that fails schema validation → re-plan.
- A `delete_file` call that requires approval → escalate, wait for human.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Your dispatcher retries a transient failure 3 times and it's still failing. The fourth attempt is the same call, same input. What's the bug — and what's the fix?"

(Expected:
- **Bug:** the dispatcher's classification is too permissive. A "transient" failure that's failed 3x is no longer transient — it's structural. The dispatcher should promote it to re-plan after the retry cap.
- **Fix:** retries don't just have a count cap; they have a *promotion* path. After K retries on the same call, reclassify and re-route.

This is the same pattern as TCP exponential backoff with eventual failure — but applied to agent control flow. The architect's discipline: failure classification is not static; it evolves with retry count.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=failure_classification_promotion`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Three failure responses, three architectural seams. Classification is not static — after K retries, transient promotes to structural. The escalation gate is where deployable agents differ from demo agents.]`

---

## Architect's Reflection

This chapter is where your agent becomes deployable. Four patterns to internalize:

1. **Failure taxonomy first, dispatcher second.** Before writing recovery code, list the failure modes you expect. Network errors, rate limits, permission denials, schema mismatches, ambiguous outputs, hallucinations. Classify each. Then write the dispatcher.

2. **Retries have a budget AND a promotion rule.** Cap retry count (3 is sane). After cap, promote to re-plan. After re-plan fails twice, promote to escalate. The path is: retry → re-plan → escalate, with budgets at each level.

3. **Re-planning needs the failure context in structured form.** When you trigger re-plan, feed the model the failure as a structured block: `<previous_attempt failed_at="..." reason="..." />`. Don't just say "try again."

4. **Escalation is structured, not silent.** When you escalate, log: what the agent was trying to do, what failed, what's needed from the human, what state has been preserved. A good escalation message is a self-contained ticket — the human shouldn't have to dig.

Production rule of thumb: every irreversible action (file delete, payment, email send, API write to production) goes through an approval gate. The agent proposes; the human disposes. Even for trusted agents — the audit trail alone is worth the friction.

## Exit Check

You can take any tool surface and design: (a) the failure taxonomy (what classes of failure exist), (b) the dispatcher rules (which class routes where), (c) the promotion rules (when retry promotes to re-plan, when re-plan promotes to escalate). You can also identify which tools deserve a HITL approval gate by default.
