# Chapter 0 — Setup: Claude Max + SDK + IntelliJ

**Trait focus:** None. Plumbing only.
**Persona:** The Toolsmith (see `personas/agents-master-course_Personas_v1.md` §0).
**Prerequisites:** Claude Max subscription, IntelliJ IDEA with Python plugin, Python 3.10+.
**Code:** `code/chapter_00_setup.py`.

> **Tutor instruction.** Claude Desktop, adopt The Toolsmith persona from the personas file. Run the 5-phase loop. This chapter is plumbing — keep it short.

---

## PHASE 1 — CALIBRATION

> **Ask Ram:** "Before installing anything — what's the single configuration mistake that would silently bill the Anthropic API instead of using your Max plan?"

(Expected answer: `ANTHROPIC_API_KEY` is set in the environment or the IntelliJ run config. The SDK uses it in preference to the Claude Code CLI session. If Ram nails this, jump to Phase 3.)

## PHASE 2 — ADAPT

- **Branch A (shallow):** Explain that `claude-agent-sdk` auths via two paths — `ANTHROPIC_API_KEY` env var OR the Claude Code CLI's stored OAuth session. The env var wins if both are present. For Max users this is a footgun.
- **Branch B (strong):** Skip to Phase 3.
- **Branch C (reinforce):** N/A (first chapter).

## PHASE 3 — CODE

Walk Ram through these four steps. Do not move on until each is green.

**Step 1 — Install the SDK and the CLI it bundles:**
```bash
pip install claude-agent-sdk
```

**Step 2 — Authenticate the CLI with your Max account (one time):**
```bash
claude login
```
Opens a browser. Sign in with your Claude Max account. Close browser when done.

**Step 3 — Open IntelliJ, set up the run config for `chapter_00_setup.py`:**
- Run → Edit Configurations → Python → `chapter_00_setup`
- Environment Variables → confirm `ANTHROPIC_API_KEY` is NOT in the list. If it is, delete it.
- Working directory: `C:\Claude Cowork\CLAUDE OUTPUTS\agents master course\code`

**Step 4 — Predict:** before running, what should `chapter_00_setup.py` print?

(Expected prediction: a single message containing the word "ready". If Ram predicts a long response or an error, that's a tell — push back.)

Now run it.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "If `ANTHROPIC_API_KEY` had been set to a valid API key in your run config, would the script have failed? What would have happened instead?"

(Expected answer: NO failure. The script would have run *successfully* but billed against the API, not the Max plan. This is why the gotcha is dangerous — it's silent.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=auth_precedence` for Chapter 1's Branch C.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:The SDK shells to the CLI. Configuration precedence is silent. Verify your env, not your assumption.]`
> Generate your session brief: `python code/shared/session_brief.py --after 0`. Open the .html in your browser.

---

## Architect's Reflection

Three things to internalize from this chapter:

1. **The SDK is a CLI wrapper.** `claude-agent-sdk` is not a fresh HTTP client. It shells to the `claude` CLI binary that `pip install` brought along. That CLI owns the OAuth session. Your Python code never sees an API key on the Max path.
2. **Auth precedence is silent, not loud.** If `ANTHROPIC_API_KEY` is set, the SDK uses it without a warning. There is no "you have two auth sources, which one?" prompt. The architect's discipline: explicit `unset` or empty value in every run config you create.
3. **Smoke test before architecture.** Chapter 0 exists to prove the auth path works end to end on your machine. Every chapter from 1–12 assumes Chapter 0 is green. If you skip this and Chapter 4 fails, you won't know if the bug is your loop or your auth.

## Exit Check

You can run `chapter_00_setup.py` from IntelliJ, see the word "ready" printed, and articulate exactly why this used your Max plan and not the API.
