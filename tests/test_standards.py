"""Tests for the opinionated tooling standard (standards.py)."""

from __future__ import annotations

from tara import standards


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
