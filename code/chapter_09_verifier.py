"""
Chapter 9 — Verifier / Critic loop.

The actor produces an answer. A SEPARATE query() call (fresh context, adversarial
system prompt) reviews it. Output blocked if critic rejects or confidence is low.

Calibrate the critic with known-bad outputs before trusting its accepts.
"""

import anyio
import json
import re
from claude_agent_sdk import query, ClaudeSDKClient, ClaudeAgentOptions


CRITIC_SYSTEM = (
    "You are an adversarial reviewer. Default to skeptical. "
    "Given a task and an answer, find what's wrong with the answer. "
    'Reply with ONLY a JSON object: {"accept": bool, "confidence": float in [0,1], "critique": str}. '
    "No prose outside the JSON."
)


async def actor_run(task: str) -> str:
    options = ClaudeAgentOptions(
        system_prompt="You answer questions concisely in one sentence.",
        max_turns=1,
    )
    async with ClaudeSDKClient(options=options) as client:
        await client.query(task)
        text = ""
        async for message in client.receive_response():
            text += str(message)
    return text.strip()


async def critic_review(task: str, answer: str) -> dict:
    """Separate call. Fresh context. Different system prompt."""
    prompt = (
        f"<task>{task}</task>\n<candidate_answer>{answer}</candidate_answer>\n"
        "Review the candidate answer."
    )
    options = ClaudeAgentOptions(system_prompt=CRITIC_SYSTEM, max_turns=1)
    text = ""
    async for message in query(prompt=prompt, options=options):
        text += str(message)

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {"accept": False, "confidence": 0.0, "critique": "non-json critic output"}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"accept": False, "confidence": 0.0, "critique": "json parse failed"}


async def commit_or_block(task: str, accept_threshold: float = 0.7) -> tuple[str, bool]:
    answer = await actor_run(task)
    verdict = await critic_review(task, answer)
    accepted = verdict.get("accept", False) and verdict.get("confidence", 0.0) >= accept_threshold
    print(f"\nTASK: {task}")
    print(f"ANSWER: {answer}")
    print(f"VERDICT: {verdict}")
    print(f"COMMITTED: {accepted}")
    return answer, accepted


async def main():
    tasks = [
        "What is the capital of France?",
        "In one sentence, summarise Newton's third law.",
        # Try a fuzzier task to see the critic disagree more often.
        "In one sentence, define 'agency' for a software agent.",
    ]
    for t in tasks:
        await commit_or_block(t)


if __name__ == "__main__":
    anyio.run(main)
