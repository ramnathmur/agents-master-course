"""
Reusable goal predicates introduced in Chapter 2.

A predicate is a callable: (output: str) -> bool.

Three flavors:
    - deterministic   (regex, string match, set membership)
    - schema-based    (JSON shape validation)
    - LLM-judge       (a separately-prompted Claude call — heavy, save for fuzzy)

Used in Ch 2, 4, 8, 9, 10.
"""

from __future__ import annotations

import json
import re
from typing import Callable


# ---------- deterministic predicates ----------

def contains_word(word: str, case_sensitive: bool = False) -> Callable[[str], bool]:
    flag = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(rf"\b{re.escape(word)}\b", flag)
    return lambda text: bool(pattern.search(text))


def word_count_equals(n: int) -> Callable[[str], bool]:
    return lambda text: len(text.split()) == n


def matches_regex(pattern: str) -> Callable[[str], bool]:
    compiled = re.compile(pattern)
    return lambda text: bool(compiled.search(text))


# ---------- schema-based predicates ----------

def is_valid_json_with_keys(required_keys: set[str]) -> Callable[[str], bool]:
    def predicate(text: str) -> bool:
        try:
            obj = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return False
        if not isinstance(obj, dict):
            return False
        return required_keys.issubset(obj.keys())
    return predicate


# ---------- composite ----------

def all_of(*predicates: Callable[[str], bool]) -> Callable[[str], bool]:
    return lambda text: all(p(text) for p in predicates)


def any_of(*predicates: Callable[[str], bool]) -> Callable[[str], bool]:
    return lambda text: any(p(text) for p in predicates)
