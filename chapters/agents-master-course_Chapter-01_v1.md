# Chapter 1 — The Bare LLM Call: Make the Absence Visible

**Trait focus:** None. This is the anchor chapter.
**Persona:** The Reductionist (see personas §1).
**Prerequisites:** Chapter 0 green.
**Code:** `code/chapter_01_bare_llm.py`.

> **Tutor instruction.** Adopt The Reductionist. Strip every abstraction. Make Ram name what's missing — don't tell him.

---

## PHASE 1 — CALIBRATION

> **Ask Ram:** "I'm about to show you 6 lines of Python that call Claude. Before you see it — what would you say this code is NOT, that an agent IS?"

(Listen for: no loop, no goal predicate, no environment access, no memory across calls, no decision-making about next steps. If Ram names 3+ of these, Branch B.)

## PHASE 2 — ADAPT

- **Branch A (shallow):** Walk through the five traits explicitly. Use the cricket analogy — a single ball bowled is not an over; an over is not an innings; an innings is not a match. Each level adds structure.
- **Branch B (strong):** Skip to code. Frame: "This is the primitive. Every chapter from 2–12 is a *deliberate departure* from this. Hold this image."
- **Branch C (reinforce auth_precedence):** Before starting, confirm `ANTHROPIC_API_KEY` is still unset. Then proceed Branch B.

## PHASE 3 — CODE

> **Tell Ram:** "Copy `code/chapter_01_bare_llm.py` to IntelliJ. Predict what it prints. Then run it."

(Expected prediction: a single message — Claude's one-sentence definition of agency. If Ram says "a stream of messages" or "multiple turns," push back — there's only one user turn, one assistant response.)

After he runs it, ask: "How many times did Claude decide what to do next, autonomously?"

(Expected answer: zero. Claude produced one response to one prompt. There was no "decision." There was a completion.)

## PHASE 4 — ASSESSMENT

> **Ask Ram, in writing:** "Write one sentence for each of the five traits — what does this code lack to satisfy *goal*, *perceive*, *reason*, *act*, *iterate*?"

Look for:
- **Goal:** no success criterion, no verifier
- **Perceive:** no access to anything outside the prompt string
- **Reason:** the model reasons inside the response, but there's no plan-then-act structure
- **Act:** no tools, no side effects, no environment change
- **Iterate:** function returns and dies; no loop

Emit `[SCORE:0.XX]`. If <0.7, set `weakSignal=trait_absence_naming`.

## PHASE 5 — WRAP

`[COMPLETE]`
`[INSIGHT:An LLM call is a function. An agent is a system around the function. Every trait you add over the next 6 chapters is structure outside the call.]`
> Generate your session brief: `python code/shared/session_brief.py --after 1`. Open the .html in your browser.

---

## Architect's Reflection

The reason Chapter 1 exists is not to teach you what an LLM call is — you already know. It exists to **make the absence load-bearing**. Every architectural decision in Chapters 2–7 is a deliberate addition of structure *around* the call, not inside it.

The most common mistake junior agent builders make: trying to put more inside the prompt (longer system prompts, more examples, more rules) instead of building structure outside (loops, predicates, tools, hooks). They're trying to make a single LLM call do agent work. It can't. The function returns and dies.

The architect's frame: **the call is the muscle; the structure around it is the skeleton.** Skeletons matter more than muscles for posture.

You'll come back to this image in Chapter 4 (when iteration adds the spine), Chapter 8 (when all five traits compose), and Chapter 12 (when many calls form a body).

## Exit Check

You can recite, in one sentence each, what `chapter_01_bare_llm.py` lacks against each of the five traits. You can also predict — without running anything — what minimal change would *add* the goal trait. (Hint: Chapter 2.)
