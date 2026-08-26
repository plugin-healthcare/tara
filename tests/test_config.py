"""Tests for Tara config persistence (config.py)."""

from __future__ import annotations

import tomllib

from tara.config import CONFIG, AgentsConfig, StandardsConfig, TaraConfig, write_config


def test_write_config_creates_file(repo):
    msg = write_config("copilot", "python", dry_run=False)
    path = repo / CONFIG
    assert path.exists()
    data = tomllib.loads(path.read_text())
    assert data["tools"] == ["copilot"]
    assert data["stack"] == "python"
    assert "wrote" in msg


def test_load_round_trips_setup_state(repo):
    write_config(["opencode"], "python", dry_run=False)
    cfg = TaraConfig.load()
    assert cfg.tools == ["copilot", "opencode"]
    assert cfg.stack == "python"


def test_load_defaults_when_absent(repo):
    cfg = TaraConfig.load()
    assert cfg.tools == ["copilot"]
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
    assert TaraConfig.load().tools == ["copilot", "opencode"]


def test_dry_run_does_not_write(repo):
    msg = write_config("copilot", "python", dry_run=True)
    assert not (repo / CONFIG).exists()
    assert "[dry-run]" in msg


def test_standards_load_reads_config(repo):
    path = repo / CONFIG
    path.parent.mkdir(parents=True)
    path.write_text('[standards]\ndev_tools = ["ruff", "ty"]\n')
    assert StandardsConfig.load().dev_tools == ["ruff", "ty"]


def test_agents_defaults_empty(repo):
    cfg = TaraConfig.load()
    assert cfg.agents.gitignore == []
    assert AgentsConfig().gitignore == []


def test_write_preserves_agents_gitignore(repo):
    path = repo / CONFIG
    path.parent.mkdir(parents=True)
    path.write_text(
        'tool = "copilot"\nstack = "python"\n\n[agents]\ngitignore = ["memory"]\n'
    )
    write_config("copilot", "python", dry_run=False)
    assert TaraConfig.load().agents.gitignore == ["memory"]


def test_fresh_config_documents_optional_settings(repo):
    write_config("copilot", "python", dry_run=False)
    text = (repo / CONFIG).read_text()
    assert "# [agents]" in text
    assert "gitignore" in text
    assert "# [standards]" in text
    assert "optional settings" in text


def test_set_option_is_not_re_documented(repo):
    path = repo / CONFIG
    path.parent.mkdir(parents=True)
    path.write_text(
        'tool = "copilot"\nstack = "python"\n\n[agents]\ngitignore = ["memory"]\n'
    )
    write_config("copilot", "python", dry_run=False)
    text = (repo / CONFIG).read_text()
    assert "# [agents]" not in text  # already set, so not re-documented
    assert "# [standards]" in text  # still absent, so documented


def test_load_migrates_legacy_tool_scalar(repo):
    path = repo / CONFIG
    path.parent.mkdir(parents=True)
    path.write_text('tool = "opencode"\nstack = "python"\n')
    assert TaraConfig.load().tools == ["copilot", "opencode"]


def test_load_migrates_legacy_all(repo):
    path = repo / CONFIG
    path.parent.mkdir(parents=True)
    path.write_text('tool = "all"\nstack = "python"\n')
    assert TaraConfig.load().tools == ["copilot", "opencode", "claude"]


def test_write_drops_legacy_tool_key(repo):
    path = repo / CONFIG
    path.parent.mkdir(parents=True)
    path.write_text('tool = "opencode"\nstack = "python"\n')
    write_config(["claude"], "python", dry_run=False)
    data = tomllib.loads(path.read_text())
    assert "tool" not in data
    assert data["tools"] == ["copilot", "claude"]


def test_port_targets_excludes_copilot(repo):
    write_config(["claude"], "python", dry_run=False)
    assert TaraConfig.load().port_targets == ["claude"]
