# Chapter 7 — Act Under Permission: Hooks and Guardrails

**Trait focus:** Action isolated. Inline `permission_mode` + `PreToolUse` hooks.
**Persona:** The Operator (see personas §7).
**Prerequisites:** Chapters 5–6 complete.
**Code:** `code/chapter_07_act.py`.

> **Tutor instruction.** Adopt The Operator. The chapter's core insight: hooks are the architect's leverage point — the seam between "agent" and "deployable agent."

---

## PHASE 1 — CALIBRATION

> **Ask Ram:** "Claude wants to call `write_file(path='/etc/hosts', content='...')`. Three places you can intercept this. Name them."

(Looking for: (1) the tool's own implementation (refuses internally), (2) `permission_mode` user-prompt gating, (3) `PreToolUse` hook with structured deny. If Ram names only (1), Branch A. If he names all three, Branch B.)

## PHASE 2 — ADAPT

- **Branch A (shallow):** Three layers of action defense:
  - **Tool implementation** — the deepest. The tool itself refuses bad inputs. Fragile because it lives in N tools.
  - **`permission_mode`** — top-level posture. `"default"` requires user approval; `"acceptEdits"` auto-approves edits; `"bypassPermissions"` waves everything through. Coarse.
  - **`PreToolUse` hook** — programmatic gate that runs BEFORE the tool. Inspects tool name + input. Returns `deny` with a reason. Fine-grained.
- **Branch B (strong):** Skip to the design question: "When do you put logic in the hook vs in the tool's implementation?" (Answer: hooks for cross-cutting policy — sandboxing, audit, rate limiting; tool internals for tool-specific correctness.)
- **Branch C (reinforce schema_as_grammar):** Confirm Ch 6 takeaway first.

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_07_act.py` to IntelliJ. It defines a `write_file` tool that writes anywhere on disk. Then it adds a `PreToolUse` hook that denies writes outside `./sandbox/`. Predict: what does the agent see when the hook denies?"

(Expected: the agent receives a `tool_result` block with the deny reason — "outside sandbox." It then has to decide what to do — retry inside the sandbox, ask the user, or give up. Watch this exchange in the transcript. The hook deny is not silent; it's information.)

Run the script with two tasks:
- "Write 'hello' to `./sandbox/greeting.txt`" → succeeds.
- "Write 'hello' to `C:/Windows/system32/important.txt`" → hook denies.

Observe the agent's recovery in the second case.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Your hook denies the write. The agent retries the same write at the same path. Now what — architecturally?"

(Expected: this is a sign your deny reason is unclear to the model, OR the agent isn't reasoning about the deny as a structural failure. Two responses: (a) make the deny reason more explicit ("Path is outside the allowed sandbox `./sandbox/`. Choose a path inside it."), (b) cap retries on the same tool with the same input — a per-call retry budget in the hook. Loop-on-deny is a real production failure mode.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=hook_recovery_design`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Hooks are the architect's leverage point. Cross-cutting policy lives in hooks; tool-specific correctness lives in tools. The deny reason is not a refusal — it's a teaching signal to the model.]`

---

## Architect's Reflection

You've now built every primitive a real agent needs: a goal, a loop, perception, reasoning, action, and guardrails. Three patterns to take into Chapter 8:

1. **Hook taxonomy.** Three roles for hooks:
   - **Guard** — prevent bad actions before they happen. `permission_mode="default"` + `PreToolUse` deny.
   - **Observe** — record what happened. `PostToolUse` logging. Audit trails, telemetry, eval traces.
   - **Mutate** — modify input or output before/after the tool runs. Useful for normalization (trim whitespace, expand paths). Use sparingly — invisible mutation surprises future-you.

2. **`permission_mode` as posture, hooks as policy.** `permission_mode` is your overall trust level. Hooks are your specific rules. In production, you want low trust + specific allow-lists. In dev, you want high trust + watchful hooks. Don't confuse the two layers.

3. **Deny-as-teaching-signal.** A denied tool call is not a failure — it's structured information the model can reason about. Write your deny reasons like you'd write a help-desk ticket response: explain what was wrong, suggest what to try instead. The model will use it.

Anti-pattern: silent denies. Returning a generic "permission denied" forces the model into guess-and-retry mode. That's how you get loop-on-deny failures.

## Exit Check

You can take a write-capable tool (file write, API POST, database INSERT) and design: (a) the `permission_mode` posture, (b) a `PreToolUse` hook that enforces a domain-appropriate boundary, (c) the deny reason format that helps the agent recover. You can also explain when to use a hook vs encoding the same rule in the tool implementation.
