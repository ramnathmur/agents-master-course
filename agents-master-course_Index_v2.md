# Agents Master Course — Index  [v2]

**For:** Ram (experienced AI practitioner, agent fundamentals already understood).
**Goal:** Architect agents using the Claude Agent SDK, block by block.
**Format:** AI-first. Each chapter is a Markdown script Claude Desktop runs *with* you, conversationally. The `.py` file beside each chapter is what you copy-paste into IntelliJ.

> **v1 → v2 revision pass complete.** See `CHANGELOG.md` for the full diff. Headline changes: Chapter 8 is now a REAL TODO-fixing agent (R1), Chapter 10's dispatcher is wired end-to-end (R2), Chapter 4 demonstrates compaction with token counts (R3), persona voices are differentiated on paper (R6), 6 chapters' Branch C reinforcements are now substantive (R5).

---

## How to use this course

1. Open the chapter Markdown (`_v2`) in Claude Desktop.
2. Say: **"Run me through this chapter."** Claude reads the chapter, adopts the chapter's persona (from `personas/agents-master-course_Personas_v2.md`), and runs you through the 5-phase teaching loop.
3. When the chapter says **"Copy this into IntelliJ"**, copy the corresponding `.py` from `code/` and run it.
4. Report back what happened. Claude adapts.
5. The chapter ends when Claude emits `[COMPLETE]` and a carry-forward insight.

The **Removal Test** still applies: each chapter is designed to collapse without the AI conversation. Reading alone gives you ~40% of the value; the dialog gives you the rest.

---

## The 5-phase teaching loop (unchanged from v1)

| Phase | What happens |
|---|---|
| 1. CALIBRATION | Persona's Voice opener + Socratic question. Claude waits. |
| 2. ADAPT | Branch A (shallow) → first principles. Branch B (strong) → nuance. Branch C (reinforce) → re-frames the prior chapter's weakSignal in this chapter's vocabulary. |
| 3. CODE | Copy `.py` to IntelliJ. Predict output FIRST. |
| 4. ASSESSMENT | One mechanical question. `[SCORE:0.XX]`. |
| 5. WRAP | `[COMPLETE]` + `[INSIGHT:...]` carry-forward. |

---

## Table of Contents (v2)

| Ch | Title | Trait focus | Persona | Chapter file | Code file |
|---|---|---|---|---|---|
| 0 | Setup | (plumbing) | The Toolsmith | `chapters/agents-master-course_Chapter-00_v1.md` | `code/chapter_00_setup.py` |
| 1 | The Bare LLM Call | (anchor) | The Reductionist | `chapters/agents-master-course_Chapter-01_v1.md` | `code/chapter_01_bare_llm.py` |
| 2 | LLM Call + Goal | Goal | The Strategist | `chapters/agents-master-course_Chapter-02_v1.md` | `code/chapter_02_goal.py` |
| 3 | Chained Calls | Composition | The Composer | `chapters/agents-master-course_Chapter-03_v1.md` | `code/chapter_03_chained.py` |
| 4 | **Iteration + Context** | Iteration | The Cybernetician | **`chapters/agents-master-course_Chapter-04_v2.md`** | `code/chapter_04_iteration.py` *(v2)* |
| 5 | **Perceive** | Perception | The Observer | **`chapters/agents-master-course_Chapter-05_v2.md`** | `code/chapter_05_perceive.py` |
| 6 | **Reason + Tool Design** | Reasoning | The Planner | **`chapters/agents-master-course_Chapter-06_v2.md`** | `code/chapter_06_reason.py` *(v2)* |
| 7 | Act Under Permission | Action | The Operator | `chapters/agents-master-course_Chapter-07_v1.md` | `code/chapter_07_act.py` |
| 8 | **Integration + Evals** | All 5 | The Architect | **`chapters/agents-master-course_Chapter-08_v2.md`** | `code/chapter_08_integration.py` *(v2)* |
| 9 | **Verifier / Critic** | All 5 + verify | The Reviewer | **`chapters/agents-master-course_Chapter-09_v2.md`** | `code/chapter_09_verifier.py` |
| 10 | **Recovery + HITL** | Goal under failure | The Incident Commander | **`chapters/agents-master-course_Chapter-10_v2.md`** | `code/chapter_10_recovery.py` *(v2)* |
| 11 | **Two-Agent + Memory** | Agent-to-agent | The Diplomat | **`chapters/agents-master-course_Chapter-11_v2.md`** | `code/chapter_11_two_agent.py` |
| 12 | **Orchestrator** | Multi-agent | The Conductor | **`chapters/agents-master-course_Chapter-12_v2.md`** | `code/chapter_12_orchestrator.py` |

Personas: `personas/agents-master-course_Personas_v2.md` (replaces v1).

---

## File Stack (v2)

```
agents master course/
├── ROADMAP.md
├── agents-master-course_Index_v2.md                      ← this file (v2 supersedes v1)
├── CHANGELOG.md                                          ← v1 → v2 diff
├── personas/
│   ├── agents-master-course_Personas_v1.md               (retained for audit)
│   └── agents-master-course_Personas_v2.md               ← active
├── chapters/
│   ├── agents-master-course_Chapter-00_v1.md             (unchanged)
│   ├── agents-master-course_Chapter-01_v1.md             (unchanged)
│   ├── agents-master-course_Chapter-02_v1.md             (unchanged)
│   ├── agents-master-course_Chapter-03_v1.md             (unchanged)
│   ├── agents-master-course_Chapter-04_v1.md → _v2.md    (revised)
│   ├── agents-master-course_Chapter-05_v1.md → _v2.md    (revised)
│   ├── agents-master-course_Chapter-06_v1.md → _v2.md    (revised)
│   ├── agents-master-course_Chapter-07_v1.md             (unchanged)
│   ├── agents-master-course_Chapter-08_v1.md → _v2.md    (revised, biggest)
│   ├── agents-master-course_Chapter-09_v1.md → _v2.md    (revised)
│   ├── agents-master-course_Chapter-10_v1.md → _v2.md    (revised)
│   ├── agents-master-course_Chapter-11_v1.md → _v2.md    (revised)
│   └── agents-master-course_Chapter-12_v1.md → _v2.md    (revised, capstone)
├── code/
│   ├── chapter_00_setup.py                               (unchanged)
│   ├── chapter_01_bare_llm.py                            (unchanged)
│   ├── chapter_02_goal.py                                (unchanged)
│   ├── chapter_03_chained.py                             (unchanged)
│   ├── chapter_04_iteration.py                           (v2 — adds main_with_compaction)
│   ├── chapter_05_perceive.py                            (unchanged)
│   ├── chapter_06_reason.py                              (v2 — tight schema validates inner shape)
│   ├── chapter_07_act.py                                 (unchanged)
│   ├── chapter_08_integration.py                         (v2 — real TODO-fixer with all 5 traits)
│   ├── chapter_09_verifier.py                            (unchanged)
│   ├── chapter_10_recovery.py                            (v2 — Dispatcher class wired end-to-end)
│   ├── chapter_11_two_agent.py                           (unchanged)
│   ├── chapter_12_orchestrator.py                        (unchanged)
│   └── shared/
│       ├── goal_predicates.py                            (unchanged)
│       ├── eval_harness.py                               (v2 — adds TrajectoryCase + LLMJudgeCase)
│       └── state_store.py                                (unchanged)
└── reviews/
    └── agents-master-course_Review_v1.md                 ← the audit that drove the v2 revisions
```

---

## Conventions (unchanged)

- **Markers:** `[SCORE:0.XX]`, `[COMPLETE]`, `[INSIGHT:...]`.
- **Code idioms:** all async, wrapped with `anyio.run(main)`. Self-contained per chapter.
- **Auth:** Chapter 0 must pass before any other chapter. `claude login` → smoke test. `ANTHROPIC_API_KEY` must NOT be set in the IntelliJ run config.
- **Architect's Reflection (v2 form):** action checklists, not essays. Designed to fail the Removal Test correctly.
