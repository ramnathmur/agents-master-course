"""
Chapter 11 — Native SDK session continuation (companion to chapter_11_two_agent.py).

Revision note (v2/v3, Review E5): the main Ch 11 file teaches cross-process
durability via state.json. That mechanism exists because the SDK does not (yet)
expose a public resume-by-ID API across process boundaries. This companion
isolates the OTHER half of the picture: the SDK's *native, in-process* session
continuation, which is implicit in the ClaudeSDKClient context manager.

The architectural point:
    - One `async with ClaudeSDKClient(...) as client:` block IS one session.
    - Inside that block, every `await client.query(...)` shares turn history
      with the previous queries. No resume token, no replay — the client
      object holds the conversation.
    - When the `async with` exits, that session is gone. A fresh
      ClaudeSDKClient is a fresh conversation with zero memory of the prior one.

That second bullet is the seam Ch 11's state.json bridges. The SDK gives you
in-memory continuity for free; you only reach for an external state store when
you need to cross a process boundary, a crash, or an agent handoff.

Run this script to see both halves: same-client memory works, new-client memory
does not. Then re-read chapter_11_two_agent.py to see why state.json earns its
keep at the agent-to-agent boundary.
"""

import anyio

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


# Keep the agent terse so the demo output is readable. The system prompt is
# identical across both clients — the only variable under test is the client
# lifetime, not the prompt.
OPTIONS = ClaudeAgentOptions(
    system_prompt=(
        "You are a terse assistant. Answer in one short sentence. "
        "If asked what you were just called, quote the exact name back."
    ),
    max_turns=4,
)


async def collect_text(client: ClaudeSDKClient) -> str:
    """Drain one response stream into a single string.

    Why a helper: receive_response() yields message blocks, not a final string.
    Every call site needs the same drain pattern, so it lives here once.
    """
    chunks: list[str] = []
    async for message in client.receive_response():
        # We only care about assistant text for this demo. Tool calls and
        # system messages are not part of what we're illustrating.
        blocks = getattr(message, "content", None)
        if not blocks:
            continue
        for block in blocks:
            text = getattr(block, "text", None)
            if text:
                chunks.append(text)
    return "".join(chunks).strip()


async def same_client_two_turns() -> None:
    """Demonstrate that one ClaudeSDKClient context = one continuous session.

    The second query never restates the name. If the SDK is doing its job,
    the model recalls it from in-memory turn history held by `client`.
    """
    print("\n--- same-client, two turns (expect: remembers) ---")
    async with ClaudeSDKClient(options=OPTIONS) as client:
        await client.query("I am going to call you Atlas. Acknowledge in one word.")
        turn1 = await collect_text(client)
        print(f"[turn 1] {turn1}")

        await client.query("What did I just call you?")
        turn2 = await collect_text(client)
        print(f"[turn 2] {turn2}")


async def new_client_loses_memory() -> None:
    """Demonstrate the boundary: a fresh client has no access to prior turns.

    This is the gap chapter_11_two_agent.py closes with state.json. The SDK
    will not transparently rehydrate the prior conversation just because you
    constructed a new client with the same options.
    """
    print("\n--- new client, same question (expect: does NOT remember) ---")
    async with ClaudeSDKClient(options=OPTIONS) as client:
        await client.query("What did I just call you?")
        answer = await collect_text(client)
        print(f"[fresh client] {answer}")


async def main() -> None:
    await same_client_two_turns()
    await new_client_loses_memory()

    # The summary is the lesson. Print it explicitly so a learner reading the
    # script output (not just the source) walks away with the contrast.
    print(
        "\n=== takeaway ===\n"
        "The SDK gives you in-process continuation for free: every query "
        "inside one ClaudeSDKClient context shares turn history. That is the\n"
        "native mechanism. It costs nothing and needs no IDs.\n\n"
        "What it does NOT give you, and what chapter_11_two_agent.py's "
        "state.json provides:\n"
        "  1. Durability across process restarts (kill the script, resume later).\n"
        "  2. Handoff between two DIFFERENT agents with different system prompts\n"
        "     (Researcher -> Writer) without replaying the full transcript.\n"
        "  3. A typed, inspectable contract (schema_version, phases, artifacts)\n"
        "     that survives outside the SDK's memory.\n"
        "Reach for state.json when you cross one of those three boundaries. "
        "Until then, the client context is enough."
    )


if __name__ == "__main__":
    anyio.run(main)
