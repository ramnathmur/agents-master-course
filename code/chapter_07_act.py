"""
Chapter 7 — Act under permission: write tool + PreToolUse/PostToolUse hooks.

v3 revision: extends the v1/v2 sandbox-guard example to exercise all three
hook roles introduced in Chapter 6 — Guard, Mutate, and Observe — on a single
tool call path. The original sandbox_guard (Guard role) stays intact; we add:

  - normalize_path_mutate (Mutate role, PreToolUse): rewrites tool_input
    before the Guard sees it, so messy model output (whitespace, ./ prefixes)
    doesn't trip the policy unnecessarily.
  - audit_observer (Observe role, PostToolUse): appends a structured record
    of every executed tool call to a module-level audit trail. The Observe
    role is fire-and-forget — it returns nothing and cannot change control
    flow, which is what makes it safe to attach to every call.

Hook ordering matters: Mutate runs first (cleans input), Guard runs second
(decides allow/deny on the cleaned input), tool executes, Observe runs last
(records the outcome). This mirrors the middleware stack pattern from
Chapter 6.

Run with two tasks:
    - Write to ./sandbox/hello.txt -> succeeds.
    - Write to C:/Windows/system32/x.txt -> hook denies; agent recovers.
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


SANDBOX = Path("./sandbox").resolve()
SANDBOX.mkdir(exist_ok=True)

# Module-level audit trail. The Observe hook appends here; main() prints it
# at exit. In a real system this would be a structured logger or an OTel
# span emitter — the principle is identical: PostToolUse is the one place
# you can record what *actually happened* (post-Guard, post-execution).
_audit_trail: list[dict] = []


@tool(
    "write_file",
    "Write text to a file. Creates the file if missing. Overwrites if present. "
    "Only paths under ./sandbox/ are allowed by policy.",
    {"path": str, "content": str},
)
async def write_file(args):
    path = Path(args["path"]).resolve()
    path.write_text(args["content"], encoding="utf-8")
    return {"content": [{"type": "text", "text": f"wrote {path}"}]}


async def normalize_path_mutate(input_data, tool_use_id, ctx):
    """PreToolUse hook (Mutate role): canonicalize the path argument.

    Models occasionally emit paths with leading/trailing whitespace or
    redundant './' segments. Rather than letting the Guard reject these on
    a technicality, we resolve them here and hand a clean tool_input to the
    next hook in the chain. The Mutate role is expressed by returning a
    hookSpecificOutput with permissionDecision="allow" AND a modified
    tool_input — the SDK forwards the rewritten input to subsequent hooks
    and to the tool itself.
    """
    tool_input = dict(input_data.get("tool_input", {}))
    raw_path = tool_input.get("path", "")
    if not raw_path:
        return {}

    cleaned = raw_path.strip()
    # Resolving collapses '.' and '..' segments without touching the
    # filesystem semantics the Guard cares about.
    normalized = str(Path(cleaned).resolve())
    if normalized == raw_path:
        return {}

    tool_input["path"] = normalized
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": "path normalized",
            "toolInput": tool_input,
        }
    }


async def sandbox_guard(input_data, tool_use_id, ctx):
    """PreToolUse hook (Guard role): deny writes outside the sandbox."""
    tool_input = input_data.get("tool_input", {})
    raw_path = tool_input.get("path", "")
    if not raw_path:
        return {}
    target = Path(raw_path).resolve()
    try:
        target.relative_to(SANDBOX)
    except ValueError:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"Path {target} is outside the allowed sandbox {SANDBOX}. "
                    f"Choose a path inside {SANDBOX} and retry."
                ),
            }
        }
    return {}


async def audit_observer(input_data, tool_use_id, ctx):
    """PostToolUse hook (Observe role): record what executed.

    Runs after the tool returns. Cannot block, deny, or mutate — its only
    job is to leave a trace. Attaching this to every tool call is cheap and
    gives you the forensic record you need when a production agent does
    something surprising.
    """
    tool_name = input_data.get("tool_name", "<unknown>")
    tool_input = input_data.get("tool_input", {})
    _audit_trail.append(
        {
            "tool_use_id": tool_use_id,
            "tool": tool_name,
            "path": tool_input.get("path"),
        }
    )
    return {}


async def main():
    server = create_sdk_mcp_server(name="fs", version="1.0.0", tools=[write_file])

    options = ClaudeAgentOptions(
        system_prompt="You write small files to disk on the user's request.",
        mcp_servers={"fs": server},
        allowed_tools=["mcp__fs__write_file"],
        hooks={
            # Mutate listed before Guard so input is cleaned before policy
            # evaluation. The SDK runs PreToolUse hooks in registration order.
            "PreToolUse": [
                HookMatcher(
                    matcher="mcp__fs__write_file",
                    hooks=[normalize_path_mutate, sandbox_guard],
                ),
            ],
            "PostToolUse": [
                HookMatcher(matcher="mcp__fs__write_file", hooks=[audit_observer]),
            ],
        },
        permission_mode="acceptEdits",
        max_turns=5,
    )

    async with ClaudeSDKClient(options=options) as client:
        # Try one task. Swap the second task to test the deny path.
        await client.query("Write the word 'hello' to ./sandbox/greeting.txt")
        # await client.query("Write the word 'hello' to C:/Windows/system32/probe.txt")
        async for message in client.receive_response():
            print(message)

    # Observe role payoff: the audit trail is independent of what the agent
    # claimed in its final message. This is the ground truth.
    print("\n--- audit trail ---")
    for entry in _audit_trail:
        print(entry)


if __name__ == "__main__":
    anyio.run(main)
