"""
Chapter 5 — Perceive: read-only tools as sensors.  [v3]

REVISION v1 -> v3:
    v1 had a single read_file_v_a tool and a commented-out v_b. The learner
    had to manually swap and re-run — the comparison happened in their head,
    not on screen. The chapter's measurable claim (rich tool descriptions
    produce shorter, more focused tool use) was unfalsifiable from one run.

    v3 registers BOTH tools under different names with real implementations,
    spins up two separate MCP servers (each exposing exactly one), runs the
    same task against both, and prints a turn-count delta at the end. The
    insight from Chapter 4 (token estimates over prose) carries forward:
    the description-quality effect becomes a number, not a vibe.
"""

import anyio
from pathlib import Path

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
)


# Sparse description — the agent has to guess what this sensor sees.
# Expect: more probing, more error-recovery turns, sometimes wrong file types.
@tool(
    "read_file_sparse",
    "Read a file.",
    {"path": str},
)
async def read_file_sparse(args):
    text = Path(args["path"]).read_text(encoding="utf-8")
    return {"content": [{"type": "text", "text": text}]}


# Rich description — answers the 4 questions a caller silently asks:
# what does it read, what does it return, when is it valid, when does it fail.
# Expect: fewer turns, no wasted probing, no binary-file mistakes.
@tool(
    "read_file_rich",
    "Read the contents of a UTF-8 text file from the project directory. "
    "Returns the full text as a string. Use only for files under 100KB. "
    "Do NOT use for binary files (images, executables) — it will raise.",
    {"path": str},
)
async def read_file_rich(args):
    text = Path(args["path"]).read_text(encoding="utf-8")
    return {"content": [{"type": "text", "text": text}]}


TASK = "What does ROADMAP.md say in its first phase?"


async def _run_with(tool_fn, tool_name: str, label: str) -> int:
    """Run TASK against a server exposing exactly one tool. Return turn count.

    Returning a scalar (not prose) is deliberate — Chapter 4 established that
    architecture deltas should be numeric. Description quality is no exception.
    """
    server = create_sdk_mcp_server(
        name="perception",
        version="1.0.0",
        tools=[tool_fn],
    )

    options = ClaudeAgentOptions(
        system_prompt="You answer questions about files. Use the available tool when needed.",
        mcp_servers={"perception": server},
        allowed_tools=[f"mcp__perception__{tool_name}"],
        max_turns=5,
    )

    print(f"\n=== {label} (tool: {tool_name}) ===")
    turns = 0
    async with ClaudeSDKClient(options=options) as client:
        await client.query(TASK)
        async for message in client.receive_response():
            turns += 1
            print(message)
    print(f"[{label}] message turns: {turns}")
    return turns


async def main_sparse() -> int:
    return await _run_with(read_file_sparse, "read_file_sparse", "SPARSE")


async def main_rich() -> int:
    return await _run_with(read_file_rich, "read_file_rich", "RICH")


async def main():
    sparse_turns = await main_sparse()
    rich_turns = await main_rich()
    delta = sparse_turns - rich_turns
    print(
        f"\n[compare] sparse={sparse_turns} turns, rich={rich_turns} turns, "
        f"delta={delta:+d}. The tool description IS the agent's mental model — "
        f"answer the 4 questions (what, returns, when valid, when fails) and "
        f"you spend fewer turns on probing."
    )


if __name__ == "__main__":
    anyio.run(main)
