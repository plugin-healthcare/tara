"""Tests for installing bundled Claude Code hooks into .claude/settings.json."""

from __future__ import annotations

import json

import pytest

from tara import catalog, hooks

BUNDLE = {
    "description": "Demo bundle.",
    "hooks": {
        "PostToolUse": [
            {
                "matcher": "Write|Edit",
                "hooks": [{"type": "command", "command": "demo-check"}],
            }
        ]
    },
}


def _settings(repo) -> dict:
    return json.loads((repo / hooks.SETTINGS).read_text())


def test_bundle_names_include_prose_style():
    assert "prose-style" in hooks.bundle_names()


def test_read_bundle_unknown_name_raises():
    # GIVEN a name no bundle uses / WHEN read / THEN it fails loudly
    with pytest.raises(hooks.HookError):
        hooks.read_bundle("does-not-exist")


def test_install_writes_settings(repo):
    line = hooks.install("prose-style")

    data = _settings(repo)
    assert [entry["matcher"] for entry in data["hooks"]["PostToolUse"]] == [
        "Write|Edit"
    ]
    assert "prose-style" in line


def test_install_is_idempotent(repo):
    hooks.install("prose-style")
    before = (repo / hooks.SETTINGS).read_text()

    line = hooks.install("prose-style")

    assert (repo / hooks.SETTINGS).read_text() == before
    assert "already" in line


def test_install_keeps_unrelated_settings_and_hooks(repo):
    path = repo / hooks.SETTINGS
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "permissions": {"allow": ["Bash(uv run:*)"]},
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Bash",
                            "hooks": [{"type": "command", "command": "mine"}],
                        }
                    ]
                },
            }
        )
    )

    hooks.install("prose-style")

    data = _settings(repo)
    assert data["permissions"] == {"allow": ["Bash(uv run:*)"]}
    assert data["hooks"]["PreToolUse"][0]["hooks"][0]["command"] == "mine"
    assert data["hooks"]["PostToolUse"]


def test_merge_appends_next_to_a_developer_entry():
    settings = {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "Write|Edit",
                    "hooks": [{"type": "command", "command": "mine"}],
                }
            ]
        }
    }

    merged, added = hooks.merge(settings, BUNDLE)

    # The developer's entry keeps its own hook list; ours is a second entry.
    assert added == 1
    commands = [
        hook["command"]
        for entry in merged["hooks"]["PostToolUse"]
        for hook in entry["hooks"]
    ]
    assert commands == ["mine", "demo-check"]


def test_merge_does_not_deduplicate_across_different_matchers():
    settings = {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [{"type": "command", "command": "demo-check"}],
                }
            ]
        }
    }

    merged, added = hooks.merge(settings, BUNDLE)

    assert added == 1
    assert [entry["matcher"] for entry in merged["hooks"]["PostToolUse"]] == [
        "Bash",
        "Write|Edit",
    ]


def test_merge_appends_only_missing_actions_for_the_same_matcher():
    bundle = {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "Write|Edit",
                    "hooks": [
                        {"type": "command", "command": "demo-check"},
                        {"type": "prompt", "prompt": "review it"},
                    ],
                }
            ]
        }
    }
    settings = {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "Write|Edit",
                    "hooks": [{"type": "command", "command": "demo-check"}],
                }
            ]
        }
    }

    merged, added = hooks.merge(settings, bundle)

    assert added == 1
    entries = merged["hooks"]["PostToolUse"]
    assert entries[1] == {
        "matcher": "Write|Edit",
        "hooks": [{"type": "prompt", "prompt": "review it"}],
    }


def test_merge_does_not_mutate_the_input():
    settings: dict = {"hooks": {}}

    hooks.merge(settings, BUNDLE)

    assert settings == {"hooks": {}}


def test_install_dry_run_writes_nothing(repo):
    line = hooks.install("prose-style", dry_run=True)

    assert not (repo / hooks.SETTINGS).exists()
    assert "would add" in line


def test_install_rejects_broken_settings(repo):
    path = repo / hooks.SETTINGS
    path.parent.mkdir(parents=True)
    path.write_text("{not json")

    with pytest.raises(hooks.HookError):
        hooks.install("prose-style")


def test_install_rejects_a_symlinked_settings_file(repo, tmp_path):
    outside = tmp_path / "outside.json"
    outside.write_text("{}")
    path = repo / hooks.SETTINGS
    path.parent.mkdir(parents=True)
    path.symlink_to(outside)

    with pytest.raises(hooks.HookError, match="symlink"):
        hooks.install("prose-style")

    assert outside.read_text() == "{}"


def test_install_rejects_a_symlinked_settings_directory(repo, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    claude_dir = repo / ".claude"
    claude_dir.symlink_to(outside, target_is_directory=True)

    with pytest.raises(hooks.HookError, match="symlink"):
        hooks.install("prose-style")

    assert not (outside / "settings.json").exists()


def test_catalog_offers_hooks(repo):
    items = catalog.catalog(["hooks"])["hooks"]

    assert [it.name for it in items] == ["prose-style"]
    assert items[0].kind == "hooks"
    assert items[0].description


def test_install_item_installs_hooks(repo):
    item = catalog.catalog(["hooks"])["hooks"][0]

    catalog.install_item(item)

    assert (repo / hooks.SETTINGS).is_file()
