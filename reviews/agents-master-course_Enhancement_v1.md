# Agents Master Course — Enhancement v1

**Reviewer:** Three parallel parameter sub-agents (breadth / depth / agent fluency).
**Date:** 2026-06-02
**Course version reviewed:** v2 (post-`reviews/agents-master-course_Review_v1.md` revisions)
**Rubric:** NEW — distinct from Review v1's depth-and-readiness / Lego-reinforcement / AI-first-delivery axes.

---

## Executive Verdict

| Parameter | Score | Verdict |
|---|---|---|
| 1. Course Breadth | 2.75/5 | **CONDITIONAL PASS** |
| 2. Course Depth | 3.5/5 | **CONDITIONAL PASS** |
| 3. Agent Fluency | 3.6/5 | **CONDITIONAL PASS** |
| HTML session-brief feasibility | Generator written | **READY TO SHIP** |
| **Overall** | | **CONDITIONAL PASS — five priority-1 enhancements would lift to PASS** |

**The course is competent and runs. It teaches reading-fluency, not writing-fluency. Production surfaces (external MCP, network tools, injection defense) are absent. Middle chapters demonstrate one side of a tradeoff and tell the learner to comment-swap for the other.**

---

## Parameter 1 — Breadth Findings

| # | Finding | Score | Tag |
|---|---|---|---|
| B1.1 | Session resume entirely absent — hand-rolled `state.json` replaces the SDK's native resume primitive | 2/5 | JOINT |
| B1.2 | External MCP integration unmentioned — every server is in-process via `create_sdk_mcp_server` | 2/5 | JOINT |
| B1.3 | Streaming, `can_use_tool`, non-Pre/Post hooks (`Notification`, `Stop`, `SessionStart`, `UserPromptSubmit`) not taught | 3/5 | CONCEPT |
| B2.1 | **ReAct never named** despite Ch 6–8 implementing perceive→reason→act loop | 3/5 | CONCEPT |
| B2.2 | Plan-and-execute taught but not labeled — blurs with chained workflow | 4/5 | CONCEPT |
| B3.1 | **Prompt-injection / jailbreak: zero coverage** across all 13 chapters | 1/5 | CONCEPT |
| B3.2 | Observability stops at a single `PostToolUse` log line — no usage/cost from `ResultMessage`, no trace IDs | 2/5 | JOINT |
| B3.3 | No rate-limit/backoff code despite Ch 10 naming rate-limits as a transient class | 2/5 | CODE |
| B3.4 | Deployment + model migration entirely absent — course ends at "it runs in IntelliJ" | 1/5 | CONCEPT |
| B4.1 | Every tool reads/writes local filesystem — no HTTP, DB, or third-party API tool example | 2/5 | CODE |
| B4.2 | Citations + structured-response surfaces absent | 2/5 | CONCEPT+CODE |

**Biggest breadth gap: external MCP integration + native SDK session resume are entirely absent.** A learner finishing Ch 12 can build an in-process SDK agent that reads local files; they have never connected to a real MCP server, never resumed a session, never built a tool that talks to a network.

---

## Parameter 2 — Depth Findings

| # | Finding | Score | Tag |
|---|---|---|---|
| D1.1 | Ch 8 v2 Reflection — 5-item eval checklist is architect-grade | 5/5 | CONCEPT |
| D1.2 | Ch 12 v2 Capstone Action Checklist (9 items) — only place whole architecture lands in one frame | 5/5 | CONCEPT |
| D1.3 | Ch 11 Reflection names "memory tiers" but never specifies boundary rules, migration mechanics, concurrency primitives | 3/5 | CONCEPT |
| D1.4 | **Ch 5 Reflection — worst on D1.** 4-question template; skips the "description vs system-prompt" tradeoff | 2/5 | CONCEPT |
| D1.5 | Ch 9 critic Reflection — no rejection-rate target, no specific known-bad construction recipe | 3/5 | CONCEPT |
| D2.1 | **`chapter_08_integration.py` — best on D2.** Genuine 5-trait file post-R1 | 5/5 | CODE |
| D2.2 | `chapter_10_recovery.py` only fires transient→promotion scenario; re-plan-cap and policy-deny reachable but not run | 3/5 | CODE |
| D2.3 | `chapter_06_reason.py` validates schema but never demonstrates rejection-resubmit loop chapter promises | 3/5 | CODE |
| D2.4 | **`chapter_05_perceive.py` — worst on D2.** Manual A/B comment-swap; no side-by-side execution | 2/5 | CODE |
| D2.5 | `chapter_11_two_agent.py` restart-resilience demo requires manual `reset_state()` comment-out | 3/5 | CODE |
| D2.6 | `chapter_04_iteration.py` v2 — dual `main()` pattern works; compaction tradeoff noted in docstring, not demoed | 4/5 | CODE |
| D3.3 | Ch 10 concept (4/5) > code (3/5) — only transient branch fires | — | CODE |
| D3.4 | Ch 6 concept (4/5) > code (3/5) — no rejection-loop demo | — | CODE |
| D3.5 | **Ch 9 code (4/5) > concept (3/5)** — rare reverse asymmetry; ship a calibration set | — | CONCEPT |
| D3.6 | Ch 11 code (4/5) > concept (3/5) — tier rules under-specified | — | CONCEPT |
| D4.4 | Ch 5 reads as undergrad tutorial, not architect | 2/5 | CONCEPT |
| D4.5 | Ch 7 hook taxonomy (Guard/Observe/Mutate) — concept 5/5, only Guard exercised in code | 3/5 | JOINT |

**Biggest depth gap: demonstration shortfall in middle chapters 5, 6, 10, 11.** All four have the same pathology — headline tradeoff named in the Markdown, only one side runs in `main()`, learner must manually mutate the script to see the other side. Ch 4 v2 already solved this via dual-`main()`. Spread the pattern.

---

## Parameter 3 — Agent Fluency Findings

| # | Finding | Score | Tag |
|---|---|---|---|
| F1.1 | 9 of 10 spot-checked vocab terms grounded; "Removal Test" absent from chapter body | 4/5 | CONCEPT |
| F2.1 | Decision: "research assistant summarizing papers" — Ch 3 + Ch 11 sufficient | 4/5 | CONCEPT |
| F2.2 | **Decision: "code-formatter watcher" — JOINT GAP.** Event-driven / daemon-shaped agents never modeled | 2/5 | JOINT |
| F2.3 | Decision: "fix all TODOs" — Ch 8 IS this task; fluent | 5/5 | JOINT |
| F3.1 | Tradeoff: sliding-window vs summarization vs scratchpad — only 1 of 3 strategies coded | 3/5 | CODE |
| F3.2 | Other 4 tradeoffs (retry/replan/escalate, tier choice, monolith/orch, actor≠judge) defensible | 4/5 | CONCEPT+CODE |
| F4.1 | 4 of 5 failure symptoms map to chapter+class; sub-agent silent-failure is the weak spot | 4/5 | JOINT |
| F5.1 | **Biggest fluency gap.** No "blank file → working agent" rehearsal. Every chapter hands a pre-built `.py`. Ch 12 Exit Check demands what was never practiced | 3/5 | JOINT |

**Biggest fluency gap: no cold-build rehearsal.** Learner has all parts and reference code; has never assembled a working agent from a blank file under time pressure. This is the wall they hit on Day 1 of real work.

---

## HTML Session-Brief Design

**Status:** Generator written and ready to ship.
**File:** `code/shared/session_brief.py` (296 lines, no external deps beyond stdlib).
**Output:** `session-briefs/agents-master-course_Brief_after-Chapter-NN_v1.html`
**Coverage:** Cumulative — Brief at Chapter N covers Chapters 0..N.
**Self-contained:** Inline CSS, no CDN, no remote fonts, no images. Opens offline in any browser.

### Section structure per brief
1. **Header** — title, generated date, "cumulative dashboard" subhead.
2. **Progress track** — 13 numbered dots (done/next).
3. **What my Professor has taught me** — one card per chapter, in order, first-person. Each card: persona + trait + voice opener (italicized) + learned paragraph + top-6 key concepts + carry-forward `[INSIGHT:...]`.
4. **Key Concepts glossary** — flat alphabetical list across all chapters covered, each tagged with originating chapter.
5. **Code primitives I can now write** — per-chapter 3-line snippet of the pattern the chapter teaches.
6. **Footer** — "Next: Chapter N+1" pointer, or "Course Complete" at Ch 12.

### Usage
```bash
# Generate the brief after a specific chapter
python code/shared/session_brief.py --after 4

# Regenerate every brief (Ch 0..12) — useful after applying enhancements
python code/shared/session_brief.py --all
```

### Integration pattern (proposed Phase 5 WRAP addition)
Every chapter's Phase 5 WRAP gets one line:
> *"Generate your session brief: run `python code/shared/session_brief.py --after <N>` from the project root. Open the .html in your browser."*

Claude Desktop can also invoke the generator directly when the student says "give me my brief" or "where am I."

---

## Convergent Gaps (Priority-1)

### CG1 — Demonstrate-both-sides pattern absent in Ch 5, 6, 10, 11
**Convergence:** Depth (D2.2, D2.3, D2.4, D2.5) + Fluency (F3.1).
**Pathology:** Headline tradeoff named in Markdown; only one side runs in `main()`. Learner must hand-mutate to see the other side.
**Fix:** Apply Ch 4 v2's dual-`main()` pattern to all four chapters.

### CG2 — Observability is one log line, not an architecture
**Convergence:** Breadth (B3.2) + Depth (D4.5) + Fluency (F4.1 sub-agent silent failure).
**Pathology:** `PostToolUse` observer just appends tool names to a list. No span IDs, no parent references, no structured event shape, no `traces.jsonl` artifact. Sub-agent silent failures have nowhere to show up.
**Fix:** Strengthen Ch 8's `audit_observer` into a real trace schema with span IDs and a JSONL trace artifact, OR add a Ch 8.5 / dedicated observability mini-chapter.

### CG3 — Production surfaces missing (external MCP + network tools + injection defense)
**Convergence:** Breadth B1.2 + B3.1 + B4.1 cluster.
**Pathology:** Every tool in the course is filesystem-only and in-process. Prompt injection has zero coverage. External MCP servers (filesystem, Slack, GitHub) never appear.
**Fix:** Add a Ch 13 "Production Surfaces" chapter covering (a) connecting to an external MCP server, (b) an HTTP-backed tool with retry/backoff, (c) prompt-injection defense patterns including the lethal-trifecta rule.

### CG4 — No cold-build rehearsal
**Convergence:** Fluency F5.1 (biggest fluency gap) + Depth D4.4 (Ch 5 reads as tutorial).
**Pathology:** Every chapter hands the learner a pre-built `.py`. Ch 12 Exit Check demands "scaffold a from-scratch agent" — never practiced.
**Fix:** Add Ch 12.5 "Cold Build" — one-line spec, 30-minute timer, blank IntelliJ file. Must hit 5 traits + 1 sub-agent + 1 tool + 1 hook + 1 eval case. Answer key is `chapter_08_integration.py` re-derived.

### CG5 — Native SDK session resume not taught
**Convergence:** Breadth B1.1 standalone (high-severity).
**Pathology:** The headline durability mechanic of the SDK is replaced by a hand-rolled `state.json`. Learner never sees `session_id`, `continue` flag, fork primitives.
**Fix:** Add a section to Ch 11 (or a Ch 11.5 mini-chapter) titled "What the SDK gives you natively." Show in-process session resume; contrast with the cross-process `state.json` pattern Ch 11 already teaches.

---

## Non-Convergent Gaps (Priority-2)

| # | Gap | Source | Suggested fix |
|---|---|---|---|
| N1 | ReAct never named | B2.1 | Add taxonomic label in Ch 6 or Ch 8 reflection |
| N2 | Plan-and-execute not labeled | B2.2 | Same — label in Ch 3 or Ch 6 |
| N3 | "Removal Test" term not in chapter body | F1.1 | Add a sentence to Index_v2 or Ch 1 |
| N4 | Ch 9 critic — no calibration set shipped | D3.5 | Add a 5-good + 5-bad fixture file to `code/shared/critic_calibration.json` |
| N5 | Ch 11 memory tiers under-specified | D1.3 | Expand reflection with tier-boundary rules + concurrency primitives |
| N6 | Ch 7 hook Observe/Mutate roles only verbal | D4.5 | Add a 10-line `PostToolUse` audit hook + a `Mutate` example (path normalization) |

---

## Enhancement Proposals

### E1 — Spread dual-`main()` pattern to Ch 5, 6, 10, 11 (Priority-1, addresses CG1)
- `code/chapter_05_perceive.py`: add `main_sparse()` + `main_rich()` running back-to-back with the same task; print response length + tool-call count for each.
- `code/chapter_06_reason.py`: add `main_valid()` (well-formed plan accepted) + `main_malformed()` (deliberately bad step → REJECT → resubmit → accept).
- `code/chapter_10_recovery.py`: extend `main()` to run THREE scenarios sequentially — transient (retry budget exhaustion → promote), structural (re-plan budget → escalate), policy (HITL deny).
- `code/chapter_11_two_agent.py`: add `main_clean()` + `main_with_kill()` — second variant kills mid-research, then resumes; shows facts persisted before the kill.

Each chapter's Markdown Phase 3 updated to reference the dual run.

### E2 — Real tracing schema in Ch 8 (Priority-1, addresses CG2)
- `code/chapter_08_integration.py`: replace `_audit_log: list[str]` with a real trace:
  ```python
  @dataclass
  class Span:
      span_id: str
      parent_id: str | None
      tool: str
      started_at: float
      duration_ms: float
      result_summary: str
  ```
- Write each span to `traces.jsonl`. Update the Markdown reflection to add a "Tracing as architecture" sub-section with span/parent/event shape.

### E3 — Add Chapter 13: "Production Surfaces" (Priority-1, addresses CG3)
New chapter Markdown + `.py`:
- (a) Connect to an external MCP server example (mock filesystem MCP for offline-safety).
- (b) An HTTP-backed `@tool` with `httpx` + retry/backoff.
- (c) Prompt-injection defense: lethal-trifecta rule, output filtering, the "untrusted content in `<![CDATA[]]>`" pattern.
- Persona: "The Engineer" — pragmatic, deployment-aware. Voice opener TBD.

### E4 — Add Chapter 12.5: "Cold Build" exercise (Priority-1, addresses CG4)
New chapter Markdown. No `.py` file (the learner WRITES one).
- One-line spec: "Build an agent that finds every Markdown file with broken internal links and proposes fixes."
- 30-minute timer.
- Must hit: 5 traits + 1 sub-agent + 1 hook + 1 eval case.
- Answer key sketch in `chapters/agents-master-course_Chapter-12-5_solutions_v1.md` for after-attempt review.

### E5 — Teach native session resume in Ch 11 (Priority-1, addresses CG5)
- Add a "Native vs hand-rolled state" section to `chapters/agents-master-course_Chapter-11_v3.md`.
- Add a small companion script `code/chapter_11_native_resume.py` demonstrating `session_id` capture and resume.

### E6 — Ship the HTML session-brief integration (Priority-1, all-new)
- Generator written: `code/shared/session_brief.py`. Already ready.
- Add a one-line WRAP instruction to every chapter Markdown (Ch 0–12).
- Run `python code/shared/session_brief.py --all` to produce all 13 briefs as a baseline deliverable.

### E7 — Add ReAct + plan-and-execute taxonomic labels (Priority-2, addresses N1, N2)
- Ch 6 reflection: add a sentence naming the ReAct pattern when the chapter introduces plan-tool-act.
- Ch 3 reflection: add a sentence naming plan-and-execute and contrasting with workflow.

### E8 — Critic calibration set (Priority-2, addresses N4)
- New file `code/shared/critic_calibration.json` with 5 known-good + 5 known-bad examples and expected verdicts. Ch 9 Reflection updated to point at it.

### E9 — Ch 11 memory-tier specification (Priority-2, addresses N5)
- Expand Ch 11 reflection (in a `_v3` bump) with: (a) tier-boundary rules, (b) concurrency primitives (file lock, CAS), (c) when to choose SQLite vs file vs queue.

### E10 — Ch 7 Observe + Mutate hook examples (Priority-2, addresses N6)
- Add `audit_observer` PostToolUse hook (10 lines) and a `Mutate` example (path normalization) to `chapter_07_act.py`. Markdown reflection updated.

---

## Open Questions for Ram

1. **CG3 / E3 — adding Chapter 13** is a significant scope expansion. Approve or scope down to a "Production Surfaces appendix" without persona/loop ceremony?
2. **CG4 / E4 — Chapter 12.5 Cold Build** — comfortable with a "no `.py` provided" chapter? It's intentionally bare. The discomfort IS the point.
3. **CG5 / E5 — native session resume** — happy to add it to Ch 11, or do you want it as a Ch 11.5 standalone?
4. **Affected-file version bump policy** — all bumped files go to `_v3`, OR do we issue a "v2.1" patch? (v3 is consistent with the prior pattern.)
5. **Run the HTML generator now** to produce all 13 briefs, or wait until after enhancements land?

---

*End of Enhancement v1.*
