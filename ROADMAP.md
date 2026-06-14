# Agents Master Course — Roadmap

**Goal:** Become independently capable of architecting Claude Agent SDK agents and multi-agent systems.
**Delivery:** Markdown chapters (you read with Claude Desktop as your tutor) + runnable Python files (you copy-paste into IntelliJ).
**Auth:** Claude Max via `claude login` (NO `ANTHROPIC_API_KEY` set).
**IDE:** IntelliJ IDEA with Python plugin.

---

## Phase 1 — Scaffolding ✅

- ✅ Folder structure created
- ✅ `agents-master-course_Index_v2.md` (v1 retained for audit)
- ✅ `personas/agents-master-course_Personas_v2.md` (v1 retained for audit)
- ✅ This roadmap

## Phase 2 — Foundations (Chapters 0–4) ✅

- ✅ Chapter 0: Setup — `claude login`, IntelliJ run config, smoke test
- ✅ Chapter 1: The Bare LLM Call
- ✅ Chapter 2: LLM Call + Goal
- ✅ Chapter 3: Chained Calls
- ✅ Chapter 4 (v2): Iteration + context (now demonstrates compaction in code)

## Phase 3 — The Perceive/Reason/Act Triad (Chapters 5–7) ✅

- ✅ Chapter 5 (v2): Perceive (joint to Ch 6 repaired)
- ✅ Chapter 6 (v2): Reason + Tool Design (tight schema actually validates)
- ✅ Chapter 7: Act under permission + hooks

## Phase 4 — Integration (Chapters 8–10) ✅

- ✅ Chapter 8 (v2): REAL TODO-fixing agent with all 5 traits + eval harness
- ✅ Chapter 9 (v2): Verifier / critic loop
- ✅ Chapter 10 (v2): Recovery + HITL (Dispatcher wired end-to-end)

## Phase 5 — Multi-Agent (Chapters 11–12) ✅

- ✅ Chapter 11 (v2): Two-Agent Systems + persistent memory
- ✅ Chapter 12 (v2): Orchestrator + Sub-Agents

## Phase 6 — Review and Revision ✅

- ✅ Multi-agent audit (3 dimensions + 3 sandbox sims) → `reviews/agents-master-course_Review_v1.md`
- ✅ 9 revisions applied → `CHANGELOG.md`

---

## Pacing

- One chapter per 60–90 min deep-work block (your 5–8 AM IST slot).
- Total course depth: ~16 hours real focus time across ~3 weeks.
- Do NOT compress the architect's reflection step — that's where the skill lands.

## Status Legend

✅ done · 🔄 in progress · ⬜ not started

## Exit Criteria

You can build, end to end, without referring back to the chapters:

1. A goal-pursuing iterative single agent with tools, guardrails, and evals.
2. A two-agent system with durable shared state and a defined handoff contract.
3. A multi-agent orchestrator with N typed sub-agents, failure handling, and result aggregation.
