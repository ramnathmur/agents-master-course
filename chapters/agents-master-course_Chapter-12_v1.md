# Chapter 12 — Orchestrator + Sub-Agents: The Capstone

**Trait focus:** Multi-agent architecture. Sub-agent persona design, routing, failure handling, sequencing.
**Persona:** The Conductor (see personas §12).
**Prerequisites:** Chapters 1–11 complete.
**Code:** `code/chapter_12_orchestrator.py`.

> **Tutor instruction.** Adopt The Conductor. This is the capstone. Reference earlier chapters concretely — every prior pattern shows up here. Don't introduce new primitives; compose existing ones.

---

## PHASE 1 — CALIBRATION

> **Ask Ram:** "An orchestrator agent has 5 sub-agents available. A new task arrives. Before any model call is made, what 5 architectural decisions has the orchestrator's designer (you) already made?"

(Looking for:
1. Decomposition strategy — how do you split tasks into sub-tasks?
2. Sub-agent persona design — what's each sub-agent's scope, tool set, model tier?
3. Routing — how does the orchestrator decide which sub-agent gets which sub-task?
4. Failure handling — what happens when a sub-agent fails?
5. Aggregation — how are sub-agent results combined?

Bonus: when NOT to split — the meta-decision.)

## PHASE 2 — ADAPT

- **Branch A (shallow):** Walk through each of the 5 decisions with examples. Use the cricket team analogy — the captain (orchestrator) decides batting order (sequencing), assigns roles (persona design), reads the field (routing), brings on a new bowler when one fails (failure handling), and reads the scoreboard (aggregation).
- **Branch B (strong):** Skip the basics. Jump to the SDK specifics: `agents={...}` on `ClaudeAgentOptions`, `AgentDefinition` shape, how the orchestrator dispatches via the Task tool under the hood, what state crosses the boundary.
- **Branch C (reinforce handoff_contract_semantics):** Confirm Ch 11 takeaway first.

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_12_orchestrator.py` to IntelliJ. This is the capstone. One orchestrator + three sub-agents: `researcher`, `coder`, `reviewer`. The task: 'Add a new utility function to a codebase, with tests.'"

Architecture:
1. **Orchestrator** — top-level `ClaudeSDKClient`. System prompt: "Decompose the task, dispatch sub-agents, handle failures, aggregate." Configured with `agents={"researcher": ..., "coder": ..., "reviewer": ...}`.
2. **`researcher` sub-agent** — `AgentDefinition` with read-only tools (`grep`, `read_file`), model = `haiku` (cheap, fast). Job: find existing patterns in the codebase.
3. **`coder` sub-agent** — tools include `write_file`, model = `sonnet`. Job: implement the utility based on researcher's findings.
4. **`reviewer` sub-agent** — read-only tools, model = `sonnet`, system prompt is adversarial. Job: review the coder's output. Returns `{accept, critique}`.
5. **Failure handling** — if reviewer rejects twice, orchestrator escalates to a human approval gate (Ch 10 pattern).

```python
from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, ClaudeSDKClient

options = ClaudeAgentOptions(
    system_prompt="You orchestrate three specialist sub-agents...",
    agents={
        "researcher": AgentDefinition(
            description="Read-only codebase exploration",
            prompt="You explore the codebase to find existing patterns. Return a fact list.",
            tools=["Grep", "Read"],
            model="haiku",
        ),
        "coder": AgentDefinition(
            description="Implements the new utility",
            prompt="You write code that matches existing patterns. Use Write only.",
            tools=["Write", "Read"],
            model="sonnet",
        ),
        "reviewer": AgentDefinition(
            description="Adversarial review of coder's output",
            prompt="You critique. Default to skeptical. Return JSON {accept, critique}.",
            tools=["Read"],
            model="sonnet",
        ),
    },
    max_turns=30,
)
```

> **Predict before running:** "Where in this design does the orchestrator decide which sub-agent to call? Not in the Python — in the SDK runtime. Trace the path."

(Expected: the orchestrator's model output contains tool-call blocks targeting the Task tool with `subagent_type="researcher"` etc. The SDK runtime intercepts those, spawns a fresh sub-agent context per call, runs it to completion, returns the result back to the orchestrator's conversation. The orchestrator never sees the sub-agent's internal turns — just the final result.)

Force a failure: make the `coder` sub-agent's first attempt subtly wrong. Watch the orchestrator → reviewer → orchestrator → coder loop play out.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Articulate, in writing, the persona of each of your three sub-agents. For each: (1) what's its scope, (2) what tools does it have and why, (3) what model tier and why, (4) what's its failure response when its parent — the orchestrator — gets a rejection on its output?"

(Look for crisp persona definitions, justified tool scopes, model-tier reasoning (haiku for cheap reads, sonnet for generation/review), and failure-response coherence. If Ram says "I'd use the same model for all three," push: that's expensive and loses the specialization signal.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=subagent_persona_design`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:An orchestrator is a sub-agent designer first, a runtime dispatcher second. The persona of each sub-agent is the architecture. The orchestrator's system prompt is the conducting score.]`

---

## Architect's Reflection — Capstone Synthesis

You've now built every pattern in this course. The orchestrator integrates them:

| Trait / Pattern | Where it appears in the orchestrator |
|---|---|
| Goal (Ch 2) | Top-level task goal, plus per-sub-agent goal predicates |
| Composition (Ch 3) | Sequencing sub-agent calls; result aggregation |
| Iteration (Ch 4) | Orchestrator loop until task complete or escalation |
| Perception (Ch 5) | Sub-agents' read tools; orchestrator sees only summaries |
| Reasoning (Ch 6) | Orchestrator plan-before-dispatch; sub-agents structured outputs |
| Action (Ch 7) | `coder` write tool; permission gates per sub-agent |
| Evals (Ch 8) | Eval set now scores end-to-end orchestrator runs |
| Verifier (Ch 9) | `reviewer` IS the verifier — a sub-agent role |
| Recovery (Ch 10) | Orchestrator-level retry/re-plan/escalate dispatcher |
| Memory + Contract (Ch 11) | Shared state between orchestrator and sub-agents via the SDK's session mechanism |

Five orchestrator-specific design rules:

1. **Sub-agent scope = lowest-common-denominator tools.** If a sub-agent only needs `read`, don't give it `write`. Tight scope reduces failure modes and reasoning load.

2. **Model tier per sub-agent.** Cheap models for cheap tasks (reads, classifications). Expensive models for generation and judgment. A blanket "use sonnet for everything" is the most common cost mistake in multi-agent systems.

3. **Result aggregation is its own design.** What shape does each sub-agent return? How does the orchestrator combine partial results? When are conflicts possible (two sub-agents return contradictory facts), and how are they resolved? This is the place new bugs are born.

4. **Decomposition is not free.** Some tasks lose information at the sub-agent boundary because context can't transfer cleanly. If sub-agent A's nuance is needed by sub-agent B, you have two options: pass it through the orchestrator (loses fidelity), or merge them (lose specialization). Choose deliberately.

5. **When NOT to use sub-agents.** If the task is short, the steps are known, and one model can hold all context — use a single agent. Sub-agents are for: parallel work, role-specialized scope, cost optimization via tier mixing, and contextual isolation (sub-agent sees ONLY what it needs).

## Exit Check — Course Complete

You can take a real, novel task — say, "Build a tool that watches a directory and auto-formats new Python files" — and architect end to end:
- Single agent vs multi-agent
- Goal predicate
- Tool surface (descriptions, schemas)
- `permission_mode` and hooks
- Iteration loop with exit conditions
- Verifier loop
- Failure dispatcher
- Persistent state if any
- If multi-agent: sub-agent personas, model tiers, contracts

You can also score your design against an eval set you write yourself, and iterate based on the scores rather than vibes.

If you can do all of the above unaided — you've completed the course. Welcome to architecting agents.

`[COURSE_COMPLETE]`
