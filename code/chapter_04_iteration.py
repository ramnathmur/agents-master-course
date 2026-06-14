"""
Chapter 4 — Iteration Until Goal Achieved + context engineering  [v2]

REVISION v1 -> v2 (Review R3):
    v1 had only main(). The chapter's headline second concept — context
    engineering / compaction — lived only in prose. v2 keeps main() as the
    unbounded baseline AND adds:

        - per-iteration token estimate logging (so you SEE context growth),
        - main_with_compaction() that keeps only the last K turns
          (sliding-window compaction).

    Run both and compare the token-estimate columns. That's the architect's
    moment: context rot becomes a number, not a vibe.
"""

import anyio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from shared.goal_predicates import word_count_equals


GOAL_WORD_COUNT = 7
goal_met = word_count_equals(GOAL_WORD_COUNT)


def estimate_tokens(text: str) -> int:
    """Crude approximation: ~4 chars per token. Real production should use the
    SDK's tokenizer; this is enough to make context growth legible."""
    return max(1, len(text) // 4)


def format_failure_feedback(attempt: str, target_words: int) -> str:
    got = len(attempt.split())
    return (
        f"<previous_attempt got_word_count={got} target_word_count={target_words}>"
        f"{attempt}</previous_attempt>\n"
        f"Adjust to exactly {target_words} words. Reply with the sentence only."
    )


# ---------- baseline: unbounded growth ----------

async def main_unbounded():
    """Original v1 loop. Conversation history grows without bound.
    Token estimate logged so you can WATCH the rot."""
    options = ClaudeAgentOptions(
        system_prompt=(
            "You write a single English sentence describing a sunrise. "
            "Reply with only the sentence."
        ),
        max_turns=12,
    )
    task = "Write a sentence about sunrise."
    cumulative_text = task
    max_iterations = 8

    print("\n=== main_unbounded (no compaction) ===")
    print(f"{'iter':>4} {'words':>5} {'cum_tokens(est)':>15}  attempt")

    async with ClaudeSDKClient(options=options) as client:
        await client.query(task)
        for iteration in range(max_iterations):
            response = ""
            async for message in client.receive_response():
                response += str(message)
            attempt = response.strip()
            cumulative_text += attempt
            print(f"{iteration+1:>4} {len(attempt.split()):>5} "
                  f"{estimate_tokens(cumulative_text):>15}  {attempt[:60]!r}")
            if goal_met(attempt):
                print("GOAL MET")
                return
            feedback = format_failure_feedback(attempt, GOAL_WORD_COUNT)
            cumulative_text += feedback
            await client.query(feedback)
        print("EXIT: turn cap reached")


# ---------- compacted: sliding window ----------

async def main_with_compaction(window_turns: int = 2):
    """Sliding-window compaction: each new query starts a FRESH ClaudeSDKClient,
    but we re-inject only the last `window_turns` of (attempt, feedback) pairs
    as a compressed preamble. The conversation history per call stays bounded.

    Tradeoff (chapter Architect's Reflection #3):
        - Cheap: no extra LLM call.
        - Loses goal memory across very long runs.
        - Doesn't catch model reasoning fixation on earlier wrong outputs.
    """
    system_prompt = (
        "You write a single English sentence describing a sunrise. "
        "Reply with only the sentence."
    )
    task = "Write a sentence about sunrise."
    history: list[tuple[str, str]] = []   # list of (attempt, feedback)
    max_iterations = 8

    print(f"\n=== main_with_compaction (window={window_turns}) ===")
    print(f"{'iter':>4} {'words':>5} {'window_tokens(est)':>18}  attempt")

    for iteration in range(max_iterations):
        # Compact: keep only the last `window_turns` (attempt, feedback) pairs.
        window = history[-window_turns:]
        preamble = "\n".join(
            f"<prior_attempt>{a}</prior_attempt>\n<prior_feedback>{f}</prior_feedback>"
            for a, f in window
        )
        prompt = f"{preamble}\n\n{task}" if preamble else task
        window_token_est = estimate_tokens(prompt)

        options = ClaudeAgentOptions(system_prompt=system_prompt, max_turns=2)
        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            response = ""
            async for message in client.receive_response():
                response += str(message)
        attempt = response.strip()
        print(f"{iteration+1:>4} {len(attempt.split()):>5} "
              f"{window_token_est:>18}  {attempt[:60]!r}")
        if goal_met(attempt):
            print("GOAL MET")
            return
        feedback = format_failure_feedback(attempt, GOAL_WORD_COUNT)
        history.append((attempt, feedback))
    print("EXIT: turn cap reached")


async def main():
    await main_unbounded()
    await main_with_compaction(window_turns=2)
    print("\n[compare] notice how cum_tokens grows linearly in the baseline but "
          "stays bounded in the compacted run. That difference is what context "
          "engineering buys you.")


if __name__ == "__main__":
    anyio.run(main)
