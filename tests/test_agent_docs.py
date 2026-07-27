"""Tests for the .agent/ agent doc store scaffolding."""

from __future__ import annotations

from tara import agent_docs


def test_write_agent_docs_creates_typed_folders_with_index(repo):
    out = agent_docs.write_agent_docs(dry_run=False)

    for name, _ in agent_docs.FOLDERS:
        index = repo / agent_docs.DOC_STORE / name / "index.md"
        assert index.is_file()
        assert f"{name}/index.md" in out

    memory_index = (repo / agent_docs.DOC_STORE / "memory" / "index.md").read_text()
    assert agent_docs.FILENAME in memory_index
    assert "| Date | File | Summary |" in memory_index


def test_write_agent_docs_gitignores_the_store(repo):
    agent_docs.write_agent_docs(dry_run=False)
    gi = (repo / agent_docs.GITIGNORE).read_text()
    assert ".agent/" in gi
    assert agent_docs._MARKER in gi


def test_write_agent_docs_appends_to_existing_gitignore(repo):
    (repo / ".gitignore").write_text("__pycache__/\n")
    agent_docs.write_agent_docs(dry_run=False)
    gi = (repo / ".gitignore").read_text()
    assert "__pycache__/" in gi  # preserved
    assert ".agent/" in gi  # appended


def test_write_agent_docs_is_idempotent(repo):
    agent_docs.write_agent_docs(dry_run=False)
    agent_docs.write_agent_docs(dry_run=False)
    gi = (repo / ".gitignore").read_text()
    assert gi.count(agent_docs._MARKER) == 1


def test_dry_run_writes_nothing(repo):
    out = agent_docs.write_agent_docs(dry_run=True)
    assert "[dry-run]" in out
    assert not (repo / agent_docs.DOC_STORE).exists()
    assert not (repo / ".gitignore").exists()
