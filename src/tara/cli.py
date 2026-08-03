"""tara CLI — a GitHub Copilot + opencode guardrail toolkit.

Installed per-repo. Every command operates on the current working directory.
Copilot's .github/ setup is the single source of truth; opencode files are a
generated port of it.
Commands:
  init      write instructions + MCP + memory; --tool opencode|all also ports
  add       pick and install more catalog artifacts (skills/agents/prompts/instructions)
  skill     manage skills directly (add/list/update/remove)
  agent     manage bundled agents directly (list/add)
  opencode  port the Copilot setup into opencode files (opencode.json + .opencode/)
  check     run the project's lint/format/test gate
  audit     lint guardrail artifacts (add --deep for an LLM content review)
  new       scaffold a prompt, agent, or document from a template
"""

from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path
from typing import Annotated

import typer

from tara import agent_docs as agent_docs_mod
from tara import audit as audit_mod
from tara import catalog as catalog_mod
from tara import check as check_mod
from tara import config as config_mod
from tara import docs as docs_mod
from tara import opencode as opencode_mod
from tara import review as review_mod
from tara import skills as skills_mod
from tara import standards as standards_mod
from tara import sync as sync_mod
from tara.core import (
    ALL_TOOLS,
    OPENCODE,
    data_path,
    repo_root,
    validate_tool,
    write_instructions,
    write_mcp,
)

app = typer.Typer(
    name="tara",
    help="GitHub Copilot guardrail toolkit. Install instructions, MCP, and skills.",
    no_args_is_help=True,
)

StackArg = Annotated[str, typer.Argument(help="Stack (default: python)")]
DryRun = Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")]
AllOpt = Annotated[
    bool, typer.Option("--all", help="Select every catalog item (non-interactive).")
]
ToolOpt = Annotated[
    str,
    typer.Option(
        "--tool",
        help="Also port to opencode: copilot (default, no port), opencode, or all.",
    ),
]

MENU_KINDS = ["skills", "agents", "prompts", "instructions", "mcp"]


@app.command()
def sync(
    all_: Annotated[
        bool,
        typer.Option(
            "--all", help="Scan all installed packages, not just direct deps."
        ),
    ] = False,
    docs: Annotated[
        bool,
        typer.Option(
            "--docs/--no-docs",
            help=(
                "For packages with no skill, probe PyPI for an llms.txt "
                "and add found ones to the mcpdoc MCP server in .mcp.json."
            ),
        ),
    ] = True,
) -> None:
    """Sync skills (and optionally docs) from installed packages.

    Phase 1 — embedded skills: copies SKILL.md files bundled inside installed
    packages (library-skills standard) into .github/skills/.

    Phase 2 — indexed skills: for installed packages with a known official skill
    repo in Tara's index (e.g. duckdb, streamlit), fetches and installs those
    skills automatically.

    Phase 3 — docs fallback (--docs, on by default): for packages still without
    any skill, queries PyPI for a docs URL and probes for llms.txt. Found sources
    are wired into the mcpdoc MCP server in .mcp.json.

    By default only direct dependencies from pyproject.toml are considered.
    """
    _run_sync(all_=all_, docs=docs)


def _run_sync(all_: bool, docs: bool) -> None:
    direct = sync_mod.direct_deps(repo_root()) or set()

    # Phase 1: embedded skills from installed packages.
    result = sync_mod.sync(all_packages=all_)
    for w in result.warnings:
        typer.echo(f"warning: {w}", err=True)
    for name in result.added:
        typer.echo(f"  skill added    {name}")
    for name in result.updated:
        typer.echo(f"  skill updated  {name}")
    for name in result.removed:
        typer.echo(f"  skill removed  {name}")
    for name in result.skipped:
        typer.echo(f"  skill skipped  {name} (core-managed, not overwritten)")
    for name in result.unchanged:
        typer.echo(f"  skill ok       {name}")

    covered = set(result.added + result.updated + result.unchanged)

    # Phase 2: indexed skills for installed packages (separate skill repos).
    packages_without_skill = direct - {
        sync_mod.normalize_package_name(s) for s in covered
    }
    to_install = skills_mod.indexed_for_packages(packages_without_skill)
    for target in to_install:
        try:
            if skills_mod.resolve_set(target) is not None:
                installed = skills_mod.add_set(target)
                for source, commit in installed:
                    typer.echo(
                        f"  skill added    {source.name} (indexed via {target})"
                        f" @ {commit[:12]}"
                    )
                    covered.add(source.name)
            else:
                source, commit = skills_mod.add(target)
                typer.echo(f"  skill added    {source.name} (indexed) @ {commit[:12]}")
                covered.add(source.name)
        except skills_mod.SkillError as exc:
            typer.echo(f"  warning: could not install indexed skill '{target}': {exc}")

    # Phase 3: llms.txt docs fallback.
    if docs:
        still_uncovered = [
            pkg
            for pkg in direct
            if sync_mod.normalize_package_name(pkg)
            not in {sync_mod.normalize_package_name(s) for s in covered}
        ]
        if still_uncovered:
            typer.echo("  checking for llms.txt fallback docs…")
            added_docs = docs_mod.sync_docs(still_uncovered)
            if added_docs:
                for label, url in added_docs.items():
                    typer.echo(f"  docs added     {label}  →  {url}")
            else:
                typer.echo("  no llms.txt found for remaining packages")

    if not any(
        [
            result.added,
            result.updated,
            result.removed,
            result.unchanged,
            result.skipped,
            to_install,
        ]
    ):
        typer.echo("No library skills found.")


# ── init ──────────────────────────────────────────────────────────────────────


@app.command()
def init(
    stack: StackArg = "python",
    tool: ToolOpt = "copilot",
    all_: AllOpt = False,
    dry_run: DryRun = False,
) -> None:
    """Set up this repo: Copilot core, MCP, agent memory, tooling, then artifacts.

    Copilot's .github/ setup is always the source. ``--tool opencode`` or
    ``--tool all`` additionally port that setup into opencode files
    (opencode.json + .opencode/); ``--tool copilot`` (default) skips the port.
    """
    try:
        tool = validate_tool(tool)
    except ValueError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from exc

    port = tool in (OPENCODE, ALL_TOOLS)

    typer.echo(f"Setting up Copilot for stack: {stack}")
    typer.echo("\nCore setup:")
    typer.echo(write_instructions(stack, dry_run))
    typer.echo(write_mcp(stack, dry_run))
    cfg = config_mod.TaraConfig.load()
    try:
        typer.echo(
            agent_docs_mod.write_agent_docs(dry_run, gitignore=cfg.agents.gitignore)
        )
    except ValueError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(config_mod.write_config(tool, stack or "python", dry_run))

    # Mandatory tooling for the check gate + pre-commit hook (python stack).
    if (stack or "python") == "python":
        _report_standards("python", write=True, dry_run=dry_run)
        _offer_dev_tools("python", dry_run=dry_run)

    if dry_run:
        typer.echo("\n[dry-run] skipping optional artifact selection")
        if port:
            _echo_port(dry_run=True)
        return

    # Optional extras: pick catalog artifacts, then scan installed packages.
    _select_and_install(MENU_KINDS, all_)
    if sys.stdin.isatty() and typer.confirm(
        "\nAlso scan installed packages for skills to sync?", default=False
    ):
        _run_sync(all_=False, docs=True)

    if port:
        _echo_port(dry_run=False)


def _echo_port(dry_run: bool) -> None:
    """Port the Copilot setup into opencode files, echoing each section."""
    typer.echo("\nPorting Copilot setup to opencode:")
    for title, lines in opencode_mod.port_all(dry_run):
        typer.echo(f"{title}:")
        for line in lines or ["  (nothing to port)"]:
            typer.echo(line)


@app.command()
def add(
    all_: AllOpt = False,
) -> None:
    """Pick and install catalog artifacts (skills, agents, prompts, instructions)."""
    _select_and_install(MENU_KINDS, all_)


@app.command(name="list")
def list_() -> None:
    """Show the Copilot triggers active in this repo: prompts, agents, skills."""
    root = repo_root()
    gh = root / ".github"

    ci = gh / "copilot-instructions.md"
    typer.echo("Always-on instructions:")
    typer.echo(f"  {'✓' if ci.is_file() else '—'} .github/copilot-instructions.md")

    scoped = (
        sorted((gh / "instructions").glob("*.instructions.md"))
        if (gh / "instructions").is_dir()
        else []
    )
    typer.echo("\nScoped instructions (applyTo globs):")
    if scoped:
        for p in scoped:
            apply_to = _frontmatter_value(p, "applyTo")
            typer.echo(f"  {p.name}  →  {apply_to or '(no applyTo)'}")
    else:
        typer.echo("  (none)")

    prompts = (
        sorted((gh / "prompts").glob("**/*.prompt.md"))
        if (gh / "prompts").is_dir()
        else []
    )
    typer.echo("\nSlash-command prompts (type / in chat):")
    if prompts:
        for p in prompts:
            keyword = p.name.removesuffix(".prompt.md")
            typer.echo(f"  /{keyword}")
    else:
        typer.echo("  (none)")

    agents = (
        sorted((gh / "agents").glob("*.agent.md")) if (gh / "agents").is_dir() else []
    )
    typer.echo("\nCustom agents:")
    if agents:
        for p in agents:
            typer.echo(f"  {p.name.removesuffix('.agent.md')}")
    else:
        typer.echo("  (none)")

    skills = (
        sorted((gh / "skills").glob("*/SKILL.md")) if (gh / "skills").is_dir() else []
    )
    typer.echo("\nSkills (model-invoked by description):")
    if skills:
        for p in skills:
            typer.echo(f"  {p.parent.name}")
    else:
        typer.echo("  (none)")


def _frontmatter_value(path: Path, key: str) -> str | None:
    return audit_mod.parse_frontmatter(path.read_text())[0].get(key)


def _select_and_install(kinds: list[str], select_all: bool) -> None:
    cat = catalog_mod.catalog(kinds)
    if not any(cat.values()):
        typer.echo(
            "Catalog is empty. Add skills to the index or bundle agents/prompts."
        )
        return

    if select_all:
        chosen = [item for items in cat.values() for item in items]
    elif not sys.stdin.isatty():
        typer.echo(
            "Not an interactive terminal. Re-run with --all or use `tara skill add`."
        )
        return
    else:
        chosen = _checkbox_select(cat)

    if not chosen:
        typer.echo("Nothing selected.")
        return

    typer.echo("\nInstalling:")
    for item in chosen:
        try:
            typer.echo(catalog_mod.install_item(item))
        except Exception as exc:  # noqa: BLE001 — surface install errors per item
            typer.echo(f"  failed {item.name}: {exc}", err=True)


_SELECT_ALL = object()  # sentinel for the "select all" picker entry


def _checkbox_select(cat: dict[str, list]) -> list:
    import questionary

    chosen: list = []
    for kind, items in cat.items():
        if not items:
            continue
        choices = [
            questionary.Choice(title="── select all ──", value=_SELECT_ALL),
            *(
                questionary.Choice(
                    title=f"{it.name}  —  {it.description[:70]}"
                    if it.description
                    else it.name,
                    value=it,
                    checked=it.checked,
                )
                for it in items
            ),
        ]
        picked = questionary.checkbox(
            f"Select {kind}:",
            choices=choices,
            instruction="(↑↓ move · space toggle · 'a' all · enter confirm)",
        ).ask()
        if not picked:
            continue
        if _SELECT_ALL in picked:
            chosen += items
        else:
            chosen += picked
    return chosen


# ── skill ─────────────────────────────────────────────────────────────────────

skill_app = typer.Typer(
    help="Manage Copilot skills (.github/skills/).", no_args_is_help=True
)
app.add_typer(skill_app, name="skill")


@skill_app.command("add")
def skill_add(
    target: Annotated[str, typer.Argument(help="Curated name, set name, or a git URL")],
    path: Annotated[
        str | None,
        typer.Option("--path", help="Skill subdir inside the repo (for git URLs)"),
    ] = None,
    ref: Annotated[
        str | None, typer.Option("--ref", help="Branch, tag, or commit SHA")
    ] = None,
    name: Annotated[str | None, typer.Option("--name", help="Local skill name")] = None,
) -> None:
    """Fetch a skill or set from the index or a git URL into .github/skills/."""
    # A bare name may refer to a set (a bundle of skills); install all of them.
    if path is None and skills_mod.resolve_set(target) is not None:
        try:
            installed = skills_mod.add_set(target)
        except skills_mod.SkillError as exc:
            typer.echo(f"error: {exc}", err=True)
            raise typer.Exit(1) from exc
        typer.echo(f"Installed set '{target}' ({len(installed)} skills):")
        for source, commit in installed:
            typer.echo(f"  {source.name} @ {commit[:12]}")
        return

    try:
        source, commit = skills_mod.add(target, path=path, ref=ref, name=name)
    except skills_mod.SkillError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Installed skill '{source.name}' @ {commit[:12]} from {source.repo}")


@skill_app.command("list")
def skill_list(
    all_: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Show every indexed skill, marking installed (✓) vs available (—).",
        ),
    ] = False,
) -> None:
    """List installed skills, or with --all, the themes the index offers."""
    if all_:
        installed = skills_mod.list_skills()
        themes = skills_mod.read_sets_index()
        if not installed and not themes:
            typer.echo(
                "No skills available. The index is empty — add a [sets.<theme>] "
                "to data/skills/index.toml, or `tara skill add <git-url> --path …`."
            )
            return
        if installed:
            typer.echo("Installed skills:")
            for r in installed:
                mark = "✓" if r["installed"] else "—"
                typer.echo(f"  {mark} {r['name']:22s} {r['ref']:16s} {r['commit']}")
            typer.echo("")
        typer.echo("Themes (install all skills with `tara skill add <theme>`):")
        for s in sorted(themes.values(), key=lambda s: s.name):
            typer.echo(f"  {s.name:22s} {s.description[:60]}")
        return

    rows = skills_mod.list_skills()
    if not rows:
        typer.echo(
            "No skills installed. Use `tara skill add`, or "
            "`tara skill list --all` to see what's available."
        )
        return
    for r in rows:
        mark = "" if r["installed"] else "  (missing on disk)"
        typer.echo(f"  ✓ {r['name']:22s} {r['ref']:16s} {r['commit']}{mark}")


@skill_app.command("update")
def skill_update(
    name: Annotated[
        str | None, typer.Argument(help="Skill to update (default: all)")
    ] = None,
) -> None:
    """Re-fetch one or all skills to their latest commit."""
    try:
        results = skills_mod.update(name)
    except skills_mod.SkillError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from exc
    for n, old, new in results:
        change = "unchanged" if old == new else f"{old} → {new}"
        typer.echo(f"{n}: {change}")


@skill_app.command("remove")
def skill_remove(
    name: Annotated[str, typer.Argument(help="Skill to remove")],
) -> None:
    """Remove a skill from disk and the manifest."""
    try:
        skills_mod.remove(name)
    except skills_mod.SkillError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Removed skill '{name}'")


# ── agent ─────────────────────────────────────────────────────────────────────

agent_app = typer.Typer(
    help="Manage Copilot agents (.github/agents/).", no_args_is_help=True
)
app.add_typer(agent_app, name="agent")


@agent_app.command("list")
def agent_list() -> None:
    """List bundled agents and whether each is installed in this repo."""
    items = catalog_mod.catalog(["agents"])["agents"]
    if not items:
        typer.echo("No agents in the catalog.")
        return
    dest = repo_root() / ".github" / "agents"
    for it in items:
        short = it.name.removesuffix(".agent.md")
        mark = "✓" if (dest / it.name).is_file() else "—"
        typer.echo(f"  {mark} {short:18s} {it.description[:70]}")


@agent_app.command("add")
def agent_add(
    name: Annotated[str, typer.Argument(help="Agent name, e.g. 'yoda'")],
) -> None:
    """Install a bundled agent into .github/agents/."""
    item = catalog_mod.find_agent(name)
    if item is None:
        available = ", ".join(
            it.name.removesuffix(".agent.md")
            for it in catalog_mod.catalog(["agents"])["agents"]
        )
        typer.echo(
            f"error: no agent '{name}'. Available: {available or '(none)'}", err=True
        )
        raise typer.Exit(1)
    typer.echo(catalog_mod.install_item(item).strip())


# ── opencode ──────────────────────────────────────────────────────────────────

opencode_app = typer.Typer(
    help="Port the Copilot setup into opencode files (opencode.json + .opencode/).",
    no_args_is_help=True,
)
app.add_typer(opencode_app, name="opencode")


@opencode_app.command("sync")
def opencode_sync(
    dry_run: DryRun = False,
) -> None:
    """Port the Copilot .github/ setup into opencode files.

    Regenerates opencode.json (referencing .github/copilot-instructions.md +
    MCP servers from .mcp.json) and mirrors .github/ agents, prompts, and skills
    into .opencode/. Safe to re-run; the Copilot side stays the source of truth.
    """
    _echo_port(dry_run=dry_run)


# ── check ─────────────────────────────────────────────────────────────────────


@app.command()
def check(
    stack: Annotated[str | None, typer.Argument(help="Stack (default: python)")] = None,
    no_fail_fast: Annotated[
        bool, typer.Option("--no-fail-fast", help="Run all checks even if one fails.")
    ] = False,
) -> None:
    """Run the project's lint/format/test gate."""
    try:
        results = check_mod.run_checks(stack, fail_fast=not no_fail_fast)
    except FileNotFoundError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(2) from exc

    typer.echo("\nSummary:")
    for r in results:
        typer.echo(f"  {'PASS' if r.passed else 'FAIL'}  {r.name}: {r.cmd}")
    if any(not r.passed for r in results):
        raise typer.Exit(1)


# ── standards ─────────────────────────────────────────────────────────────────

_STATUS_LABEL = {
    "ok": "ok",
    "missing": "missing",
    "differs": "differs (not overwritten)",
    "no-pyproject": "no pyproject.toml yet",
}


def _report_standards(stack: str, *, write: bool, dry_run: bool) -> None:
    """Report how the repo's tooling compares to the standard; may write pre-commit."""
    typer.echo(f"\nTooling standard ({stack}):")

    pc = standards_mod.compare_precommit(stack)
    if pc == "missing" and write:
        standards_mod.write_precommit(stack, dry_run)
        prefix = "[dry-run] " if dry_run else ""
        typer.echo(f"  pre-commit     {prefix}wrote {standards_mod.PRECOMMIT}")
        typer.echo("                 run `uv run pre-commit install` to enable it")
    elif pc == "missing":
        typer.echo("  pre-commit     missing (run `tara standards --write`)")
    elif pc == "differs":
        typer.echo("  pre-commit     differs from standard (not overwritten)")
    else:
        typer.echo("  pre-commit     ok")

    categories = standards_mod.compare_pyproject(stack)
    for cs in categories:
        typer.echo(f"  [tool.{cs.name}]".ljust(17) + _STATUS_LABEL[cs.status])

    unpinned = standards_mod.unpinned_dependencies()
    if unpinned:
        typer.echo(
            f"  dependencies   {len(unpinned)} without a version: {', '.join(unpinned)}"
        )
    else:
        typer.echo("  dependencies   ok (all pinned)")

    missing_tools = standards_mod.missing_dev_tools()
    if missing_tools:
        typer.echo(f"  dev tools      missing: {', '.join(missing_tools)}")
    else:
        typer.echo("  dev tools      ok (ruff, ty, pytest, pre-commit declared)")

    if any(cs.status != "ok" for cs in categories):
        typer.echo(
            "  → run `tara standards --show` for the canonical tool block to paste"
        )


def _offer_dev_tools(stack: str, *, dry_run: bool) -> None:
    """Add the standard's required dev tools, then install the hook if wanted."""
    missing = standards_mod.missing_dev_tools()
    if not missing:
        return
    joined = " ".join(missing)
    if dry_run:
        typer.echo(f"  [dry-run] uv add --dev {joined}")
        return
    if not (
        sys.stdin.isatty()
        and typer.confirm(
            f"\nInstall required dev tools for the check gate ({', '.join(missing)})?",
            default=True,
        )
    ):
        typer.echo(f"  skipped — add later with `uv add --dev {joined}`")
        return
    ok, cmd = standards_mod.add_dev_tools(missing, dry_run)
    typer.echo(f"  {'ran' if ok else 'failed'}: {cmd}")
    if not ok:
        return
    precommit_exists = (repo_root() / standards_mod.PRECOMMIT).exists()
    if (
        "pre-commit" in missing
        and precommit_exists
        and typer.confirm(
            "Install the git pre-commit hook now (uv run pre-commit install)?",
            default=True,
        )
    ):
        hook_ok, hook_cmd = standards_mod.install_precommit_hook(dry_run)
        typer.echo(f"  {'ran' if hook_ok else 'failed'}: {hook_cmd}")


@app.command()
def standards(
    stack: StackArg = "python",
    show: Annotated[
        bool,
        typer.Option(
            "--show", help="Print the canonical pyproject tool block and exit."
        ),
    ] = False,
    write: Annotated[
        bool,
        typer.Option(
            "--write",
            help="Write .pre-commit-config.yaml if absent (never overwrites).",
        ),
    ] = False,
    dry_run: DryRun = False,
) -> None:
    """Report how this repo's tooling differs from Tara's opinionated standard."""
    if show:
        typer.echo(standards_mod.pyproject_tools_text(stack), nl=False)
        return
    _report_standards(stack, write=write, dry_run=dry_run)


# ── audit ─────────────────────────────────────────────────────────────────────


@app.command()
def audit(
    paths: Annotated[
        list[Path] | None,
        typer.Argument(help="Files to audit (default: scan .github/)"),
    ] = None,
    deep: Annotated[
        bool,
        typer.Option("--deep", help="Run an LLM content review via the Copilot CLI."),
    ] = False,
    strict: Annotated[
        bool, typer.Option("--strict", help="Exit non-zero on warnings too.")
    ] = False,
) -> None:
    """Lint Copilot guardrail artifacts (skills, agents, instructions) + MCP config."""
    if paths:
        findings = [f for p in paths for f in audit_mod.audit_path(p)]
        targets = paths
    else:
        findings = audit_mod.audit_all()
        targets = [p for p, _ in audit_mod.discover()] + audit_mod.mcp_config_paths()

    if not targets:
        typer.echo(
            "No artifacts found under .github/ (skills, agents, instructions) "
            "or MCP config (.mcp.json)."
        )
        return

    if findings:
        typer.echo("Findings:")
        for line in audit_mod.format_findings(findings):
            typer.echo(line)
    else:
        typer.echo(f"No issues across {len(targets)} artifact(s).")

    if deep:
        typer.echo("\nDeep review (Copilot CLI):")
        try:
            review_mod.deep_review(targets)
        except review_mod.ReviewUnavailable as exc:
            typer.echo(f"error: {exc}", err=True)
            raise typer.Exit(2) from exc

    has_error = any(f.level == audit_mod.ERROR for f in findings)
    has_warning = any(f.level == audit_mod.WARNING for f in findings)
    if has_error or (strict and has_warning):
        raise typer.Exit(1)


# ── new (scaffolding) ─────────────────────────────────────────────────────────

_TEMPLATE_MAP = {
    "story": ("agile/story.md", "docs/stories", "{slug}.md"),
    "epic": ("agile/epic.md", "docs/epics", "{slug}.md"),
    "bug": ("agile/bug.md", "docs/bugs", "{slug}.md"),
    "spike": ("agile/spike.md", "docs/spikes", "{slug}.md"),
    "adr": ("decisions/adr.md", "docs/decisions", "{number:04d}-{slug}.md"),
    "post-mortem": ("engineering/post-mortem.md", "docs/post-mortems", "{slug}.md"),
    "runbook": ("engineering/runbook.md", "docs/runbooks", "{slug}.md"),
    "changelog": ("changelog.md", ".", "CHANGELOG.md"),
    "ci": ("ci-github.yml", ".github/workflows", "ci.yml"),
}

# kind -> one-line description, shown by `tara new` with no arguments.
_KIND_HELP = {
    "prompt": ".github/prompts/<name>.prompt.md slash-command prompt",
    "agent": ".github/agents/<name>.agent.md custom agent",
    "story": "agile story",
    "epic": "agile epic",
    "bug": "bug report",
    "spike": "spike",
    "adr": "architecture decision record",
    "post-mortem": "post-mortem",
    "runbook": "operational runbook",
    "changelog": "Keep a Changelog CHANGELOG.md",
    "ci": "secure GitHub Actions CI workflow",
}
_NEW_KINDS = ["prompt", "agent", *_TEMPLATE_MAP]


@app.command()
def new(
    kind: Annotated[
        str | None,
        typer.Argument(help=f"What to scaffold: {', '.join(_NEW_KINDS)}"),
    ] = None,
    name: Annotated[
        str | None,
        typer.Argument(help="Name (prompt/agent) or title (docs that need a slug)"),
    ] = None,
) -> None:
    """Scaffold a prompt, agent, or document from a template.

    Run `tara new` with no arguments to list every kind. Examples:
    `tara new prompt review`, `tara new agent data-analyst`,
    `tara new adr "use postgres over mongodb"`, `tara new ci`.
    """
    if kind is None:
        typer.echo("Usage: tara new <kind> [name]\n\nKinds:")
        for k in _NEW_KINDS:
            typer.echo(f"  {k:<12} {_KIND_HELP[k]}")
        return
    if kind == "prompt":
        _new_prompt(name)
    elif kind == "agent":
        _new_agent(name)
    elif kind in _TEMPLATE_MAP:
        _new_from_template(kind, name)
    else:
        typer.echo(
            f"Unknown kind '{kind}'. Choose from: {', '.join(_NEW_KINDS)}", err=True
        )
        raise typer.Exit(1)


def _new_prompt(name: str | None) -> None:
    if not name:
        typer.echo("'prompt' needs a name argument.", err=True)
        raise typer.Exit(1)
    path = repo_root() / ".github" / "prompts" / f"{name}.prompt.md"
    _scaffold(
        path, '---\ndescription: "TODO: when to use this"\n---\n\nTODO: prompt body\n'
    )


def _new_agent(name: str | None) -> None:
    if not name:
        typer.echo("'agent' needs a name argument.", err=True)
        raise typer.Exit(1)
    path = repo_root() / ".github" / "agents" / f"{name}.agent.md"
    _scaffold(
        path,
        '---\ndescription: "TODO: Use when … (include trigger phrases)"\n'
        "tools: [read, search]\nuser-invocable: true\n---\n\n"
        "You are a specialist at TODO.\n\n## Constraints\n- Only do TODO.\n\n"
        "## Output\nTODO\n",
    )


def _new_from_template(kind: str, title: str | None) -> None:
    template_rel, dest_dir, filename_pattern = _TEMPLATE_MAP[kind]
    needs_title = "{slug}" in filename_pattern or "{title}" in template_rel
    if needs_title and not title:
        typer.echo(f"'{kind}' needs a title argument.", err=True)
        raise typer.Exit(1)

    template_path = data_path() / "templates" / template_rel
    slug = (title or "").lower().replace(" ", "-").replace("/", "-")
    today = _dt.date.today().isoformat()

    dest = repo_root() / dest_dir
    number = 0
    if "{number" in filename_pattern:
        dest.mkdir(parents=True, exist_ok=True)
        number = len(sorted(dest.glob("[0-9]*.md"))) + 1
        filename = filename_pattern.format(number=number, slug=slug)
    else:
        filename = filename_pattern.format(slug=slug)

    content = (
        template_path.read_text()
        .replace("{title}", title or "")
        .replace("{date}", today)
        .replace("{number}", f"{number:04d}" if number else "")
    )
    _scaffold(dest / filename, content)


def _scaffold(path: Path, content: str) -> None:
    if path.exists():
        typer.echo(f"Already exists: {path}", err=True)
        raise typer.Exit(1)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    typer.echo(f"Created {path.relative_to(repo_root())}")
