"""Tests for the Claude Code port: instructions, agents, commands, skills."""

from __future__ import annotations

from pathlib import Path

from tara import claude, core, frontmatter

# ── tool name mapping ─────────────────────────────────────────────────────────


def test_claude_tools_maps_search_to_glob_and_grep():
    assert claude.claude_tools(["read", "search"]) == ["Glob", "Grep", "Read"]


def test_claude_tools_reads_a_delimited_string():
    assert claude.claude_tools("read, bash") == ["Bash", "Read"]


def test_claude_tools_drops_unknown_names():
    assert claude.claude_tools(["read", "telepathy"]) == ["Read"]


def test_claude_tools_empty_for_missing_value():
    assert claude.claude_tools(None) == []


def test_claude_agent_name_strips_suffix():
    assert claude.claude_agent_name("yoda.agent.md") == "yoda"


# ── agent translation ─────────────────────────────────────────────────────────


def _make_agent(directory: Path, name: str, tools: str = "read, search") -> Path:
    src = directory / f"{name}.agent.md"
    src.write_text(
        f"---\n"
        f'description: "The {name} agent."\n'
        f"tools: [{tools}]\n"
        f"user-invocable: true\n"
        f"---\n\n"
        f"Body of {name}.\n"
    )
    return src


def test_translate_agent_writes_name_description_and_tools(tmp_path):
    fm, body = frontmatter.parse(claude.translate_agent(_make_agent(tmp_path, "yoda")))
    assert fm["name"] == "yoda"
    assert fm["description"] == "The yoda agent."
    assert fm["tools"] == "Glob, Grep, Read"
    assert body == "Body of yoda."


def test_translate_agent_drops_copilot_only_frontmatter(tmp_path):
    fm, _ = frontmatter.parse(claude.translate_agent(_make_agent(tmp_path, "yoda")))
    assert "user-invocable" not in fm


def test_translate_agent_omits_tools_when_none_map(tmp_path):
    """No tools key means the subagent inherits Claude Code's full toolset."""
    src = tmp_path / "open.agent.md"
    src.write_text('---\ndescription: "Open agent."\n---\n\nBody.\n')
    fm, _ = frontmatter.parse(claude.translate_agent(src))
    assert "tools" not in fm


# ── prompt → command translation ──────────────────────────────────────────────


def test_translate_prompt_keeps_description_drops_agent_and_tools(tmp_path):
    src = tmp_path / "fix.prompt.md"
    src.write_text(
        "---\n"
        'description: "Fix lint errors."\n'
        "agent: agent\n"
        "tools: [read, edit]\n"
        "---\n\n"
        "Do the fixing.\n"
    )
    fm, body = frontmatter.parse(claude.translate_prompt(src))
    assert fm == {"description": "Fix lint errors."}
    assert body == "Do the fixing."


# ── port_instructions ─────────────────────────────────────────────────────────


def test_port_instructions_writes_an_import_pointer(repo):
    claude.port_instructions()
    text = (repo / core.CLAUDE_INSTRUCTIONS).read_text()
    assert claude.GENERATED_MARKER in text
    assert "@.github/copilot-instructions.md" in text


def test_port_instructions_overwrites_its_own_output(repo):
    claude.port_instructions()
    (repo / core.CLAUDE_INSTRUCTIONS).write_text(f"{claude.GENERATED_MARKER}\nstale\n")
    claude.port_instructions()
    assert "stale" not in (repo / core.CLAUDE_INSTRUCTIONS).read_text()


def test_port_instructions_leaves_a_hand_written_file_alone(repo):
    (repo / core.CLAUDE_INSTRUCTIONS).write_text("# My own brief\n")
    line = claude.port_instructions()
    assert "skipped" in line
    assert (repo / core.CLAUDE_INSTRUCTIONS).read_text() == "# My own brief\n"


def test_port_instructions_dry_run(repo):
    line = claude.port_instructions(dry_run=True)
    assert "[dry-run]" in line
    assert not (repo / core.CLAUDE_INSTRUCTIONS).exists()


# ── port_mcp ──────────────────────────────────────────────────────────────────


def test_port_mcp_reuses_the_existing_file(repo):
    (repo / core.MCP_CONFIG).write_text('{"mcpServers": {}}')
    assert "reused" in claude.port_mcp()


def test_port_mcp_reports_a_missing_file(repo):
    assert "missing" in claude.port_mcp()


def test_port_mcp_never_writes(repo):
    (repo / core.MCP_CONFIG).write_text('{"mcpServers": {}}')
    claude.port_mcp()
    assert (repo / core.MCP_CONFIG).read_text() == '{"mcpServers": {}}'


# ── port_agents ───────────────────────────────────────────────────────────────


def test_port_agents_no_agents_returns_empty(repo):
    assert claude.port_agents() == []


def test_port_agents_writes_one_file_per_agent(repo):
    agents_dir = repo / claude.COPILOT_AGENTS_DIR
    agents_dir.mkdir(parents=True)
    _make_agent(agents_dir, "yoda")
    claude.port_agents()
    assert (repo / claude.CLAUDE_AGENTS_DIR / "yoda.md").exists()


# ── port_commands ─────────────────────────────────────────────────────────────


def test_port_commands_writes_starter_commands(repo):
    claude.port_commands()
    commands = repo / claude.CLAUDE_COMMANDS_DIR
    assert (commands / "check.md").exists()
    assert (commands / "review.md").exists()


def test_starter_commands_emit_the_hyphenated_allowed_tools_key(repo):
    """Claude Code reads `allowed-tools`, not the Python field name."""
    claude.port_commands()
    fm, _ = frontmatter.parse(
        (repo / claude.CLAUDE_COMMANDS_DIR / "check.md").read_text()
    )
    assert fm["allowed-tools"] == "Bash(uv run:*)"
    assert "allowed_tools" not in fm


def test_port_commands_preserves_prompt_nesting(repo):
    src = repo / claude.COPILOT_PROMPTS_DIR / "python"
    src.mkdir(parents=True)
    (src / "add-types.prompt.md").write_text(
        '---\ndescription: "Add type hints."\n---\n\nAdd them.\n'
    )
    claude.port_commands()
    assert (repo / claude.CLAUDE_COMMANDS_DIR / "python" / "add-types.md").exists()


def test_port_commands_lets_a_prompt_win_over_a_starter(repo):
    src = repo / claude.COPILOT_PROMPTS_DIR
    src.mkdir(parents=True)
    (src / "check.prompt.md").write_text(
        '---\ndescription: "My own check."\n---\n\nCheck it.\n'
    )
    claude.port_commands()
    text = (repo / claude.CLAUDE_COMMANDS_DIR / "check.md").read_text()
    assert "My own check." in text


# ── port_skills ───────────────────────────────────────────────────────────────


def _make_skill(directory: Path, name: str) -> None:
    skill = directory / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(f"---\nname: {name}\n---\n\nBody.\n")


def test_port_skills_mirrors_each_skill(repo):
    _make_skill(repo / claude.COPILOT_SKILLS_DIR, "demo")
    claude.port_skills()
    assert (repo / claude.CLAUDE_SKILLS_DIR / "demo" / "SKILL.md").exists()


def test_port_skills_prunes_a_stale_skill(repo):
    _make_skill(repo / claude.COPILOT_SKILLS_DIR, "demo")
    _make_skill(repo / claude.CLAUDE_SKILLS_DIR, "removed")
    claude.port_skills()
    assert not (repo / claude.CLAUDE_SKILLS_DIR / "removed").exists()


def test_port_skills_dry_run_writes_nothing(repo):
    _make_skill(repo / claude.COPILOT_SKILLS_DIR, "demo")
    claude.port_skills(dry_run=True)
    assert not (repo / claude.CLAUDE_SKILLS_DIR).exists()


# ── port_all ──────────────────────────────────────────────────────────────────


def test_port_all_reports_every_section(repo):
    titles = [title for title, _ in claude.port_all()]
    assert titles == ["Instructions", "MCP", "Agents", "Commands", "Skills"]
