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
