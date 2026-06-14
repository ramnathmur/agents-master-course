# Chapter 12.5 — Cold Build: From Blank File to Working Agent (No Safety Net)  [v1]

**Trait focus:** All five (goal, perception, reasoning, action, iteration) + build-fluency under time pressure.
**Persona:** The Architect (personas, Ch 8). Borrow The Conductor (Ch 12) only if your design fans out.
**Voice opener:** *"Every prior chapter handed you a `.py`. This one doesn't. The discomfort is the point — architects who can only modify provided code aren't architects yet."*
**Prerequisites:** Chapters 1–12 complete.
**Code:** None. You write it. Blank file. 30 minutes.

> **Why this chapter exists:** Reading the v2/v3 chapters trains pattern recognition. Recognition is not generation. This is Review E4 — the cold build that separates fluent architects from fluent readers.

---

## PHASE 1 — CALIBRATION

Open with the Voice sample, then:

> **Ask Ram:** "On a blank IntelliJ file, with no internet lookup, how long do you think it'll take you to build an agent that finds every Markdown file with broken internal links and proposes fixes? Estimate in minutes. Write the number down before you start. We'll measure against it."

Capture the estimate. The gap between estimate and actual is the calibration signal — chronic underestimation means the patterns aren't yet reflexive; chronic overestimation means you're avoiding the keyboard.

## PHASE 2 — ADAPT

- **Branch A (shallow):** Walk through the skeleton structure that should already be in your head — `import anyio`, `from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions`, a goal predicate function, one perception tool (filesystem read), one reasoning step (model call), one action tool with a hook, a `while not done` loop with an iteration cap, and a single `eval_case` dict at the bottom. If you can't sketch this skeleton from memory, the rest of Phase 3 will hurt — review Chapters 4–8 first.
- **Branch B (strong):** Skip the skeleton. Read the spec below. Start the timer. Go.
- **Branch C (reinforce):** "Last chapter your weak signal was `subagent_persona_design`. In this exercise, you have ONE agent — but you're the architect of its scope, tools, and goal predicate. Apply the same persona-design discipline to your own agent: what is its scope, what are its tools and why, what is its 'done' condition, what does failure look like? The fact that you're not naming sub-agents doesn't excuse you from naming this one's persona."

## PHASE 3 — CODE — NO PROVIDED CODE

**Spec (one line):**
> Build an agent that scans a directory of Markdown files, finds every internal link `[text](path)` whose path does not exist on disk, and either fixes the path (if a close match exists) or appends a `<!-- BROKEN LINK -->` note next to the link.

**Constraints:**
- 30-minute timer. Open IntelliJ. Start. At 30:00, stop — regardless of state.
- No internet lookup. SDK reference docs allowed (the same way you'd allow yourself `man` pages). No copy-paste from prior chapter files.
- Required surface area:
  1. **Goal predicate** — a function or lambda that returns `True` when the agent is done. Not vibes. A checkable boolean.
  2. **Perception tool** — directory scan + Markdown read. Glob + read_text.
  3. **Reasoning step** — model decides: fix path vs annotate.
  4. **Action tool with a hook** — file write, gated by a `PreToolUse` hook that blocks writes outside the target directory (sandbox) OR audits every write (log line). Ch 7 discipline.
  5. **Iteration loop** — three exit conditions: goal met, iteration cap (e.g. 20), or budget exhausted (e.g. wall-clock seconds via `anyio` monotonic). Ch 4.
  6. **At least one eval case** — a fixture directory with one known broken link and one known-good link, plus an assertion that the agent fixes exactly the broken one. Ch 8.
- **Bonus (not required, +0.1 score):** one sub-agent — e.g. a `link_resolver` sub-agent dispatched to find close-match candidates. Ch 12.

**Style discipline (non-negotiable, same as every prior chapter):**
- All async. Wrap entry with `anyio.run(main)`.
- Module docstring at top: one paragraph stating what this is and which traits it exercises.
- Comments explain WHY (architectural decision), never WHAT (syntax).
- No `pass`-only bodies, no `NotImplementedError` left behind, no `TODO`s. Ship it or fail it.
- Time-sensitive logic uses `anyio.sleep` or a monotonic counter, not wall-clock subtraction across event loop yields.

Start the timer. Close this file. Open a blank one.

## PHASE 4 — ASSESSMENT

When the timer hits 30:00, stop typing. Then:

> **Ask Ram:**
> (a) "Walk me through what you built. Where is your goal predicate — point at the line."
> (b) "Where is your iteration exit condition? All three of them?"
> (c) "Where would your eval set live, and what's the assertion?"
> (d) "What did you have to look up vs what came reflexively? Be specific — name the API call or the import path."

**Scoring rubric:**

| Outcome | Score |
|---|---|
| All 5 traits present (goal predicate, perception, reasoning, action+hook, iteration), 1 eval case, 1 hook, runs end-to-end on the fixture | `[SCORE:1.0]` |
| 4 of 5 traits present, runs end-to-end | `[SCORE:0.8]` |
| Some traits present, partial run (e.g. detects broken links but can't write the fix; or runs but no hook; or no eval) | `[SCORE:0.6]` |
| Doesn't run end-to-end — import error, infinite loop, exception on fixture | `[SCORE:0.4]` |
| Bonus: working sub-agent dispatch | `+0.1` (cap at 1.0) |

If `[SCORE] < 0.7`, the weak signal is `build_fluency_under_pressure` — repeat this chapter next month with a new spec before advancing to real work.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Reading-fluency is not writing-fluency. The chapters taught you to recognize the patterns; this exercise revealed which patterns are reflexive and which still need lookup. The lookup list is your next study plan — not a failure, a map.]`

> Generate your session brief: `python code/shared/session_brief.py --after 12`.

---

## Architect's Reflection — Action Checklist

Answer in writing within 10 minutes of stopping the timer. No editing later.

1. **Look up vs reflexive** — List exactly 3 things you had to look up (e.g. `ClaudeAgentOptions` field name, hook event constant, glob recursive flag). Each one becomes a re-study target — go back to the chapter that introduced it and re-do its Phase 3 from memory.
2. **Time per trait** — Which trait cost you the most minutes? (Usually the hook or the eval case.) That trait is your weak primitive. The chapters where it was introduced (Ch 7 for hooks, Ch 8 for evals) get re-read this week, not next month.
3. **What you skipped** — Did you skip the eval case? The hook? The iteration cap? Why? The honest answer is almost always "they felt optional under time pressure." They're not. In production they're the difference between an agent and a script. Note which one you skipped and why — that's the trait you under-respect.
4. **What you'd build differently with 60 minutes** — List 3 things. Not "make it nicer." Specific architectural choices: a second eval case covering an edge (relative vs absolute paths), a sub-agent for fuzzy match scoring, a verifier that re-reads the file after the write. These are the items you knew you should do but ran out of clock for — name them so they're not lost.

## Exit Check

Do this exercise again next month with a different spec (suggestions: an agent that consolidates duplicate import statements across a Python package; an agent that detects and proposes fixes for stale URLs in a links file). Same 30-minute timer. Same scoring rubric.

If you can hit 5 traits + 1 hook + 1 eval in 30 minutes without lookup — **you are fluent.** The course was not wasted on you.

If you can't yet — repeat. Fluency is built by cold reps, not by re-reading. The chapters are the warm-up. This is the lift.
