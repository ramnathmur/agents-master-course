"""
Chapter 10 — Error Recovery, Re-Planning, and Human-in-the-Loop  [v3]

REVISION v1 -> v2 (Review R2):
    v1 defined classify_failure() but never called it. Only the HITL gate ran.
    The headline three-class dispatcher was dead code. v2 wires the dispatcher
    into a real outer loop that:

        - intercepts each tool result via PostToolUse hook,
        - classifies it (transient / structural / policy),
        - routes to retry-with-budget, re-plan-with-context, or escalate,
        - and applies the promotion rule (K retries -> reclassify as structural).

REVISION v2 -> v3 (Review E1):
    v2 wired the dispatcher but main() only fired the transient->structural
    branch. The structural-replan-exhaustion and policy-escalation branches
    were unreachable from a clean run. v3 keeps the dispatcher untouched and
    drives THREE scenarios sequentially so all three Dispatcher branches are
    visible in one execution. do_work() and hitl_gate() learn one new mode
    ('policy_block') so scenario 3 can exercise the HITL deny path.
"""

import anyio
from pathlib import Path

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher,
    tool,
    create_sdk_mcp_server,
)


SANDBOX = Path("./ch10_sandbox").resolve()
SANDBOX.mkdir(exist_ok=True)


# ---------- a tool that can fail in three different classes on demand ----------

@tool(
    "do_work",
    "Perform a unit of work. The 'mode' arg controls the failure shape, used "
    "here to exercise the recovery dispatcher.",
    {"mode": str, "payload": str},
)
async def do_work(args):
    mode = args["mode"]
    payload = args["payload"]
    if mode == "ok":
        return {"content": [{"type": "text", "text": f"ok: {payload}"}]}
    if mode == "transient":
        # Simulate timeout / rate-limit — typically retried.
        return {"content": [{"type": "text", "text": "transient: timeout after 5s"}]}
    if mode == "structural":
        return {"content": [{"type": "text", "text": "structural: schema mismatch on field X"}]}
    if mode == "policy_block":
        # The tool itself succeeds shape-wise; the HITL gate is the actual
        # gatekeeper for this mode. We still return a recognisable string
        # in case the call ever slips past the gate (defence in depth).
        return {"content": [{"type": "text", "text": "policy: human reviewer declined"}]}
    return {"content": [{"type": "text", "text": f"ok: {payload}"}]}


# ---------- failure classifier (now actually used) ----------

def classify_failure(result_text: str) -> str:
    t = result_text.lower()
    if "transient" in t or "timeout" in t or "rate limit" in t:
        return "transient"
    if "structural" in t or "schema" in t or "invalid" in t:
        return "structural"
    if "deny" in t or "approval" in t or "declined" in t:
        return "policy"
    return "ok"


# ---------- HITL gate (policy class) ----------

async def hitl_gate(input_data, tool_use_id, ctx):
    name = input_data.get("tool_name", "?")
    args = input_data.get("tool_input", {})
    # Demonstration: only auto-approve in this scripted run. Replace with
    # a real input() prompt for genuine human-in-the-loop.
    auto = args.get("mode") != "policy_block"
    print(f"[HITL] proposed call: {name}({args}) -> {'auto-approve' if auto else 'deny'}")
    if auto:
        return {}
    # A PreToolUse deny short-circuits the tool, so PostToolUse will not fire
    # with a useful payload. Seed _last_result directly so the outer dispatcher
    # can still classify this turn as 'policy'. This keeps the dispatcher
    # contract (always read _last_result after a turn) intact.
    _last_result["tool"] = name
    _last_result["text"] = "policy: human reviewer declined this action"
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Human reviewer declined this action.",
        }
    }


# ---------- PostToolUse observer that captures last result for the dispatcher ----------

_last_result: dict = {"text": "", "tool": ""}


async def capture_result(input_data, tool_use_id, ctx):
    """We capture the tool output text so the outer dispatcher can classify it."""
    name = input_data.get("tool_name", "?")
    output = input_data.get("tool_response", {}).get("content", [])
    text = " ".join(c.get("text", "") for c in output if isinstance(c, dict))
    _last_result["tool"] = name
    _last_result["text"] = text
    return {}


# ---------- dispatcher: the heart of v2 ----------

class Dispatcher:
    """Routes failure classes to retry / re-plan / escalate with budgets."""

    RETRY_CAP = 3
    REPLAN_CAP = 2

    def __init__(self):
        self.retry_count = 0
        self.replan_count = 0
        self.history: list[tuple[str, str]] = []   # (class, action)

    def decide(self, classification: str) -> str:
        """Return the next action for the agent loop given the classification."""
        if classification == "ok":
            return "commit"

        if classification == "transient":
            if self.retry_count < self.RETRY_CAP:
                self.retry_count += 1
                self.history.append(("transient", f"retry#{self.retry_count}"))
                return "retry"
            # Promotion: too many retries -> structural.
            self.history.append(("transient->structural", "promote"))
            return self.decide("structural")

        if classification == "structural":
            if self.replan_count < self.REPLAN_CAP:
                self.replan_count += 1
                self.history.append(("structural", f"replan#{self.replan_count}"))
                return "replan"
            self.history.append(("structural->policy", "promote"))
            return "escalate"

        if classification == "policy":
            self.history.append(("policy", "escalate"))
            return "escalate"

        return "escalate"


# ---------- agent runner that uses the dispatcher ----------

async def run_with_recovery(task_prompt: str) -> None:
    server = create_sdk_mcp_server(name="ops", version="1.0.0", tools=[do_work])
    options = ClaudeAgentOptions(
        system_prompt=(
            "You execute the user's task using the do_work tool. The 'mode' "
            "argument can be 'ok', 'transient', 'structural', or 'policy_block'. "
            "On a failure result, the harness will tell you whether to retry, "
            "re-plan, or stop. When asked to re-plan, pick a different mode."
        ),
        mcp_servers={"ops": server},
        allowed_tools=["mcp__ops__do_work"],
        hooks={
            "PreToolUse": [HookMatcher(matcher="mcp__ops__do_work", hooks=[hitl_gate])],
            "PostToolUse": [HookMatcher(matcher="mcp__ops__do_work", hooks=[capture_result])],
        },
        permission_mode="acceptEdits",
        max_turns=10,
    )

    dispatcher = Dispatcher()

    async with ClaudeSDKClient(options=options) as client:
        await client.query(task_prompt)

        for round_num in range(6):
            async for _ in client.receive_response():
                pass

            classification = classify_failure(_last_result["text"])
            action = dispatcher.decide(classification)
            print(f"[round {round_num+1}] result={_last_result['text']!r} "
                  f"-> class={classification} -> action={action}")

            if action == "commit":
                print("[dispatcher] task complete")
                break
            if action == "retry":
                await client.query("The last call failed with a transient error. "
                                   "Retry the same call with the same arguments.")
                continue
            if action == "replan":
                await client.query(
                    f"<previous_failure class='structural'>{_last_result['text']}</previous_failure>\n"
                    "That approach won't work. Re-plan with a different mode argument."
                )
                continue
            if action == "escalate":
                print("[dispatcher] ESCALATED — human attention required")
                break

    print(f"\n[dispatcher history] {dispatcher.history}")


async def scenario_transient_promotion():
    # Exercises the retry-with-budget branch and the transient->structural
    # promotion rule. The model keeps re-issuing the transient call because
    # the harness explicitly tells it to retry; once RETRY_CAP is hit, the
    # dispatcher promotes the class and switches to re-plan.
    print("=== scenario 1: transient failure with promotion ===")
    await run_with_recovery(
        "Call do_work with mode='transient' and payload='hello'. "
        "Do exactly what the harness instructs after each call."
    )


async def scenario_structural_replan():
    # Exercises the re-plan branch and its REPLAN_CAP=2 ceiling. The first
    # call is structural, the harness asks for a different mode, the model
    # picks another structural-shaped argument (the prompt biases it that
    # way), and after the cap the dispatcher escalates. This is how a real
    # workflow surfaces "the schema itself is wrong, stop guessing."
    print("\n=== scenario 2: structural failure -> replan cap -> escalate ===")
    await run_with_recovery(
        "Call do_work with mode='structural' and payload='ingest'. "
        "If the harness asks you to re-plan, try mode='structural' again "
        "with a different payload — the underlying schema is broken, so "
        "every variant will keep failing structurally."
    )


async def scenario_policy_escalate():
    # Exercises the policy branch directly. The HITL gate denies the call
    # because mode == 'policy_block', the deny path seeds _last_result with
    # a 'policy' marker, and the dispatcher escalates on the first turn —
    # no retries, no re-plans. Policy failures bypass the budget logic.
    print("\n=== scenario 3: policy block -> HITL deny -> escalate ===")
    await run_with_recovery(
        "Call do_work with mode='policy_block' and payload='delete-prod'. "
        "Do exactly what the harness instructs after each call."
    )


async def main():
    # Three scenarios in sequence so all three Dispatcher branches —
    # retry-with-promotion, replan-with-cap, and direct-escalate — are
    # observable in a single run. Sequential (not concurrent) because the
    # module-level _last_result is shared mutable state; parallelising
    # would race the dispatcher's view of "the last turn's outcome."
    await scenario_transient_promotion()
    await scenario_structural_replan()
    await scenario_policy_escalate()


if __name__ == "__main__":
    anyio.run(main)
