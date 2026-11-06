"""Tests for the catalog and the `agent` command group helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from prompt_toolkit.application import create_app_session

from tara import catalog, frontmatter, generate


def test_catalog_lists_bundled_agents(repo):
    names = [it.name for it in catalog.catalog(["agents"])["agents"]]
    assert "yoda.agent.md" in names
    assert "marvin.agent.md" in names


def test_find_agent_by_short_name(repo):
    item = catalog.find_agent("yoda")
    assert item is not None
    assert item.name == "yoda.agent.md"
    assert item.kind == "agent"


def test_find_agent_by_filename(repo):
    item = catalog.find_agent("yoda.agent.md")
    assert item is not None
    assert item.name == "yoda.agent.md"


def test_find_agent_unknown_returns_none(repo):
    assert catalog.find_agent("does-not-exist") is None


def test_install_agent_copies_into_repo(repo):
    item = catalog.find_agent("yoda")
    assert item is not None
    catalog.install_item(item)
    installed = repo / ".github" / "agents" / "yoda.agent.md"
    assert installed.is_file()
    assert "Yoda" in installed.read_text()


def test_install_instruction_skips_a_symlinked_destination_directory(repo):
    outside = repo / "outside"
    outside.mkdir()
    instructions = repo / ".github" / "instructions"
    instructions.parent.mkdir()
    instructions.symlink_to(outside, target_is_directory=True)
    item = next(
        item
        for item in catalog.catalog(["instructions"])["instructions"]
        if item.name == "markdown.instructions.md"
    )

    with pytest.raises(catalog.CatalogInstallError, match="symlink"):
        catalog.install_item(item)
    assert not (outside / item.name).exists()


def test_catalog_lists_mcp_servers(repo):
    items = catalog.catalog(["mcp"])["mcp"]
    names = [it.name for it in items]
    assert "github" in names
    assert "likec4" in names
    # github is a sensible default and should be pre-checked
    assert next(it for it in items if it.name == "github").checked is True
    assert next(it for it in items if it.name == "likec4").checked is False


def test_install_mcp_merges_into_vscode_config(repo):
    import json

    from tara import core

    core.write_mcp("python", dry_run=False)  # seed an empty servers map
    item = next(it for it in catalog.catalog(["mcp"])["mcp"] if it.name == "likec4")
    catalog.install_item(item)

    data = json.loads((repo / core.MCP_CONFIG).read_text())
    assert "likec4" in data["mcpServers"]
    assert data["mcpServers"]["likec4"]["command"] == "npx"
    assert data["mcpServers"]["likec4"]["args"] == ["-y", "@likec4/mcp@1.58.0"]
    # No VS Code-only ${workspaceFolder}: LikeC4 defaults to the launch cwd.
    assert "env" not in data["mcpServers"]["likec4"]


def test_install_third_party_mcp_warns(repo):
    from tara import core

    core.write_mcp("python", dry_run=False)
    item = next(it for it in catalog.catalog(["mcp"])["mcp"] if it.name == "polars")
    status = catalog.install_item(item)
    # Opt-in remote server: the user must be warned the payload goes off-machine.
    assert "\u26a0" in status
    assert "third party" in status


def test_install_default_mcp_does_not_warn(repo):
    from tara import core

    core.write_mcp("python", dry_run=False)
    # github is remote but Copilot-hosted and a curated default: no warning.
    item = next(it for it in catalog.catalog(["mcp"])["mcp"] if it.name == "github")
    assert "\u26a0" not in catalog.install_item(item)
    # git is a local default: no warning either.
    item = next(it for it in catalog.catalog(["mcp"])["mcp"] if it.name == "git")
    assert "\u26a0" not in catalog.install_item(item)


def _make_bundled_skill(data_dir, name: str) -> None:
    folder = data_dir / "catalog" / "skills" / name
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(
        f"---\nname: {name}\n"
        f'description: "The {name} skill. Use when testing bundled skills."\n'
        f"---\n\n# {name}\n\nEnough body content to be a usable skill here.\n"
    )
    (folder / "references").mkdir()
    (folder / "references" / "note.md").write_text("reference material\n")


def test_catalog_skills_includes_bundled(repo, tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    _make_bundled_skill(data_dir, "writing-adrs")
    monkeypatch.setattr(catalog, "data_path", lambda: data_dir)

    items = catalog.catalog_skills()
    adrs = next(it for it in items if it.name == "writing-adrs")
    assert adrs.kind == "skill"
    assert adrs.source is not None
    assert "adr" in adrs.description.lower()


def test_install_bundled_skill_copies_tree(repo, tmp_path, monkeypatch):
    from tara import skills

    data_dir = tmp_path / "data"
    _make_bundled_skill(data_dir, "writing-adrs")
    monkeypatch.setattr(catalog, "data_path", lambda: data_dir)

    item = next(it for it in catalog.catalog_skills() if it.name == "writing-adrs")
    line = catalog.install_item(item)
    assert "bundled" in line

    dest = repo / skills.SKILLS_DIR / "writing-adrs"
    assert (dest / "SKILL.md").is_file()
    assert (dest / "references" / "note.md").is_file()
    # bundled skills are not tracked in the manifest
    assert "writing-adrs" not in skills.read_manifest()


def test_regression_install_bundled_skill_preserves_local_changes(
    repo, tmp_path, monkeypatch
):
    from tara import skills

    data_dir = tmp_path / "data"
    _make_bundled_skill(data_dir, "writing-adrs")
    monkeypatch.setattr(catalog, "data_path", lambda: data_dir)

    item = next(it for it in catalog.catalog_skills() if it.name == "writing-adrs")
    catalog.install_item(item)
    stale = repo / skills.SKILLS_DIR / "writing-adrs" / "stale.md"
    stale.write_text("stale\n")

    with pytest.raises(RuntimeError, match="skipped"):
        catalog.install_item(item)
    assert stale.read_text() == "stale\n"


@pytest.mark.parametrize("kind", ["agents", "prompts", "instructions"])
def test_regression_direct_catalog_install_preserves_authored_files(
    repo, monkeypatch, kind
):
    item = catalog.catalog([kind])[kind][0]
    directory = "agents" if item.kind == "agent" else kind
    destination = repo / ".github" / directory / item.name
    destination.parent.mkdir(parents=True)
    destination.write_text("authored content\n")
    monkeypatch.setattr("tara.generate._interactive", lambda: False)

    with pytest.raises(RuntimeError, match="skipped"):
        catalog.install_item(item)

    assert destination.read_text() == "authored content\n"


@pytest.mark.parametrize("approved", [False, True])
def test_regression_catalog_install_obeys_takeover_confirmation(
    repo, monkeypatch, approved
):
    item = catalog.find_agent("yoda")
    assert item is not None
    destination = repo / ".github" / "agents" / item.name
    destination.parent.mkdir(parents=True)
    destination.write_text("authored content\n")
    monkeypatch.setattr("tara.generate.confirm_takeover", lambda *args: approved)

    if approved:
        catalog.install_item(item)
        assert item.source is not None
        assert destination.read_bytes() == item.source.read_bytes()
    else:
        with pytest.raises(RuntimeError, match="skipped"):
            catalog.install_item(item)
        assert destination.read_text() == "authored content\n"


def test_regression_catalog_takeover_previews_the_replacement_file(
    repo, monkeypatch, capsys
):
    item = catalog.find_agent("yoda")
    assert item is not None
    destination = repo / ".github" / "agents" / item.name
    destination.parent.mkdir(parents=True)
    destination.write_text("authored content\n")
    monkeypatch.setattr(generate, "_interactive", lambda: True)
    monkeypatch.setattr(
        "questionary.confirm",
        lambda *args, **kwargs: SimpleNamespace(unsafe_ask=lambda: False),
    )

    with create_app_session(), pytest.raises(catalog.CatalogInstallError):
        catalog.install_item(item)

    output = capsys.readouterr().out
    assert "-authored content" in output
    assert "+description:" in output


def test_instructions_index_lists_package_triggers():
    assert catalog.instructions_index()["dagster.instructions.md"] == ["dagster"]


def test_instructions_for_packages_matches_installed(repo):
    items = catalog.instructions_for_packages({"Dagster"})

    assert [it.name for it in items] == ["dagster.instructions.md"]
    assert items[0].kind == "instructions"


def test_instructions_for_packages_ignores_unrelated(repo):
    assert catalog.instructions_for_packages({"requests"}) == []


def test_instructions_for_packages_skips_a_file_already_in_the_repo(repo):
    dest = repo / ".github" / "instructions"
    dest.mkdir(parents=True)
    (dest / "dagster.instructions.md").write_text("my own version\n")

    assert catalog.instructions_for_packages({"dagster"}) == []


def test_catalog_offers_the_runbook_prompt(repo):
    # GIVEN the bundled catalog
    # WHEN the prompts are listed
    names = [it.name for it in catalog.catalog(["prompts"])["prompts"]]
    # THEN the runbook prompt is offered
    assert "runbook.prompt.md" in names


def test_runbook_instructions_apply_to_runbooks_only(repo):
    # GIVEN the bundled runbook instructions
    items = catalog.catalog(["instructions"])["instructions"]
    item = next(it for it in items if it.name == "runbooks.instructions.md")
    assert item.source is not None
    # WHEN their frontmatter is read
    fm, _ = frontmatter.parse(item.source.read_text())
    # THEN they are scoped to the runbooks folder
    assert fm["applyTo"] == ".agents/runbooks/**/*.md"
