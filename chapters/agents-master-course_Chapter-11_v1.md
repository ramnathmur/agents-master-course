# Chapter 11 — Two-Agent Systems: Handoff and Persistent Memory

**Trait focus:** Agent-to-agent. Inline persistent memory (gap #6 from research).
**Persona:** The Diplomat (see personas §11).
**Prerequisites:** Chapter 10 complete.
**Code:** `code/chapter_11_two_agent.py`, `code/shared/state_store.py`.

> **Tutor instruction.** Adopt The Diplomat. The single most important sentence in this chapter: "Two-agent systems are two agents with a contract over shared state. The contract IS the architecture."

---

## PHASE 1 — CALIBRATION

> **Ask Ram:** "I have two agents — Researcher and Writer. The Researcher gathers facts; the Writer turns them into prose. They run in separate Python processes. What three things must they agree on before any code is written?"

(Looking for: (1) where shared state lives — file, DB, queue; (2) the schema of the handoff payload — what shape the facts take; (3) the protocol for "researcher is done, writer can start" — polling, file flag, queue message. If Ram names all three, Branch B.)

## PHASE 2 — ADAPT

- **Branch A (shallow):** Walk through the three contract elements:
  - **Storage:** where shared state lives. Options: file (`state.json`), SQLite, Redis, message queue. Each has tradeoffs in durability and concurrency.
  - **Schema:** the structure of the handoff payload. Loose schema = misinterpretation. Tight JSON schema = enforceable contract.
  - **Protocol:** the signaling mechanism. Polling (cheap, latency), file flags (simple, racy), queues (clean, more infra).
- **Branch B (strong):** Skip to the failure modes: what happens when Agent A writes incomplete state? When Agent B reads stale state? When both write concurrently? Then introduce persistent memory across process restarts — what survives a kill, what doesn't.
- **Branch C (reinforce failure_classification_promotion):** Confirm Ch 10 takeaway first.

## PHASE 3 — CODE

> **Tell Ram:** "Two files. `shared/state_store.py` is a file-based atomic store — read, write, append, with file-locking to handle concurrent writes. `chapter_11_two_agent.py` defines Researcher and Writer as separate `ClaudeSDKClient` instances, with a JSON contract between them."

Architecture:
1. **`state_store.py`** — atomic read/write to `state.json`. Functions: `read_state()`, `write_state(dict)`, `append_facts(list)`, `mark_phase_complete(name)`.
2. **Researcher agent:** scoped tools to `search_web`, `read_url`. System prompt: "Gather facts on X. Append each fact to the state store as `{fact: str, source: str}`. Mark `research` phase complete when done."
3. **Writer agent:** scoped tools to `read_state`, `write_file`. System prompt: "Read the facts from state. Compose them into a 300-word brief. Wait if `research` phase is not yet complete."
4. **Driver:** runs Researcher and Writer sequentially in the same script (for teaching simplicity), but each agent only sees its scoped tools.

> **Predict before running:** "I'll kill the Researcher mid-run by hitting Ctrl-C. When I restart it, what should it do? When the Writer eventually runs, what should it see?"

Expected: a well-designed Researcher reads `state.json` on start, sees partial facts, and resumes from where it left off (or restarts depending on policy). The Writer sees whatever facts persisted to disk before the kill. Durable state = restart resilience.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Researcher and Writer disagree about what 'research is complete' means. Researcher writes facts until it 'feels done.' Writer reads and gets a half-baked input. Where in your architecture is the bug?"

(Expected: in the *contract*, specifically the "phase complete" semantics. Three fixes possible:
1. **Quantitative gate** — Researcher must produce ≥ N facts before marking complete.
2. **Coverage gate** — Researcher's task includes a checklist; all items must be covered.
3. **Critic gate** — a separate verifier reviews the fact set before allowing the phase to mark complete.

The architectural lesson: when two agents communicate, "done" is not a feeling — it's a checkable predicate. Same goal-predicate discipline from Ch 2, now applied to inter-agent handoff.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=handoff_contract_semantics`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:The contract IS the architecture. Storage + schema + protocol. Durable state = restart resilience. "Done" is a checkable predicate, not a feeling.]`

---

## Architect's Reflection

Multi-agent systems are an emerging field with many flavors (CrewAI, AutoGen, LangGraph, raw SDK). What survives across them all:

1. **State ownership.** Each piece of shared state has exactly one writer. Two writers to the same field is a data race waiting to happen. If two agents both need to update X, design a coordinator that owns X and accepts proposals.

2. **Schema versioning.** The shared-state schema WILL change. Build in a `schema_version` field from day one. When you bump it, write a migration. This sounds excessive for a 2-agent system; it sounds reasonable when you have 5.

3. **Memory tiers.** This chapter implicitly introduces three:
   - **Session memory** — within one agent's `ClaudeSDKClient`. Dies with the process.
   - **Shared state** — `state.json`. Survives within a run, across agents.
   - **Persistent memory** — could be a vector DB, a knowledge base, episodic logs. Survives across runs. Out of scope for this chapter, but you'll want it in Ch 12's orchestrator if sub-agents should learn from prior runs.

4. **Two agents vs one.** When NOT to split: when the cost of context-sharing exceeds the benefit of specialization. Two agents have to re-establish context every handoff. For short tasks, one agent with two roles in its system prompt is often cheaper and faster.

## Exit Check

You can take any two-agent task and design: (a) the storage layer (file, SQLite, queue), (b) the JSON schema of the shared state, (c) the handoff protocol (signaling mechanism), (d) the "phase complete" predicate that prevents premature handoff. You can also identify when a two-agent design is overkill and a single agent with split roles is better.
