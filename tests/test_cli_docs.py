"""docs/cli.md must stay in sync with the Typer app."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from gen_cli_docs import render  # noqa: E402


def test_cli_docs_in_sync():
    committed = (Path(__file__).resolve().parent.parent / "docs" / "cli.md").read_text()
    assert committed == render(), (
        "docs/cli.md is stale. Run: uv run python scripts/gen_cli_docs.py"
    )
