"""Port a GitHub Copilot setup into opencode files.

Copilot's ``.github/`` layout is the single source of truth. This module
projects it into the files opencode reads, so there is only ever one copy to
maintain:

- ``opencode.json``        references ``.github/copilot-instructions.md`` (no
                           duplicate AGENTS.md) and carries the MCP servers from
                           ``.mcp.json`` translated into opencode's schema
- ``.opencode/agents/``    translated from ``.github/agents/*.agent.md``
- ``.opencode/commands/``  translated from ``.github/prompts/**/*.prompt.md``
                           plus starter ``check``/``review`` commands
- ``.opencode/skills/``    mirrored from ``.github/skills/`` (identical SKILL.md)

Everything here is generated; users edit the Copilot side (or wingman's central
standard) and re-run ``wingman opencode sync`` to regenerate.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from wingman import core
from wingman.audit import parse_frontmatter
from wingman.core import (
    COPILOT_INSTRUCTIONS,
    OPENCODE_CONFIG,
    read_mcp_servers,
    repo_root,
)

# Copilot sources.
COPILOT_AGENTS_DIR = Path(".github") / "agents"
COPILOT_PROMPTS_DIR = Path(".github") / "prompts"
COPILOT_SKILLS_DIR = Path(".github") / "skills"

# opencode destinations.
OPENCODE_AGENTS_DIR = Path(".opencode") / "agents"
OPENCODE_COMMANDS_DIR = Path(".opencode") / "commands"
OPENCODE_SKILLS_DIR = Path(".opencode") / "skills"

# Copilot tool names that imply write / bash access.
_WRITE_TOOLS = frozenset({"write", "create", "edit", "apply_patch", "patch"})
_BASH_TOOLS = frozenset({"bash", "shell", "terminal", "run", "execute"})

# Starter commands, written only when the Copilot prompts didn't already
# produce a command of the same name and the file doesn't already exist.
_STARTER_COMMANDS: dict[str, str] = {
    "check.md": (
        "---\n"
        "description: Run the lint and test gate (ruff + pytest)\n"
        "---\n\n"
        "Run the project check gate and report any failures:\n\n"
        "!`uv run ruff check --fix && uv run ruff format && uv run pytest`\n"
    ),
    "review.md": (
        "---\n"
        "description: Review staged changes for quality and correctness\n"
        "---\n\n"
        "@gilfoyle Review these staged changes for quality, correctness, and"
        " performance issues:\n\n"
        "!`git diff --staged`\n"
    ),
}


def _write_text(dest: Path, text: str, dry_run: bool) -> str:
    root = repo_root()
    rel = dest.relative_to(root)
    if dry_run:
        return f"  [dry-run] {rel}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text)
    return f"  wrote {rel}"


# ── Frontmatter translation ───────────────────────────────────────────────────


def _quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _parse_tools(raw: str) -> list[str]:
    """Parse a YAML inline list or space/comma-separated string into tool names."""
    raw = raw.strip().removeprefix("[").removesuffix("]")
    return [
        t.strip().strip("'\"").lower() for t in re.split(r"[,\s]+", raw) if t.strip()
    ]


def _agent_frontmatter(copilot_fm: dict[str, str]) -> str:
    """Return the opencode agent YAML frontmatter body (without the ``---`` fences).

    opencode uses the singular ``permission`` key; each capability the Copilot
    tool list lacks is denied.
    """
    lines: list[str] = []
    description = copilot_fm.get("description", "").strip()
    if description:
        lines.append(f"description: {_quote(description)}")
    lines.append("mode: subagent")

    tools = _parse_tools(copilot_fm.get("tools", ""))
    deny: list[str] = []
    if not any(t in _WRITE_TOOLS for t in tools):
        deny.append("edit: deny")
    if not any(t in _BASH_TOOLS for t in tools):
        deny.append("bash: deny")
    if deny:
        lines.append("permission:")
        lines.extend(f"  {d}" for d in deny)
    return "\n".join(lines)


def translate_agent(source: Path) -> str:
    """Translate a Copilot ``.agent.md`` file into opencode agent markdown."""
    fm, body = parse_frontmatter(source.read_text())
    return f"---\n{_agent_frontmatter(fm)}\n---\n\n{body}\n"


def translate_prompt(source: Path) -> str:
    """Translate a Copilot ``.prompt.md`` file into an opencode command.

    Keeps the ``description`` and body; drops Copilot-only frontmatter
    (``agent``/``tools``) that opencode commands don't use.
    """
    fm, body = parse_frontmatter(source.read_text())
    description = fm.get("description", "").strip()
    if description:
        return f"---\ndescription: {_quote(description)}\n---\n\n{body}\n"
    return f"{body}\n"


def opencode_agent_name(filename: str) -> str:
    """Map ``foo.agent.md`` (Copilot) to ``foo.md`` (opencode)."""
    return f"{filename.removesuffix('.agent.md')}.md"


# ── Port steps ────────────────────────────────────────────────────────────────


def port_config(dry_run: bool = False) -> str:
    """Write opencode.json referencing Copilot instructions + translated MCP servers."""
    root = repo_root()
    instructions: list[str] = []
    if (root / COPILOT_INSTRUCTIONS).exists():
        instructions.append(str(COPILOT_INSTRUCTIONS))
    config = {
        "$schema": core.OPENCODE_SCHEMA,
        "instructions": instructions,
        "mcp": core.to_opencode_mcp(read_mcp_servers()),
    }
    return _write_text(
        root / OPENCODE_CONFIG, json.dumps(config, indent=2) + "\n", dry_run
    )


def port_agents(dry_run: bool = False) -> list[str]:
    """Translate every ``.github/agents/*.agent.md`` into ``.opencode/agents/``."""
    root = repo_root()
    src_dir = root / COPILOT_AGENTS_DIR
    if not src_dir.is_dir():
        return []
    lines: list[str] = []
    for src in sorted(src_dir.glob("*.agent.md")):
        dest = root / OPENCODE_AGENTS_DIR / opencode_agent_name(src.name)
        lines.append(_write_text(dest, translate_agent(src), dry_run))
    return lines


def port_commands(dry_run: bool = False) -> list[str]:
    """Translate ``.github/prompts/**/*.prompt.md`` and add starter commands.

    Prompt-derived commands take precedence; a starter command is only written
    when no command of that name exists (on disk or from a ported prompt).
    """
    root = repo_root()
    lines: list[str] = []
    produced: set[str] = set()

    src_dir = root / COPILOT_PROMPTS_DIR
    if src_dir.is_dir():
        for src in sorted(src_dir.glob("**/*.prompt.md")):
            rel = src.relative_to(src_dir)
            dest = (
                root
                / OPENCODE_COMMANDS_DIR
                / rel.with_name(rel.name.removesuffix(".prompt.md") + ".md")
            )
            produced.add(dest.name)
            lines.append(_write_text(dest, translate_prompt(src), dry_run))

    for filename, content in _STARTER_COMMANDS.items():
        dest = root / OPENCODE_COMMANDS_DIR / filename
        if filename in produced or dest.exists():
            continue
        lines.append(_write_text(dest, content, dry_run))
    return lines


def port_skills(dry_run: bool = False) -> list[str]:
    """Mirror ``.github/skills/`` into ``.opencode/skills/`` (identical SKILL.md).

    Skills present only under opencode (stale copies of removed Copilot skills)
    are pruned so the two stay in sync.
    """
    root = repo_root()
    src_dir = root / COPILOT_SKILLS_DIR
    dst_dir = root / OPENCODE_SKILLS_DIR
    sources = (
        {p.parent.name for p in src_dir.glob("*/SKILL.md")}
        if src_dir.is_dir()
        else set()
    )
    existing = {p.name for p in dst_dir.iterdir()} if dst_dir.is_dir() else set()

    lines: list[str] = []
    for name in sorted(sources):
        dest = dst_dir / name
        rel = dest.relative_to(root)
        if dry_run:
            lines.append(f"  [dry-run] {rel}")
            continue
        if dest.exists():
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src_dir / name, dest, ignore=shutil.ignore_patterns(".git"))
        lines.append(f"  mirrored {rel}")

    for stale in sorted(existing - sources):
        dest = dst_dir / stale
        if dry_run:
            lines.append(f"  [dry-run] prune {dest.relative_to(root)}")
            continue
        shutil.rmtree(dest)
        lines.append(f"  pruned {dest.relative_to(root)}")
    return lines


def port_all(dry_run: bool = False) -> list[tuple[str, list[str]]]:
    """Port every part of the Copilot setup into opencode files.

    Returns ``(section_title, status_lines)`` pairs for display.
    """
    return [
        ("Config", [port_config(dry_run)]),
        ("Agents", port_agents(dry_run)),
        ("Commands", port_commands(dry_run)),
        ("Skills", port_skills(dry_run)),
    ]
