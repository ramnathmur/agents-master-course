# Agents Master Course — Index  [v3]

**For:** Ram (experienced AI practitioner, agent fundamentals already understood).
**Goal:** Architect agents using the Claude Agent SDK, block by block.
**Format:** AI-first. Each chapter Markdown is a script Claude Desktop runs *with* you, conversationally. `.py` files copy-paste into IntelliJ. After each session, run the brief generator for a cumulative HTML dashboard.

> **v2 → v3 revision pass complete.** See `CHANGELOG.md`. Headline changes (Enhancement v1, 10 enhancements):
> - Dual-`main()` demo pattern in Ch 5, 6, 10, 11 (E1)
> - Real Span trace schema with parent_id stack in Ch 8 (E2)
> - **New Chapter 13: Production Surfaces** — external MCP, HTTP tool with retry/backoff, prompt-injection defense (E3)
> - **New Chapter 12.5: Cold Build** — 30-min blank-file rehearsal (E4)
> - Native SDK session-resume contrast in Ch 11 (E5)
> - **HTML session-brief generator** wired into every chapter's WRAP (E6)
> - ReAct + plan-and-execute taxonomic labels (E7)
> - `critic_calibration.json` fixture (E8)
> - Memory-tier spec expansion in Ch 11 (E9)
> - Observe + Mutate hook examples wired in Ch 7 code (E10)

---

## How to use this course

1. Open the chapter Markdown (`_v3` where present, else `_v2` or `_v1`) in Claude Desktop.
2. Say: **"Run me through this chapter."** Claude adopts the persona from `personas/agents-master-course_Personas_v3.md` and runs the 5-phase loop.
3. Copy the chapter's `.py` to IntelliJ and run it. Predict the output first.
4. After `[COMPLETE]`, run: `python code/shared/session_brief.py --after <N>` and open the resulting HTML in your browser.

---

## Table of Contents (v3)

| Ch | Title | Persona | Chapter file | Code file |
|---|---|---|---|---|
| 0 | Setup | The Toolsmith | `chapters/agents-master-course_Chapter-00_v1.md` | `code/chapter_00_setup.py` |
| 1 | The Bare LLM Call | The Reductionist | `chapters/agents-master-course_Chapter-01_v1.md` | `code/chapter_01_bare_llm.py` |
| 2 | LLM Call + Goal | The Strategist | `chapters/agents-master-course_Chapter-02_v1.md` | `code/chapter_02_goal.py` |
| 3 | **Chained Calls** | The Composer | **`chapters/agents-master-course_Chapter-03_v2.md`** | `code/chapter_03_chained.py` |
| 4 | Iteration + Context | The Cybernetician | `chapters/agents-master-course_Chapter-04_v2.md` | `code/chapter_04_iteration.py` |
| 5 | **Perceive** | The Observer | **`chapters/agents-master-course_Chapter-05_v3.md`** | `code/chapter_05_perceive.py` *(v3)* |
| 6 | **Reason + Tool Design** | The Planner | **`chapters/agents-master-course_Chapter-06_v3.md`** | `code/chapter_06_reason.py` *(v3)* |
| 7 | **Act + Hooks** | The Operator | **`chapters/agents-master-course_Chapter-07_v2.md`** | `code/chapter_07_act.py` *(v2)* |
| 8 | **Integration + Evals + Tracing** | The Architect | **`chapters/agents-master-course_Chapter-08_v3.md`** | `code/chapter_08_integration.py` *(v3)* |
| 9 | Verifier / Critic | The Reviewer | `chapters/agents-master-course_Chapter-09_v2.md` | `code/chapter_09_verifier.py` |
| 10 | **Recovery + HITL (3 scenarios)** | The Incident Commander | **`chapters/agents-master-course_Chapter-10_v3.md`** | `code/chapter_10_recovery.py` *(v3)* |
| 11 | **Two-Agent + Memory + Native Resume** | The Diplomat | **`chapters/agents-master-course_Chapter-11_v3.md`** | `code/chapter_11_two_agent.py` *(v3)* + `code/chapter_11_native_resume.py` *(new)* |
| 12 | Orchestrator + Sub-Agents | The Conductor | `chapters/agents-master-course_Chapter-12_v2.md` | `code/chapter_12_orchestrator.py` |
| **12.5** | **Cold Build (NEW)** | The Architect (reprise) | **`chapters/agents-master-course_Chapter-12-5_v1.md`** | *(no .py — you write it)* |
| **13** | **Production Surfaces (NEW)** | **The Engineer** | **`chapters/agents-master-course_Chapter-13_v1.md`** | **`code/chapter_13_production.py`** *(new)* |

Personas: `personas/agents-master-course_Personas_v3.md` (replaces v2; adds The Engineer §13).

---

## Shared modules

```
code/shared/
├── goal_predicates.py            (unchanged)
├── eval_harness.py               (v2 — Case + TrajectoryCase + LLMJudgeCase)
├── state_store.py                (unchanged — public reset_state)
├── critic_calibration.json       (NEW — 5 good + 5 bad fixtures for Ch 9)
└── session_brief.py              (NEW — cumulative HTML brief generator)
```

---

## Generating session briefs

```bash
# After completing Chapter N
python code/shared/session_brief.py --after <N>

# Regenerate all briefs (Ch 0–13)
python code/shared/session_brief.py --all
```

Briefs land at `session-briefs/agents-master-course_Brief_after-Chapter-NN_v1.html`. Cumulative: Brief at Ch N covers Chapters 0..N. Single self-contained HTML file, opens offline.

---

## Conventions (unchanged from v2)

- **Markers:** `[SCORE:0.XX]`, `[COMPLETE]`, `[INSIGHT:...]`.
- **Code idioms:** all async, wrapped with `anyio.run(main)`. Self-contained per chapter.
- **Auth:** Chapter 0 must pass before any other chapter. `claude login` → smoke test. `ANTHROPIC_API_KEY` must NOT be set in the IntelliJ run config.
- **Architect's Reflection (v2/v3 form):** action checklists, not essays. Designed to fail the Removal Test correctly.
- **v1 / v2 files retained on disk for audit trail** — use the v3 pointers above for the active course.
