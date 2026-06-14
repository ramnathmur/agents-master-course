# Agents Master Course — Index

**For:** Ram (experienced AI practitioner, agent fundamentals already understood).
**Goal:** Architect agents using the Claude Agent SDK, block by block.
**Format:** This is an AI-first course. Each chapter is a Markdown script that Claude Desktop runs *with* you, conversationally. The `.py` file beside each chapter is what you copy-paste into IntelliJ and execute.

---

## How to use this course

1. Open the chapter Markdown in Claude Desktop.
2. Say: **"Run me through this chapter."** Claude reads the chapter, adopts the chapter's persona (from `personas/agents-master-course_Personas_v1.md`), and runs you through the 5-phase teaching loop.
3. When the chapter says **"Copy this into IntelliJ"**, copy the corresponding `.py` from `code/` and run it.
4. Report back what happened. Claude adapts based on your response.
5. The chapter ends when Claude emits `[COMPLETE]` and a one-line carry-forward insight.

You can also read chapters statically — but per the **Removal Test**, the chapter is designed to collapse without the AI conversation. Reading alone gives you ~40% of the value. The other 60% comes from the dialog.

---

## The 5-phase teaching loop

Every chapter follows this loop. Claude is the loop. The Markdown encodes the script.

| Phase | What happens |
|---|---|
| 1. CALIBRATION | One Socratic, mechanism-probing question. Short. Claude waits. |
| 2. ADAPT | Branch A (shallow) → first principles. Branch B (strong) → nuance. Branch C (reinforce) → fix the weak signal from a prior chapter. |
| 3. CODE | You copy the chapter's `.py` to IntelliJ. Run it. Predict the output FIRST. |
| 4. ASSESSMENT | One mechanical question. Claude scores `[SCORE:0.XX]`. |
| 5. WRAP | `[COMPLETE]` + one carry-forward insight that seeds the next chapter. |

---

## The 5 agent traits this course teaches

| Trait | Isolated in | Composed in |
|---|---|---|
| Goal-orientation | Ch 2 | Ch 4, 8, 9, 10 |
| Perception | Ch 5 | Ch 8, 9 |
| Reasoning | Ch 6 | Ch 8, 9 |
| Action | Ch 7 | Ch 8, 9, 10 |
| Iteration / Autonomy | Ch 4 | Ch 8, 9, 10, 11, 12 |

Multi-agent architecture (Ch 11, 12) is treated as a separate axis above the trait grid.

---

## Table of Contents

| Ch | Title | Trait focus | Persona | File |
|---|---|---|---|---|
| 0 | Setup — Claude Max + SDK + IntelliJ | (plumbing) | The Toolsmith | `chapters/agents-master-course_Chapter-00_v1.md` |
| 1 | The Bare LLM Call | (anchor — none) | The Reductionist | `chapters/agents-master-course_Chapter-01_v1.md` |
| 2 | LLM Call + Goal | Goal | The Strategist | `chapters/agents-master-course_Chapter-02_v1.md` |
| 3 | Chained Calls | Composition | The Composer | `chapters/agents-master-course_Chapter-03_v1.md` |
| 4 | Iteration Until Goal Achieved | Iteration + context | The Cybernetician | `chapters/agents-master-course_Chapter-04_v1.md` |
| 5 | Perceive | Perception | The Observer | `chapters/agents-master-course_Chapter-05_v1.md` |
| 6 | Reason + Tool Design | Reasoning + tools | The Planner | `chapters/agents-master-course_Chapter-06_v1.md` |
| 7 | Act Under Permission | Action + guardrails | The Operator | `chapters/agents-master-course_Chapter-07_v1.md` |
| 8 | Five Traits Together + Evals | All 5 + evals | The Architect | `chapters/agents-master-course_Chapter-08_v1.md` |
| 9 | Verifier / Critic Loop | All 5 + verification | The Reviewer | `chapters/agents-master-course_Chapter-09_v1.md` |
| 10 | Recovery + HITL | Goal under failure | The Incident Commander | `chapters/agents-master-course_Chapter-10_v1.md` |
| 11 | Two-Agent Systems + Memory | Agent-to-agent | The Diplomat | `chapters/agents-master-course_Chapter-11_v1.md` |
| 12 | Orchestrator + Sub-Agents | Multi-agent | The Conductor | `chapters/agents-master-course_Chapter-12_v1.md` |

---

## File Stack

```
agents master course/
├── ROADMAP.md                                           ← phased build status
├── agents-master-course_Index_v1.md                     ← this file
├── personas/agents-master-course_Personas_v1.md         ← the 13 named personas + system-prompt skeletons
├── chapters/agents-master-course_Chapter-XX_v1.md       ← one per chapter
└── code/
    ├── chapter_XX_*.py                                  ← one runnable file per chapter
    └── shared/                                          ← reusable modules introduced mid-course
        ├── goal_predicates.py
        ├── eval_harness.py
        └── state_store.py
```

---

## Conventions

- **Markdown markers** Claude emits during teaching: `[SCORE:0.XX]`, `[COMPLETE]`, `[INSIGHT:<phrase>]`. Treat these as control signals, not output you should answer.
- **Code idioms:** all async, wrapped with `anyio.run(main)`. Every script is self-contained — no hidden imports.
- **Auth:** verify Chapter 0 works before any other chapter. If Chapter 0 fails, every subsequent chapter fails.
- **Architect's reflection** at the end of each chapter is the deliverable. Skip it and you've just typed code, not learned architecture.
