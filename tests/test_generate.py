"""Tests for the ownership rules that keep Tara from overwriting user files."""

from __future__ import annotations

from tara import generate


def test_marked_prefixes_the_body_with_the_marker():
    assert generate.marked("Body.").startswith(generate.MARKER)


def test_is_generated_is_true_for_a_missing_file(repo):
    assert generate.is_generated(repo / "nope.md")


def test_is_generated_is_true_for_marked_output(repo):
    path = repo / "out.md"
    path.write_text(generate.marked("Body."))
    assert generate.is_generated(path)


def test_is_generated_is_false_for_a_hand_written_file(repo):
    path = repo / "out.md"
    path.write_text("mine\n")
    assert not generate.is_generated(path)


def test_is_generated_is_false_for_a_directory(repo):
    (repo / "dir").mkdir()
    assert not generate.is_generated(repo / "dir")


def test_write_generated_requires_force_when_non_interactive(repo):
    path = repo / "out.md"
    path.write_text("mine\n")
    line = generate.write_generated(path, generate.marked("New."), dry_run=False)
    assert path.read_text() == "mine\n"
    assert "requires --force" in line


def test_write_generated_force_overwrites_a_hand_written_file(repo):
    path = repo / "out.md"
    path.write_text("mine\n")
    line = generate.write_generated(
        path, generate.marked("New."), dry_run=False, force=True
    )
    assert "New." in path.read_text()
    assert "wrote" in line


def test_write_generated_never_follows_a_destination_symlink(repo):
    outside = repo.parent / "outside.md"
    path = repo / "out.md"
    path.symlink_to(outside)

    line = generate.write_generated(
        path, generate.marked("New."), dry_run=False, force=True
    )

    assert path.is_symlink()
    assert not outside.exists()
    assert "symlink" in line


def test_confirm_takeover_shows_diff_before_prompt(repo, monkeypatch, capsys):
    path = repo / "out.md"
    path.write_text("old\n")
    monkeypatch.setattr(generate, "_interactive", lambda: True)

    class _Prompt:
        def unsafe_ask(self):
            return False

    monkeypatch.setattr("questionary.confirm", lambda *args, **kwargs: _Prompt())
    generate.write_generated(path, generate.marked("new"), dry_run=False)

    output = capsys.readouterr().out
    assert "--- out.md (current)" in output
    assert "+++ out.md (generated)" in output
    assert "-old" in output
    assert "+new" in output


def test_write_generated_writes_when_absent(repo):
    path = repo / "nested" / "out.md"
    line = generate.write_generated(path, generate.marked("New."), dry_run=False)
    assert "New." in path.read_text()
    assert "wrote" in line


def test_write_generated_dry_run_writes_nothing(repo):
    path = repo / "out.md"
    line = generate.write_generated(path, generate.marked("New."), dry_run=True)
    assert not path.exists()
    assert "[dry-run]" in line


def test_record_and_owned_round_trip(repo):
    generate.record("claude", "skills", {"b", "a"})
    assert generate.owned("claude", "skills") == {"a", "b"}


def test_owned_is_empty_when_the_state_file_is_corrupt(repo):
    path = repo / generate.STATE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{ not json")
    assert generate.owned("claude", "skills") == set()


def test_unmarked_file_is_never_implicitly_adopted(repo):
    path = repo / "out.md"
    path.write_text("old unmarked output\n")
    assert not generate.is_generated(path)


def test_mirror_skills_skips_a_same_named_file(repo):
    source = repo / "source" / "demo"
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text("generated\n")
    destination = repo / "destination"
    destination.mkdir()
    collision = destination / "demo"
    collision.write_text("mine\n")

    lines = generate.mirror_skills("claude", source.parent, destination, dry_run=False)

    assert collision.read_text() == "mine\n"
    assert any("requires --force" in line for line in lines)


# ── containment ───────────────────────────────────────────────────────────────


def _symlinked_dir(repo, tmp_path_factory, name: str):
    """Symlink ``repo/name`` to a directory outside the repository."""
    outside = tmp_path_factory.mktemp("outside")
    link = repo / name
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(outside, target_is_directory=True)
    return outside


def test_unsafe_reason_is_none_for_a_normal_path(repo):
    assert generate.unsafe_reason(repo / ".claude" / "agents" / "x.md") is None


def test_unsafe_reason_reports_a_symlinked_ancestor(repo, tmp_path_factory):
    _symlinked_dir(repo, tmp_path_factory, ".claude")

    reason = generate.unsafe_reason(repo / ".claude" / "agents" / "x.md")

    assert reason is not None
    assert "symlink" in reason
    assert ".claude" in reason


def test_unsafe_reason_reports_a_path_outside_the_repository(repo):
    reason = generate.unsafe_reason(repo / ".." / "elsewhere.md")

    assert reason is not None
    assert "outside" in reason


def test_write_generated_skips_a_symlinked_parent(repo, tmp_path_factory):
    outside = _symlinked_dir(repo, tmp_path_factory, ".claude")

    line = generate.write_generated(
        repo / ".claude" / "agents" / "x.md",
        generate.marked("New."),
        dry_run=False,
        force=True,
    )

    assert "symlink" in line
    assert list(outside.iterdir()) == []


def test_write_configured_skips_a_symlinked_parent(repo, tmp_path_factory):
    outside = _symlinked_dir(repo, tmp_path_factory, ".claude")

    line = generate.write_configured(
        repo / ".claude" / "settings.json", "{}\n", dry_run=False, force=True
    )

    assert "symlink" in line
    assert list(outside.iterdir()) == []


def test_mirror_skills_skips_a_symlinked_destination_parent(repo, tmp_path_factory):
    src = repo / ".github" / "skills" / "demo"
    src.mkdir(parents=True)
    (src / "SKILL.md").write_text("---\nname: demo\n---\n\nBody.\n")
    outside = _symlinked_dir(repo, tmp_path_factory, ".claude")

    lines = generate.mirror_skills(
        "claude", repo / ".github" / "skills", repo / ".claude" / "skills", False
    )

    assert any("symlink" in line for line in lines)
    assert list(outside.iterdir()) == []


def test_remove_generated_markdown_ignores_a_symlinked_parent(repo, tmp_path_factory):
    outside = _symlinked_dir(repo, tmp_path_factory, ".claude")
    (outside / "agents").mkdir()
    victim = outside / "agents" / "x.md"
    victim.write_text(generate.marked("Outside."))

    lines = generate.remove_generated_markdown(repo / ".claude" / "agents", False)

    assert lines == []
    assert victim.is_file()


def test_remove_generated_file_ignores_a_symlinked_parent(repo, tmp_path_factory):
    outside = _symlinked_dir(repo, tmp_path_factory, "docs")
    victim = outside / "x.md"
    victim.write_text(generate.marked("Outside."))

    assert generate.remove_generated_file(repo / "docs" / "x.md", False) is None
    assert victim.is_file()


def test_remove_owned_skills_ignores_a_symlinked_parent(repo, tmp_path_factory):
    generate.record("claude", "skills", ["demo"])
    outside = _symlinked_dir(repo, tmp_path_factory, ".claude")
    (outside / "skills" / "demo").mkdir(parents=True)

    generate.remove_owned_skills("claude", repo / ".claude" / "skills", False)

    assert (outside / "skills" / "demo").is_dir()
