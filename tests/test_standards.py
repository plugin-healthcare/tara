"""Tests for the opinionated tooling standard (standards.py)."""

from __future__ import annotations

from wingman import standards


def test_no_pyproject_reports_no_pyproject(repo):
    statuses = {c.name: c.status for c in standards.compare_pyproject("python")}
    assert set(statuses) == set(standards.PYPROJECT_CATEGORIES)
    assert all(s == "no-pyproject" for s in statuses.values())


def test_matching_pyproject_is_ok(repo):
    (repo / "pyproject.toml").write_text(standards.pyproject_tools_text("python"))
    statuses = {c.name: c.status for c in standards.compare_pyproject("python")}
    assert all(s == "ok" for s in statuses.values())


def test_missing_and_differing_categories(repo):
    # Only [tool.ruff] present, and it differs from the standard.
    (repo / "pyproject.toml").write_text(
        "[project]\nname = 't'\nversion = '0.1.0'\n\n[tool.ruff]\nline-length = 88\n"
    )
    statuses = {c.name: c.status for c in standards.compare_pyproject("python")}
    assert statuses["ruff"] == "differs"
    assert statuses["pytest"] == "missing"
    assert statuses["ty"] == "missing"
    assert statuses["uv"] == "missing"


def test_precommit_missing_then_written(repo):
    assert standards.compare_precommit("python") == "missing"
    assert standards.write_precommit("python") is True
    assert (repo / ".pre-commit-config.yaml").exists()
    assert standards.compare_precommit("python") == "ok"


def test_precommit_not_overwritten_when_differs(repo):
    path = repo / ".pre-commit-config.yaml"
    path.write_text("repos: []\n")
    assert standards.compare_precommit("python") == "differs"
    assert standards.write_precommit("python") is False
    assert path.read_text() == "repos: []\n"


def test_write_precommit_dry_run_does_not_write(repo):
    assert standards.write_precommit("python", dry_run=True) is True
    assert not (repo / ".pre-commit-config.yaml").exists()


def test_unpinned_dependencies_none_without_pyproject(repo):
    assert standards.unpinned_dependencies() == []


def test_unpinned_dependencies_flags_bare_names(repo):
    (repo / "pyproject.toml").write_text(
        "[project]\n"
        "name = 't'\n"
        "version = '0.1.0'\n"
        'dependencies = ["httpx>=0.27", "requests", "polars[all]"]\n\n'
        "[project.optional-dependencies]\n"
        'plot = ["matplotlib"]\n\n'
        "[dependency-groups]\n"
        'dev = ["pytest>=9", "ruff", {include-group = "plot"}]\n'
    )
    assert standards.unpinned_dependencies() == [
        "matplotlib",
        "polars",
        "requests",
        "ruff",
    ]


def test_pinned_dependencies_are_clean(repo):
    (repo / "pyproject.toml").write_text(
        "[project]\n"
        "name = 't'\n"
        "version = '0.1.0'\n"
        'dependencies = ["httpx>=0.27", "typer==0.12.0", "tool @ git+https://x/y"]\n'
    )
    assert standards.unpinned_dependencies() == []


def test_missing_dev_tools_none_without_pyproject(repo):
    assert standards.missing_dev_tools() == []


def test_missing_dev_tools_lists_absent_tools(repo):
    (repo / "pyproject.toml").write_text(
        "[project]\n"
        "name = 't'\n"
        "version = '0.1.0'\n\n"
        "[dependency-groups]\n"
        'dev = ["ruff>=0.15", "pytest>=9"]\n'
    )
    # ruff + pytest present; ty + pre-commit still missing.
    assert standards.missing_dev_tools() == ["ty", "pre-commit"]


def test_missing_dev_tools_empty_when_all_present(repo):
    (repo / "pyproject.toml").write_text(
        "[project]\n"
        "name = 't'\n"
        "version = '0.1.0'\n\n"
        "[dependency-groups]\n"
        'dev = ["ruff", "ty", "pytest", "pre-commit"]\n'
    )
    assert standards.missing_dev_tools() == []


def test_add_dev_tools_dry_run_builds_command(repo):
    ok, cmd = standards.add_dev_tools(["ty", "pre-commit"], dry_run=True)
    assert ok
    assert cmd == "[dry-run] uv add --dev ty pre-commit"


def test_add_dev_tools_noop_for_empty_list(repo):
    ok, msg = standards.add_dev_tools([], dry_run=False)
    assert ok
    assert "no dev tools" in msg


def test_install_precommit_hook_dry_run(repo):
    ok, cmd = standards.install_precommit_hook(dry_run=True)
    assert ok
    assert cmd == "[dry-run] uv run pre-commit install"
