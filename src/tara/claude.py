"""Port a GitHub Copilot setup into Claude Code files.

Copilot's ``.github/`` layout is the single source of truth. This module
projects it into the files Claude Code reads, so there is only ever one copy to
maintain:

- ``CLAUDE.md``            a thin pointer that ``@``-imports
                           ``.github/copilot-instructions.md`` (no duplicated
                           instruction text)
- ``.claude/agents/``      translated from ``.github/agents/*.agent.md``
- ``.claude/commands/``    translated from ``.github/prompts/**/*.prompt.md``
                           plus starter ``check``/``review`` commands
- ``.claude/skills/``      mirrored from ``.github/skills/`` (identical SKILL.md)

MCP needs no translation: Claude Code reads the repo-root ``.mcp.json`` with the
same ``mcpServers`` schema Tara already writes.

Everything here is generated; users edit the Copilot side (or Tara's central
standard) and re-run ``tara integrations`` to regenerate.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field

from tara import frontmatter, generate
from tara.core import (
    CLAUDE_INSTRUCTIONS,
    COPILOT_INSTRUCTIONS,
    MCP_CONFIG,
    repo_root,
)
from tara.frontmatter import Frontmatter

# Copilot sources.
COPILOT_AGENTS_DIR = Path(".github") / "agents"
COPILOT_PROMPTS_DIR = Path(".github") / "prompts"
COPILOT_SKILLS_DIR = Path(".github") / "skills"

# Claude Code destinations.
CLAUDE_AGENTS_DIR = Path(".claude") / "agents"
CLAUDE_COMMANDS_DIR = Path(".claude") / "commands"
CLAUDE_SKILLS_DIR = Path(".claude") / "skills"

# Marks a file as Tara-generated. A file without it is the developer's, so the
# port leaves it alone rather than destroying their own context.
GENERATED_MARKER = generate.MARKER

# Copilot's tool vocabulary mapped onto Claude Code's built-in tool names. One
# Copilot capability can imply several Claude tools (``search`` covers both
# Glob and Grep).
_TOOL_MAP: dict[str, tuple[str, ...]] = {
    "read": ("Read",),
    "search": ("Glob", "Grep"),
    "codebase": ("Glob", "Grep", "Read"),
    "usages": ("Glob", "Grep"),
    "findtestfiles": ("Glob",),
    "problems": ("Read",),
    "edit": ("Edit", "Write"),
    "editfiles": ("Edit", "Write"),
    "write": ("Write",),
    "create": ("Write",),
    "apply_patch": ("Edit",),
    "patch": ("Edit",),
    "execute": ("Bash",),
    "bash": ("Bash",),
    "shell": ("Bash",),
    "terminal": ("Bash",),
    "run": ("Bash",),
    "runcommands": ("Bash",),
    "runtasks": ("Bash",),
    "fetch": ("WebFetch",),
    "websearch": ("WebSearch",),
    "web_search": ("WebSearch",),
}

# Fallback allowlist when a Copilot agent names only tools Claude has no
# equivalent for. Omitting ``tools`` would inherit *everything* including Bash
# and Write, so an unrecognised list fails closed onto read-only access.
_SAFE_TOOLS = ("Glob", "Grep", "Read")
_ALL_CLAUDE_TOOLS = sorted(
    {tool for mapped_tools in _TOOL_MAP.values() for tool in mapped_tools}
)


class ClaudeAgent(Frontmatter):
    """Frontmatter of a Claude Code subagent (``.claude/agents/<name>.md``).

    ``tools`` is an explicit allowlist; leaving it unset inherits the full toolset.
    """

    name: str
    description: str | None = None
    tools: list[str] | None = None


class ClaudeCommand(Frontmatter):
    """Frontmatter of a Claude Code slash command (``.claude/commands/<name>.md``).

    ``allowed_tools`` is emitted as ``allowed-tools``, the key Claude Code reads
    to permit the ``!`` bash pre-execution in a command body. The rename is a
    serialization alias, so the field keeps its Python name on construction.
    """

    description: str | None = None
    allowed_tools: str | None = Field(default=None, serialization_alias="allowed-tools")


# Starter commands, written only when the Copilot prompts didn't already
# produce a command of the same name and the file doesn't already exist.
_STARTER_COMMANDS: dict[str, tuple[ClaudeCommand, str]] = {
    "check.md": (
        ClaudeCommand(
            description="Run the lint and test gate (ruff + pytest)",
            allowed_tools="Bash(uv run:*)",
        ),
        "Run the project check gate and report any failures:\n\n"
        "!`uv run ruff check --fix && uv run ruff format && uv run pytest`",
    ),
    "review.md": (
        ClaudeCommand(
            description="Review staged changes for quality and correctness",
            allowed_tools="Bash(git diff:*)",
        ),
        "Use the gilfoyle subagent to review these staged changes for quality,"
        " correctness, and performance issues:\n\n"
        "!`git diff --staged`",
    ),
}


# ── Frontmatter translation ───────────────────────────────────────────────────


def claude_tools(copilot_tools: object) -> list[str]:
    """Map a Copilot ``tools`` value onto sorted Claude Code tool names.

    Unknown names are dropped: granting a tool Claude does not have would make
    the whole allowlist invalid.
    """
    names: set[str] = set()
    for tool in frontmatter.tokens(copilot_tools):
        names.update(_TOOL_MAP.get(tool, ()))
    return sorted(names)


def claude_agent_name(filename: str) -> str:
    """Map ``foo.agent.md`` (Copilot) to the Claude subagent name ``foo``."""
    return filename.removesuffix(".agent.md")


def translate_agent(source: Path) -> str:
    """Translate a Copilot ``.agent.md`` file into Claude Code subagent markdown.

    An agent that declared tools always gets an explicit allowlist: if none of
    its names map onto Claude tools it falls back to :data:`_SAFE_TOOLS` rather
    than omitting the key, which would silently inherit Bash and Write.
    """
    fm, body = frontmatter.parse(source.read_text())
    if "tools" not in fm:
        tools = None
    else:
        declared = frontmatter.tokens(fm["tools"])
        if not declared:
            tools = []
        elif any(name in {"*", "all"} for name in declared):
            tools = _ALL_CLAUDE_TOOLS
        else:
            tools = claude_tools(fm["tools"]) or list(_SAFE_TOOLS)
    agent = ClaudeAgent(
        name=claude_agent_name(source.name),
        description=frontmatter.text_of(fm.get("description")) or None,
        tools=tools,
    )
    return agent.render(generate.marked(body))


def translate_prompt(source: Path) -> str:
    """Translate a Copilot ``.prompt.md`` file into a Claude Code slash command.

    Keeps the ``description`` and body; drops Copilot-only frontmatter
    (``agent``/``tools``) that Claude commands don't use.
    """
    fm, body = frontmatter.parse(source.read_text())
    description = frontmatter.text_of(fm.get("description"))
    if not description:
        return generate.marked(body)
    return ClaudeCommand(description=description).render(generate.marked(body))


# ── Port steps ────────────────────────────────────────────────────────────────


def port_instructions(dry_run: bool = False, force: bool = False) -> str:
    """Write ``CLAUDE.md`` as a pointer importing the Copilot instructions.

    A pre-existing CLAUDE.md that Tara did not generate is left untouched, so a
    hand-written project brief is never clobbered.
    """
    root = repo_root()
    dest = root / CLAUDE_INSTRUCTIONS
    text = (
        f"{GENERATED_MARKER}\n"
        f"<!-- Edit {COPILOT_INSTRUCTIONS.as_posix()} instead, then re-run "
        f"`tara integrations`. -->\n\n"
        f"# Project instructions\n\n"
        f"@{COPILOT_INSTRUCTIONS.as_posix()}\n"
    )
    return generate.write_generated(dest, text, dry_run, force)


def port_mcp() -> str:
    """Report on ``.mcp.json``; Claude Code reads Tara's schema as-is.

    Nothing is written: Copilot and Claude Code share the repo-root
    ``mcpServers`` format, so the file Tara already wrote is the one Claude
    Code loads.
    """
    rel = MCP_CONFIG.as_posix()
    if (repo_root() / MCP_CONFIG).exists():
        return f"  reused {rel} (Claude Code reads it natively, no port needed)"
    return f"  missing {rel} (run `tara init` to write it)"


def port_agents(dry_run: bool = False, force: bool = False) -> list[str]:
    """Translate every ``.github/agents/*.agent.md`` into ``.claude/agents/``.

    A destination file Tara did not generate is left untouched.
    """
    root = repo_root()
    src_dir = root / COPILOT_AGENTS_DIR
    if not src_dir.is_dir():
        return []
    lines: list[str] = []
    for src in sorted(src_dir.glob("*.agent.md")):
        dest = root / CLAUDE_AGENTS_DIR / f"{claude_agent_name(src.name)}.md"
        lines.append(
            generate.write_generated(dest, translate_agent(src), dry_run, force)
        )
    return lines


def port_commands(dry_run: bool = False, force: bool = False) -> list[str]:
    """Translate ``.github/prompts/**/*.prompt.md`` and add starter commands.

    Nesting is preserved: Claude Code turns ``python/add-types.md`` into the
    namespaced ``/python:add-types`` command. Prompt-derived commands take
    precedence; a starter command is only written when no command exists at that
    path (on disk or from a ported prompt).
    """
    root = repo_root()
    lines: list[str] = []
    produced: set[str] = set()

    src_dir = root / COPILOT_PROMPTS_DIR
    if src_dir.is_dir():
        for src in sorted(src_dir.glob("**/*.prompt.md")):
            rel = src.relative_to(src_dir)
            rel_dest = rel.with_name(rel.name.removesuffix(".prompt.md") + ".md")
            dest = root / CLAUDE_COMMANDS_DIR / rel_dest
            # Keyed by path, not basename: a nested python/check.md is a
            # different command from the root check.md starter.
            produced.add(rel_dest.as_posix())
            lines.append(
                generate.write_generated(dest, translate_prompt(src), dry_run, force)
            )

    for filename, (command, body) in _STARTER_COMMANDS.items():
        dest = root / CLAUDE_COMMANDS_DIR / filename
        if filename in produced or dest.exists():
            continue
        lines.append(
            generate.write_generated(
                dest, command.render(generate.marked(body)), dry_run, force
            )
        )
    return lines


def port_skills(dry_run: bool = False, force: bool = False) -> list[str]:
    """Mirror ``.github/skills/`` into ``.claude/skills/`` (identical SKILL.md).

    Only skills Tara mirrored before are refreshed or pruned; a skill directory
    the developer put there is never replaced or deleted.
    """
    root = repo_root()
    return generate.mirror_skills(
        "claude",
        root / COPILOT_SKILLS_DIR,
        root / CLAUDE_SKILLS_DIR,
        dry_run,
        force,
    )


def port_all(dry_run: bool = False, force: bool = False) -> list[tuple[str, list[str]]]:
    """Port every part of the Copilot setup into Claude Code files.

    Returns ``(section_title, status_lines)`` pairs for display.
    """
    return [
        ("Instructions", [port_instructions(dry_run, force)]),
        ("MCP", [port_mcp()]),
        ("Agents", port_agents(dry_run, force)),
        ("Commands", port_commands(dry_run, force)),
        ("Skills", port_skills(dry_run, force)),
    ]


def remove_all(dry_run: bool = False) -> list[str]:
    """Remove Tara-owned Claude Code artifacts for a disabled integration."""
    root = repo_root()
    lines: list[str] = []
    instruction = generate.remove_generated_file(root / CLAUDE_INSTRUCTIONS, dry_run)
    if instruction is not None:
        lines.append(instruction)
    lines.extend(generate.remove_generated_markdown(root / CLAUDE_AGENTS_DIR, dry_run))
    lines.extend(
        generate.remove_generated_markdown(root / CLAUDE_COMMANDS_DIR, dry_run)
    )
    lines.extend(
        generate.remove_owned_skills("claude", root / CLAUDE_SKILLS_DIR, dry_run)
    )
    return lines
