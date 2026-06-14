"""
Chapter 11 — Two-agent system with persistent shared state.

v2: Researcher writes facts to state.json, then marks the 'research' phase
complete. Writer waits for that phase, reads facts, produces a brief, writes
to state['artifacts'].

v3 revision: adds a second main flow that demonstrates restart resilience
in action (Review E1). The contract from Chapter 10 (file-backed state +
phase flags) implies a property: a Researcher restarted mid-phase must
resume from existing facts, not redo them. v3 simulates a kill mid-research
by directly appending two facts via state_store, raising an exception, then
calling run_researcher again. The agent observes the existing facts on disk
and appends rather than restarting — same agent code, no resume flag, no
checkpoint API. The persistence layer carries the resumability.

The contract IS the architecture:
    storage  -> file (state.json)
    schema   -> shared/state_store.py (schema_version=1)
    protocol -> 'research' phase boolean flag
"""

import anyio
import json
from pathlib import Path

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
)
from shared import state_store


STATE_PATH = Path("./state.json").resolve()


# ---------- tools for the researcher ----------

@tool(
    "append_fact",
    "Append a single fact to the shared state store. Each call adds one fact "
    "with a source. Use multiple calls for multiple facts.",
    {"fact": str, "source": str},
)
async def append_fact(args):
    state_store.append_facts(
        [{"fact": args["fact"], "source": args["source"]}], STATE_PATH
    )
    return {"content": [{"type": "text", "text": "fact appended"}]}


@tool(
    "mark_research_complete",
    "Call ONLY after you have appended at least 3 facts. Marks research phase done.",
    {},
)
async def mark_research_complete(args):
    state_store.mark_phase_complete("research", STATE_PATH)
    return {"content": [{"type": "text", "text": "research phase marked complete"}]}


# ---------- tools for the writer ----------

@tool(
    "read_all_facts",
    "Read every fact recorded by the researcher. Returns a JSON list.",
    {},
)
async def read_all_facts(args):
    state = state_store.read_state(STATE_PATH)
    return {"content": [{"type": "text", "text": json.dumps(state["facts"])}]}


@tool(
    "save_brief",
    "Save the final 300-word brief to state.artifacts.brief.",
    {"brief": str},
)
async def save_brief(args):
    state = state_store.read_state(STATE_PATH)
    state["artifacts"]["brief"] = args["brief"]
    state_store.mark_phase_complete("writing", STATE_PATH)
    state_store.write_state(state, STATE_PATH)
    return {"content": [{"type": "text", "text": "brief saved"}]}


# ---------- agents ----------

async def run_researcher(topic: str) -> None:
    server = create_sdk_mcp_server(
        name="research",
        version="1.0.0",
        tools=[append_fact, mark_research_complete],
    )
    # The system prompt teaches the agent to inspect state before acting.
    # This is the resumability hook: existing facts are visible via the
    # state file on disk; the agent decides how many more to add. We do
    # not need a separate "resume" code path.
    options = ClaudeAgentOptions(
        system_prompt=(
            "You are the Researcher. Produce 3-5 concise factual claims about the topic. "
            "Call append_fact for EACH fact (one call per fact). When done, "
            "call mark_research_complete. Do NOT write any prose to the user."
        ),
        mcp_servers={"research": server},
        allowed_tools=[
            "mcp__research__append_fact",
            "mcp__research__mark_research_complete",
        ],
        max_turns=10,
    )
    # If facts already exist on disk, tell the agent — otherwise it will
    # happily duplicate work. The state file is the source of truth; the
    # prompt just surfaces it.
    existing = state_store.read_state(STATE_PATH)["facts"]
    prompt = f"Topic: {topic}"
    if existing:
        prompt += (
            f"\n\nThe state store already contains {len(existing)} facts from a "
            f"prior (interrupted) run. Do not duplicate them. Append only new "
            f"facts to reach 3-5 total, then mark_research_complete. Existing: "
            f"{json.dumps(existing)}"
        )
    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)
        async for _ in client.receive_response():
            pass


async def run_writer(topic: str) -> None:
    if not state_store.is_phase_complete("research", STATE_PATH):
        print("[writer] research phase not complete — aborting")
        return
    server = create_sdk_mcp_server(
        name="writing",
        version="1.0.0",
        tools=[read_all_facts, save_brief],
    )
    options = ClaudeAgentOptions(
        system_prompt=(
            "You are the Writer. First call read_all_facts. Then compose a "
            "~300-word brief in plain prose. Then call save_brief with the result."
        ),
        mcp_servers={"writing": server},
        allowed_tools=[
            "mcp__writing__read_all_facts",
            "mcp__writing__save_brief",
        ],
        max_turns=10,
    )
    async with ClaudeSDKClient(options=options) as client:
        await client.query(f"Topic: {topic}")
        async for _ in client.receive_response():
            pass


# ---------- demos ----------

class SimulatedKill(Exception):
    """Stand-in for SIGINT/SIGTERM. We raise this synthetically so the
    chapter can demonstrate restart behavior without actually killing the
    process. The handling pattern is identical to a real interrupt."""


async def _partial_research_then_die() -> None:
    # Bypass the agent entirely and write two facts directly through the
    # state store. This simulates "the Researcher got 2 facts in before
    # being killed" without the cost or non-determinism of running the
    # real model and racing a cancellation. The persistence layer is what
    # we are stress-testing, not the model.
    state_store.append_facts(
        [
            {
                "fact": "The southwest monsoon delivers roughly 75% of India's annual rainfall.",
                "source": "simulated-prior-run",
            },
            {
                "fact": "Kharif crops such as rice and cotton are sown with the monsoon's onset in June.",
                "source": "simulated-prior-run",
            },
        ],
        STATE_PATH,
    )
    raise SimulatedKill("researcher process terminated mid-phase")


async def main_clean() -> None:
    """The Chapter 10 baseline: fresh state, Researcher then Writer."""
    topic = "the monsoon's effect on Indian agriculture"

    state_store.reset_state(STATE_PATH)

    print("\n[main_clean] researcher starting")
    await run_researcher(topic)
    state = state_store.read_state(STATE_PATH)
    print(f"[main_clean] researcher produced {len(state['facts'])} facts")

    print("[main_clean] writer starting")
    await run_writer(topic)
    state = state_store.read_state(STATE_PATH)
    print("\n=== main_clean: final brief ===")
    print(state["artifacts"].get("brief", "(no brief produced)"))


async def main_with_simulated_kill() -> None:
    """Restart resilience demo. Reset state, write 2 facts then crash,
    restart the Researcher, finish with the Writer. The Researcher
    should see 2 facts already present and only append the remainder —
    not redo the first two."""
    topic = "the monsoon's effect on Indian agriculture"

    state_store.reset_state(STATE_PATH)

    print("\n[main_kill] simulating partial researcher run that dies after 2 facts")
    try:
        await _partial_research_then_die()
    except SimulatedKill as e:
        # In production this is where you'd see "process killed (signal 9)"
        # in your supervisor's log. The state file survived. That's the
        # whole point of the file-backed contract from Chapter 10.
        print(f"[main_kill] caught: {e}")

    pre = state_store.read_state(STATE_PATH)
    print(f"[main_kill] state survived crash with {len(pre['facts'])} facts")

    print("[main_kill] restarting researcher — it should append, not restart")
    await run_researcher(topic)
    post = state_store.read_state(STATE_PATH)
    print(f"[main_kill] researcher now has {len(post['facts'])} facts total "
          f"(should be > {len(pre['facts'])})")

    print("[main_kill] writer starting")
    await run_writer(topic)
    state = state_store.read_state(STATE_PATH)
    print("\n=== main_kill: final brief ===")
    print(state["artifacts"].get("brief", "(no brief produced)"))


async def main() -> None:
    # Run the clean flow first to establish the baseline, then run the
    # crash-recovery flow. Each call starts with reset_state so the two
    # demos do not contaminate each other.
    await main_clean()
    await main_with_simulated_kill()


if __name__ == "__main__":
    anyio.run(main)
