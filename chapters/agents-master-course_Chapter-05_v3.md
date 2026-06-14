# Chapter 5 — Perceive: What the Agent Sees  [v3]

**Trait focus:** Perception isolated.
**Persona:** The Observer (personas v2, §5).
**Voice opener:** *"The agent doesn't see what's there — it sees what you described. Show me the description, and I'll predict the behavior."*
**Prerequisites:** Chapter 4 complete.
**Code:** `code/chapter_05_perceive.py`.

> **Revision v1 → v2:** Branch C expanded (R5); Exit Check now forecasts Ch 6's schema-vs-description distinction explicitly (R8 joint repair).
> **Revision v2 → v3:** dual-main demo enabled in code; brief generator integrated (Reviews E1, E6).

---

## PHASE 1 — CALIBRATION

Open with the Voice sample, then:

> **Ask Ram:** "Without writing any code yet — what's the difference between a tool that lets the agent *read* something versus a tool that lets it *act*?"

## PHASE 2 — ADAPT

- **Branch A (shallow):** Tools split into perception (read-only, reversible) vs effectors (state-changing, dangerous). Different permission boundaries.
- **Branch B (strong):** Architectural framing: perception is a contract. The tool *description* is the contract.
- **Branch C (reinforce `context_rot` from Ch 4):** "In Chapter 4 your weak signal was context rot — the loop's history dominated the model's attention. Read-only tools introduce a parallel risk: the description IS context the agent reads on every turn. Bad descriptions don't just confuse the agent once — they corrupt every subsequent decision. The same context-hygiene discipline applies."

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_05_perceive.py`. v3 ships two entry points: `main_sparse()` and `main_rich()`. Run both back-to-back."

Execute `main_sparse()` first, then `main_rich()` against the same task. Compare two things side-by-side:

1. **Turn count** — how many loop iterations before the agent commits to an answer.
2. **Tool-call count** — how many distinct invocations (and how many wasted/exploratory ones) before convergence.

Expected delta: sparse description → more turns, wider tool-call attempts, more clarifying questions, more failures. Rich description → focused tool use, fewer turns, near-zero exploratory calls. The numbers ARE the lesson — don't summarize, count.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "I give you a tool called `lookup`. No description. You're the agent. What do you do on your first turn?"

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=tool_description_ergonomics` for Chapter 6.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Perception is a contract. The tool description IS the agent's mental model. Bad descriptions produce reasoning failures upstream of any tool call.]`

> Generate your session brief: `python code/shared/session_brief.py --after 5`. Open the .html in your browser.

---

## Architect's Reflection (action checklist form)

For every read-only tool you define, the description must answer four questions in 1–3 sentences:

1. **What does this tool do?**
2. **What input shape does it expect?**
3. **What does it return?**
4. **When should I NOT use it?** (boundary against other tools)

Anti-pattern: descriptions that read like API docs ("Reads a file."). Pattern: descriptions that read like a coworker briefing a new hire.

## Exit Check + Forward Pointer to Chapter 6

You can write a `@tool` definition for three read-only tools — `search_web`, `read_database_row`, `get_calendar_events` — each with a 4-question description.

**Forward pointer (R8 joint repair):** Notice that you've been engineering the tool's *description* — the prose contract the model reads to decide *whether* to use the tool. In Chapter 6 you'll engineer the tool's *schema* — the structural contract the model fills in when it *does* use the tool. Description = vocabulary; schema = grammar. Both are required, and Chapter 6 is where the grammar half lands.
