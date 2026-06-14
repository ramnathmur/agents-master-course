"""
Chapter 0 — Setup smoke test.

Prerequisites:
    pip install claude-agent-sdk
    claude login        # authenticate the CLI with your Claude Max account

In IntelliJ run config:
    Confirm ANTHROPIC_API_KEY is NOT set (or is empty).
    Working directory: this file's parent.

Expected output: a message containing the single word "ready".
"""

import anyio
from claude_agent_sdk import query


async def main():
    async for message in query(prompt="Reply with the single word: ready"):
        print(message)


if __name__ == "__main__":
    anyio.run(main)
