"""Detect hard-wrapped markdown: prose broken mid-sentence at a column width.

The house style is one sentence per source line, however long. A "hard wrap"
is a paragraph or list-item line that doesn't end in terminal punctuation and
is immediately followed by another non-blank line continuing the same block.
Fenced code, tables, and headings are never checked. Lines that open with a
bold term (``**Label**``) or a ``Label:`` prefix are treated like list items:
each one is its own unit, never a continuation of the line before it.

This is a heuristic, not a parser: it flags the common case (an editor or
model wrapping prose at ~80-100 columns) and stays quiet on legitimately long
single-line sentences and on markdown structure it doesn't understand.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

_FENCE = re.compile(r"^(```|~~~)")
_FRONTMATTER = re.compile(r"^---\s*$")
_HEADING = re.compile(r"^#{1,6}\s")
_TABLE_ROW = re.compile(r"^\|")
_HTML_COMMENT = re.compile(r"^<!--.*-->$")
_LIST_MARKER = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+")
_STANDALONE_LABEL = re.compile(r"^(\*\*[^*]+\*\*:?|[A-Z][\w() -]*:)(\s|$)")
_TERMINAL = re.compile(r"[.!?:;)\]][\"')\]`*_]*$")


@dataclass
class Violation:
    """One hard-wrapped line: ``path`` at 1-based ``line`` continues ``text``."""

    path: Path
    line: int
    text: str


def find_violations(text: str, path: Path = Path("<string>")) -> list[Violation]:
    """Return each line in ``text`` that a following line hard-wraps onto."""
    violations: list[Violation] = []
    in_code = False
    in_frontmatter = False
    block_ends_here = True  # true once no continuation line can attach
    prev_line = ""
    prev_index = 0
    for index, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if index == 1 and _FRONTMATTER.match(stripped):
            in_frontmatter = True
            block_ends_here = True
            continue
        if in_frontmatter:
            if _FRONTMATTER.match(stripped):
                in_frontmatter = False
            block_ends_here = True
            continue
        if _FENCE.match(stripped):
            in_code = not in_code
            block_ends_here = True
            continue
        if in_code:
            continue
        if not stripped or _HEADING.match(stripped) or _TABLE_ROW.match(stripped):
            block_ends_here = True
            continue
        # A self-contained HTML comment never continues onto the next line.
        if _HTML_COMMENT.match(stripped):
            block_ends_here = True
            continue
        # A new list item starts a fresh unit, even without a blank line
        # before it, so it never counts as a hard-wrap continuation. A line
        # that opens with a bold term or a "Label:" prefix is a definition-
        # list-style item and gets the same treatment.
        starts_list_item = bool(_LIST_MARKER.match(raw_line)) or bool(
            _STANDALONE_LABEL.match(stripped)
        )
        if not block_ends_here and not starts_list_item:
            violations.append(Violation(path, prev_index, prev_line))
        block_ends_here = bool(_TERMINAL.search(stripped))
        prev_line = stripped
        prev_index = index
    return violations


def check_file(path: Path) -> list[Violation]:
    """Run :func:`find_violations` against a file on disk."""
    return find_violations(path.read_text(encoding="utf-8"), path)


def main(argv: list[str]) -> int:
    """Pre-commit entry point: check each path given, print violations, fail on any."""
    violations = [v for arg in argv for v in check_file(Path(arg))]
    for v in violations:
        print(
            f"{v.path}:{v.line}: hard-wrapped line, continued by the next line "
            f"instead of ending the sentence: {v.text!r}"
        )
    if violations:
        print(
            f"\n{len(violations)} hard-wrapped line(s). "
            "Write one sentence per line instead of wrapping at a column width."
        )
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
