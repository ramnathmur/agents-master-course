"""
Chapter 2 — LLM Call + Goal.

Goal-orientation = goal-in-prompt + verifier-in-code.
The verifier MUST be independent of the model (deterministic Python here).

Run with two inputs and observe both:
    - the True case (goal met)
    - the False case (goal missed) — no retry yet (that's Chapter 4).
"""

import anyio
from claude_agent_sdk import query, ClaudeAgentOptions

from shared.goal_predicates import matches_regex


# Goal: extract a city name. Verifier: output matches a Title-Case word pattern.
GOAL_PROMPT_TEMPLATE = (
    "Extract the city name from the sentence below. "
    "Reply with ONLY the city name. Nothing else.\n\n"
    "Sentence: {sentence}"
)

# Predicate: a single capitalised word, 2-30 characters, no punctuation.
is_city_like = matches_regex(r"^[A-Z][a-zA-Z]{1,29}$")


async def run(sentence: str) -> tuple[str, bool]:
    options = ClaudeAgentOptions(
        system_prompt="You extract entities. Reply with only the requested entity.",
        max_turns=1,
    )
    full_text = ""
    async for message in query(
        prompt=GOAL_PROMPT_TEMPLATE.format(sentence=sentence),
        options=options,
    ):
        # In practice you'd inspect message types; here we collect text content.
        full_text += str(message)
    cleaned = full_text.strip()
    return cleaned, is_city_like(cleaned)


async def main():
    cases = [
        "I flew to Mumbai last week.",
        "I love long walks.",
    ]
    for sentence in cases:
        output, ok = await run(sentence)
        verdict = "GOAL MET" if ok else "GOAL MISSED"
        print(f"\nInput:  {sentence}")
        print(f"Output: {output!r}")
        print(f"        {verdict}")


if __name__ == "__main__":
    anyio.run(main)
