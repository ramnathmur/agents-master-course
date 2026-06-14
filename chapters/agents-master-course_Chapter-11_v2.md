# Chapter 11 — Two-Agent Systems: Handoff and Persistent Memory  [v2]

**Trait focus:** Agent-to-agent. Persistent memory.
**Persona:** The Diplomat (personas v2, §11).
**Voice opener:** *"Two agents do not share consciousness — they share a contract. Storage, schema, protocol: pick one of each before you write any code."*
**Prerequisites:** Chapter 10 complete.
**Code:** `code/chapter_11_two_agent.py`, `code/shared/state_store.py`.

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

Predict: if I kill the Researcher mid-run by Ctrl-C, what does the Writer see when it eventually runs?

Expected: whatever facts persisted to disk before the kill. The Writer either proceeds with partial data (if research phase was marked complete) or aborts (if not). Durable state = restart resilience.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Researcher writes facts until it 'feels done.' Writer reads and gets a half-baked input. Where in your architecture is the bug?"

Expected: in the contract — specifically the "phase complete" semantics. Three fixes possible: quantitative gate (≥ N facts), coverage gate (checklist), critic gate (separate verifier). "Done" is a checkable predicate, not a feeling. Same Ch 2 discipline, applied to inter-agent handoff.

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=handoff_contract_semantics`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:The contract IS the architecture. Storage + schema + protocol. Durable state = restart resilience. "Done" is a predicate, not a feeling.]`

---

## Architect's Reflection (action checklist form)

For every multi-agent system you design:

1. **State ownership** — does each shared field have exactly ONE writer? Two writers = data race.
2. **Schema versioning** — is `schema_version` field present? When you bump it, do you write a migration?
3. **Memory tiers** — have I named which data lives in session memory (dies with process) vs shared state (within run) vs persistent (across runs)?
4. **Phase-complete predicate** — is it quantitative, coverage-based, or critic-gated? Not vibes.
5. **Two-agent vs one** — is the cost of context-sharing worth more than the benefit of specialization?

## Exit Check

Take any two-agent task. Design (a) storage layer, (b) shared-state schema, (c) handoff protocol, (d) phase-complete predicate. Identify when single-agent-with-split-roles is the better design.
