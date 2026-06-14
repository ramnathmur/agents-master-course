# Chapter 7 — Act Under Permission: Hooks and Guardrails

> **v1 to v2:** Observe and Mutate hook examples wired in code; brief integration (Reviews E10, E6).

**Trait focus:** Action isolated. Inline `permission_mode` + `PreToolUse` / `PostToolUse` hooks.
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
- **Branch C (reinforce schema_as_grammar from Ch 6):** Confirm the takeaway first.

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_07_act.py` to IntelliJ. It defines a `write_file` tool and wires THREE hooks: `sandbox_guard` (PreToolUse, Guard role) denies writes outside `./sandbox/`; `normalize_path_mutate` (PreToolUse, Mutate role) rewrites `~` and backslashes before the guard sees the path; `audit_observer` (PostToolUse, Observe role) appends every call to an in-memory `_audit_trail`. Predict: when the hook denies, what does the agent see — and what does the audit trail look like at the end?"

(Expected: the agent receives a `tool_result` block with the deny reason — "outside sandbox." The audit trail records BOTH successful and denied calls. Run `main()` and inspect the `_audit_trail` printed at the end — every Pre/Post event is there, in order. The hook deny is not silent; it's information. The audit trail is your evidence.)

Run the script with two tasks:
- "Write 'hello' to `./sandbox/greeting.txt`" → mutate normalizes the path, guard allows, observer logs success.
- "Write 'hello' to `C:/Windows/system32/important.txt`" → mutate is a no-op, guard denies, observer logs the denial.

Inspect `_audit_trail` at the end. Confirm Mutate ran before Guard, and Observer ran after both outcomes.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Your hook denies the write. The agent retries the same write at the same path. Now what — architecturally?"

(Expected: this is a sign your deny reason is unclear to the model, OR the agent isn't reasoning about the deny as a structural failure. Two responses: (a) make the deny reason more explicit ("Path is outside the allowed sandbox `./sandbox/`. Choose a path inside it."), (b) cap retries on the same tool with the same input — a per-call retry budget enforced inside the Guard hook, with the counter recorded by the Observer. Loop-on-deny is a real production failure mode.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=hook_recovery_design`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Hooks are the architect's leverage point. Cross-cutting policy lives in hooks; tool-specific correctness lives in tools. The deny reason is not a refusal — it's a teaching signal to the model.]`

> Generate your session brief: `python code/shared/session_brief.py --after 7`.

---

## Architect's Reflection

You've now built every primitive a real agent needs: a goal, a loop, perception, reasoning, action, and guardrails. Work through this checklist before Chapter 8:

1. **Map the hook taxonomy onto your code.** Three roles, all now live in `chapter_07_act.py`:
   - **Guard** — `sandbox_guard` (PreToolUse). Prevent bad actions before they happen. `permission_mode="default"` is the coarse layer; the Guard hook is the surgical one.
   - **Observe** — `audit_observer` (PostToolUse). Record what happened. The `_audit_trail` list is your audit log, telemetry feed, and eval trace seed. In production, this writes to a sink, not a list.
   - **Mutate** — `normalize_path_mutate` (PreToolUse). Modify input before the tool runs. Path normalization is the canonical safe case. Use sparingly — invisible mutation surprises future-you. Document every Mutate hook with a comment explaining *why* the rewrite is safe.

2. **Treat `permission_mode` as posture, hooks as policy.** `permission_mode` is your overall trust level. Hooks are your specific rules. In production, you want low trust + specific allow-lists. In dev, you want high trust + watchful Observers (like `audit_observer`). Don't confuse the two layers.

3. **Treat deny as a teaching signal.** A denied tool call is not a failure — it's structured information the model can reason about. Write your deny reasons (in `sandbox_guard`) like you'd write a help-desk ticket response: explain what was wrong, suggest what to try instead. The model will use it.

4. **Audit before you alert.** Until `audit_observer` is wired and you can read the trail, you have no ground truth for what your agent actually did. Build the Observer first; design the alerts second.

Anti-pattern: silent denies. Returning a generic "permission denied" forces the model into guess-and-retry mode. That's how you get loop-on-deny failures.

## Exit Check

You can take a write-capable tool (file write, API POST, database INSERT) and design: (a) the `permission_mode` posture, (b) a Guard `PreToolUse` hook that enforces a domain-appropriate boundary, (c) an Observe `PostToolUse` hook that captures the audit trail, (d) any Mutate hooks needed for input normalization, and (e) the deny reason format that helps the agent recover. You can also explain when to use a hook vs encoding the same rule in the tool implementation.
