"""Tests for the Claude Code port: instructions, agents, commands, skills."""

from __future__ import annotations

import shutil
from pathlib import Path

from tara import claude, core, frontmatter, generate

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
    assert fm["tools"] == ["Glob", "Grep", "Read"]
    assert body.endswith("Body of yoda.")
    assert generate.MARKER in body


def test_translate_agent_drops_copilot_only_frontmatter(tmp_path):
    fm, _ = frontmatter.parse(claude.translate_agent(_make_agent(tmp_path, "yoda")))
    assert "user-invocable" not in fm


def test_translate_agent_omits_tools_when_none_declared(tmp_path):
    """No tools key means the subagent inherits Claude Code's full toolset."""
    src = tmp_path / "open.agent.md"
    src.write_text('---\ndescription: "Open agent."\n---\n\nBody.\n')
    fm, _ = frontmatter.parse(claude.translate_agent(src))
    assert "tools" not in fm


def test_translate_agent_falls_back_to_read_only_tools(tmp_path):
    """An unmappable tool list must not silently inherit Bash and Write."""
    src = tmp_path / "narrow.agent.md"
    src.write_text('---\ndescription: "Narrow."\ntools: [nonsense]\n---\n\nBody.\n')
    fm, _ = frontmatter.parse(claude.translate_agent(src))
    assert fm["tools"] == ["Glob", "Grep", "Read"]


def test_translate_agent_maps_copilot_tool_vocabulary(tmp_path):
    src = tmp_path / "vs.agent.md"
    src.write_text(
        '---\ndescription: "VS."\ntools: [codebase, editFiles, runCommands]\n---\n\nB.\n'
    )
    fm, _ = frontmatter.parse(claude.translate_agent(src))
    assert fm["tools"] == ["Bash", "Edit", "Glob", "Grep", "Read", "Write"]


def test_translate_agent_preserves_an_explicit_empty_tool_list(tmp_path):
    src = tmp_path / "empty.agent.md"
    src.write_text('---\ndescription: "Empty."\ntools: []\n---\n\nBody.\n')
    fm, _ = frontmatter.parse(claude.translate_agent(src))
    assert fm["tools"] == []


def test_translate_agent_expands_wildcard_to_explicit_tool_names(tmp_path):
    src = tmp_path / "all.agent.md"
    src.write_text('---\ndescription: "All."\ntools: ["*"]\n---\n\nBody.\n')
    fm, _ = frontmatter.parse(claude.translate_agent(src))
    assert fm["tools"] == [
        "Bash",
        "Edit",
        "Glob",
        "Grep",
        "Read",
        "WebFetch",
        "WebSearch",
        "Write",
    ]


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
    assert body.endswith("Do the fixing.")


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


def test_port_commands_keeps_starter_when_only_a_nested_prompt_shares_a_name(repo):
    """A nested prompt lands at a different path, so it must not suppress the starter."""
    src = repo / claude.COPILOT_PROMPTS_DIR / "python"
    src.mkdir(parents=True)
    (src / "check.prompt.md").write_text(
        '---\ndescription: "Python check."\n---\n\nCheck python.\n'
    )
    claude.port_commands()
    commands = repo / claude.CLAUDE_COMMANDS_DIR
    assert (commands / "python" / "check.md").exists()
    assert (commands / "check.md").exists()


# ── port_skills ───────────────────────────────────────────────────────────────


def _make_skill(directory: Path, name: str) -> None:
    skill = directory / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(f"---\nname: {name}\n---\n\nBody.\n")


def test_port_skills_mirrors_each_skill(repo):
    _make_skill(repo / claude.COPILOT_SKILLS_DIR, "demo")
    claude.port_skills()
    assert (repo / claude.CLAUDE_SKILLS_DIR / "demo" / "SKILL.md").exists()


def test_port_skills_prunes_a_skill_it_generated(repo):
    """A mirrored skill whose Copilot source disappeared is cleaned up."""
    _make_skill(repo / claude.COPILOT_SKILLS_DIR, "demo")
    claude.port_skills()
    shutil.rmtree(repo / claude.COPILOT_SKILLS_DIR / "demo")
    claude.port_skills()
    assert not (repo / claude.CLAUDE_SKILLS_DIR / "demo").exists()


def test_port_skills_never_prunes_a_skill_it_did_not_generate(repo):
    """A hand-written Claude skill is the developer's; Tara leaves it alone."""
    _make_skill(repo / claude.COPILOT_SKILLS_DIR, "demo")
    _make_skill(repo / claude.CLAUDE_SKILLS_DIR, "my-own")
    claude.port_skills()
    assert (repo / claude.CLAUDE_SKILLS_DIR / "my-own" / "SKILL.md").is_file()


def test_port_skills_skips_an_unowned_collision(repo):
    """A same-named skill Tara did not write is reported, not overwritten."""
    _make_skill(repo / claude.COPILOT_SKILLS_DIR, "demo")
    _make_skill(repo / claude.CLAUDE_SKILLS_DIR, "demo")
    dest = repo / claude.CLAUDE_SKILLS_DIR / "demo"
    (dest / "SKILL.md").write_text("mine\n")
    lines = claude.port_skills()
    assert (dest / "SKILL.md").read_text() == "mine\n"
    assert any("skipped" in line for line in lines)


def test_port_skills_ignores_a_stray_file_in_the_destination(repo):
    """A plain file next to the skills must not crash the mirror."""
    _make_skill(repo / claude.COPILOT_SKILLS_DIR, "demo")
    dst = repo / claude.CLAUDE_SKILLS_DIR
    dst.mkdir(parents=True)
    (dst / "README.md").write_text("notes\n")
    claude.port_skills()
    assert (dst / "README.md").is_file()
    assert (dst / "demo" / "SKILL.md").is_file()


def test_port_skills_dry_run_writes_nothing(repo):
    _make_skill(repo / claude.COPILOT_SKILLS_DIR, "demo")
    claude.port_skills(dry_run=True)
    assert not (repo / claude.CLAUDE_SKILLS_DIR).exists()


# ── port_all ──────────────────────────────────────────────────────────────────


def test_port_all_reports_every_section(repo):
    titles = [title for title, _ in claude.port_all()]
    assert titles == ["Instructions", "MCP", "Agents", "Commands", "Skills"]


# ── never overwriting the developer's files ───────────────────────────────────


def test_port_agents_leaves_a_hand_written_agent_alone(repo):
    src = repo / claude.COPILOT_AGENTS_DIR
    src.mkdir(parents=True)
    (src / "yoda.agent.md").write_text('---\ndescription: "Y."\n---\n\nBody.\n')
    dest = repo / claude.CLAUDE_AGENTS_DIR / "yoda.md"
    dest.parent.mkdir(parents=True)
    dest.write_text("my own agent\n")
    lines = claude.port_agents()
    assert dest.read_text() == "my own agent\n"
    assert any("skipped" in line for line in lines)


def test_port_agents_refreshes_its_own_output(repo):
    src = repo / claude.COPILOT_AGENTS_DIR
    src.mkdir(parents=True)
    (src / "yoda.agent.md").write_text('---\ndescription: "Y."\n---\n\nBody.\n')
    claude.port_agents()
    dest = repo / claude.CLAUDE_AGENTS_DIR / "yoda.md"
    assert generate.MARKER in dest.read_text()
    (src / "yoda.agent.md").write_text('---\ndescription: "Y2."\n---\n\nBody.\n')
    claude.port_agents()
    assert "Y2." in dest.read_text()


def test_port_commands_leaves_a_hand_written_command_alone(repo):
    src = repo / claude.COPILOT_PROMPTS_DIR
    src.mkdir(parents=True)
    (src / "fix.prompt.md").write_text('---\ndescription: "F."\n---\n\nBody.\n')
    dest = repo / claude.CLAUDE_COMMANDS_DIR / "fix.md"
    dest.parent.mkdir(parents=True)
    dest.write_text("mine\n")
    claude.port_commands()
    assert dest.read_text() == "mine\n"
