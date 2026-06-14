"""
Chapter 1 — The Bare LLM Call.

This is the primitive. No loop, no goal predicate, no tool, no memory.
A function: prompt in, completion out, return-and-die.

Every chapter from 2 onward adds STRUCTURE AROUND this call, not inside it.
"""

import anyio
from claude_agent_sdk import query


async def main():
    async for message in query(prompt="Define agency in one sentence."):
        print(message)


if __name__ == "__main__":
    anyio.run(main)
