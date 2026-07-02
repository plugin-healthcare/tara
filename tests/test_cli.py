"""CLI-level tests for the skill and agent command groups."""

from __future__ import annotations

from typer.testing import CliRunner

from wingman.cli import app

runner = CliRunner()


def test_skill_list_empty_hints_at_all(repo):
    result = runner.invoke(app, ["skill", "list"])
    assert result.exit_code == 0
    assert "No skills installed" in result.output
    assert "--all" in result.output


def test_skill_list_all_marks_installed(repo, skill_source):
    url, ref = skill_source
    add = runner.invoke(app, ["skill", "add", url, "--path", "demo", "--ref", ref])
    assert add.exit_code == 0
    result = runner.invoke(app, ["skill", "list", "--all"])
    assert result.exit_code == 0
    assert "demo" in result.output
    assert "✓" in result.output


def test_agent_add_then_list_marks_installed(repo):
    runner.invoke(app, ["agent", "add", "yoda"])
    result = runner.invoke(app, ["agent", "list"])
    assert result.exit_code == 0
    assert "✓ yoda" in result.output


def test_agent_add_unknown_fails(repo):
    result = runner.invoke(app, ["agent", "add", "nope"])
    assert result.exit_code == 1
    assert "no agent" in result.output


def test_new_doc_changelog_writes_root_singleton(repo):
    result = runner.invoke(app, ["new", "changelog"])
    assert result.exit_code == 0
    changelog = repo / "CHANGELOG.md"
    assert changelog.is_file()
    assert "Keep a Changelog" in changelog.read_text()


def test_new_doc_ci_writes_workflow(repo):
    result = runner.invoke(app, ["new", "ci"])
    assert result.exit_code == 0
    workflow = repo / ".github" / "workflows" / "ci.yml"
    assert workflow.is_file()
    body = workflow.read_text()
    assert "permissions:" in body
    assert "uv audit" in body
    # third-party actions must be SHA-pinned, not tag-pinned
    assert "actions/checkout@9c091bb" in body


def test_new_doc_adr_requires_title(repo):
    result = runner.invoke(app, ["new", "adr"])
    assert result.exit_code == 1
    assert "needs a title" in result.output


def test_new_doc_adr_with_title(repo):
    result = runner.invoke(app, ["new", "adr", "use postgres over mongodb"])
    assert result.exit_code == 0
    adr = repo / "docs" / "decisions" / "0001-use-postgres-over-mongodb.md"
    assert adr.is_file()
