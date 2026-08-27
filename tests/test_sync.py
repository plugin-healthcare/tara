"""Tests for library-skill sync, focused on the core-ownership guard."""

from __future__ import annotations

from pathlib import Path

import pytest

from tara import sync as sync_mod

SKILL_MD = (
    "---\n"
    "name: {name}\n"
    'description: "The {name} skill. Use when testing sync behavior."\n'
    "---\n\n# {name}\n\nEnough body content for the skill to be usable here.\n"
)


def _make_library_skill(base: Path, name: str) -> Path:
    """Create a fake installed-package skill dir and return its SKILL.md path."""
    folder = base / name
    folder.mkdir(parents=True)
    md = folder / "SKILL.md"
    md.write_text(SKILL_MD.format(name=name))
    return md


@pytest.fixture
def patch_discover(monkeypatch):
    """Return a helper that stubs _discover to yield the given SKILL.md paths."""

    def _apply(md_paths: list[Path]) -> None:
        raw = [
            {"package": "pkg", "version": "1.0.0", "skill_md": str(p)} for p in md_paths
        ]
        monkeypatch.setattr(sync_mod, "_discover", lambda root: (raw, None))

    return _apply


def test_sync_adds_new_library_skill(repo, tmp_path, patch_discover):
    md = _make_library_skill(tmp_path / "lib", "foo")
    patch_discover([md])

    result = sync_mod.sync(all_packages=True)

    assert result.added == ["foo"]
    assert result.skipped == []
    assert (repo / sync_mod.SKILLS_DIR / "foo" / "SKILL.md").is_file()
    assert "foo" in sync_mod.read_lock()


def test_sync_skips_core_managed_skill(repo, tmp_path, patch_discover):
    # A core skill already sits in .github/skills/ but is NOT in sync's lock.
    core = repo / sync_mod.SKILLS_DIR / "writing-adrs"
    core.mkdir(parents=True)
    (core / "SKILL.md").write_text("core content, do not overwrite\n")

    md = _make_library_skill(tmp_path / "lib", "writing-adrs")
    patch_discover([md])

    result = sync_mod.sync(all_packages=True)

    assert result.skipped == ["writing-adrs"]
    assert result.added == []
    assert result.skipped_reasons["writing-adrs"] == "core catalog"
    # Core file is untouched and sync never recorded ownership of it.
    assert (core / "SKILL.md").read_text() == "core content, do not overwrite\n"
    assert "writing-adrs" not in sync_mod.read_lock()


def test_sync_reports_a_git_managed_skill_as_git_managed(
    repo, tmp_path, patch_discover
):
    """A skill in skills.toml came from a git repo, not Tara's own catalog."""
    installed = repo / sync_mod.SKILLS_DIR / "developing-with-streamlit"
    installed.mkdir(parents=True)
    (installed / "SKILL.md").write_text("from the streamlit theme\n")
    (repo / ".tara").mkdir(exist_ok=True)
    (repo / ".tara" / "skills.toml").write_text(
        "[skills.developing-with-streamlit]\n"
        'repo = "https://github.com/streamlit/agent-skills"\n'
        'path = "developing-with-streamlit"\n'
        'ref = "main"\n'
    )

    md = _make_library_skill(tmp_path / "lib", "developing-with-streamlit")
    patch_discover([md])

    result = sync_mod.sync(all_packages=True)

    assert result.skipped == ["developing-with-streamlit"]
    assert result.skipped_reasons["developing-with-streamlit"] == "git-managed"
