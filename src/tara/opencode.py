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

Everything here is generated; users edit the Copilot side (or Tara's central
standard) and re-run ``tara integrations`` to regenerate.
"""

from __future__ import annotations

import json
from pathlib import Path

from tara import core, frontmatter, generate
from tara.core import (
    COPILOT_INSTRUCTIONS,
    OPENCODE_CONFIG,
    read_mcp_servers,
    repo_root,
)
from tara.frontmatter import Frontmatter

# Copilot sources.
COPILOT_AGENTS_DIR = Path(".github") / "agents"
COPILOT_PROMPTS_DIR = Path(".github") / "prompts"
COPILOT_SKILLS_DIR = Path(".github") / "skills"

# opencode destinations.
OPENCODE_AGENTS_DIR = Path(".opencode") / "agents"
OPENCODE_COMMANDS_DIR = Path(".opencode") / "commands"
OPENCODE_SKILLS_DIR = Path(".opencode") / "skills"

# Copilot tool names that imply write / bash access.
_WRITE_TOOLS = frozenset(
    {"write", "create", "edit", "editfiles", "apply_patch", "patch"}
)
_BASH_TOOLS = frozenset(
    {"bash", "shell", "terminal", "run", "runcommands", "runtasks", "execute"}
)


class OpencodeAgent(Frontmatter):
    """Frontmatter of an opencode agent (``.opencode/agents/<name>.md``).

    opencode uses the singular ``permission`` key, mapping a capability to
    ``allow`` or ``deny``.
    """

    description: str | None = None
    mode: str = "subagent"
    permission: dict[str, str] | None = None


class OpencodeCommand(Frontmatter):
    """Frontmatter of an opencode command (``.opencode/commands/<name>.md``)."""

    description: str | None = None


# Starter commands, written only when the Copilot prompts didn't already
# produce a command of the same name and the file doesn't already exist.
_STARTER_COMMANDS: dict[str, tuple[OpencodeCommand, str]] = {
    "check.md": (
        OpencodeCommand(description="Run the lint and test gate (ruff + pytest)"),
        "Run the project check gate and report any failures:\n\n"
        "!`uv run ruff check --fix && uv run ruff format && uv run pytest`",
    ),
    "review.md": (
        OpencodeCommand(
            description="Review staged changes for quality and correctness"
        ),
        "@gilfoyle Review these staged changes for quality, correctness, and"
        " performance issues:\n\n"
        "!`git diff --staged`",
    ),
}


# ── Frontmatter translation ───────────────────────────────────────────────────


def _agent_permission(
    copilot_tools: object, declared: bool = True
) -> dict[str, str] | None:
    """Deny each capability the Copilot tool list does not grant.

    Returns ``None`` when nothing is denied, so the key is omitted entirely.
    """
    tools = frontmatter.tokens(copilot_tools)
    if not declared or any(tool in {"*", "all"} for tool in tools):
        return None
    if not tools:
        return {"*": "deny"}
    deny = {
        capability: "deny"
        for capability, granting in (("edit", _WRITE_TOOLS), ("bash", _BASH_TOOLS))
        if not any(t in granting for t in tools)
    }
    return deny or None


def translate_agent(source: Path) -> str:
    """Translate a Copilot ``.agent.md`` file into opencode agent markdown."""
    fm, body = frontmatter.parse(source.read_text())
    agent = OpencodeAgent(
        description=frontmatter.text_of(fm.get("description")) or None,
        permission=_agent_permission(fm.get("tools"), declared="tools" in fm),
    )
    return agent.render(generate.marked(body))


def translate_prompt(source: Path) -> str:
    """Translate a Copilot ``.prompt.md`` file into an opencode command.

    Keeps the ``description`` and body; drops Copilot-only frontmatter
    (``agent``/``tools``) that opencode commands don't use.
    """
    fm, body = frontmatter.parse(source.read_text())
    description = frontmatter.text_of(fm.get("description"))
    if not description:
        return generate.marked(body)
    return OpencodeCommand(description=description).render(generate.marked(body))


def opencode_agent_name(filename: str) -> str:
    """Map ``foo.agent.md`` (Copilot) to ``foo.md`` (opencode)."""
    return f"{filename.removesuffix('.agent.md')}.md"


# ── Port steps ────────────────────────────────────────────────────────────────


def port_config(dry_run: bool = False, force: bool = False) -> str:
    """Update opencode.json with Copilot instructions + translated MCP servers.

    Only the three keys Tara owns are touched; any other settings already in the
    file (``model``, ``theme``, ``provider``, ``agent``, ...) are preserved.
    """
    root = repo_root()
    dest = root / OPENCODE_CONFIG
    if dest.is_symlink():
        return f"  skipped {OPENCODE_CONFIG} (destination is a symlink, left untouched)"
    config: dict[str, object] = {}
    if dest.exists():
        try:
            loaded = json.loads(dest.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            return f"  skipped {OPENCODE_CONFIG} (cannot safely merge: {exc})"
        if isinstance(loaded, dict):
            config = loaded
        else:
            return (
                f"  skipped {OPENCODE_CONFIG} "
                "(cannot safely merge: root must be an object)"
            )

    instructions: list[str] = []
    if (root / COPILOT_INSTRUCTIONS).exists():
        instructions.append(str(COPILOT_INSTRUCTIONS))
    config["$schema"] = core.OPENCODE_SCHEMA
    config["instructions"] = instructions
    config["mcp"] = core.to_opencode_mcp(read_mcp_servers())

    text = json.dumps(config, indent=2) + "\n"
    rel = dest.relative_to(root)
    if dest.is_file() and dest.read_text(encoding="utf-8") == text:
        return f"  unchanged {rel}"
    if dry_run:
        return f"  [dry-run] {rel}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    return f"  wrote {rel}"


def port_agents(dry_run: bool = False, force: bool = False) -> list[str]:
    """Translate every ``.github/agents/*.agent.md`` into ``.opencode/agents/``.

    A destination file Tara did not generate is left untouched.
    """
    root = repo_root()
    src_dir = root / COPILOT_AGENTS_DIR
    if not src_dir.is_dir():
        return []
    lines: list[str] = []
    for src in sorted(src_dir.glob("*.agent.md")):
        dest = root / OPENCODE_AGENTS_DIR / opencode_agent_name(src.name)
        lines.append(
            generate.write_generated(dest, translate_agent(src), dry_run, force)
        )
    return lines


def port_commands(dry_run: bool = False, force: bool = False) -> list[str]:
    """Translate ``.github/prompts/**/*.prompt.md`` and add starter commands.

    Prompt-derived commands take precedence; a starter command is only written
    when no command exists at that path (on disk or from a ported prompt).
    """
    root = repo_root()
    lines: list[str] = []
    produced: set[str] = set()

    src_dir = root / COPILOT_PROMPTS_DIR
    if src_dir.is_dir():
        for src in sorted(src_dir.glob("**/*.prompt.md")):
            rel = src.relative_to(src_dir)
            rel_dest = rel.with_name(rel.name.removesuffix(".prompt.md") + ".md")
            dest = root / OPENCODE_COMMANDS_DIR / rel_dest
            # Keyed by path, not basename: a nested python/check.md is a
            # different command from the root check.md starter.
            produced.add(rel_dest.as_posix())
            lines.append(
                generate.write_generated(dest, translate_prompt(src), dry_run, force)
            )

    for filename, (command, body) in _STARTER_COMMANDS.items():
        dest = root / OPENCODE_COMMANDS_DIR / filename
        if filename in produced or dest.exists():
            continue
        lines.append(
            generate.write_generated(
                dest, command.render(generate.marked(body)), dry_run, force
            )
        )
    return lines


def port_skills(dry_run: bool = False, force: bool = False) -> list[str]:
    """Mirror ``.github/skills/`` into ``.opencode/skills/`` (identical SKILL.md).

    Only skills Tara mirrored before are refreshed or pruned; a skill directory
    the developer put there is never replaced or deleted.
    """
    root = repo_root()
    return generate.mirror_skills(
        "opencode",
        root / COPILOT_SKILLS_DIR,
        root / OPENCODE_SKILLS_DIR,
        dry_run,
        force,
    )


def port_all(dry_run: bool = False, force: bool = False) -> list[tuple[str, list[str]]]:
    """Port every part of the Copilot setup into opencode files.

    Returns ``(section_title, status_lines)`` pairs for display.
    """
    return [
        ("Config", [port_config(dry_run, force)]),
        ("Agents", port_agents(dry_run, force)),
        ("Commands", port_commands(dry_run, force)),
        ("Skills", port_skills(dry_run, force)),
    ]


def _remove_config(dry_run: bool) -> str | None:
    """Remove Tara-managed OpenCode keys while preserving user settings."""
    path = repo_root() / OPENCODE_CONFIG
    if not path.is_file() or path.is_symlink():
        return None
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(config, dict):
        return None
    for key in ("$schema", "instructions", "mcp"):
        config.pop(key, None)
    if dry_run:
        return f"  [dry-run] update {OPENCODE_CONFIG}"
    if config:
        path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        return f"  updated {OPENCODE_CONFIG}"
    path.unlink()
    return f"  removed {OPENCODE_CONFIG}"


def remove_all(dry_run: bool = False) -> list[str]:
    """Remove Tara-owned OpenCode artifacts for a disabled integration."""
    root = repo_root()
    lines: list[str] = []
    config = _remove_config(dry_run)
    if config is not None:
        lines.append(config)
    lines.extend(
        generate.remove_generated_markdown(root / OPENCODE_AGENTS_DIR, dry_run)
    )
    lines.extend(
        generate.remove_generated_markdown(root / OPENCODE_COMMANDS_DIR, dry_run)
    )
    lines.extend(
        generate.remove_owned_skills("opencode", root / OPENCODE_SKILLS_DIR, dry_run)
    )
    return lines
