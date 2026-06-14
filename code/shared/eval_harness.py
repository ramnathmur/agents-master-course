"""
Reusable eval harness  [v2]

REVISION v1 -> v2 (Review R9):
    v1 implemented only outcome scoring (Case). The chapter Architect's
    Reflection text discussed three modes — outcome, trajectory, LLM-judge —
    but the code shipped one. v2 adds:

        - TrajectoryCase  : scores based on a trace of tool calls vs an
                            expected pattern. Detects "wrong reasoning,
                            right answer" failures.
        - LLMJudgeCase    : scores via a separate query() call with a
                            rubric system prompt. Returns a float in [0,1].

    Outcome remains the default (cheap, deterministic, fast). The two new
    modes opt in per case.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Sequence

from claude_agent_sdk import query, ClaudeAgentOptions


# ---------- outcome (v1) ----------

@dataclass
class Case:
    name: str
    input: str
    score_fn: Callable[[str], float]


# ---------- trajectory (v2 / R9) ----------

@dataclass
class TrajectoryCase:
    """Score a run by the tool-call sequence it produced."""
    name: str
    input: str
    expected_pattern: Sequence[str]    # list of tool names that MUST appear in order
    forbidden: Sequence[str] = field(default_factory=list)   # tools that must NOT appear

    def score(self, trace: Sequence[str]) -> float:
        if any(f in trace for f in self.forbidden):
            return 0.0
        i = 0
        for name in trace:
            if i < len(self.expected_pattern) and name == self.expected_pattern[i]:
                i += 1
        return i / len(self.expected_pattern) if self.expected_pattern else 0.0


# ---------- LLM-judge (v2 / R9) ----------

_JUDGE_SYSTEM = (
    "You are a strict, adversarial reviewer. Score the candidate against the "
    "rubric. Return ONLY a JSON object: "
    '{"score": float in [0,1], "rationale": str}. No prose.'
)


@dataclass
class LLMJudgeCase:
    """Score by asking a separate model call to grade against a rubric."""
    name: str
    input: str
    rubric: str   # human-readable scoring criteria

    async def score(self, candidate_output: str) -> float:
        prompt = (
            f"<rubric>{self.rubric}</rubric>\n"
            f"<task>{self.input}</task>\n"
            f"<candidate>{candidate_output}</candidate>\n"
            "Score 0.0 to 1.0."
        )
        options = ClaudeAgentOptions(system_prompt=_JUDGE_SYSTEM, max_turns=1)
        text = ""
        async for message in query(prompt=prompt, options=options):
            text += str(message)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return 0.0
        try:
            obj = json.loads(match.group(0))
            return float(obj.get("score", 0.0))
        except (json.JSONDecodeError, TypeError, ValueError):
            return 0.0


# ---------- result + suite runner ----------

@dataclass
class Result:
    name: str
    output: str
    score: float
    error: str | None = None


async def run_suite(
    cases: list[Case],
    agent_fn: Callable[[str], Awaitable[str]],
) -> list[Result]:
    results: list[Result] = []
    for case in cases:
        try:
            output = await agent_fn(case.input)
            score = case.score_fn(output)
            results.append(Result(name=case.name, output=output, score=score))
        except Exception as exc:
            results.append(Result(name=case.name, output="", score=0.0, error=str(exc)))
    return results


async def run_trajectory_suite(
    cases: list[TrajectoryCase],
    agent_fn: Callable[[str], Awaitable[tuple[str, list[str]]]],
) -> list[Result]:
    """agent_fn must return (output_text, trace_of_tool_names)."""
    results: list[Result] = []
    for case in cases:
        try:
            output, trace = await agent_fn(case.input)
            score = case.score(trace)
            results.append(Result(name=case.name,
                                  output=f"{output} | trace={trace}",
                                  score=score))
        except Exception as exc:
            results.append(Result(name=case.name, output="", score=0.0, error=str(exc)))
    return results


async def run_judge_suite(
    cases: list[LLMJudgeCase],
    agent_fn: Callable[[str], Awaitable[str]],
) -> list[Result]:
    results: list[Result] = []
    for case in cases:
        try:
            output = await agent_fn(case.input)
            score = await case.score(output)
            results.append(Result(name=case.name, output=output, score=score))
        except Exception as exc:
            results.append(Result(name=case.name, output="", score=0.0, error=str(exc)))
    return results


def summarize(results: list[Result]) -> dict:
    total = len(results)
    if total == 0:
        return {"pass_rate": 0.0, "mean_score": 0.0, "errors": 0}
    passed = sum(1 for r in results if r.score >= 0.8 and r.error is None)
    errors = sum(1 for r in results if r.error is not None)
    mean = sum(r.score for r in results) / total
    return {"pass_rate": passed / total, "mean_score": mean, "errors": errors}


def report(results: list[Result]) -> None:
    for r in results:
        flag = "PASS" if r.score >= 0.8 and r.error is None else "FAIL"
        err = f" [{r.error}]" if r.error else ""
        print(f"  {flag}  {r.name:30s}  score={r.score:.2f}{err}")
    s = summarize(results)
    print(f"\n  pass_rate={s['pass_rate']:.0%}  mean={s['mean_score']:.2f}  errors={s['errors']}")
