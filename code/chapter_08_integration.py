"""
Chapter 8 — Five Traits Together + eval harness  [v3]

REVISION v1 -> v2 (Review R1):
    v1 was a one-sentence-summary loop with no tools, no hooks, no perception,
    no action. That contradicted the chapter Markdown. v2 is a real
    TODO-fixing agent that exercises ALL FIVE traits in one runnable file:

        - GOAL:      every TODO either fixed or annotated as deferred.
        - PERCEIVE:  list_files + read_file (read-only @tool sensors).
        - REASON:    structured plan tool the model must call before action.
        - ACT:       write_file (gated by sandbox PreToolUse hook).
        - ITERATE:   ClaudeSDKClient loop with goal predicate + turn cap.

REVISION v2 -> v3 (Review E2):
    v2's audit trail was a flat list[str] of tool names — useful for a
    print line, useless as a real observability artifact. v3 replaces it
    with a Span trace (id, parent_id, tool, start counter, duration ticks,
    result summary) emitted as JSONL. The parent_id field comes from a
    span stack pushed in PreToolUse and popped in PostToolUse, so nested
    tool calls form a proper tree. Counters (not wall clocks) keep the
    teaching artifact reproducible; production code would substitute
    time.monotonic_ns() in the same slots.
"""

import anyio
import itertools
import json
import re
import shutil
from dataclasses import dataclass, asdict
from pathlib import Path

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher,
    tool,
    create_sdk_mcp_server,
)

from shared.eval_harness import Case, run_suite, report


SANDBOX = Path("./ch08_sandbox").resolve()
TRACE_PATH = Path(
    r"C:\Claude Cowork\CLAUDE OUTPUTS\agents master course\traces.jsonl"
)
TODO_PATTERN = re.compile(r"#\s*TODO\b", re.IGNORECASE)


# ---------- trace schema ----------

@dataclass
class Span:
    span_id: str
    parent_id: str | None
    tool: str
    started_at_counter: int   # monotonic int — deterministic across runs
    duration_ticks: int       # fixed placeholder; real systems use ns durations
    result_summary: str


# ---------- tools: perception (read-only) ----------

@tool(
    "list_python_files",
    "List every .py file under the working directory recursively. "
    "Returns a JSON array of relative paths. Use this FIRST to discover targets.",
    {},
)
async def list_python_files(args):
    files = sorted(str(p.relative_to(SANDBOX)) for p in SANDBOX.rglob("*.py"))
    return {"content": [{"type": "text", "text": json.dumps(files)}]}


@tool(
    "read_file",
    "Read a UTF-8 text file. Returns the full content. "
    "Use AFTER list_python_files to inspect a candidate.",
    {"path": str},
)
async def read_file(args):
    target = (SANDBOX / args["path"]).resolve()
    text = target.read_text(encoding="utf-8")
    return {"content": [{"type": "text", "text": text}]}


# ---------- tools: action (write, sandboxed) ----------

@tool(
    "write_file",
    "Overwrite a file with new content. Use to apply a TODO fix or annotate "
    "a deferred TODO. Path must be inside the sandbox.",
    {"path": str, "content": str},
)
async def write_file(args):
    target = (SANDBOX / args["path"]).resolve()
    target.write_text(args["content"], encoding="utf-8")
    return {"content": [{"type": "text", "text": f"wrote {target.relative_to(SANDBOX)}"}]}


# ---------- reasoning: structured plan tool ----------

_ALLOWED_PLAN_ACTIONS = {"fix", "defer"}


def _validate_plan_step(idx: int, step) -> str | None:
    """Mirrors Ch 6's _validate_step discipline. Returns None if valid."""
    if not isinstance(step, dict):
        return f"step #{idx} is not an object"
    missing = {"file", "action", "expected_outcome"} - step.keys()
    if missing:
        return f"step #{idx} missing required fields: {sorted(missing)}"
    if step["action"] not in _ALLOWED_PLAN_ACTIONS:
        return f"step #{idx} action={step['action']!r} not in {sorted(_ALLOWED_PLAN_ACTIONS)}"
    if not isinstance(step["file"], str) or not step["file"].strip():
        return f"step #{idx} file must be a non-empty string"
    if not isinstance(step["expected_outcome"], str) or not step["expected_outcome"].strip():
        return f"step #{idx} expected_outcome must be a non-empty string"
    return None


@tool(
    "propose_plan",
    "Call this FIRST before any write. Submit a structured plan: for each "
    "TODO discovered, provide an object with file (path), action ('fix' or "
    "'defer'), and expected_outcome (per-step success criterion).",
    {"steps": list},
)
async def propose_plan(args):
    steps = args.get("steps")
    if not isinstance(steps, list) or len(steps) == 0:
        return {"content": [{"type": "text",
                "text": "REJECT: 'steps' must be a non-empty list of step objects."}]}
    for idx, step in enumerate(steps):
        err = _validate_plan_step(idx, step)
        if err:
            return {"content": [{"type": "text",
                    "text": f"REJECT: {err}. Reformat and resubmit."}]}
    return {"content": [{"type": "text", "text": f"plan accepted: {len(steps)} steps"}]}


# ---------- hook: PreToolUse sandbox guard ----------

async def sandbox_guard(input_data, tool_use_id, ctx):
    tool_input = input_data.get("tool_input", {})
    raw_path = tool_input.get("path")
    if not raw_path:
        return {}
    target = (SANDBOX / raw_path).resolve()
    try:
        target.relative_to(SANDBOX)
    except ValueError:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"Path {target} is outside the sandbox {SANDBOX}. "
                    "Use a path relative to the sandbox root."
                ),
            }
        }
    return {}


# ---------- hooks: trace span lifecycle ----------

# A monotonic counter is the deterministic substitute for time.monotonic_ns()
# in the teaching artifact: same input -> same trace. Production agents would
# swap in nanosecond clocks at the same call sites without touching the schema.
_trace: list[Span] = []
_span_counter = itertools.count(1)
_span_stack: list[str] = []
_open_spans: dict[str, dict] = {}   # tool_use_id -> partial span fields


async def span_open(input_data, tool_use_id, ctx):
    """PreToolUse: allocate a span_id, capture parent from the stack, push."""
    span_id = f"s{next(_span_counter)}"
    parent_id = _span_stack[-1] if _span_stack else None
    _open_spans[tool_use_id] = {
        "span_id": span_id,
        "parent_id": parent_id,
        "tool": input_data.get("tool_name", "?"),
        "started_at_counter": int(span_id[1:]),
    }
    _span_stack.append(span_id)
    return {}


def _summarize_result(input_data) -> str:
    """First 80 chars of the first text block — enough to debug, bounded for JSONL."""
    response = input_data.get("tool_response") or input_data.get("tool_result") or {}
    if isinstance(response, dict):
        content = response.get("content")
        if isinstance(content, list) and content:
            first = content[0]
            if isinstance(first, dict):
                text = first.get("text", "")
                return str(text)[:80]
    return str(response)[:80]


async def audit_observer(input_data, tool_use_id, ctx):
    """PostToolUse: close the span, append to trace, pop the stack."""
    partial = _open_spans.pop(tool_use_id, None)
    if partial is None:
        # Defensive: a PostToolUse without a matching PreToolUse means hook
        # registration is wrong. Drop silently rather than crash the agent.
        return {}
    span = Span(
        span_id=partial["span_id"],
        parent_id=partial["parent_id"],
        tool=partial["tool"],
        started_at_counter=partial["started_at_counter"],
        duration_ticks=50,
        result_summary=_summarize_result(input_data),
    )
    _trace.append(span)
    if _span_stack and _span_stack[-1] == span.span_id:
        _span_stack.pop()
    return {}


# ---------- goal predicate ----------

def goal_met(sandbox_dir: Path) -> bool:
    """Goal: no unresolved TODOs remain in any .py file under the sandbox.
    A TODO is 'resolved' if it has been deleted OR rewritten to start with
    '# DEFERRED:' (the chapter's annotation contract)."""
    for py in sandbox_dir.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if TODO_PATTERN.search(stripped) and not stripped.startswith("# DEFERRED:"):
                return False
    return True


# ---------- fixture management ----------

FIXTURES = {
    "fixture_clean": {
        "math_utils.py": "def add(a, b):\n    return a + b\n",
    },
    "fixture_one_todo": {
        "calc.py": "def add(a, b):\n    # TODO: handle non-numeric inputs\n    return a + b\n",
    },
    "fixture_multi_todo": {
        "io_utils.py": (
            "def read(path):\n"
            "    # TODO: add encoding parameter\n"
            "    return open(path).read()\n"
            "\n"
            "def write(path, data):\n"
            "    # TODO: atomic write\n"
            "    open(path, 'w').write(data)\n"
        ),
    },
}


def install_fixture(name: str) -> None:
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    SANDBOX.mkdir(parents=True)
    for fname, content in FIXTURES[name].items():
        (SANDBOX / fname).write_text(content, encoding="utf-8")


# ---------- agent run + eval ----------

async def run_agent(task: str) -> str:
    """task here is the fixture name; the agent works against SANDBOX."""
    install_fixture(task)
    # Note: we do NOT clear _trace between runs — main() writes the full
    # multi-run trace so eval reviewers can see cross-case patterns.

    server = create_sdk_mcp_server(
        name="todo_fix",
        version="1.0.0",
        tools=[list_python_files, read_file, propose_plan, write_file],
    )

    options = ClaudeAgentOptions(
        system_prompt=(
            "You fix or defer every TODO in the project. "
            "ALWAYS list_python_files first, then read each candidate, then "
            "propose_plan, then write_file to apply each plan step. "
            "Annotate deferred TODOs by replacing '# TODO:' with '# DEFERRED:'. "
            "Stop when no unresolved TODOs remain."
        ),
        mcp_servers={"todo_fix": server},
        allowed_tools=[
            "mcp__todo_fix__list_python_files",
            "mcp__todo_fix__read_file",
            "mcp__todo_fix__propose_plan",
            "mcp__todo_fix__write_file",
        ],
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="mcp__todo_fix__write_file", hooks=[sandbox_guard]),
                HookMatcher(matcher="mcp__todo_fix__", hooks=[span_open]),
            ],
            "PostToolUse": [
                HookMatcher(matcher="mcp__todo_fix__", hooks=[audit_observer]),
            ],
        },
        permission_mode="acceptEdits",
        max_turns=15,
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(f"Resolve every TODO in this project.")
        async for _ in client.receive_response():
            pass

    return "GOAL_MET" if goal_met(SANDBOX) else "GOAL_MISSED"


def score_fn(output: str) -> float:
    return 1.0 if output == "GOAL_MET" else 0.0


async def main():
    cases = [
        Case("fixture_clean",      "fixture_clean",      score_fn),
        Case("fixture_one_todo",   "fixture_one_todo",   score_fn),
        Case("fixture_multi_todo", "fixture_multi_todo", score_fn),
    ]
    print("running eval suite (Ch 8 v3 — TODO fixer with all 5 traits + span trace):\n")
    results = await run_suite(cases, run_agent)
    report(results)

    # JSONL is the deliberate trace format: one span per line, append-friendly,
    # streamable into any log pipeline. asdict() keeps the schema canonical.
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with TRACE_PATH.open("w", encoding="utf-8") as fh:
        for span in _trace:
            fh.write(json.dumps(asdict(span)) + "\n")
    print(f"\n  wrote trace: {TRACE_PATH}")
    print(f"  trace span count: {len(_trace)}")


if __name__ == "__main__":
    anyio.run(main)
