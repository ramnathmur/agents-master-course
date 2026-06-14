# Chapter 4 — Iteration Until Goal Achieved + Context Engineering  [v2]

**Trait focus:** Iteration / autonomy. Inline context engineering.
**Persona:** The Cybernetician (personas v2, §4).
**Voice opener:** *"The loop is the spine. Now show me the three places it can die — and the disease that creeps in even when it doesn't."*
**Prerequisites:** Chapters 2 (goal) and 3 (composition) complete.
**Code:** `code/chapter_04_iteration.py` (v2 — now has `main_unbounded()` AND `main_with_compaction()`).

> **Revision v1 → v2:** code now demonstrates compaction, not just discusses it. Phase 3 runs BOTH baseline and compacted versions side by side.

---

## PHASE 1 — CALIBRATION

Open with the Voice sample, then:

> **Ask Ram:** "You have a goal predicate from Ch 2. You have chained calls from Ch 3. What's the minimum change that turns this into something you'd call an agent?"

## PHASE 2 — ADAPT

- **Branch A (shallow):** Walk through the loop architecture and the three exit conditions (goal met / turn cap / token cap). All three required.
- **Branch B (strong):** Skip mechanics. Jump to "What does the model see on iteration N? Where does the failure signal go?" Then context engineering.
- **Branch C (reinforce `control_plane_ownership` from Ch 3):** "In Chapter 3 your weak signal was naming where Python owns the control plane. In this chapter, Claude takes control via the loop. Notice the shift — the `while` predicate is now a function of the model's output. The baton has changed hands."

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_04_iteration.py` to IntelliJ. Two functions this time: `main_unbounded()` (the baseline) and `main_with_compaction(window_turns=2)`. Predict the token-count column for each before running."

(Expected: baseline grows roughly linearly per iteration; compacted stays bounded at the window size.)

Run both. Compare the `cum_tokens(est)` column to `window_tokens(est)`. **That's the chapter's measurable insight: context rot becomes a number, not a vibe.**

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Your unbounded loop runs 8 iterations. The conversation history is now 8 user/assistant pairs. Two architectural problems are about to bite. Name them. (Bonus: a third.)"

Expected: context rot, O(N²) token cost, reasoning fixation.

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=context_rot` for Chapter 5.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Iteration adds the spine of agency. Context rot is its disease. The architect chooses the compaction strategy before the loop is long enough to fail.]`
> Generate your session brief: `python code/shared/session_brief.py --after 4`. Open the .html in your browser.

---

## Architect's Reflection (action checklist form)

Before you ship any iterative agent, answer these in writing:

1. **Exit conditions** — have I named all three (goal / turn cap / token cap)? Which exits first in the common case?
2. **Failure-feedback shape** — raw error, structured critique, or replan instruction? Which fits this task?
3. **Context strategy** — sliding window, summarization, or scratchpad? Cost vs goal-memory tradeoff?

The architect's anti-pattern: choosing none of the three context strategies. That's the default for tutorial code and the default that fails first in production.

## Exit Check

You can take any iterative task and architect (a) the goal predicate, (b) the three exit conditions, (c) the failure-feedback shape, (d) the context strategy. You can also explain why `main_with_compaction()` uses bounded tokens but loses goal memory over long runs — and when that tradeoff is acceptable.
