"""Read and write the YAML frontmatter of the markdown files agents consume.

Frontmatter is YAML by mandate: Copilot, Claude Code, and opencode all require a
``---`` delimited YAML block at the top of skills, agents, and prompts. So
reading goes through a real YAML parser and writing goes through Pydantic models
that declare each target tool's schema. Nothing here hand-builds or hand-scans
YAML text, which is what keeps quoting, escaping, and block scalars correct.

(Tara's own config files are TOML; only these agent-facing files are YAML.)
"""

from __future__ import annotations

import re
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict

DELIM = "---"

# Long descriptions must stay on one line: line-wrapped YAML is still valid, but
# it makes diffs noisy and trips naive third-party readers.
_NO_WRAP = 10**6


def parse(text: str) -> tuple[dict[str, Any], str]:
    """Split a markdown document into its frontmatter mapping and its body.

    Values keep their YAML types, so ``tools: [read, search]`` parses as a list
    rather than a string that has to be re-scanned. Returns ``({}, text)`` when
    the document has no valid ``---`` delimited YAML mapping.
    """
    lines = text.splitlines()
    if not lines or lines[0].rstrip() != DELIM:
        return {}, text
    # The closing delimiter must sit at column 0: an indented `---` belongs to a
    # block scalar's content, and treating it as the end truncates the mapping.
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == DELIM), None)
    if end is None:
        return {}, text
    try:
        # The trailing newline matters: without it a block scalar in the last
        # key clips differently from one followed by another key.
        data = yaml.safe_load("\n".join(lines[1:end]) + "\n")
    except yaml.YAMLError:
        return {}, text
    if not isinstance(data, dict):
        return {}, text
    return data, "\n".join(lines[end + 1 :]).strip()


def text_of(value: Any) -> str:
    """Coerce one frontmatter value to a trimmed string (``''`` when missing).

    YAML types leak into frontmatter (``description: 1.0`` is a float), so
    callers that want text go through this instead of assuming ``str``.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple)):
        return ", ".join(text_of(v) for v in value)
    return str(value)


def tokens(value: Any) -> list[str]:
    """Read a value written either as a YAML list or a delimited string.

    Tool lists appear both ways in the wild (``tools: [read, search]`` and
    ``tools: read, search``); both yield lowercased names.
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        items = [text_of(v) for v in value]
    else:
        items = re.split(r"[,\s]+", text_of(value).strip("[]"))
    return [item.lower() for item in items if item]


class Frontmatter(BaseModel):
    """Base for a target tool's frontmatter schema.

    ``extra="forbid"`` keeps a port honest: a key the target tool does not
    understand fails at construction instead of being written to disk.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    def render(self, body: str) -> str:
        """Serialize this frontmatter plus ``body`` into a markdown document.

        Unset (``None``) fields are omitted, and PyYAML handles all quoting.
        """
        data = self.model_dump(exclude_none=True, by_alias=True)
        block = yaml.safe_dump(
            data,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            width=_NO_WRAP,
        )
        return f"{DELIM}\n{block}{DELIM}\n\n{body.strip()}\n"
