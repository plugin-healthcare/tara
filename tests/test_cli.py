"""CLI-level tests for the skill and agent command groups."""

from __future__ import annotations

from typer.testing import CliRunner

from tara import generate
from tara.cli import app
from tara.config import CONFIG, TaraConfig

runner = CliRunner()


def test_root_help_supports_short_alias():
    result = runner.invoke(app, ["-h"])
    assert result.exit_code == 0
    assert "Usage: tara" in result.output


def test_nested_help_supports_short_alias():
    result = runner.invoke(app, ["skill", "add", "-h"])
    assert result.exit_code == 0
    assert "tara skill add" in result.output


def test_version_supports_long_and_short_aliases():
    long = runner.invoke(app, ["--version"])
    short = runner.invoke(app, ["-V"])
    assert long.exit_code == 0
    assert short.exit_code == 0
    assert long.output == short.output == "tara 1.1.0\n"


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


def test_init_opencode_generates_from_copilot(repo):
    result = runner.invoke(app, ["init", "--tools", "opencode", "--all"])
    assert result.exit_code == 0, result.output
    # opencode files are generated from the Copilot setup, which exists too.
    assert (repo / ".github" / "copilot-instructions.md").is_file()
    assert (repo / ".mcp.json").is_file()
    # No duplicate AGENTS.md; opencode.json references the Copilot instructions.
    assert not (repo / "AGENTS.md").exists()
    config = repo / "opencode.json"
    assert config.is_file()
    assert ".github/copilot-instructions.md" in config.read_text()


def test_init_claude_generates_from_copilot(repo):
    result = runner.invoke(app, ["init", "--tools", "claude", "--all"])
    assert result.exit_code == 0, result.output
    claude_md = repo / "CLAUDE.md"
    assert claude_md.is_file()
    # A pointer, not a second copy of the instructions.
    assert "@.github/copilot-instructions.md" in claude_md.read_text()
    assert (repo / ".claude" / "commands" / "check.md").is_file()


def test_init_all_generates_every_tool(repo):
    result = runner.invoke(app, ["init", "--tools", "all", "--all"])
    assert result.exit_code == 0, result.output
    assert (repo / "opencode.json").is_file()
    assert (repo / "CLAUDE.md").is_file()
    assert (repo / ".github" / "copilot-instructions.md").is_file()
    assert (repo / ".mcp.json").is_file()


def test_init_accepts_comma_separated_tools(repo):
    result = runner.invoke(app, ["init", "--tools", "claude,opencode", "--all"])
    assert result.exit_code == 0, result.output
    assert (repo / "CLAUDE.md").is_file()
    assert (repo / "opencode.json").is_file()


def test_init_copilot_default_does_not_generate(repo):
    result = runner.invoke(app, ["init", "--all"])
    assert result.exit_code == 0, result.output
    assert (repo / ".github" / "copilot-instructions.md").is_file()
    assert not (repo / "opencode.json").exists()
    assert not (repo / "CLAUDE.md").exists()


def test_init_supports_short_all_and_dry_run_aliases(repo):
    result = runner.invoke(app, ["init", "-a", "-n"])
    assert result.exit_code == 0, result.output
    assert not (repo / ".github" / "copilot-instructions.md").exists()


def test_init_rejects_unknown_integration(repo):
    result = runner.invoke(app, ["init", "--tools", "vim"])
    assert result.exit_code == 1
    assert "unknown integration" in result.output


# ── tools ─────────────────────────────────────────────────────────────────────


def test_integrations_sets_targets_and_generates(repo):
    runner.invoke(app, ["init", "--all"])
    result = runner.invoke(app, ["integrations", "claude"])
    assert result.exit_code == 0, result.output
    assert (repo / "CLAUDE.md").is_file()
    assert TaraConfig.load().integrations == ["copilot", "claude"]


def test_integrations_accepts_comma_separated_names(repo):
    runner.invoke(app, ["init", "--all"])
    result = runner.invoke(app, ["integrations", "claude,opencode"])
    assert result.exit_code == 0, result.output
    assert TaraConfig.load().integrations == ["copilot", "opencode", "claude"]


def test_integrations_regenerates_configured_targets_without_args(repo):
    runner.invoke(app, ["init", "--tools", "claude", "--all"])
    runner.invoke(app, ["agent", "add", "yoda"])
    result = runner.invoke(app, ["integrations"])
    assert result.exit_code == 0, result.output
    assert (repo / ".claude" / "agents" / "yoda.md").is_file()


def test_integrations_list_shows_targets(repo):
    runner.invoke(app, ["init", "--tools", "claude", "--all"])
    result = runner.invoke(app, ["integrations", "--list"])
    assert result.exit_code == 0, result.output
    assert "\u2713 copilot" in result.output
    assert "\u2713 claude" in result.output
    assert "\u2014 opencode" in result.output


def test_integrations_copilot_only_generates_nothing(repo):
    runner.invoke(app, ["init", "--integrations", "claude", "--all"])
    assert (repo / "CLAUDE.md").exists()
    result = runner.invoke(app, ["integrations", "copilot"])
    assert result.exit_code == 0, result.output
    assert "nothing to generate" in result.output
    assert not (repo / "CLAUDE.md").exists()


def test_removing_an_integration_preserves_hand_written_files(repo):
    runner.invoke(app, ["init", "--integrations", "claude", "--all"])
    custom = repo / ".claude" / "agents" / "custom.md"
    custom.parent.mkdir(parents=True, exist_ok=True)
    custom.write_text("mine\n")

    result = runner.invoke(app, ["integrations", "copilot"])

    assert result.exit_code == 0, result.output
    assert custom.read_text() == "mine\n"


def test_integrations_rejects_unknown(repo):
    result = runner.invoke(app, ["integrations", "vim"])
    assert result.exit_code == 1
    assert "unknown integration" in result.output


def test_integrations_generates_installed_agents_for_claude(repo):
    runner.invoke(app, ["agent", "add", "yoda"])
    result = runner.invoke(app, ["integrations", "claude"])
    assert result.exit_code == 0, result.output
    translated = repo / ".claude" / "agents" / "yoda.md"
    assert translated.is_file()
    assert "name: yoda" in translated.read_text()


def test_integrations_force_overwrites_an_existing_claude_agent(repo):
    runner.invoke(app, ["agent", "add", "yoda"])
    dest = repo / ".claude" / "agents" / "yoda.md"
    dest.parent.mkdir(parents=True)
    dest.write_text("mine\n")

    refused = runner.invoke(app, ["integrations", "claude"])
    assert refused.exit_code == 0, refused.output
    assert dest.read_text() == "mine\n"
    assert "requires --force" in refused.output

    forced = runner.invoke(app, ["integrations", "claude", "-f"])
    assert forced.exit_code == 0, forced.output
    assert generate.MARKER in dest.read_text()


def test_integrations_supports_short_list_alias(repo):
    runner.invoke(app, ["init", "--all"])
    result = runner.invoke(app, ["integrations", "-l"])
    assert result.exit_code == 0, result.output
    assert "Integrations:" in result.output


def test_tools_command_remains_as_a_deprecated_alias(repo):
    runner.invoke(app, ["init", "--all"])
    result = runner.invoke(app, ["tools", "-l"])
    assert result.exit_code == 0, result.output
    assert "deprecated" in result.output


def test_integrations_generates_installed_agents_for_opencode(repo):
    runner.invoke(app, ["agent", "add", "yoda"])
    result = runner.invoke(app, ["integrations", "opencode"])
    assert result.exit_code == 0, result.output
    translated = repo / ".opencode" / "agents" / "yoda.md"
    assert translated.is_file()
    assert "mode: subagent" in translated.read_text()
    assert (repo / ".opencode" / "commands" / "check.md").is_file()


# ── backwards compatibility with the 1.0.0 surface ────────────────────────────


def test_init_accepts_legacy_tool_flag(repo):
    """`--tool` is the original spelling and must keep working."""
    result = runner.invoke(app, ["init", "--tool", "opencode", "--all"])
    assert result.exit_code == 0, result.output
    assert (repo / "opencode.json").is_file()
    assert TaraConfig.load().integrations == ["copilot", "opencode"]


def test_sync_regenerates_configured_tools(repo):
    """`tara sync` keeps its 1.0.0 skill sync and also refreshes tool files."""
    runner.invoke(app, ["init", "--tools", "claude", "--all"])
    runner.invoke(app, ["agent", "add", "yoda"])
    (repo / ".claude" / "agents" / "yoda.md").unlink(missing_ok=True)

    result = runner.invoke(app, ["sync", "--no-docs"])
    assert result.exit_code == 0, result.output
    assert (repo / ".claude" / "agents" / "yoda.md").is_file()


def test_sync_without_extra_tools_still_succeeds(repo):
    """Copilot-only repos have nothing to generate; sync must not fail."""
    runner.invoke(app, ["init", "--all"])
    result = runner.invoke(app, ["sync", "--no-docs"])
    assert result.exit_code == 0, result.output
    assert not (repo / "CLAUDE.md").exists()


def test_opencode_sync_alias_still_generates(repo):
    """`tara opencode sync` is hidden but must keep working."""
    runner.invoke(app, ["agent", "add", "yoda"])
    result = runner.invoke(app, ["opencode", "sync"])
    assert result.exit_code == 0, result.output
    assert (repo / "opencode.json").is_file()
    assert (repo / ".opencode" / "agents" / "yoda.md").is_file()


def test_commands_report_a_broken_config_and_exit_non_zero(repo):
    """A typo in .tara/config.toml must be named, not silently ignored."""
    path = repo / CONFIG
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('tools = ["copilot", "emacs"]\nstack = "python"\n')
    result = runner.invoke(app, ["integrations", "--list"])
    assert result.exit_code != 0
    assert "unknown integration 'emacs'" in result.output


def test_unrelated_commands_still_run_with_a_broken_config(repo):
    path = repo / CONFIG
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('tools = ["copilot", "emacs"]\nstack = "python"\n')
    result = runner.invoke(app, ["new", "changelog"])
    assert result.exit_code == 0, result.output
