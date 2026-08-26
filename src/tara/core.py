"""Core logic: assemble Copilot guardrails + MCP config from packaged defaults.

Tara is installed per-repo. Every command operates on the current working
directory (the project being set up). Default instructions and MCP servers ship
as package data under ``tara/data`` and can be extended per-repo via optional
``.tara/`` override files.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from importlib import resources
from pathlib import Path

# Outputs (relative to the repo being set up)
COPILOT_INSTRUCTIONS = Path(".github") / "copilot-instructions.md"
# Root .mcp.json (the editor-agnostic location the Copilot CLI reads). Uses the
# `mcpServers` schema key. Not VS Code's `.vscode/mcp.json`.
MCP_CONFIG = Path(".mcp.json")

# opencode output (relative to the repo being set up). opencode.json references
# the Copilot instruction file directly, so no duplicate AGENTS.md is written.
OPENCODE_CONFIG = Path("opencode.json")

# Claude Code output (relative to the repo being set up). CLAUDE.md is a thin
# pointer that `@`-imports the Copilot instruction file, so there is no second
# copy of the instructions to maintain. Claude Code reads the root .mcp.json
# (`mcpServers` schema) natively, so MCP needs no translation.
CLAUDE_INSTRUCTIONS = Path("CLAUDE.md")

# ── Tool selection ────────────────────────────────────────────────────────────

# Copilot's .github/ setup is always the source of truth, so it is always a
# configured tool and never a port target. The others are generated from it.
COPILOT = "copilot"
OPENCODE = "opencode"
CLAUDE = "claude"
SUPPORTED_TOOLS = (COPILOT, OPENCODE, CLAUDE)

# Shorthand accepted on the CLI and in legacy configs, meaning every tool.
ALL_TOOLS = "all"


def normalize_tools(values: Iterable[str] | str) -> list[str]:
    """Validate a set of tool names into the canonical configured list.

    Accepts the ``all`` shorthand, ignores case and blanks, de-duplicates, and
    always includes Copilot, since every other tool is generated from it. A bare
    string is treated as a single name, not as a sequence of characters.
    Raises ValueError naming the first unrecognised tool.
    """
    if isinstance(values, str):
        values = [values]
    selected = {COPILOT}
    for value in values:
        name = value.strip().lower()
        if not name:
            continue
        if name == ALL_TOOLS:
            selected.update(SUPPORTED_TOOLS)
            continue
        if name not in SUPPORTED_TOOLS:
            raise ValueError(
                f"unknown tool '{value}'; choose from "
                f"{', '.join((*SUPPORTED_TOOLS, ALL_TOOLS))}"
            )
        selected.add(name)
    return [tool for tool in SUPPORTED_TOOLS if tool in selected]


def port_targets(tools: Iterable[str]) -> list[str]:
    """The configured tools whose files Tara generates (everything but Copilot)."""
    return [tool for tool in normalize_tools(tools) if tool != COPILOT]


# ── Frontmatter helpers (shared by the ports) ─────────────────────────────────
# See :mod:`tara.frontmatter` for reading and writing agent-file frontmatter.


def data_path() -> Path:
    """On-disk path to bundled package data (``tara/data``)."""
    return Path(str(resources.files("tara").joinpath("data")))


def repo_root() -> Path:
    """The project Tara is operating on (current working directory)."""
    return Path.cwd()


def available_stacks() -> list[str]:
    """Stacks that have instructions and/or MCP defaults bundled."""
    data = data_path()
    names: set[str] = set()
    for sub in ("instructions", "mcp"):
        folder = data / sub
        if folder.is_dir():
            for f in folder.iterdir():
                if f.name.startswith("base."):
                    continue
                names.add(f.stem)
    return sorted(names)


# ── MCP ───────────────────────────────────────────────────────────────────────


def _load_servers(path: Path) -> dict:
    """Read an MCP server map, accepting both the CLI and VS Code schema keys."""
    if not path.exists():
        return {}
    raw = json.loads(path.read_text())
    return raw.get("mcpServers") or raw.get("servers") or {}


def merged_servers(stack: str | None) -> dict:
    """Merge base + optional stack + optional repo-local MCP servers."""
    data = data_path()
    servers = _load_servers(data / "mcp" / "base.json")
    if stack:
        servers |= _load_servers(data / "mcp" / f"{stack}.json")
    servers |= _load_servers(repo_root() / ".tara" / "mcp.local.json")
    return servers


# ── Instructions ──────────────────────────────────────────────────────────────


def assemble_instructions(stack: str | None) -> str:
    """Merge base + optional stack + optional repo-local instructions."""
    data = data_path()
    parts = [(data / "instructions" / "base.md").read_text()]
    if stack:
        stack_file = data / "instructions" / f"{stack}.md"
        if stack_file.exists():
            parts.append(stack_file.read_text())
    local = repo_root() / ".tara" / "instructions.local.md"
    if local.exists():
        parts.append(local.read_text())
    return "\n\n---\n\n".join(p.rstrip() for p in parts) + "\n"


# ── Writers (GitHub Copilot only) ─────────────────────────────────────────────


def _write(rel: Path, text: str, dry_run: bool) -> str:
    path = repo_root() / rel
    if dry_run:
        return f"  [dry-run] {rel}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return f"  wrote {rel}"


def write_instructions(stack: str | None, dry_run: bool) -> str:
    """Write ``.github/copilot-instructions.md`` from the assembled instructions."""
    return _write(COPILOT_INSTRUCTIONS, assemble_instructions(stack), dry_run)


def write_mcp(stack: str | None, dry_run: bool) -> str:
    """Write ``.mcp.json`` with the MCP servers merged for ``stack``."""
    content = json.dumps({"mcpServers": merged_servers(stack)}, indent=2) + "\n"
    return _write(MCP_CONFIG, content, dry_run)


# ── opencode MCP schema translation ───────────────────────────────────────────

OPENCODE_SCHEMA = "https://opencode.ai/config.json"


def _to_opencode_server(config: dict) -> dict:
    """Translate one Copilot-schema MCP server into opencode's schema.

    Copilot/`.mcp.json` uses ``{command, args, env}`` for stdio servers and
    ``{type: "http", url, headers}`` for remote ones. opencode expects a
    top-level ``mcp`` map whose entries are ``{type: "local", command: [...],
    environment}`` or ``{type: "remote", url, headers}``.
    """
    if config.get("url") or config.get("type") == "http":
        server: dict = {"type": "remote", "url": config.get("url", ""), "enabled": True}
        if config.get("headers"):
            server["headers"] = config["headers"]
        return server

    command = (
        [config["command"], *config.get("args", [])] if config.get("command") else []
    )
    server = {"type": "local", "command": command, "enabled": True}
    if config.get("env"):
        server["environment"] = config["env"]
    return server


def to_opencode_mcp(servers: dict) -> dict:
    """Translate a Copilot-schema server map into opencode's ``mcp`` map."""
    return {name: _to_opencode_server(cfg) for name, cfg in servers.items()}


def read_mcp_servers() -> dict:
    """Current servers in the repo's .mcp.json (base + local if absent)."""
    path = repo_root() / MCP_CONFIG
    if not path.exists():
        return dict(merged_servers(None))
    return _load_servers(path)


def add_mcp_server(name: str, config: dict, dry_run: bool = False) -> str:
    """Merge one MCP server into .mcp.json, keeping existing servers."""
    if dry_run:
        return f"  [dry-run] mcp {name}"
    servers = read_mcp_servers()
    servers[name] = config
    content = json.dumps({"mcpServers": servers}, indent=2) + "\n"
    return _write(MCP_CONFIG, content, dry_run)
