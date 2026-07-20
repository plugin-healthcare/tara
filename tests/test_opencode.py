"""Tests for the opencode port: MCP translation, agent/prompt/skill porting."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tara import core, opencode

# ── MCP schema translation ────────────────────────────────────────────────────


def test_to_opencode_mcp_translates_stdio_server():
    servers = {"git": {"command": "uvx", "args": ["mcp-server-git@1.0"]}}
    out = core.to_opencode_mcp(servers)
    assert out["git"] == {
        "type": "local",
        "command": ["uvx", "mcp-server-git@1.0"],
        "enabled": True,
    }


def test_to_opencode_mcp_translates_remote_server():
    servers = {"polars": {"type": "http", "url": "https://mcp.pola.rs/mcp"}}
    out = core.to_opencode_mcp(servers)
    assert out["polars"] == {
        "type": "remote",
        "url": "https://mcp.pola.rs/mcp",
        "enabled": True,
    }


def test_to_opencode_mcp_carries_env_and_headers():
    servers = {
        "local": {"command": "run", "args": [], "env": {"A": "1"}},
        "remote": {"url": "https://x", "headers": {"Authorization": "t"}},
    }
    out = core.to_opencode_mcp(servers)
    assert out["local"]["environment"] == {"A": "1"}
    assert out["remote"]["headers"] == {"Authorization": "t"}


# ── tool validation ───────────────────────────────────────────────────────────


def test_validate_tool_accepts_known():
    assert core.validate_tool("copilot") == "copilot"
    assert core.validate_tool("opencode") == "opencode"
    assert core.validate_tool("all") == "all"


def test_validate_tool_rejects_unknown():
    with pytest.raises(ValueError):
        core.validate_tool("nope")


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


def test_translate_agent_strips_copilot_frontmatter(tmp_path):
    result = opencode.translate_agent(_make_agent(tmp_path, "yoda"))
    assert "user-invocable" not in result
    assert "tools:" not in result


def test_translate_agent_sets_mode_subagent(tmp_path):
    result = opencode.translate_agent(_make_agent(tmp_path, "yoda"))
    assert "mode: subagent" in result


def test_translate_agent_uses_singular_permission_key(tmp_path):
    result = opencode.translate_agent(_make_agent(tmp_path, "yoda"))
    assert "permission:" in result
    assert "permissions:" not in result


def test_translate_agent_denies_edit_and_bash_for_read_only(tmp_path):
    result = opencode.translate_agent(
        _make_agent(tmp_path, "yoda", tools="read, search")
    )
    assert "edit: deny" in result
    assert "bash: deny" in result


def test_translate_agent_allows_edit_when_write_tool_present(tmp_path):
    result = opencode.translate_agent(
        _make_agent(tmp_path, "builder", tools="read, write, search")
    )
    assert "edit: deny" not in result


def test_translate_agent_allows_bash_when_bash_tool_present(tmp_path):
    result = opencode.translate_agent(
        _make_agent(tmp_path, "runner", tools="read, bash")
    )
    assert "bash: deny" not in result


def test_translate_agent_preserves_description_and_body(tmp_path):
    result = opencode.translate_agent(_make_agent(tmp_path, "yoda"))
    assert "The yoda agent." in result
    assert "Body of yoda." in result


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
    result = opencode.translate_prompt(src)
    assert 'description: "Fix lint errors."' in result
    assert "agent:" not in result
    assert "tools:" not in result
    assert "Do the fixing." in result


# ── port_config ───────────────────────────────────────────────────────────────


def test_port_config_writes_schema_and_instructions_reference(repo):
    (repo / ".github").mkdir()
    (repo / core.COPILOT_INSTRUCTIONS).write_text("# instructions\n")
    opencode.port_config()
    data = json.loads((repo / core.OPENCODE_CONFIG).read_text())
    assert data["$schema"] == core.OPENCODE_SCHEMA
    assert data["instructions"] == [".github/copilot-instructions.md"]
    assert "mcp" in data


def test_port_config_omits_instructions_when_absent(repo):
    opencode.port_config()
    data = json.loads((repo / core.OPENCODE_CONFIG).read_text())
    assert data["instructions"] == []


def test_port_config_translates_mcp_from_repo(repo):
    (repo / core.MCP_CONFIG).write_text(
        json.dumps(
            {"mcpServers": {"git": {"command": "uvx", "args": ["mcp-server-git"]}}}
        )
    )
    opencode.port_config()
    data = json.loads((repo / core.OPENCODE_CONFIG).read_text())
    assert data["mcp"]["git"]["type"] == "local"
    assert data["mcp"]["git"]["command"] == ["uvx", "mcp-server-git"]


def test_port_config_dry_run(repo):
    line = opencode.port_config(dry_run=True)
    assert "[dry-run]" in line
    assert not (repo / core.OPENCODE_CONFIG).exists()


# ── port_agents ───────────────────────────────────────────────────────────────


def test_port_agents_no_agents_returns_empty(repo):
    assert opencode.port_agents() == []


def test_port_agents_translates_installed_agents(repo):
    agents_dir = repo / opencode.COPILOT_AGENTS_DIR
    agents_dir.mkdir(parents=True)
    _make_agent(agents_dir, "yoda")
    lines = opencode.port_agents()
    assert len(lines) == 1
    dest = repo / opencode.OPENCODE_AGENTS_DIR / "yoda.md"
    assert dest.is_file()
    content = dest.read_text()
    assert "mode: subagent" in content
    assert "Body of yoda." in content


def test_port_agents_dry_run(repo):
    agents_dir = repo / opencode.COPILOT_AGENTS_DIR
    agents_dir.mkdir(parents=True)
    _make_agent(agents_dir, "yoda")
    lines = opencode.port_agents(dry_run=True)
    assert "[dry-run]" in lines[0]
    assert not (repo / opencode.OPENCODE_AGENTS_DIR / "yoda.md").exists()


# ── port_commands ─────────────────────────────────────────────────────────────


def test_port_commands_translates_prompts_preserving_nesting(repo):
    prompts = repo / opencode.COPILOT_PROMPTS_DIR / "python"
    prompts.mkdir(parents=True)
    (prompts / "add-types.prompt.md").write_text(
        '---\ndescription: "Add types."\nagent: agent\n---\n\nAdd types.\n'
    )
    opencode.port_commands()
    dest = repo / opencode.OPENCODE_COMMANDS_DIR / "python" / "add-types.md"
    assert dest.is_file()
    assert "Add types." in dest.read_text()


def test_port_commands_writes_starter_when_absent(repo):
    lines = opencode.port_commands()
    assert any("check.md" in line for line in lines)
    assert (repo / opencode.OPENCODE_COMMANDS_DIR / "check.md").is_file()


def test_port_commands_prompt_supersedes_starter(repo):
    prompts = repo / opencode.COPILOT_PROMPTS_DIR
    prompts.mkdir(parents=True)
    (prompts / "review.prompt.md").write_text(
        '---\ndescription: "My review."\n---\n\nReview it.\n'
    )
    opencode.port_commands()
    review = repo / opencode.OPENCODE_COMMANDS_DIR / "review.md"
    assert "Review it." in review.read_text()


def test_port_commands_skips_existing_starter(repo):
    cmd_dir = repo / opencode.OPENCODE_COMMANDS_DIR
    cmd_dir.mkdir(parents=True)
    (cmd_dir / "check.md").write_text("custom content\n")
    opencode.port_commands()
    assert (cmd_dir / "check.md").read_text() == "custom content\n"


def test_port_commands_dry_run(repo):
    lines = opencode.port_commands(dry_run=True)
    assert all("[dry-run]" in line for line in lines)
    assert not (repo / opencode.OPENCODE_COMMANDS_DIR / "check.md").exists()


# ── port_skills ───────────────────────────────────────────────────────────────


def _make_skill(directory: Path, name: str) -> None:
    skill = directory / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: The {name} skill.\n---\nBody.\n"
    )


def test_port_skills_mirrors_source(repo):
    _make_skill(repo / opencode.COPILOT_SKILLS_DIR, "demo")
    opencode.port_skills()
    assert (repo / opencode.OPENCODE_SKILLS_DIR / "demo" / "SKILL.md").is_file()


def test_port_skills_prunes_stale(repo):
    _make_skill(repo / opencode.OPENCODE_SKILLS_DIR, "gone")
    opencode.port_skills()
    assert not (repo / opencode.OPENCODE_SKILLS_DIR / "gone").exists()


def test_port_skills_dry_run(repo):
    _make_skill(repo / opencode.COPILOT_SKILLS_DIR, "demo")
    lines = opencode.port_skills(dry_run=True)
    assert any("[dry-run]" in line for line in lines)
    assert not (repo / opencode.OPENCODE_SKILLS_DIR / "demo").exists()


# ── port_all ──────────────────────────────────────────────────────────────────


def test_port_all_returns_all_sections(repo):
    sections = dict(opencode.port_all())
    assert set(sections) == {"Config", "Agents", "Commands", "Skills"}
    assert (repo / core.OPENCODE_CONFIG).is_file()
