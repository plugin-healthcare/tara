"""The catalog: bundled agents/prompts/instructions plus indexed skills.

Drives the interactive ``tara init`` / ``tara add`` selection. Skills are
fetched from git via :mod:`tara.skills`; agents, prompts, and scoped
instructions are copied from package data into the repo's ``.github/``.
"""

from __future__ import annotations

import json
import shutil
import tomllib
from dataclasses import dataclass
from pathlib import Path

from tara import frontmatter, generate, hooks, skills
from tara.core import add_mcp_server, data_path, repo_root
from tara.sync import normalize_package_name

GITHUB = Path(".github")


@dataclass
class CatalogItem:
    """One offerable catalog artifact (skill, agent, prompt, instructions, or MCP)."""

    name: str
    kind: str  # skill | agent | prompt | instructions | hooks | mcp
    description: str
    source: Path | None = None  # package-data path for bundled items
    is_set: bool = False  # skill themes that install a bundle of skills
    checked: bool = False  # pre-selected in the picker (e.g. default MCP servers)


# ── Discovery ─────────────────────────────────────────────────────────────────


def _first_paragraph(text: str) -> str:
    fm, body = frontmatter.parse(text)
    description = frontmatter.text_of(fm.get("description"))
    if description:
        return description
    for line in body.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return ""


def _bundled(kind: str, folder: str, pattern: str) -> list[CatalogItem]:
    base = data_path() / "catalog" / folder
    if not base.is_dir():
        return []
    items: list[CatalogItem] = []
    for path in sorted(base.glob(pattern)):
        rel = path.relative_to(base)
        items.append(
            CatalogItem(
                name=str(rel),
                kind=kind,
                description=_first_paragraph(path.read_text()),
                source=path,
            )
        )
    return items


def _bundled_skills() -> list[CatalogItem]:
    """Skills shipped as package data under ``data/catalog/skills/<name>/``.

    Each is a folder holding a ``SKILL.md``; the folder name is the skill name.
    These have no upstream git source, so they carry a ``source`` path and are
    installed by copying the tree (not tracked in the manifest).
    """
    base = data_path() / "catalog" / "skills"
    if not base.is_dir():
        return []
    items: list[CatalogItem] = []
    for skill_md in sorted(base.glob("*/SKILL.md")):
        folder = skill_md.parent
        items.append(
            CatalogItem(
                name=folder.name,
                kind="skill",
                description=_first_paragraph(skill_md.read_text()),
                source=folder,
            )
        )
    return items


def catalog_skills() -> list[CatalogItem]:
    """Skill themes offered in the picker, one entry per theme (set).

    Selecting a theme installs all of its skills. Tara's own bundled skills
    (package data, copied in) are listed first, then any loose ``[skills.*]``
    index entries not covered by a theme are appended as individual items.
    """
    items: list[CatalogItem] = _bundled_skills()
    seen = {it.name for it in items}

    for name, sset in skills.read_sets_index().items():
        items.append(
            CatalogItem(
                name=name, kind="skill", description=sset.description, is_set=True
            )
        )

    index = data_path() / "skills" / "index.toml"
    if index.exists():
        loose = tomllib.loads(index.read_text()).get("skills", {})
        for name, entry in loose.items():
            if name in seen:
                continue
            items.append(
                CatalogItem(
                    name=name,
                    kind="skill",
                    description=entry.get("description", ""),
                )
            )
    return items


def _mcp_catalog_raw() -> dict:
    path = data_path() / "mcp" / "catalog.toml"
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text()).get("servers", {})


def _is_remote(config: dict) -> bool:
    """True for http endpoints whose request payload leaves the machine."""
    return "url" in config or config.get("type") == "http"


def catalog_mcp() -> list[CatalogItem]:
    """Optional MCP servers offered in the picker, one entry per server.

    Each description is prefixed with where the server runs and whether data
    leaves the machine: ``[local]`` (stdio subprocess, files stay on disk) or
    ``[remote]`` (http endpoint, queries go to a third party).
    """
    items: list[CatalogItem] = []
    for name, entry in _mcp_catalog_raw().items():
        config = entry.get("config", {})
        tag = "[remote]" if _is_remote(config) else "[local]"
        description = f"{tag} {entry.get('description', '')}".strip()
        items.append(
            CatalogItem(
                name=name,
                kind="mcp",
                description=description,
                checked=bool(entry.get("default", False)),
            )
        )
    return items


def catalog_hooks() -> list[CatalogItem]:
    """Claude Code hook bundles offered in the picker, one entry per bundle.

    Installing one merges its events into ``.claude/settings.json``; it is only
    useful once the Claude Code integration is configured.
    """
    items: list[CatalogItem] = []
    for name in hooks.bundle_names():
        bundle = hooks.read_bundle(name)
        items.append(
            CatalogItem(
                name=name,
                kind="hooks",
                description=str(bundle.get("description", "")),
            )
        )
    return items


def instructions_index() -> dict[str, list[str]]:
    """Package triggers per bundled instruction file, from ``instructions/index.toml``.

    A file with no entry is never installed automatically; it stays opt-in
    through the picker.
    """
    path = data_path() / "catalog" / "instructions" / "index.toml"
    if not path.exists():
        return {}
    raw = tomllib.loads(path.read_text()).get("instructions", {})
    return {
        name: list(entry.get("packages", []))
        for name, entry in raw.items()
        if isinstance(entry, dict)
    }


def instructions_for_packages(installed: set[str]) -> list[CatalogItem]:
    """Bundled instruction files triggered by an installed package.

    Matching is on the normalized distribution name, so ``ruamel-yaml`` and
    ``ruamel.yaml`` are the same package. A file already present in the repo is
    skipped: it may be the developer's own edit of it, which install would
    overwrite.
    """
    normalized = {normalize_package_name(p) for p in installed}
    triggers = instructions_index()
    if not triggers:
        return []
    present = {
        item.name: item
        for item in _bundled("instructions", "instructions", "*.instructions.md")
    }
    dest_dir = repo_root() / _DEST["instructions"]
    out: list[CatalogItem] = []
    for name, packages in sorted(triggers.items()):
        item = present.get(name)
        if item is None or (dest_dir / name).exists():
            continue
        if any(normalize_package_name(p) in normalized for p in packages):
            out.append(item)
    return out


def catalog(kinds: list[str]) -> dict[str, list[CatalogItem]]:
    """Collect catalog items for each requested kind, keyed by kind."""
    out: dict[str, list[CatalogItem]] = {}
    if "skills" in kinds:
        out["skills"] = catalog_skills()
    if "agents" in kinds:
        out["agents"] = _bundled("agent", "agents", "*.agent.md")
    if "prompts" in kinds:
        out["prompts"] = _bundled("prompt", "prompts", "**/*.prompt.md")
    if "instructions" in kinds:
        out["instructions"] = _bundled(
            "instructions", "instructions", "*.instructions.md"
        )
    if "hooks" in kinds:
        out["hooks"] = catalog_hooks()
    if "mcp" in kinds:
        out["mcp"] = catalog_mcp()
    return out


def find_agent(name: str) -> CatalogItem | None:
    """Resolve a catalog agent by short name ('yoda') or filename ('yoda.agent.md')."""
    filename = name if name.endswith(".agent.md") else f"{name}.agent.md"
    return next(
        (it for it in catalog(["agents"])["agents"] if it.name == filename), None
    )


# ── Install ───────────────────────────────────────────────────────────────────

_DEST = {
    "agent": GITHUB / "agents",
    "prompt": GITHUB / "prompts",
    "instructions": GITHUB / "instructions",
}


def install_item(item: CatalogItem) -> str:
    """Install one catalog item into the repo. Returns a status line."""
    if item.kind == "skill":
        if item.source is not None:  # bundled skill: copy the tree, no manifest entry
            dest = repo_root() / skills.SKILLS_DIR / item.name
            if dest.exists():
                shutil.rmtree(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(item.source, dest, ignore=shutil.ignore_patterns(".git"))
            return f"  skill   {item.name} (bundled)"
        if item.is_set:
            installed = skills.add_set(item.name)
            names = ", ".join(s.name for s, _ in installed)
            return f"  theme   {item.name} ({len(installed)} skills: {names})"
        source, commit = skills.add(item.name)
        return f"  skill   {source.name} @ {commit[:12]}"

    if item.kind == "hooks":
        return hooks.install(item.name)

    if item.kind == "mcp":
        entry = _mcp_catalog_raw().get(item.name)
        if entry is None:
            raise ValueError(f"unknown MCP server '{item.name}'")
        config = entry.get("config", {})
        line = add_mcp_server(item.name, config)
        # Opt-in remote servers send the model's tool-call arguments to a
        # third party. The curated defaults (Copilot-hosted github, local git)
        # stay within the trust boundary, so only warn for the rest.
        if _is_remote(config) and not entry.get("default", False):
            line += (
                f"\n  \u26a0 {item.name} is a remote server: the model composes "
                "the request, so your queries (and any data, schema, or code it "
                "embeds) are sent to a third party. Enable only for non-sensitive "
                "work (see docs/mcp.md)."
            )
        return line

    assert item.source is not None
    dest = repo_root() / _DEST[item.kind] / item.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(item.source, dest)
    return f"  {item.kind:7s} {item.name}"


def rebuild_item(item: CatalogItem, dry_run: bool = False, force: bool = False) -> str:
    """Restore one selected catalog item without silently replacing a collision."""
    if item.kind == "hooks":
        return hooks.install(item.name, dry_run=dry_run)
    if item.kind == "mcp":
        if dry_run:
            return f"  [dry-run] mcp {item.name}"
        return install_item(item)

    if item.kind == "skill":
        dest = repo_root() / skills.SKILLS_DIR / item.name
        if item.source is None:
            if dest.exists() and not force:
                rel = dest.relative_to(repo_root())
                return f"  skipped {rel} (overwrite requires --force)"
            if dry_run:
                return f"  [dry-run] skill {item.name}"
            return install_item(item)
        replacement = item.source
    else:
        assert item.source is not None
        dest = repo_root() / _DEST[item.kind] / item.name
        replacement = item.source

    if dest.exists() and not force:
        if (
            dest.is_file()
            and replacement.is_file()
            and dest.read_bytes() == replacement.read_bytes()
        ):
            return f"  unchanged {dest.relative_to(repo_root())}"
        if dry_run:
            rel = dest.relative_to(repo_root())
            return f"  [dry-run] replace {rel} (confirmation required)"
        if not generate.confirm_takeover(dest, replacement, item.kind):
            return f"  skipped {dest.relative_to(repo_root())} (overwrite requires --force)"
    if dry_run:
        return f"  [dry-run] {item.kind} {item.name}"
    return install_item(item)


def installed_items(kinds: list[str]) -> list[CatalogItem]:
    """Recognize catalog entries already present in an older Tara repository."""
    root = repo_root()
    skill_manifest = skills.read_manifest()
    installed: list[CatalogItem] = []
    for items in catalog(kinds).values():
        for item in items:
            if item.kind == "skill":
                present = (
                    item.name in skill_manifest
                    or (root / skills.SKILLS_DIR / item.name).is_dir()
                )
            elif item.kind == "hooks":
                present = hooks.is_installed(item.name)
            elif item.kind == "mcp":
                present = item.name in _installed_mcp_names()
            else:
                present = (root / _DEST[item.kind] / item.name).is_file()
            if present:
                installed.append(item)
    return installed


def _installed_mcp_names() -> set[str]:
    """Names in the current repo MCP configuration."""
    path = repo_root() / ".mcp.json"
    if not path.is_file():
        return set()
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return set()
    servers = data.get("mcpServers", {}) if isinstance(data, dict) else {}
    return set(servers) if isinstance(servers, dict) else set()
