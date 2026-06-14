# Chapter 4 — Iteration Until Goal Achieved + Context Engineering

**Trait focus:** Iteration / autonomy. Plus inline context engineering (gap #2 from research).
**Persona:** The Cybernetician (see personas §4).
**Prerequisites:** Chapters 2 (goal) and 3 (composition) complete.
**Code:** `code/chapter_04_iteration.py`.

> **Tutor instruction.** Adopt The Cybernetician. This is where Ram crosses from workflow into agent. Make the loop architecture explicit. Don't let him skip the context-rot section — it's the first real failure mode he'll hit.

---

## PHASE 1 — CALIBRATION

> **Ask Ram:** "You have a goal predicate from Ch 2. You have chained calls from Ch 3. What's the minimum change that turns this into something you'd call an agent?"

(Looking for: a loop that re-prompts on goal-miss, with model-decided next-step. If Ram says "a while loop" — push: "what does the loop body look like, and what does the model see on iteration 3 vs iteration 1?")

## PHASE 2 — ADAPT

- **Branch A (shallow):** Walk through the loop architecture step by step. Show the three exit conditions: goal met / turn cap / token cap. Explain why all three are required (no exit = infinite loop or runaway cost).
- **Branch B (strong):** Skip the loop mechanics. Jump straight to: "What does the model see on iteration N? Where does the failure signal go?" Then context engineering: compaction, scratchpads, sub-context isolation.
- **Branch C (reinforce control_plane_ownership):** Confirm — "In Chapter 3 your weak signal was naming where Python owns the control plane. In this chapter, Claude takes control via the loop. Notice the shift."

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_04_iteration.py` to IntelliJ. Read it before running. Predict: under what task input will this loop hit the turn cap without reaching the goal?"

(Expected: a task where the goal predicate is too strict, or the model can't see the structure it needs to satisfy the predicate. This is the "predicate too strict" failure mode — separate from the "model too weak" mode.)

The script uses `ClaudeSDKClient` (stateful), runs a while loop, checks a predicate, appends failure context on miss, and exits on goal/turn-cap/token-cap.

After Ram runs it, force a deliberate failure:
- Make the goal predicate require a 7-word output.
- Watch the loop iterate, re-prompt with the word count failure, and converge.
- Then log the token count per iteration. Watch it grow.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "You ran the loop for 8 iterations. The conversation history is now 8 user/assistant pairs. Two architectural problems are about to bite. Name them."

(Expected:
1. **Context rot** — by iteration 5+, the failure history dominates the context. The model sees more failure than goal. Compaction or summarization is required.
2. **Token cost** — the iteration is `O(N²)` in tokens because each iteration replays all prior turns. Without truncation, cost grows fast.

Bonus: a third one — **reasoning fixation** — the model anchors on its earlier wrong answers and can't shake them. Sometimes worth blowing away history and starting fresh with a critique-and-restart strategy.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=context_rot` for Chapter 5.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Iteration adds the spine of agency. Context rot is its disease. The architect chooses the compaction strategy before the loop is long enough to fail.]`

---

## Architect's Reflection

You've now built the smallest real agent. Three architectural decisions you made (deliberately or not) deserve a name:

1. **Exit condition design.** Three are non-negotiable: goal met, turn cap, token cap. A loop without all three is a production incident waiting to happen. The Claude Agent SDK has `max_turns` on `ClaudeAgentOptions` for this reason. Token caps you usually enforce yourself.

2. **Failure-feedback shape.** When the goal predicate fails on iteration N, what do you feed back to the model for iteration N+1? Three styles:
   - **Raw error** — pass the predicate's failure message verbatim. Cheap. Often unclear to the model.
   - **Structured critique** — wrap the failure in a labeled block: `<failure reason="word_count_off" got="9" expected="7"/>`. Higher signal-to-noise.
   - **Replan instruction** — "Your previous attempt failed. Re-plan from scratch, considering: [critique]." Use this when the model is anchored on a wrong direction.

3. **Context engineering.** Three options as the context grows:
   - **Sliding window** — keep last K turns. Loses goal memory. Cheap.
   - **Summarization** — compress old turns into a running summary. Preserves goal memory. Costs an extra call per compaction.
   - **Scratchpad** — model writes intermediate state to a tool-managed scratchpad, freeing the conversation. Highest leverage; more setup.

There's no universally right choice. The architect picks based on task length, goal stability, and cost budget. What's wrong is choosing none — that's the default for most tutorial code and the default that fails first in production.

## Exit Check

You can take any iterative task (e.g., "write a poem until it has exactly 50 syllables") and architect: (a) the goal predicate, (b) the three exit conditions, (c) the failure-feedback shape, (d) the context strategy. You can also predict when each design will fail and why.
