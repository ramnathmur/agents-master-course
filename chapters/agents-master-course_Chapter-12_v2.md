# Chapter 12 — Orchestrator + Sub-Agents: The Capstone  [v2]

**Trait focus:** Multi-agent architecture.
**Persona:** The Conductor (personas v2, §12).
**Voice opener:** *"Whom do you dispatch first, and why? Before any model call, you've already made five architectural decisions. Name them."*
**Prerequisites:** Chapters 1–11 complete.
**Code:** `code/chapter_12_orchestrator.py`.

> **Revision v1 → v2:** Branch C expanded with substantive reframing (R5); Reflection converted to capstone action checklist (R7).

---

## PHASE 1 — CALIBRATION

Open with the Voice sample, then:

> **Ask Ram:** "An orchestrator agent has 5 sub-agents available. A new task arrives. Before any model call is made, what 5 architectural decisions has the orchestrator's designer (you) already made?"

Expected five: (1) decomposition strategy, (2) sub-agent persona design, (3) routing, (4) failure handling, (5) **aggregation**. The fifth is the one most architects miss — it's where new bugs are born. Plus the meta-decision: when NOT to split.

## PHASE 2 — ADAPT

- **Branch A (shallow):** Walk through each of the 5 decisions with the cricket-captain analogy.
- **Branch B (strong):** Skip basics. Jump to SDK specifics: `agents={...}`, `AgentDefinition`, dispatch via Task tool, state across boundaries.
- **Branch C (reinforce `handoff_contract_semantics` from Ch 11):** "In Chapter 11 your weak signal was handoff contract semantics — defining 'done' as a checkable predicate. Orchestrator-to-sub-agent handoffs are the same contract problem, but FAN-IN — the orchestrator receives results from N sub-agents and must aggregate them. Aggregation contracts are the fifth decision you'll forget about. Same predicate discipline applies: each sub-agent's 'I'm done' must be checkable BY the orchestrator, not asserted BY the sub-agent."

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_12_orchestrator.py`. One orchestrator + three sub-agents (researcher/coder/reviewer) declared via `agents={...}` on `ClaudeAgentOptions`. Task: add a `slugify` utility with a pytest. Predict: in the orchestrator's transcript, where do you see the routing decision being made? Hint: not in your Python."

Trace the dispatch path: orchestrator emits Task-tool blocks → SDK runtime spawns fresh sub-agent context → result returns to orchestrator. The orchestrator never sees sub-agent internal turns.

Force a failure: edit the coder's system prompt to produce subtly wrong code. Watch reviewer → orchestrator → coder rework cycle. After 2 strikes, escalation.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Articulate, in writing, the persona of each of your three sub-agents. For each: (1) scope, (2) tools and why, (3) model tier and why, (4) failure response when the orchestrator gets a rejection on its output."

Look for: crisp persona definitions, justified tool scopes, model-tier reasoning (haiku for cheap reads, sonnet for generation/review), failure-response coherence.

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=subagent_persona_design`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:An orchestrator is a sub-agent designer first, a runtime dispatcher second. The persona of each sub-agent is the architecture. The orchestrator's system prompt is the conducting score.]`
> Generate your session brief: `python code/shared/session_brief.py --after 12`. Open the .html in your browser.
`[COURSE_COMPLETE]`

---

## Capstone Action Checklist

For any agent system you design from this point forward, answer in writing:

1. **Single agent or multi-agent?** What's the cost of splitting (context loss, coordination) vs the benefit (specialization, tier mixing, parallel work)?
2. **Goal predicate** — top-level + per-sub-agent. Each "done" is checkable, not felt.
3. **Tool surface per agent** — 4-question description (Ch 5), tight schema (Ch 6), permission posture (Ch 7).
4. **Iteration loop** — three exit conditions (Ch 4). Context strategy named.
5. **Verifier loop** — where, with what rubric, calibrated against what known-bad set (Ch 9).
6. **Failure dispatcher** — taxonomy + budgets + promotion + escalation (Ch 10).
7. **Persistent state** — what survives across runs? Schema versioned (Ch 11).
8. **For multi-agent only:** sub-agent personas, model tiers, routing contract, aggregation contract.
9. **Eval set** — minimum 5 cases, scored deterministically or via judge, regression-gated (Ch 8).

## Trait → Chapter Capstone Map (unchanged from v1, retained for reference)

| Trait / Pattern | Chapter |
|---|---|
| Goal | 2 |
| Composition | 3 |
| Iteration + context | 4 |
| Perception | 5 |
| Reasoning + tool design | 6 |
| Action + hooks | 7 |
| Five-trait integration + evals | 8 |
| Verifier / critic | 9 |
| Recovery / HITL | 10 |
| Memory + two-agent contract | 11 |
| Multi-agent orchestration | 12 |

## Exit Check — Course Complete

Take a novel task ("Build a tool that watches a directory and auto-formats new Python files"). Decide single-agent vs multi-agent. Walk the 9-item checklist above for your chosen design. Score it against an eval set you write yourself.

If you can do that unaided — you've completed the course. Welcome to architecting agents.
