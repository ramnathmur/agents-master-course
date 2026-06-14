"""
Chapter 3 — Chained Calls.

Workflow != agency. Python owns the sequence.
Call 1 generates a plan (JSON). Call 2 executes step 1 of the plan.

Trace the control plane:
    - Where does Python decide what call 2 is?  (the line that constructs call 2's prompt)
    - Where could Claude decide instead?         (only with a loop + a tool — Ch 4-7)
"""

import anyio
import json
from claude_agent_sdk import query, ClaudeAgentOptions


PLAN_SYSTEM = (
    "You produce ONLY valid JSON. No additional text. "
    'Output EXACTLY this shape: {"steps": [{"id": 1, "action": "read", "target": "filename", "expected_outcome": "description"}, ...]} '
    "Ensure all strings use double quotes. No trailing commas. "
    "If you cannot complete the task, still output valid empty JSON: {\"steps\": []}"
    "No prose."
)

EXEC_SYSTEM = "You execute one step of a plan. Reply with a short sentence describing the result."


async def call_for_plan(task: str) -> dict:
    options = ClaudeAgentOptions(system_prompt=PLAN_SYSTEM, max_turns=1)
    text = ""
    async for message in query(prompt=task, options=options):
        text += str(message)
    # Find the JSON block; tolerate leading/trailing noise.
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON in plan response: {text!r}")

    json_str = text[start : end + 1]

    # Attempt to parse with error handling
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # Try cleaning common JSON issues from LLM outputs
        cleaned_json = json_str.replace("'", '"')  # Replace single quotes with double quotes
        try:
            return json.loads(cleaned_json)
        except json.JSONDecodeError:
            # If cleaning didn't help, raise the original error with context
            raise ValueError(
                f"Invalid JSON in plan response. Error: {e}\n"
                f"Original: {json_str!r}\n"
                f"Cleaned: {cleaned_json!r}"
            ) from e


async def execute_step(step: dict) -> str:
    options = ClaudeAgentOptions(system_prompt=EXEC_SYSTEM, max_turns=1)
    prompt = f"Step {step['id']}: {step['action']} -> {step['target']}"
    text = ""
    async for message in query(prompt=prompt, options=options):
        text += str(message)
    return text.strip()


async def main():
    task = "Plan a 3-day trip to Goa for a solo traveler. 3 steps maximum."
    plan = await call_for_plan(task)
    print("PLAN:")
    print(json.dumps(plan, indent=2))

    # Python — not the model — picks step 0. This is the control plane.
    first_step = plan["steps"][0]
    print(f"\nEXECUTING STEP {first_step['id']}:")
    result = await execute_step(first_step)
    print(result)


if __name__ == "__main__":
    anyio.run(main)
