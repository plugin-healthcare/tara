"""Tests for Tara config persistence (config.py)."""

from __future__ import annotations

import tomllib

from tara.config import CONFIG, StandardsConfig, TaraConfig, write_config


def test_write_config_creates_file(repo):
    msg = write_config("copilot", "python", dry_run=False)
    path = repo / CONFIG
    assert path.exists()
    data = tomllib.loads(path.read_text())
    assert data["tool"] == "copilot"
    assert data["stack"] == "python"
    assert "wrote" in msg


def test_load_round_trips_setup_state(repo):
    write_config("opencode", "python", dry_run=False)
    cfg = TaraConfig.load()
    assert cfg.tool == "opencode"
    assert cfg.stack == "python"


def test_load_defaults_when_absent(repo):
    cfg = TaraConfig.load()
    assert cfg.tool == "copilot"
    assert cfg.stack == "python"
    assert cfg.standards.dev_tools == StandardsConfig().dev_tools


def test_write_preserves_standards_overrides(repo):
    path = repo / CONFIG
    path.parent.mkdir(parents=True)
    path.write_text(
        'tool = "copilot"\nstack = "python"\n\n[standards]\ndev_tools = ["ruff"]\n'
    )
    msg = write_config("opencode", "python", dry_run=False)
    assert "updated" in msg
    assert StandardsConfig.load().dev_tools == ["ruff"]
    assert TaraConfig.load().tool == "opencode"


def test_dry_run_does_not_write(repo):
    msg = write_config("copilot", "python", dry_run=True)
    assert not (repo / CONFIG).exists()
    assert "[dry-run]" in msg


def test_standards_load_reads_config(repo):
    path = repo / CONFIG
    path.parent.mkdir(parents=True)
    path.write_text('[standards]\ndev_tools = ["ruff", "ty"]\n')
    assert StandardsConfig.load().dev_tools == ["ruff", "ty"]
