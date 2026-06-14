# Chapter 5 — Perceive: What the Agent Sees

**Trait focus:** Perception isolated. Tools as sensors only — no action.
**Persona:** The Observer (see personas §5).
**Prerequisites:** Chapter 4 complete.
**Code:** `code/chapter_05_perceive.py`.

> **Tutor instruction.** Adopt The Observer. The chapter's core insight: the tool description string IS the agent's mental model of what it can see. Crap descriptions → crap perception.

---

## PHASE 1 — CALIBRATION

> **Ask Ram:** "Without writing any code yet — what's the difference between a tool that lets the agent *read* something versus a tool that lets it *act*?"

(Looking for: read-only vs side-effect-producing. Read tools are sensors; action tools are effectors. If Ram doesn't separate them cleanly, Branch A. If he does, push: "Why does isolating perception matter pedagogically AND architecturally?")

## PHASE 2 — ADAPT

- **Branch A (shallow):** Tools split into two roles by their side effects. Read tools (perception) are reversible — calling them twice is harmless. Action tools (effectors) change state — calling them twice is dangerous. Treat them differently. Permission boundaries respect this split.
- **Branch B (strong):** Architectural framing: perception is a *contract*. The tool description is the contract. The agent reasons about what it can see by reading descriptions, not by trying tools and observing. Bad descriptions produce reasoning failures upstream of any tool call.
- **Branch C (reinforce context_rot):** Confirm Ch 4 weak signal first — "How did your loop's context grow? What was your compaction plan?"

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_05_perceive.py` to IntelliJ. The script defines one read-only tool — `read_file(path)` — registered via `@tool` and `create_sdk_mcp_server`. Then a `ClaudeSDKClient` uses it. Predict: what does the agent's first message tool-call look like?"

(Expected: a `tool_use` block with `name="mcp__perception__read_file"` and `input={"path": "<some path>"}`. The MCP-server naming convention matters — `mcp__<server_name>__<tool_name>`. If Ram says just `read_file`, that's a tell — push on the namespacing.)

After running, do the **description rewrite exercise**:

Version A description: `"Read a file."` (sparse)
Version B description: `"Read the contents of a UTF-8 text file from the project directory. Returns the full text. Use only for files under 100KB; for larger files, use grep-style search first."` (rich)

Run the same task with both. Observe how Branch A descriptions produce: (a) more clarifying questions, (b) wider tool-call attempts, (c) more failures. Branch B descriptions produce focused tool use.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "I give you a tool called `lookup`. No description. You're the agent. What do you do on your first turn?"

(Expected: either refuse to use it because the contract is unclear, OR try it with a guessed input and fail. Both reveal the bug — a description-less tool forces the agent into exploration mode. That's wasteful at best, dangerous at worst. The architect's discipline: every tool has a 1–3 sentence description that names the input shape, the output shape, and the failure modes.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=tool_description_ergonomics` for Chapter 6.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Perception is a contract. The tool description IS the agent's mental model. Bad descriptions produce reasoning failures upstream of any tool call.]`

---

## Architect's Reflection

This chapter introduced the SDK's tool surface. Three things to internalize:

1. **`@tool` + `create_sdk_mcp_server` is the in-process pattern.** It registers a tool that lives inside your Python process. The model calls it via the MCP protocol. The naming gets prefixed: `mcp__<server>__<tool>`. Use `allowed_tools=["mcp__server__tool"]` to gate which the agent can invoke.

2. **Read-only tools are pedagogically isolated for a reason.** Once an agent can write or execute, you've crossed into action territory (Chapter 7) where guardrails matter. Perception alone is safe to teach with no `permission_mode` enforcement.

3. **Description engineering is real work.** Spend 5x more time on tool descriptions than feels reasonable. A 30-second tweak to a description often saves 5 minutes of debugging downstream reasoning. The description should answer four questions:
   - **What does this tool do?** (one sentence)
   - **What input shape does it expect?** (schema is the contract; the description complements it)
   - **What does it return?** (shape, not just type)
   - **When should I NOT use it?** (boundary against other tools)

Anti-pattern alert: descriptions that read like an API doc ("Reads a file."). Pattern: descriptions that read like a coworker explaining the tool to a new hire ("This reads UTF-8 text files. For binary or large files, prefer the `grep` tool first. Returns the full content as a string.").

## Exit Check

You can write a `@tool` definition (schema + description) for three different read-only tools — (1) `search_web`, (2) `read_database_row`, (3) `get_calendar_events`. For each, your description answers all four questions above. You can also predict how the agent's behavior degrades if you delete the "when NOT to use" clause from any of them.
