"""Tests for the .agents/ agent doc store scaffolding."""

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


def test_store_is_tracked_by_default(repo):
    agent_docs.write_agent_docs(dry_run=False)
    assert not (repo / ".gitignore").exists()


def test_gitignore_list_ignores_only_listed_subfolders(repo):
    agent_docs.write_agent_docs(dry_run=False, gitignore=["memory"])
    gi = (repo / agent_docs.GITIGNORE).read_text()
    assert ".agents/memory/" in gi
    assert ".agents/plan/" not in gi
    assert agent_docs._MARKER in gi


def test_gitignore_list_appends_to_existing_gitignore(repo):
    (repo / ".gitignore").write_text("__pycache__/\n")
    agent_docs.write_agent_docs(dry_run=False, gitignore=["memory"])
    gi = (repo / ".gitignore").read_text()
    assert "__pycache__/" in gi  # preserved
    assert ".agents/memory/" in gi  # appended


def test_gitignore_list_is_idempotent(repo):
    agent_docs.write_agent_docs(dry_run=False, gitignore=["memory"])
    agent_docs.write_agent_docs(dry_run=False, gitignore=["memory"])
    gi = (repo / ".gitignore").read_text()
    assert gi.count(".agents/memory/") == 1
    assert gi.count(agent_docs._MARKER) == 1


def test_empty_gitignore_list_tracks_everything(repo):
    agent_docs.write_agent_docs(dry_run=False, gitignore=[])
    assert not (repo / ".gitignore").exists()


def test_dry_run_writes_nothing(repo):
    out = agent_docs.write_agent_docs(dry_run=True, gitignore=["memory"])
    assert "[dry-run]" in out
    assert not (repo / agent_docs.DOC_STORE).exists()
    assert not (repo / ".gitignore").exists()
