"""Tests for YAML frontmatter parsing and Pydantic-modelled rendering."""

from __future__ import annotations

import pytest
import yaml
from pydantic import ValidationError

from tara import frontmatter
from tara.frontmatter import Frontmatter

# ── parse ─────────────────────────────────────────────────────────────────────


def test_parse_scalars():
    fm, body = frontmatter.parse(
        '---\nname: demo\ndescription: "Use when testing."\n---\n\n# Demo\nbody\n'
    )
    assert fm["name"] == "demo"
    assert fm["description"] == "Use when testing."
    assert body.startswith("# Demo")


def test_parse_without_frontmatter_returns_original_text():
    fm, body = frontmatter.parse("# No frontmatter\nbody\n")
    assert fm == {}
    assert "No frontmatter" in body


def test_parse_unterminated_frontmatter_returns_original_text():
    fm, body = frontmatter.parse("---\nname: demo\nbody without a closing fence\n")
    assert fm == {}
    assert "body without a closing fence" in body


def test_parse_invalid_yaml_returns_empty():
    fm, _ = frontmatter.parse("---\nname: [unclosed\n---\n\nbody\n")
    assert fm == {}


def test_parse_non_mapping_returns_empty():
    fm, _ = frontmatter.parse("---\n- just\n- a list\n---\n\nbody\n")
    assert fm == {}


def test_parse_folded_block_scalar():
    text = (
        "---\n"
        "name: query\n"
        "description: >\n"
        "  Run SQL queries against DuckDB.\n"
        "  Accepts raw SQL or questions.\n"
        "argument-hint: <SQL>\n"
        "---\n\nbody\n"
    )
    fm, _ = frontmatter.parse(text)
    assert fm["name"] == "query"
    assert fm["description"] == (
        "Run SQL queries against DuckDB. Accepts raw SQL or questions.\n"
    )
    assert fm["argument-hint"] == "<SQL>"


def test_parse_literal_block_scalar():
    text = "---\ndescription: |\n  line one\n  line two\n---\n\nbody\n"
    fm, _ = frontmatter.parse(text)
    assert fm["description"] == "line one\nline two\n"


def test_parse_keeps_native_yaml_types():
    fm, _ = frontmatter.parse("---\ntools: [read, search]\n---\n\nbody\n")
    assert fm["tools"] == ["read", "search"]


def test_parse_keeps_nested_structures():
    text = "---\nreferences:\n  - dagster-core\n  - cli-patterns\n---\n\nbody\n"
    fm, _ = frontmatter.parse(text)
    assert fm["references"] == ["dagster-core", "cli-patterns"]


# ── text_of / tokens ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, ""),
        ("  spaced  ", "spaced"),
        (1.0, "1.0"),
        (["a", "b"], "a, b"),
    ],
)
def test_text_of_coerces(value, expected):
    assert frontmatter.text_of(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, []),
        (["Read", "Search"], ["read", "search"]),
        ("read, search", ["read", "search"]),
        ("[read search]", ["read", "search"]),
        ("", []),
    ],
)
def test_tokens_accepts_lists_and_strings(value, expected):
    assert frontmatter.tokens(value) == expected


# ── render ────────────────────────────────────────────────────────────────────


class _Sample(Frontmatter):
    """Frontmatter model used by the render tests."""

    name: str
    description: str | None = None


def test_render_round_trips_through_yaml():
    text = _Sample(name="demo", description="Use when testing.").render("Body.")
    fm, body = frontmatter.parse(text)
    assert fm == {"name": "demo", "description": "Use when testing."}
    assert body == "Body."


def test_render_omits_unset_fields():
    assert "description" not in _Sample(name="demo").render("Body.")


def test_render_quotes_values_that_need_it():
    tricky = 'He said "yes": maybe #1'
    text = _Sample(name="demo", description=tricky).render("Body.")
    assert frontmatter.parse(text)[0]["description"] == tricky


def test_render_keeps_long_descriptions_on_one_line():
    long = "Use when " + "x" * 400
    text = _Sample(name="demo", description=long).render("Body.")
    block = text.split("---")[1]
    assert len(block.strip().splitlines()) == 2  # name + description, unwrapped
    assert frontmatter.parse(text)[0]["description"] == long


def test_render_emits_valid_yaml_for_unicode():
    text = _Sample(name="demo", description="↑↓ move · space toggle").render("Body.")
    assert yaml.safe_load(text.split("---")[1])["description"] == (
        "↑↓ move · space toggle"
    )


def test_model_rejects_unknown_keys():
    with pytest.raises(ValidationError):
        _Sample.model_validate({"name": "demo", "bogus": "nope"})
