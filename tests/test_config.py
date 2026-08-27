"""Tests for Tara config persistence (config.py)."""

from __future__ import annotations

import tomllib

import pytest

from tara.config import (
    CONFIG,
    AgentsConfig,
    ConfigError,
    StandardsConfig,
    TaraConfig,
    write_config,
)


def test_write_config_creates_file(repo):
    msg = write_config("copilot", "python", dry_run=False)
    path = repo / CONFIG
    assert path.exists()
    data = tomllib.loads(path.read_text())
    assert data["integrations"] == ["copilot"]
    assert data["stack"] == "python"
    assert "wrote" in msg


def test_load_round_trips_setup_state(repo):
    write_config(["opencode"], "python", dry_run=False)
    cfg = TaraConfig.load()
    assert cfg.integrations == ["copilot", "opencode"]
    assert cfg.stack == "python"


def test_load_defaults_when_absent(repo):
    cfg = TaraConfig.load()
    assert cfg.integrations == ["copilot"]
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
    assert TaraConfig.load().integrations == ["copilot", "opencode"]


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
    assert TaraConfig.load().integrations == ["copilot", "opencode"]


def test_load_migrates_legacy_all(repo):
    path = repo / CONFIG
    path.parent.mkdir(parents=True)
    path.write_text('tool = "all"\nstack = "python"\n')
    assert TaraConfig.load().integrations == ["copilot", "opencode"]


def test_write_drops_legacy_tool_key(repo):
    path = repo / CONFIG
    path.parent.mkdir(parents=True)
    path.write_text('tool = "opencode"\nstack = "python"\n')
    write_config(["claude"], "python", dry_run=False)
    data = tomllib.loads(path.read_text())
    assert "tool" not in data
    assert "tools" not in data
    assert data["integrations"] == ["copilot", "claude"]


def test_write_expands_all_to_explicit_integration_names(repo):
    write_config("all", "python", dry_run=False)
    data = tomllib.loads((repo / CONFIG).read_text())
    assert data["integrations"] == ["copilot", "opencode", "claude"]


def test_port_targets_excludes_copilot(repo):
    write_config(["claude"], "python", dry_run=False)
    assert TaraConfig.load().port_targets == ["claude"]


# ── hand-edited configs must fail loudly, not guess ───────────────────────────


def _write_raw(repo, text: str) -> None:
    path = repo / CONFIG
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_load_rejects_an_unknown_integration(repo):
    _write_raw(repo, 'tools = ["copilot", "emacs"]\nstack = "python"\n')
    with pytest.raises(ConfigError) as exc:
        TaraConfig.load()
    assert "unknown integration 'emacs'" in str(exc.value)
    assert "integrations" in str(exc.value)


def test_load_rejects_malformed_toml(repo):
    _write_raw(repo, "tools = [unquoted\n")
    with pytest.raises(ConfigError) as exc:
        TaraConfig.load()
    assert "not valid TOML" in str(exc.value)


def test_load_rejects_a_bad_value_type(repo):
    _write_raw(repo, "stack = 3\n")
    with pytest.raises(ConfigError) as exc:
        TaraConfig.load()
    assert "stack" in str(exc.value)


def test_load_rejects_a_non_list_tools_value(repo):
    _write_raw(repo, 'tools = 3\nstack = "python"\n')
    with pytest.raises(ConfigError) as exc:
        TaraConfig.load()
    assert "integrations must be a string or list of strings" in str(exc.value)


def test_load_rejects_non_string_tool_names(repo):
    _write_raw(repo, 'tools = ["copilot", 3]\nstack = "python"\n')
    with pytest.raises(ConfigError) as exc:
        TaraConfig.load()
    assert "integrations must contain only strings" in str(exc.value)
