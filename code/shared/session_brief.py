"""
Session-brief generator — emits a self-contained cumulative HTML dashboard
after each chapter.

Usage:
    python code/shared/session_brief.py --after 4
        -> writes session-briefs/agents-master-course_Brief_after-Chapter-04_v1.html
    python code/shared/session_brief.py --all
        -> regenerates every brief Ch 00..12

The brief at Chapter N covers Chapters 0..N (cumulative). Single .html file,
no CDN, no remote assets — opens offline in any browser.

Design contract:
    1. Parses chapter Markdowns at their ACTIVE version (per index_v2 pointers).
    2. Extracts: title, persona, voice opener, trait focus, [INSIGHT:...] marker,
       reflection action checklist items (becomes "Key Concepts").
    3. Emits HTML with sections: progress track, what-the-Professor-taught-me
       (first-person, cumulative), key-concepts glossary, code-primitives,
       next-up footer.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ---------- file-path policy ----------

COURSE_ROOT = Path(__file__).resolve().parents[2]
CHAPTERS_DIR = COURSE_ROOT / "chapters"
CODE_DIR = COURSE_ROOT / "code"
BRIEFS_DIR = COURSE_ROOT / "session-briefs"

# Active versions per Index_v3 pointers. Ch 12.5 is a special non-integer
# chapter handled separately by the optional --include-12-5 flag.
ACTIVE_VERSION = {0: 1, 1: 1, 2: 1, 3: 2, 4: 2,
                  5: 3, 6: 3, 7: 2, 8: 3, 9: 2,
                  10: 3, 11: 3, 12: 2, 13: 1}


def chapter_md_path(n: int) -> Path:
    v = ACTIVE_VERSION[n]
    return CHAPTERS_DIR / f"agents-master-course_Chapter-{n:02d}_v{v}.md"


def chapter_py_filename(n: int) -> str:
    """Best-effort match of code filename suffix per chapter (used for the
    'Code primitives I can now write' section)."""
    suffixes = {
        0: "setup", 1: "bare_llm", 2: "goal", 3: "chained", 4: "iteration",
        5: "perceive", 6: "reason", 7: "act", 8: "integration",
        9: "verifier", 10: "recovery", 11: "two_agent", 12: "orchestrator",
        13: "production",
    }
    return f"chapter_{n:02d}_{suffixes[n]}.py"


# ---------- parsing ----------

@dataclass
class ChapterExtract:
    n: int
    title: str
    persona: str
    voice_opener: str
    trait_focus: str
    insight: str
    key_concepts: list[str] = field(default_factory=list)
    learned_paragraph: str = ""
    code_filename: str = ""


def _first_match(pattern: str, text: str, flags: int = 0) -> str:
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ""


def parse_chapter(n: int) -> ChapterExtract:
    md_path = chapter_md_path(n)
    if not md_path.exists():
        raise FileNotFoundError(f"missing chapter file: {md_path}")
    text = md_path.read_text(encoding="utf-8")

    title = _first_match(r"^#\s+Chapter\s+\d+\s*[—\-:]\s*(.+?)(?:\s+\[v\d+\])?$",
                         text, re.MULTILINE)
    persona = _first_match(r"\*\*Persona:\*\*\s*(.+?)(?:\(|$)", text)
    voice_opener = _first_match(r"\*\*Voice opener:\*\*\s*\*?\"?(.+?)\"?\*?\s*$",
                                text, re.MULTILINE)
    trait_focus = _first_match(r"\*\*Trait focus:\*\*\s*(.+?)$", text, re.MULTILINE)
    insight = _first_match(r"\[INSIGHT:(.+?)\]", text, re.DOTALL)

    # Key concepts = items in the Architect's Reflection checklist (numbered)
    # or first-line bullet items. We parse 1./2./3. lists.
    reflection_block = ""
    rm = re.search(r"## Architect'?s Reflection.*?(?=\n##\s|\Z)", text, re.DOTALL)
    if rm:
        reflection_block = rm.group(0)
    key_concepts = re.findall(
        r"^\d+\.\s+\*\*(.+?)\*\*\s*[—\-:]\s*(.+?)$",
        reflection_block, re.MULTILINE,
    )
    # Fallback: chapter-12 capstone checklist or any chapter without bold.
    if not key_concepts:
        key_concepts = re.findall(
            r"^\d+\.\s+(.+?)\s*[—\-:]\s*(.+?)$",
            reflection_block, re.MULTILINE,
        )

    # First-person learned-paragraph: paraphrase the insight + trait focus.
    if insight:
        learned = (f"I worked through {title}. The chapter focused on "
                   f"{trait_focus.lower() if trait_focus else 'a new architectural surface'}. "
                   f"What I'm carrying forward: {insight}")
    else:
        learned = f"I worked through {title}. (No insight marker found in chapter text.)"

    return ChapterExtract(
        n=n,
        title=title or f"Chapter {n}",
        persona=persona or "(persona missing)",
        voice_opener=voice_opener,
        trait_focus=trait_focus,
        insight=insight,
        key_concepts=[(k.strip(), v.strip()) for k, v in key_concepts],
        learned_paragraph=learned,
        code_filename=chapter_py_filename(n),
    )


# ---------- HTML rendering ----------

STYLE = """
:root {
  --bg: #fafaf7;
  --ink: #1a1a1a;
  --muted: #5a5a55;
  --accent: #b45309;
  --rule: #d6d3c5;
  --card: #ffffff;
  --code: #f3f1e7;
}
* { box-sizing: border-box; }
body { margin: 0; font-family: Georgia, "Iowan Old Style", serif;
       background: var(--bg); color: var(--ink); line-height: 1.55; }
.wrap { max-width: 880px; margin: 0 auto; padding: 48px 32px 96px; }
header { border-bottom: 2px solid var(--ink); padding-bottom: 16px; margin-bottom: 32px; }
h1 { font-size: 28px; margin: 0; letter-spacing: -0.01em; }
.subhead { color: var(--muted); margin-top: 4px; font-size: 15px; }
h2 { font-size: 20px; margin: 40px 0 12px; padding-bottom: 4px; border-bottom: 1px solid var(--rule); }
h3 { font-size: 16px; margin: 24px 0 6px; color: var(--accent); }
.progress { display: flex; flex-wrap: wrap; gap: 4px; margin: 16px 0 32px; }
.dot { display: inline-flex; align-items: center; gap: 6px;
       background: var(--card); border: 1px solid var(--rule);
       padding: 6px 10px; border-radius: 14px; font-size: 13px; }
.dot.done { background: var(--ink); color: var(--bg); border-color: var(--ink); }
.dot.next { background: var(--accent); color: var(--bg); border-color: var(--accent); }
.dot .num { font-weight: 700; }
.card { background: var(--card); border: 1px solid var(--rule); border-radius: 6px;
        padding: 20px 24px; margin: 14px 0; }
.card .meta { color: var(--muted); font-size: 13px; margin-bottom: 8px; }
.card .voice { font-style: italic; color: var(--accent); margin: 8px 0; }
.card .insight { background: var(--code); border-left: 3px solid var(--accent);
                 padding: 10px 14px; margin: 10px 0 0; font-size: 14px; }
dl.glossary dt { font-weight: 700; margin-top: 12px; }
dl.glossary dt .ch { color: var(--muted); font-weight: 400; font-size: 12px; margin-left: 8px; }
dl.glossary dd { margin: 4px 0 0 16px; color: var(--ink); }
code, pre { font-family: "JetBrains Mono", Consolas, monospace; font-size: 13px;
            background: var(--code); padding: 1px 4px; border-radius: 3px; }
pre { padding: 12px; overflow-x: auto; }
footer { margin-top: 64px; padding-top: 16px; border-top: 1px solid var(--rule);
         color: var(--muted); font-size: 13px; }
"""


PRIMITIVE_SNIPPETS = {
    0: ("Smoke test", "async for m in query(prompt=...): print(m)"),
    1: ("Bare LLM call", "await query(prompt=...) — function: input → output → die"),
    2: ("Goal predicate", "ok = is_city_like(model_output)   # Python-side verifier"),
    3: ("Chained calls", "plan = await call_for_plan(task)\nresult = await execute_step(plan['steps'][0])"),
    4: ("Iteration with compaction", "while not goal_met(attempt) and iter < cap:\n    await client.query(failure_feedback)"),
    5: ("Read-only tool", "@tool('read_file', '4-question description', {'path': str})\nasync def read_file(args): ..."),
    6: ("Tight schema tool", "@tool('make_plan_tight', '...', {'steps': list})\nasync def f(args): validate_each_step()"),
    7: ("Hook-gated write", "HookMatcher(matcher='mcp__fs__write_file', hooks=[sandbox_guard])"),
    8: ("All-5 agent + eval", "ClaudeSDKClient with @tool perceive/reason/act + PreToolUse + eval_harness.run_suite"),
    9: ("Actor != Judge", "verdict = await critic_review(task, actor_output)  # separate query() + adversarial prompt"),
    10: ("Failure dispatcher", "Dispatcher().decide(classify_failure(result)) -> retry|replan|escalate"),
    11: ("Two-agent contract", "researcher → state_store → writer; phase-complete predicate gates handoff"),
    12: ("Orchestrator + sub-agents", "ClaudeAgentOptions(agents={'researcher': AgentDefinition(...), 'coder': ..., 'reviewer': ...})"),
    13: ("Production surfaces", "External MCP server config + fetch_url @tool with retry+backoff + CDATA-fence untrusted_text injection defense"),
}


def render_brief(after_n: int, chapters: list[ChapterExtract]) -> str:
    e = html.escape
    last = max(ch.n for ch in chapters)
    title = f"Session Brief — after Chapter {after_n:02d}"

    # Progress dots
    dots_html = []
    for i in range(13):
        cls = "done" if i <= after_n else ""
        dots_html.append(f'<span class="dot {cls}"><span class="num">{i:02d}</span></span>')
    progress = "\n".join(dots_html)

    # What the Professor taught me — cumulative
    cards = []
    for ch in chapters:
        kc_html = ""
        if ch.key_concepts:
            items = "".join(f"<li><strong>{e(k)}</strong> — {e(v)}</li>"
                            for k, v in ch.key_concepts[:6])
            kc_html = f"<ul style='margin:8px 0;padding-left:20px'>{items}</ul>"
        voice_html = f'<div class="voice">"{e(ch.voice_opener)}"</div>' if ch.voice_opener else ""
        insight_html = f'<div class="insight"><strong>Carry-forward:</strong> {e(ch.insight)}</div>' if ch.insight else ""
        cards.append(f"""
        <div class="card">
          <div class="meta">Chapter {ch.n:02d} · {e(ch.persona)} · Trait: {e(ch.trait_focus or "—")}</div>
          <h3>{e(ch.title)}</h3>
          {voice_html}
          <p>{e(ch.learned_paragraph)}</p>
          {kc_html}
          {insight_html}
        </div>""")
    cards_html = "\n".join(cards)

    # Key concepts glossary — flatten + dedupe + sort
    glossary: dict[str, tuple[str, int]] = {}
    for ch in chapters:
        for k, v in ch.key_concepts:
            if k not in glossary:
                glossary[k] = (v, ch.n)
    glossary_items = "".join(
        f'<dt>{e(term)}<span class="ch">(Ch {ch_n:02d})</span></dt><dd>{e(defn)}</dd>'
        for term, (defn, ch_n) in sorted(glossary.items(), key=lambda x: x[0].lower())
    )

    # Code primitives I can now write
    prims = []
    for ch in chapters:
        name, snippet = PRIMITIVE_SNIPPETS.get(ch.n, ("", ""))
        if name:
            prims.append(
                f"<h3>Ch {ch.n:02d} · {e(name)} <span style='color:var(--muted);font-size:12px'>"
                f"({e(ch.code_filename)})</span></h3>"
                f"<pre>{e(snippet)}</pre>"
            )
    prims_html = "\n".join(prims)

    # Footer
    if after_n >= 13:
        footer = "<strong>Course complete (Ch 0-13 + 12.5 Cold Build).</strong> Exit Check: take a novel task and run the Ch 12 capstone checklist, then audit against the Ch 13 lethal-trifecta rule."
    elif after_n == 12:
        footer = "Next: Chapter 12.5 — Cold Build (no .py, 30-min blank-file exercise) then Chapter 13 — Production Surfaces."
    else:
        next_n = after_n + 1
        try:
            nxt = parse_chapter(next_n)
            footer = f"Next: Chapter {next_n:02d} — {e(nxt.title)} · {e(nxt.persona)}"
        except FileNotFoundError:
            footer = f"Next: Chapter {next_n:02d}"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} — Agents Master Course</title>
<style>{STYLE}</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>{e(title)}</h1>
    <div class="subhead">Agents Master Course · Cumulative dashboard · Chapters 00–{last:02d}</div>
  </header>

  <h2>Progress</h2>
  <div class="progress">{progress}</div>

  <h2>What my Professor has taught me</h2>
  <p style="color:var(--muted);font-size:14px;margin-bottom:8px">
    First-person, cumulative. One card per chapter, in order. The carry-forward insight at
    the bottom of each card is the seed of the next chapter.
  </p>
  {cards_html}

  <h2>Key Concepts (glossary)</h2>
  <dl class="glossary">
    {glossary_items if glossary_items else "<dd>(no concepts captured yet)</dd>"}
  </dl>

  <h2>Code primitives I can now write</h2>
  {prims_html}

  <footer>{footer}</footer>
</div>
</body>
</html>
"""


# ---------- entry point ----------

def generate(after_n: int) -> Path:
    if after_n not in ACTIVE_VERSION:
        raise ValueError(f"chapter {after_n} not in 0..13")
    chapters = [parse_chapter(n) for n in range(after_n + 1)]
    html_text = render_brief(after_n, chapters)
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = BRIEFS_DIR / f"agents-master-course_Brief_after-Chapter-{after_n:02d}_v1.html"
    out_path.write_text(html_text, encoding="utf-8")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Generate cumulative session brief.")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--after", type=int, help="Chapter number 0..12")
    g.add_argument("--all", action="store_true", help="Regenerate every brief 0..12")
    args = parser.parse_args()

    if args.all:
        for n in range(14):
            path = generate(n)
            print(f"wrote {path.name}")
    else:
        path = generate(args.after)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
