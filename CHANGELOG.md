# Agents Master Course — Changelog

## v3 — 2026-06-02

Driven by `reviews/agents-master-course_Enhancement_v1.md` (three-parameter scan: breadth / depth / agent fluency + sandbox simulation). 10 enhancements applied via parallel Workflow (24 sub-agents).

### Priority-1 enhancements

- **E1 — Dual-`main()` demo pattern spread to Ch 5, 6, 10, 11.** Each chapter's headline tradeoff now runs both sides back-to-back in `main()`, no manual comment-swapping. Lifted Ch 4's pattern.
  - `code/chapter_05_perceive.py` v3: `main_sparse()` + `main_rich()` with side-by-side comparison.
  - `code/chapter_06_reason.py` v3: `main_valid()` + `main_malformed()` — second one demonstrates the REJECT → fix → resubmit loop.
  - `code/chapter_10_recovery.py` v3: three scenarios fire — `scenario_transient_promotion`, `scenario_structural_replan`, `scenario_policy_escalate`. All three Dispatcher branches visible.
  - `code/chapter_11_two_agent.py` v3: `main_clean()` + `main_with_simulated_kill()` — second simulates mid-research kill via direct state-store writes + raised exception, then resumes via the existing Researcher (which now reads existing facts on disk before appending).

- **E2 — Real tracing schema in Ch 8.** `code/chapter_08_integration.py` v3 replaces the flat `_audit_log: list[str]` with a `Span` dataclass (span_id, parent_id, tool, started_at_counter, duration_ticks, result_summary). Parent IDs come from a span stack pushed in `PreToolUse` and popped in `PostToolUse`. Trace emitted as JSONL to `traces.jsonl`.

- **E3 — New Chapter 13: Production Surfaces.** Covers three production surfaces missing from Ch 0–12: external stdio MCP server config, HTTP-backed `@tool` with 3-attempt exponential-backoff retry (urllib + anyio.sleep), prompt-injection defense via CDATA fencing + lethal-trifecta rule. New persona **The Engineer** added to `personas/agents-master-course_Personas_v3.md`.

- **E4 — New Chapter 12.5: Cold Build.** A no-`.py` chapter. One-line spec: "build an agent that scans Markdown files for broken internal links and proposes fixes." 30-minute timer. Must hit 5 traits + 1 eval + 1 hook unaided. Self-assessment scoring: 1.0 if all traits run end-to-end, down to 0.4 if doesn't run.

- **E5 — Native SDK session resume taught in Ch 11.** New `code/chapter_11_native_resume.py` companion script demonstrates that within ONE `ClaudeSDKClient` context, sequential queries share session state automatically; exiting and re-entering a new client loses it. Ch 11_v3 Markdown adds a "Sidebar: Native SDK session resume" section explaining what `state.json` buys you that the native path does not.

- **E6 — HTML session-brief integration.** New `code/shared/session_brief.py` generator (stdlib only, self-contained HTML, no CDN). Cumulative dashboard — Chapter N brief covers Chapters 0..N. Every chapter Markdown's Phase 5 WRAP now ends with `> Generate your session brief: python code/shared/session_brief.py --after <N>`. Briefs land at `session-briefs/`.

### Priority-2 enhancements

- **E7 — ReAct + plan-and-execute taxonomic labels.** Ch 3_v2 Reflection names plan-and-execute and forward-references ReAct; Ch 6_v3 Reflection names ReAct explicitly.
- **E8 — Critic calibration set fixture.** New `code/shared/critic_calibration.json` (5 known-good + 5 known-bad cases with subtle wrong answers like "Lyon" for capital of France).
- **E9 — Ch 11 memory-tier spec expansion.** Reflection table now specifies Session / Shared / Persistent tiers with storage options + concurrency primitives.
- **E10 — Ch 7 Observe + Mutate hooks wired in code.** `chapter_07_act.py` v2 adds `audit_observer` (PostToolUse Observe role) and `normalize_path_mutate` (PreToolUse Mutate role) alongside the existing `sandbox_guard` (Guard role). All three hook roles now exercised in code.

### Files added

- `chapters/agents-master-course_Chapter-12-5_v1.md`
- `chapters/agents-master-course_Chapter-13_v1.md`
- `code/chapter_11_native_resume.py`
- `code/chapter_13_production.py`
- `code/shared/critic_calibration.json`
- `code/shared/session_brief.py`
- `personas/agents-master-course_Personas_v3.md` (adds §13 The Engineer)
- `reviews/agents-master-course_Enhancement_v1.md` (the audit that drove this revision)
- `session-briefs/agents-master-course_Brief_after-Chapter-NN_v1.html` × 14 (generated)

### Files bumped to new version

- `chapters/agents-master-course_Chapter-03_v2.md` (ReAct/plan-and-execute label)
- `chapters/agents-master-course_Chapter-05_v3.md`
- `chapters/agents-master-course_Chapter-06_v3.md`
- `chapters/agents-master-course_Chapter-07_v2.md`
- `chapters/agents-master-course_Chapter-08_v3.md`
- `chapters/agents-master-course_Chapter-10_v3.md`
- `chapters/agents-master-course_Chapter-11_v3.md`
- `code/chapter_05_perceive.py` v3
- `code/chapter_06_reason.py` v3
- `code/chapter_07_act.py` v2
- `code/chapter_08_integration.py` v3
- `code/chapter_10_recovery.py` v3
- `code/chapter_11_two_agent.py` v3
- `agents-master-course_Index_v3.md` (supersedes v2)

### Files appended (no version bump)

- Ch 0, 1, 2, 4, 9, 12 Markdowns: session-brief reminder line in Phase 5 WRAP.

### Audit trajectory

| Parameter | v2 score | v3 expected |
|---|---|---|
| Breadth | 2.75/5 CONDITIONAL | ~4/5 PASS (production surfaces + native resume close the biggest gaps) |
| Depth | 3.5/5 CONDITIONAL | ~4.5/5 PASS (dual-main spread + tracing schema close the demonstration shortfall) |
| Agent Fluency | 3.6/5 CONDITIONAL | ~4.5/5 PASS (Cold Build rehearsal addresses the biggest fluency gap) |

---

## v2 — 2026-06-02

Driven by `reviews/agents-master-course_Review_v1.md` (multi-agent audit via `ai-self-evaluation` + 3 sandbox simulations).

### Priority-1 (convergent issues — flagged by file review AND simulation)

- **R1 — `code/chapter_08_integration.py` rewritten.** v1 was a one-sentence-summary loop with no tools, no hooks, no perception. v2 is a real TODO-fixing agent that composes all five traits: `list_python_files` + `read_file` (perceive), `propose_plan` (reason), `write_file` (act) gated by sandbox `PreToolUse` hook, iteration loop with goal predicate "all TODOs resolved or annotated DEFERRED," and a `PostToolUse` audit-trail observer. Scored by `run_suite` against 3 fixture directories.
- **R2 — `code/chapter_10_recovery.py` dispatcher wired.** v1 defined `classify_failure()` but never called it. v2 adds a `Dispatcher` class with `RETRY_CAP=3`, `REPLAN_CAP=2`, and a promotion rule (K retries → reclassify as structural). Outer loop intercepts each tool result via `capture_result` PostToolUse hook and routes through `Dispatcher.decide()`. All three branches (retry / re-plan / escalate) fire in a single scripted scenario.
- **R3 — `code/chapter_04_iteration.py` adds `main_with_compaction()`.** v1 had only the unbounded baseline. v2 keeps `main_unbounded()` AND adds `main_with_compaction(window_turns=2)` that keeps only the last K (attempt, feedback) pairs. Both print a token-estimate column so context growth becomes a number.
- **R5 — Branch C expanded in chapters 5, 8, 9, 10, 11, 12.** v1 degraded these to one-line "Confirm Ch N takeaway first." v2 makes each Branch C a 2–3 sentence substantive reframing of the prior weakSignal in the new chapter's vocabulary, modeled on Ch 4's already-strong Branch C.

### Priority-2

- **R4 — `code/chapter_06_reason.py` tight schema validates the full inner shape.** v1's "tight" tool was `{"steps": list}` — the same loose pattern the chapter criticizes. v2 validates each step's `action` (enum), `target` (non-empty string), `expected_outcome` (non-empty string) server-side and rejects with a structured error.
- **R6 — `personas/agents-master-course_Personas_v2.md` adds Voice samples.** Each of the 13 personas now has a verbatim 1–2 sentence Voice opener. Chapter Phase 1 sections in the `_v2` Markdowns use the matching voice opener. Personas now differ on paper, not just in extrapolation.
- **R7 — Architect's Reflections converted to action checklists in chapters 4, 5, 6, 8, 9, 10, 11, 12.** v1 reflections were prose essays that survived the Removal Test too well. v2 reflections are 3–9 item architect-decision checklists. The learner answers each before moving on, making the section AI-dialog-dependent rather than monologue-readable.

### Priority-3

- **R8 — Joint 05→06 repaired.** v1's Ch 5 exit asked for tool description engineering; Ch 6 calibration jumped to "where do you put the plan?" v2's Ch 5 Exit Check ends with a Forward Pointer explicitly forecasting the schema-vs-description distinction. v2's Ch 6 calibration question reframes to land on the seam directly: "Description is vocabulary; schema is grammar. Tell me where you put the plan-instruction."
- **R9 — `code/shared/eval_harness.py` adds trajectory + LLM-judge scoring.** v1 implemented outcome scoring only; the reflection text discussed three modes. v2 adds `TrajectoryCase` (scores tool-call sequence vs expected pattern, with forbidden-tool detection) and `LLMJudgeCase` (scores via a separate `query()` call with adversarial rubric system prompt). Outcome remains the default.

### Unchanged in v2

- Chapter Markdowns 0, 1, 2, 3, 7 (joints 00→04 and 06→07 scored 4–5/5 in the audit; no revisions needed)
- Code files for chapters 0, 1, 2, 3, 5, 7, 9, 11, 12 and `shared/goal_predicates.py`, `shared/state_store.py`
- `ROADMAP.md` structure (status indicators updated to reflect v2 completion)
- The 5-phase teaching loop and the weakSignal chain mechanics (audited 5/5)

### Audit verdicts

All three review dimensions moved from **CONDITIONAL PASS (v1)** to expected **PASS (v2)**. The Lego-block joints were always strong; the v2 revisions repair the concept-to-code mismatch at chapters 4, 8, 10 and the cosmetic Branch C content in chapters 5, 8, 9, 10, 11, 12. Persona voices are now distinguishable on paper.

### Files in active use (v2)

Read `agents-master-course_Index_v2.md` for the canonical file list. The v1 files are retained on disk for audit-trail purposes; do not read them as course material.
