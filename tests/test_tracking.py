"""Tests for the agent hand-off ledger setup."""

from __future__ import annotations

from wingman import tracking


def test_write_tracking_creates_folder_readme_and_gitignore(repo):
    out = tracking.write_tracking(dry_run=False)

    folder = repo / tracking.DEFAULT_DIR
    assert (folder / tracking.HANDOFFS).is_dir()
    assert (folder / "README.md").is_file()
    gi = (repo / ".gitignore").read_text()
    assert ".agent/tracking/handoffs/" in gi
    assert "!.agent/tracking/README.md" in gi
    assert ".agent/tracking/README.md" in out


def test_readme_documents_schema_and_commands(repo):
    tracking.write_tracking(dry_run=False)
    readme = (repo / tracking.DEFAULT_DIR / "README.md").read_text()
    for column, _desc in tracking.SCHEMA:
        assert f"`{column}`" in readme
    assert "read_parquet" in readme
    assert "COPY" in readme


def test_write_tracking_appends_to_existing_gitignore(repo):
    (repo / ".gitignore").write_text("__pycache__/\n")
    tracking.write_tracking(dry_run=False)
    gi = (repo / ".gitignore").read_text()
    assert "__pycache__/" in gi  # preserved
    assert ".agent/tracking/handoffs/" in gi  # appended


def test_write_tracking_is_idempotent(repo):
    tracking.write_tracking(dry_run=False)
    tracking.write_tracking(dry_run=False)
    gi = (repo / ".gitignore").read_text()
    assert gi.count(".agent/tracking/handoffs/") == 1


def test_dry_run_writes_nothing(repo):
    out = tracking.write_tracking(dry_run=True)
    assert "[dry-run]" in out
    assert not (repo / tracking.DEFAULT_DIR).exists()
    assert not (repo / ".gitignore").exists()


def test_config_opt_out_of_gitignore(repo):
    cfg = repo / ".wingman"
    cfg.mkdir()
    (cfg / "config.toml").write_text("[tracking]\ngitignore = false\n")

    out = tracking.write_tracking(dry_run=False)
    assert (repo / tracking.DEFAULT_DIR / "README.md").is_file()
    assert not (repo / ".gitignore").exists()
    assert "gitignore=false" in out


def test_config_custom_dir(repo):
    cfg = repo / ".wingman"
    cfg.mkdir()
    (cfg / "config.toml").write_text('[tracking]\ndir = ".notes/ledger"\n')

    tracking.write_tracking(dry_run=False)
    assert (repo / ".notes" / "ledger" / tracking.HANDOFFS).is_dir()
    gi = (repo / ".gitignore").read_text()
    assert ".notes/ledger/handoffs/" in gi
