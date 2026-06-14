"""
Chapter 06 — Reason: structured plan-before-act + tool design  [v3]

REVISION v1 -> v2 (Review R4):
    v1's "tight" schema was {"steps": list} — exactly the kind of loose
    declaration the chapter criticizes. v2 fixes the self-undercutting bug:
    the tight tool now validates the FULL inner shape on every call
    (action is an enum, target and expected_outcome are non-empty strings,
    each step's fields are checked), and rejects malformed inputs with a
    structured error. Sloppy tool is unchanged so the contrast still works.

REVISION v2 -> v3 (Review R5):
    v2 demonstrated server-side validation but only ran ONE happy path,
    so the REJECT branch was theoretical. v3 splits main() into two
    runs that share the same tools and server:

        main_valid()      — agent submits a well-formed plan; tight tool
                            accepts on first call. Baseline.
        main_malformed()  — system prompt nudges the model to omit
                            `expected_outcome` on the FIRST call. The
                            REJECT message becomes a teaching signal:
                            the model reads the error, fixes the shape,
                            and resubmits. The whole loop happens inside
                            the same client session.

    The two runs together make the chapter's argument visible: a tight
    schema is not just a guardrail — it is an inline tutor that corrects
    the model mid-thought, as in chapter 4's iteration-until-goal pattern
    but at the TOOL boundary instead of the prompt boundary.
"""

import anyio

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
)


ALLOWED_ACTIONS = {"read", "write", "analyze", "communicate"}


# ---------- sloppy: accepts whatever ----------

@tool(
    "make_plan_sloppy",
    "Submit a plan for a task.",
    {"plan": str},
)
async def make_plan_sloppy(args):
    return {"content": [{"type": "text", "text": f"plan accepted: {args['plan']}"}]}


# ---------- tight: enforces the full inner shape ----------

def _validate_step(idx: int, step) -> str | None:
    """Return None if valid; an error string otherwise."""
    if not isinstance(step, dict):
        return f"step #{idx} is not an object"
    missing = {"action", "target", "expected_outcome"} - step.keys()
    if missing:
        return f"step #{idx} missing required fields: {sorted(missing)}"
    action = step["action"]
    if action not in ALLOWED_ACTIONS:
        return (f"step #{idx} action={action!r} is not one of "
                f"{sorted(ALLOWED_ACTIONS)}")
    if not isinstance(step["target"], str) or not step["target"].strip():
        return f"step #{idx} target must be a non-empty string"
    if not isinstance(step["expected_outcome"], str) or not step["expected_outcome"].strip():
        return f"step #{idx} expected_outcome must be a non-empty string"
    return None


@tool(
    "make_plan_tight",
    "Submit a structured plan. Each step is an object with three required "
    "fields: "
    "  action (one of read | write | analyze | communicate), "
    "  target (non-empty string naming the file / URL / entity), "
    "  expected_outcome (non-empty string — the per-step success criterion).",
    {"steps": list},
)
async def make_plan_tight(args):
    steps = args.get("steps")
    if not isinstance(steps, list) or len(steps) == 0:
        return {"content": [{"type": "text",
                "text": "REJECT: 'steps' must be a non-empty list of step objects."}]}
    for idx, step in enumerate(steps):
        err = _validate_step(idx, step)
        if err:
            return {"content": [{"type": "text",
                    "text": f"REJECT: {err}. Reformat and resubmit."}]}
    summary = "\n".join(
        f"  {i+1}. [{s['action']}] {s['target']}  -> expect: {s['expected_outcome']}"
        for i, s in enumerate(steps)
    )
    return {"content": [{"type": "text", "text": f"plan accepted:\n{summary}"}]}


# A single server instance is reused across both runs. Tools are stateless,
# so there's no cross-run leakage; this just avoids the noise of re-creating
# the MCP server twice in the demo output.
def _build_server():
    return create_sdk_mcp_server(
        name="planning",
        version="1.0.0",
        tools=[make_plan_sloppy, make_plan_tight],
    )


_ALLOWED_TOOLS = [
    "mcp__planning__make_plan_sloppy",
    "mcp__planning__make_plan_tight",
]


# ---------- run 1: clean acceptance ----------

async def main_valid():
    """Happy path. The system prompt fully describes the schema, so the
    model's first make_plan_tight call should validate and return
    'plan accepted'. This is the control case — without it, the rejection
    run below has nothing to be contrasted against."""
    options = ClaudeAgentOptions(
        system_prompt=(
            "You ALWAYS call make_plan_tight before any other action. "
            "Each step must have action (read|write|analyze|communicate), "
            "target, and expected_outcome. If make_plan_tight returns REJECT, "
            "fix the validation error and resubmit."
        ),
        mcp_servers={"planning": _build_server()},
        allowed_tools=_ALLOWED_TOOLS,
        max_turns=4,
    )

    print("\n=== main_valid (well-formed first attempt expected) ===")
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Plan a 3-day trip to Goa for a solo traveler.")
        async for message in client.receive_response():
            print(message)


# ---------- run 2: rejection-as-teaching-signal ----------

async def main_malformed():
    """Force a malformed first attempt, then watch the loop self-correct.

    The system prompt deliberately under-specifies the schema — it names
    `action` and `target` but omits `expected_outcome`, and adds a
    suggestion ("keep each step compact, two fields are enough") that
    biases the model toward dropping the third field on call #1.

    When the tight tool returns REJECT with the structured error string,
    the model has everything it needs to repair the shape and resubmit
    inside the same session. The REJECT message itself becomes the
    in-context tutor — same idea as chapter 4's iteration feedback,
    but enforced at the tool boundary instead of the prompt boundary.

    We bump max_turns to 6 so the agent has headroom for: malformed call,
    REJECT, retry, ACCEPT, optional summary turn."""
    options = ClaudeAgentOptions(
        system_prompt=(
            "You ALWAYS call make_plan_tight before any other action. "
            "Each step has an action (read|write|analyze|communicate) and a "
            "target. Keep each step compact — two fields are usually enough. "
            "If a tool returns a message starting with REJECT, read the error "
            "carefully, fix the structure exactly as the error describes, and "
            "call the tool again."
        ),
        mcp_servers={"planning": _build_server()},
        allowed_tools=_ALLOWED_TOOLS,
        max_turns=6,
    )

    print("\n=== main_malformed (rejection-resubmit loop expected) ===")
    print("Watch for: 1st call -> REJECT (missing expected_outcome), "
          "2nd call -> plan accepted.")
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Plan a 3-day trip to Goa for a solo traveler.")
        async for message in client.receive_response():
            print(message)


async def main():
    await main_valid()
    await main_malformed()
    print("\n[compare] main_valid lands on the first call; main_malformed "
          "needs the REJECT to converge. The tight schema is doing the "
          "teaching — see chapter 4 for the prompt-layer analogue.")


if __name__ == "__main__":
    anyio.run(main)
