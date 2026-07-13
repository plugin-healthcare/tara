"""Tests for the agent memory / handover folder setup."""

from __future__ import annotations

from wingman import handover


def test_write_handover_creates_folder_readme_and_gitignore(repo):
    out = handover.write_handover(dry_run=False)

    folder = repo / handover.DEFAULT_DIR
    assert (folder / "README.md").is_file()
    gi = (repo / handover.GITIGNORE).read_text()
    assert ".agent/memory/*" in gi
    assert "!.agent/memory/README.md" in gi
    assert ".agent/memory/README.md" in out


def test_write_handover_appends_to_existing_gitignore(repo):
    (repo / ".gitignore").write_text("__pycache__/\n")
    handover.write_handover(dry_run=False)
    gi = (repo / ".gitignore").read_text()
    assert "__pycache__/" in gi  # preserved
    assert ".agent/memory/*" in gi  # appended


def test_write_handover_is_idempotent(repo):
    handover.write_handover(dry_run=False)
    handover.write_handover(dry_run=False)
    gi = (repo / ".gitignore").read_text()
    assert gi.count(".agent/memory/*") == 1


def test_dry_run_writes_nothing(repo):
    out = handover.write_handover(dry_run=True)
    assert "[dry-run]" in out
    assert not (repo / handover.DEFAULT_DIR).exists()
    assert not (repo / ".gitignore").exists()


def test_config_opt_out_of_gitignore(repo):
    cfg = repo / ".wingman"
    cfg.mkdir()
    (cfg / "config.toml").write_text("[handover]\ngitignore = false\n")

    out = handover.write_handover(dry_run=False)
    assert (repo / handover.DEFAULT_DIR / "README.md").is_file()
    assert not (repo / ".gitignore").exists()
    assert "gitignore=false" in out


def test_config_custom_dir(repo):
    cfg = repo / ".wingman"
    cfg.mkdir()
    (cfg / "config.toml").write_text('[handover]\ndir = ".notes/agent"\n')

    handover.write_handover(dry_run=False)
    assert (repo / ".notes" / "agent" / "README.md").is_file()
    gi = (repo / ".gitignore").read_text()
    assert ".notes/agent/*" in gi
