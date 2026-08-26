"""Tests for the deterministic guardrail auditor."""

from __future__ import annotations

from tara import audit


def _write_skill(repo, name, text):
    folder = repo / ".github" / "skills" / name
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(text)
    return folder / "SKILL.md"


def test_audit_good_skill_is_clean(repo):
    path = _write_skill(
        repo,
        "demo",
        "---\n"
        "name: demo\n"
        'description: "A demo skill. Use when testing tara auditing behaviour."\n'
        "---\n\n"
        "# Demo\n\n" + ("usable instruction content. " * 10) + "\n",
    )
    findings = audit.audit_skill(path)
    assert findings == []


def test_audit_bad_skill_flags_name_and_description(repo):
    path = _write_skill(
        repo,
        "demo",
        "---\nname: wrong\n---\n\nshort\n",
    )
    findings = audit.audit_skill(path)
    levels = {f.level for f in findings}
    messages = " ".join(f.message for f in findings)
    assert audit.ERROR in levels
    assert "name" in messages
    assert "description" in messages


def test_audit_imperative_description_is_clean(repo):
    path = _write_skill(
        repo,
        "convert-file",
        "---\n"
        "name: convert-file\n"
        "description: >\n"
        "  Convert between CSV, JSON, Parquet, and other tabular formats.\n"
        "---\n\n"
        "# Convert\n\n" + ("usable instruction content. " * 10) + "\n",
    )
    findings = audit.audit_skill(path)
    assert all("when" not in f.message for f in findings)
    assert findings == []


def test_has_trigger_accepts_imperative_and_phrases():
    assert audit._has_trigger("Run SQL queries against DuckDB.")
    assert audit._has_trigger("ALWAYS use before data pipeline tasks.")
    assert audit._has_trigger("Use when writing modern Python.")
    assert not audit._has_trigger("A grab bag of miscellaneous helpers.")


def test_audit_non_trigger_description_warns(repo):
    path = _write_skill(
        repo,
        "demo",
        "---\n"
        "name: demo\n"
        'description: "A grab bag of miscellaneous helpers for the repo."\n'
        "---\n\n"
        "# Demo\n\n" + ("usable instruction content. " * 10) + "\n",
    )
    findings = audit.audit_skill(path)
    assert any("when" in f.message for f in findings)


def test_audit_all_discovers_and_returns_findings(repo):
    _write_skill(repo, "demo", "---\nname: wrong\n---\n\nx\n")
    findings = audit.audit_all()
    assert any(f.level == audit.ERROR for f in findings)


def _write_mcp(repo, servers, name=".mcp.json"):
    import json

    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"mcpServers": servers}))
    return path


def test_has_version_pin_recognises_pinned_specs():
    assert audit._has_version_pin("mcp-server-git@2026.6.16")
    assert audit._has_version_pin("@likec4/mcp@1.58.0")
    assert audit._has_version_pin("some-pkg==1.2.3")
    assert audit._has_version_pin("git+https://example.com/pkg.git")
    assert not audit._has_version_pin("mcp-server-git")
    assert not audit._has_version_pin("@likec4/mcp")
    assert not audit._has_version_pin("")


def test_runner_package_finds_positional_and_flag_forms():
    assert audit._runner_package(["mcp-server-git"]) == "mcp-server-git"
    assert audit._runner_package(["-y", "@likec4/mcp"]) == "@likec4/mcp"
    assert audit._runner_package(["--from", "pkg==1.0", "tool"]) == "pkg==1.0"
    assert audit._runner_package(["-p=pkg@1.0", "cmd"]) == "pkg@1.0"
    assert audit._runner_package(["--only-flags"]) is None


def test_audit_mcp_flags_unpinned_runner(repo):
    path = _write_mcp(repo, {"git": {"command": "uvx", "args": ["mcp-server-git"]}})
    findings = audit.audit_mcp_config(path)
    assert len(findings) == 1
    assert findings[0].level == audit.WARNING
    assert "unpinned" in findings[0].message
    assert "git" in findings[0].message


def test_audit_mcp_pinned_runner_is_clean(repo):
    path = _write_mcp(
        repo,
        {
            "git": {"command": "uvx", "args": ["mcp-server-git@2026.6.16"]},
            "likec4": {"command": "npx", "args": ["-y", "@likec4/mcp@1.58.0"]},
        },
    )
    assert audit.audit_mcp_config(path) == []


def test_audit_mcp_ignores_remote_http_servers(repo):
    path = _write_mcp(
        repo, {"github": {"type": "http", "url": "https://example.com/mcp/"}}
    )
    assert audit.audit_mcp_config(path) == []


def test_audit_mcp_invalid_json_is_error(repo):
    path = repo / ".mcp.json"
    path.write_text("{ not json")
    findings = audit.audit_mcp_config(path)
    assert findings and findings[0].level == audit.ERROR


def test_audit_all_flags_unpinned_local_mcp_override(repo):
    _write_mcp(
        repo,
        {"git": {"command": "uvx", "args": ["mcp-server-git"]}},
        name=".tara/mcp.local.json",
    )
    findings = audit.audit_all()
    assert any("unpinned" in f.message for f in findings)


def test_mcp_config_paths_lists_existing(repo):
    assert audit.mcp_config_paths() == []
    _write_mcp(repo, {})
    assert audit.mcp_config_paths() == [repo / ".mcp.json"]


def test_format_findings_includes_level(repo):
    path = _write_skill(repo, "demo", "---\nname: wrong\n---\n\nx\n")
    lines = audit.format_findings(audit.audit_skill(path))
    assert any("[error]" in line for line in lines)
