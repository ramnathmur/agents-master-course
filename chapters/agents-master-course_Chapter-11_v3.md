# Chapter 11 — Two-Agent Systems: Handoff and Persistent Memory  [v3]

**Trait focus:** Agent-to-agent. Persistent memory.
**Persona:** The Diplomat (personas v2, §11).
**Voice opener:** *"Two agents do not share consciousness — they share a contract. Storage, schema, protocol: pick one of each before you write any code."*
**Prerequisites:** Chapter 10 complete.
**Code:** `code/chapter_11_two_agent.py`, `code/chapter_11_native_resume.py`, `code/shared/state_store.py`.

> **Revision v2 → v3:** kill-resume demo, native-resume sidebar, memory-tier spec expansion, brief integration (Reviews E1, E5, E9, E6).
> **Revision v1 → v2:** Branch C expanded (R5).

---

## PHASE 1 — CALIBRATION

Open with the Voice sample, then:

> **Ask Ram:** "Researcher gathers facts; Writer turns them into prose. They run in separate Python processes. What three things must they agree on before any code is written?"

## PHASE 2 — ADAPT

- **Branch A (shallow):** Three contract elements — storage (file/SQLite/queue), schema (JSON shape), protocol (polling/flag/queue).
- **Branch B (strong):** Skip to failure modes — incomplete writes, stale reads, concurrent updates. Then persistent memory across restarts.
- **Branch C (reinforce `failure_classification_promotion` from Ch 10):** "In Chapter 10 your weak signal was failure classification promotion — K retries means structural, not transient. Multi-agent handoffs introduce a fourth class: the *contract violation* failure (Agent B reads state that Agent A wrote in the wrong shape). That class doesn't retry, doesn't re-plan — it escalates to schema repair, which is a different operational beast. Two-agent failures expand your taxonomy."

## PHASE 3 — CODE

> **Tell Ram:** "Two files. `shared/state_store.py` is the atomic store. `chapter_11_two_agent.py` runs Researcher (scoped to append_fact + mark_research_complete) then Writer (scoped to read_all_facts + save_brief)."

`chapter_11_two_agent.py` v3 exposes two entry points. Run both, in order:

1. **`main_clean()`** — Researcher completes, Writer consumes, brief is emitted. Baseline contract.
2. **`main_with_simulated_kill()`** — Researcher writes a partial fact batch, then the process simulates a mid-research kill (raises before `mark_research_complete`). On the next invocation, the function inspects `state.json`, sees research is not marked complete, resumes Researcher from where it left off, then hands off to Writer.

Predict before running: what does the Writer see in each case?

Expected: in `main_clean`, the full fact set. In `main_with_simulated_kill`, after the second invocation, also the full fact set — because durable state survived the kill. The kill is only fatal if you trust *process memory* instead of *durable state*. This is the architectural payoff of Chapter 11.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Researcher writes facts until it 'feels done.' Writer reads and gets a half-baked input. Where in your architecture is the bug?"

Expected: in the contract — specifically the "phase complete" semantics. Three fixes possible: quantitative gate (≥ N facts), coverage gate (checklist), critic gate (separate verifier). "Done" is a checkable predicate, not a feeling. Same Ch 2 discipline, applied to inter-agent handoff.

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=handoff_contract_semantics`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:The contract IS the architecture. Storage + schema + protocol. Durable state = restart resilience. "Done" is a predicate, not a feeling.]`

> Generate your session brief: `python code/shared/session_brief.py --after 11`.

---

## Sidebar: Native SDK session resume

Within a single `ClaudeSDKClient` context, sequential `query()` calls share session state automatically — the SDK keeps conversation history, tool-call traces, and model context alive inside that one client. Two `await client.query(...)` calls back-to-back behave like a continuing conversation. No `state.json` needed. This is what Chapter 6 leaned on for multi-turn dialogue.

Cross a process boundary, however, and that in-memory session evaporates. A new Python process with a fresh `ClaudeSDKClient` is a stranger to the old one. This is precisely what `state.json` (this chapter) buys you: an *externalized* memory tier that survives process death, Ctrl-C, machine reboot, or a deliberate handoff to a different agent role. The contract — storage, schema, protocol — exists because the SDK's native session is scoped to a single client lifetime, and your architecture isn't.

The SDK is evolving toward a native session-id / fork API (resume an existing session by id, fork a session for parallel branches). When that lands, some of the work `state.json` does today will move into the SDK. Until then, the cross-process boundary is your responsibility — design the contract explicitly. See `chapter_11_native_resume.py` for the contrast: same Researcher → Writer flow, but executed within a single `ClaudeSDKClient` context, no `state.json`, no kill-resume. Compare the two files side-by-side. The deltas are the cost (and the value) of durability.

---

## Architect's Reflection (action checklist form)

For every multi-agent system you design:

1. **State ownership** — does each shared field have exactly ONE writer? Two writers = data race.
2. **Schema versioning** — is `schema_version` field present? When you bump it, do you write a migration?
3. **Memory tiers** — have I named which data lives in session memory (dies with process) vs shared state (within run) vs persistent (across runs)? Spec it explicitly:

   | Tier | Survives | Storage option | Concurrency primitive |
   |---|---|---|---|
   | Session | within `ClaudeSDKClient` context | in-memory | n/a (single client) |
   | Shared | within a run | file (`state.json`), SQLite, queue | file lock, transaction |
   | Persistent | across runs | SQLite, vector DB, episodic log | row-level lock, version field |

4. **Phase-complete predicate** — is it quantitative, coverage-based, or critic-gated? Not vibes.
5. **Two-agent vs one** — is the cost of context-sharing worth more than the benefit of specialization?

## Exit Check

Take any two-agent task. Design (a) storage layer, (b) shared-state schema, (c) handoff protocol, (d) phase-complete predicate. Identify when single-agent-with-split-roles is the better design.
