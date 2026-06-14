"""
Chapter 12 — Orchestrator + Sub-Agents (capstone).

One orchestrator. Three sub-agents:
    researcher  -> read-only exploration, haiku tier
    coder       -> write capability, sonnet tier
    reviewer    -> adversarial read-only critic, sonnet tier

Decisions made before any model call:
    1. Decomposition       — research -> code -> review, sequential
    2. Sub-agent persona   — distinct system prompts per AgentDefinition.prompt
    3. Routing             — orchestrator emits Task tool calls with subagent_type
    4. Failure handling    — reviewer reject -> coder rework; 2 strikes -> escalate
    5. Aggregation         — orchestrator collects sub-agent outputs; final = reviewer-accepted code

The orchestrator's *system prompt* is the conducting score. Treat it as such.
"""

import anyio

from claude_agent_sdk import (
    AgentDefinition,
    ClaudeSDKClient,
    ClaudeAgentOptions,
)


ORCHESTRATOR_PROMPT = """\
You orchestrate three specialist sub-agents to add a small utility function
to a Python codebase with a passing test.

WORKFLOW:
  1. Dispatch the `researcher` sub-agent to find existing utility patterns
     in the project (naming, docstring style, test layout).
  2. Dispatch the `coder` sub-agent to write a new utility plus a pytest test,
     matching the patterns the researcher found.
  3. Dispatch the `reviewer` sub-agent to critique the coder's output.
  4. If the reviewer rejects, send the critique back to the coder for one
     rework attempt. If the reviewer rejects the rework too, STOP and report
     a human-escalation-needed message — do NOT loop further.

RULES:
  - Always start with the researcher.
  - Never call the coder without the researcher's findings in scope.
  - Never accept the final result without the reviewer's accept.
  - Be terse in your own messages. The sub-agents do the heavy work.
"""


def build_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt=ORCHESTRATOR_PROMPT,
        agents={
            "researcher": AgentDefinition(
                description="Read-only codebase exploration. Cheap tier.",
                prompt=(
                    "You explore the codebase. Return a SHORT bulleted fact list: "
                    "naming conventions, docstring style, test framework, test layout. "
                    "No prose, no recommendations — facts only."
                ),
                tools=["Grep", "Read", "Glob"],
                model="haiku",
            ),
            "coder": AgentDefinition(
                description="Implements the new utility + test.",
                prompt=(
                    "You receive a fact list and a feature request. Produce a single "
                    "Python file containing the utility and a pytest test. Match the "
                    "conventions in the fact list. Return ONLY the final file content."
                ),
                tools=["Read", "Write"],
                model="sonnet",
            ),
            "reviewer": AgentDefinition(
                description="Adversarial review. Default skeptical.",
                prompt=(
                    "You are an adversarial reviewer. Review the coder's output for "
                    "correctness, convention match, test coverage. Reply with JSON "
                    '{"accept": bool, "critique": str}. No prose outside the JSON.'
                ),
                tools=["Read"],
                model="sonnet",
            ),
        },
        max_turns=30,
    )


async def main():
    options = build_options()
    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "Add a `slugify(text: str) -> str` utility to the project. It should lowercase, "
            "replace whitespace with hyphens, and strip non-alphanumeric chars. Include a pytest."
        )
        async for message in client.receive_response():
            print(message)


if __name__ == "__main__":
    anyio.run(main)
