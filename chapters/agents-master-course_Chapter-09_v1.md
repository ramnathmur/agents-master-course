# Chapter 9 — Deeper Integration: Verifier / Critic Loop

**Trait focus:** All five + actor/judge separation (gap #5 from research).
**Persona:** The Reviewer (see personas §9).
**Prerequisites:** Chapter 8 complete with eval harness working.
**Code:** `code/chapter_09_verifier.py`.

> **Tutor instruction.** Adopt The Reviewer. Make Ram see self-confirmation bias in action. The actor and the judge must be structurally different.

---

## PHASE 1 — CALIBRATION

> **Ask Ram:** "Your Ch 8 agent produces an answer. You ask the *same* agent in the *same* conversation 'is your answer correct?' What's the architectural problem with that as a verifier?"

(Listen for: same model + same context = self-confirmation bias. The model is biased toward agreeing with its own prior output. If Ram says "it might be wrong sometimes," that's too soft. If he names the structural bias, Branch B.)

## PHASE 2 — ADAPT

- **Branch A (shallow):** Walk through self-confirmation bias. Explain why a verifier must differ from the actor along at least one of: (a) different prompt (different rubric, adversarial framing), (b) different context (no access to the actor's reasoning), (c) different model (smaller critic catches obvious errors; larger catches subtle ones). Best practice: vary all three when possible.
- **Branch B (strong):** Skip to design: "Should the critic see the actor's chain of thought, or only the final output? Pick one. Defend it."
- **Branch C (reinforce eval_regression_discipline):** Confirm Ch 8 takeaway first.

(For Branch B: arguments both ways. Seeing chain of thought lets the critic catch reasoning errors; not seeing it forces the critic to evaluate the output on its own merits. Most production critics see the output only — it's a cleaner test. But for debugging an agent's reasoning, see-the-CoT is useful.)

## PHASE 3 — CODE

> **Tell Ram:** "Copy `chapter_09_verifier.py` to IntelliJ. It wraps the Ch 8 agent. After the agent produces a final answer, a SEPARATE `query()` call (different system prompt, fresh context) reviews it against a rubric and returns `{accept: bool, critique: str, confidence: float}`. The wrapper blocks commit if confidence < 0.7."

Architecture:
1. **Actor:** the Ch 8 single-agent system.
2. **Judge:** new function `verify_output(task, output)` that uses `query()` with a verifier system prompt. Note: NO conversation history is shared. Fresh context.
3. **Decision gate:** the wrapper inspects `{accept, confidence}` and decides whether to commit or re-actor.

> **Predict before running:** "I'm going to give the actor a task where its first answer will be plausible but wrong. What does the critic need to see in the verifier prompt to catch it?"

(Push Ram to write the verifier system prompt himself before reading mine. Compare. Iterate.)

Force a failure case: give the agent a task where the goal predicate passes but the output is subtly wrong (e.g., correct format, wrong content). Watch the critic catch what the predicate missed.

## PHASE 4 — ASSESSMENT

> **Ask Ram:** "Your critic accepts 99% of actor outputs. Two interpretations. What are they, and how do you tell them apart?"

(Expected:
1. **The actor is genuinely correct.** Good. Verify with the eval harness — if eval scores are >0.95, congratulations.
2. **The critic is too lenient or sees the actor's reasoning and gets confirmation-biased.** Bad. Test by feeding the critic deliberately-wrong outputs that match the actor's typical style. If it still says "accept," the critic is broken.

This is a classic LLM-judge calibration step. The Reviewer's job: distrust the critic's positive results until you've tested it against known-bad outputs.)

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=critic_calibration`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:Actor and judge must be structurally different. Verify the critic with known-bad inputs before trusting its accept signals. The judge is a separate system, not a self-check.]`

---

## Architect's Reflection

The critic is a second model with a different job. Treat it that way:

1. **Critic system prompt is adversarial.** "Find what's wrong with this output. Default to skeptical. List specific failure modes." Not "is this good?" — that primes acceptance.

2. **Critic has its own eval set.** Yes, really. You evaluate the critic by giving it known-good and known-bad outputs and checking whether its accept/reject calls match. A miscalibrated critic is worse than no critic — it adds false confidence.

3. **Verifier ≠ re-planner.** The critic says "this is wrong, here's why." It does NOT say "here's how to fix it." Fixing belongs to the actor on the next turn, or to the recovery layer (Chapter 10). Conflating verification and re-planning is a common mistake — they're different architectural surfaces.

4. **Cost vs reliability tradeoff.** Every actor output triggers a critic call. That's 2x cost. For low-stakes tasks, skip the critic. For high-stakes (production user-facing, irreversible actions), the 2x is well spent. The architect makes this call per task class, not per agent.

## Exit Check

You can take any agent output and design: (a) the critic's system prompt (adversarial framing, specific failure modes to look for), (b) the critic's calibration set (5 known-good + 5 known-bad outputs), (c) the decision gate (accept threshold, what happens on reject). You can also explain why the critic must NOT share context with the actor.
