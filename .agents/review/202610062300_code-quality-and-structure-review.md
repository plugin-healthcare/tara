# Code quality and package structure review

Review of `src/tara/` on `feat/claude-code-support` at `65102c1`, covering cleanliness, structure, the split between content and library, and package readiness.
It does not repeat the bug findings in `202610062245_pr-17-branch-review.md`.
Line numbers marked `~` are within a few lines.

The design idea is sound: Copilot's `.github/` is the source and the other tools' files are generated from it.
The package that carries it is a pile of modules that all reach into the current directory and each have their own writer, parser and error type.
None of this blocks 2.0.0 except the contract and error-handling items flagged "pre-2.0". The restructure is 2.x work.

I read every module in `src/tara/`, the pyproject, the bundled standards and the existing bug review.
I did not read the test bodies.
Nothing below repeats the bug review.
Line numbers marked `~` are within a few lines.


## 1.
Cleanliness and simplicity

**C1.
No exception hierarchy, so errors either escape as tracebacks or get swallowed.** High, pre-2.0.
- **Evidence:**
  - Four unrelated base classes: `ConfigError(Exception)` at `config.py:23`, `HookError(Exception)` at `hooks.py:27`, `SkillError(RuntimeError)` at `skills.py:33`, `ReviewUnavailable(RuntimeError)` at `review.py:17`.
  - Built-in exceptions used as domain errors: `ValueError` from `agent_docs._relpath`, `core.normalize_integrations` and `catalog.install_item`, and `FileNotFoundError` at `check.py:~57`.
- **What escapes as a traceback:**
  - `add` calls `TaraConfig.load()` directly at `cli.py:423` and skips `_load_config`.
  - `tara standards` and `init` reach `StandardsConfig.load()` (`standards.py:37, 55, 135`) unguarded.
  - The `rebuild` loop at `cli.py:~1288` goes through `catalog.rebuild_item` to `hooks.install`, which raises an uncaught `HookError`.
    A malformed `.claude/settings.json` also crashes rebuild discovery through `installed_items` and `hooks.is_installed`.
- **What gets swallowed:** `except Exception` at `cli.py:213` and `cli.py:515` turns an `AttributeError` in your own code into a one-line "warning".
- **Fix:**
  - Add `errors.py` with `class TaraError(Exception)` and make the existing classes subclass it.
    Keep them re-exported from their current modules.
  - Add `def main(): try: app() except TaraError as e: echo(f"error: {e}", err=True); sys.exit(1)` and point `[project.scripts]` at `tara.cli:main`.
    The CLI surface does not change.
  - Replace both `except Exception` with `except TaraError`.

**C2.
`audit --deep` ignores the review's exit code.** Medium, pre-2.0.
`cli.py:922` calls `review_mod.deep_review(targets)` and throws away the return code, so a failed Copilot run exits 0.
Fix: `if review_mod.deep_review(targets) != 0: raise typer.Exit(1)`.

**C3.
`claude.py` and `opencode.py` are near-copies.** Medium, 2.x.
- `port_agents` (`claude.py:~236` / `opencode.py:~185`), `port_commands` (`~255` / `~203`), `port_skills`, `remove_all`, `_STARTER_COMMANDS` and the `COPILOT_*_DIR` constants (`claude.py:37-39` / `opencode.py:34-36`) differ only in destination directory, name mapping and translate function.
  That is about 120 duplicated lines.
- Fix: put shared loops in `integrations/_common.py`, for example `port_agents(src, dst, name_fn, translate) -> list[Outcome]`.
  Each integration keeps only its translators and paths.

**C4.
The Copilot tool vocabulary is encoded twice, differently.** Medium, 2.x, but do it before adding a third integration.
- Claude uses `_TOOL_MAP` (`claude.py:57`).
  OpenCode uses `_WRITE_TOOLS` and `_BASH_TOOLS` (`opencode.py:43-48`).
  The `"*"`/`"all"` handling is reimplemented in each.
- Every new Copilot tool name has to be added in two places with two semantics.
  That is how permission drift happens.
- Fix: one `integrations/tools.py` with `COPILOT_TOOLS: dict[str, frozenset[Capability]]` (read, search, edit, bash, web).
  Each integration then maps capabilities to its own names.

**C5.
Ten write paths with three different dry-run behaviours.** Medium.
The reorder is pre-2.0; the merge is 2.x.
- Writers: `core._write` (`core.py:152`), `generate.write_generated` (`generate.py:~144`), `generate.write_configured` (`generate.py:171`), plus inline writes in `opencode.port_config`, `hooks.install`, `docs.add_llms_sources`, `agent_docs`, `standards.write_precommit`, `cli._scaffold`, and `skills`/`sync` `copytree`.
- `write_generated` and `write_configured` are about 90% identical.
- `write_generated` runs the interactive takeover prompt before it checks `dry_run` (`generate.py:160-164`), and so does `mirror_skills` (`generate.py:~269-276`).
  A user who runs `--dry-run` gets asked "Overwrite?", answers yes, and nothing happens.
- Pre-2.0 fix: move the `if dry_run` return above the confirm in both places.
- 2.x fix: one `fs.write_text(dest, text, *, owned: Callable[[Path], bool], dry_run, force, confirm) -> Outcome`.

**C6.
The same files are parsed in many places, with different rules.** Medium.
The two small fixes are pre-2.0; the rest is 2.x.
- **`.mcp.json`** is read in 5 places:
  - `core._load_servers` (`core.py:114`)
  - `catalog._installed_mcp_names` (`catalog.py:373`)
  - `docs.read_mcp` (`docs.py:~92`)
  - `cli.py:1117-1129`
  - `cli.py:1183-1189`

  Three of them accept the VS Code `servers` key and two do not.
  `core._load_servers` has no error handling, so a malformed `.tara/mcp.local.json` crashes `init` with a `JSONDecodeError`.
- **`data/mcp/catalog.toml`** is read in 3 places: `catalog.py:125`, `cli.py:1146` and `cli.py:1158-1166`.
- **`data/skills/index.toml`** is parsed in 4 functions (`catalog.py:~108`, and `skills.resolve_index`, `read_sets_index` and `indexed_for_packages`).
  One `catalog()` call parses it up to 3 times.
- **pyproject requirements** are parsed twice with different regexes:
  - `sync.direct_deps` (`sync.py:89-128`) pastes the same 5-line block three times and splits on `[~>=<!\[;,\s]`.
  - `standards._requirement_name` splits on `[<>=!~;@\[\s]`.
  - `pkg@git+https://…` with no spaces therefore gives a different name in each module.
- **PEP 503 name normalisation** is implemented twice: `sync.normalize_package_name` (`sync.py:84`) and `skills._normalize` (`skills.py:185`).
- **TOML is hand-written twice:** `config._esc/_fmt/_dump` (`config.py:~170-205`) and `skills._esc` plus `write_manifest` (`skills.py:104-120`).
  `write_manifest` emits `[skills.{name}]` without quoting the key.
  `tara skill add … --name foo.v2` writes a nested table, and every later `read_manifest` dies with `KeyError: 'repo'`.
- **Pre-2.0 fix:** quote the key (`f"[skills.{json.dumps(name)}]"`, since a JSON string is a valid TOML basic string here), and delete `skills._normalize` in favour of the `sync` one.
- **2.x fix:** one module per format with Pydantic models: `.mcp.json`, the catalog TOML files, `.tara/skills.toml`, `.tara/checks.toml` (`check.py:48` does `c["name"]`, which is a `KeyError` on user input), and the lock files.
  Use `packaging.requirements.Requirement` instead of either regex.

**C7.
Domain logic lives in the CLI.** Medium, 2.x.
- `cli.py:1060-1238` (`_same_tree`, `_matches_catalog_source`, `_catalog_mcp_config`, `_mcp_config_is_owned`, `_rebuild_catalog_item`, `_rebuild_manifest`, `_configured_catalog_items`) is about 180 lines of rebuild logic.
  It can only be tested through `CliRunner`.
- `_run_sync` (`cli.py:162-250`) is a 90-line, four-phase service that echoes as it goes.
- `cli.py:1133-1137` redeclares the destinations that `catalog._DEST` (`catalog.py:253`) already defines.
- `rebuild` builds the `.mcp.json` text itself (`cli.py:1272`) instead of calling the same render that `core.write_mcp` (`core.py:168`) uses.
- Fix: move them to `rebuild.py` and a sync service that return structured results.
  The CLI only renders.

**C8.
Artifact kinds are bare strings, switched on in four places.** Medium.
The enum is optional pre-2.0; the handlers are 2.x.
- `CatalogItem.kind: str  # skill | agent | …` (`catalog.py:28`) uses a comment as its type.
- If-chains on `kind` appear in `catalog.install_item`, `rebuild_item`, `installed_items` and `cli._matches_catalog_source`.
- The singular/plural mapping is written three times: `config._ARTIFACT_FIELDS` (`config.py:246`), `cli._ARTIFACT_KINDS` (`cli.py:1060`) and `MENU_KINDS` (`cli.py:130`).
  The literal list of kinds appears again at `cli.py:1205` and `1222`.
- Fix: `class ArtifactKind(StrEnum)` with a `.plural` property, defined once.
  Config keys stay plural, so the schema does not change.

**C9.
Dead code and needless indirection.** Low, pre-2.0.
Each item is trivial.
- `core.port_targets` (`core.py:74`) is unused in `src/`.
  Meanwhile `cli.py` reimplements it inline in `init` and `integrations` instead of using `TaraConfig.port_targets`.
- `core.py:84-85` is an empty "Frontmatter helpers" section header.
- `claude.GENERATED_MARKER = generate.MARKER` (`claude.py:50`) is an alias that adds nothing.
- The lazy `import questionary` in `cli.py:~394, ~525` and the lazy `from tara import frontmatter` in `review.py:23` buy nothing, because `generate.py:24` imports questionary at module load and `cli` imports `generate`.
- The status line from `record_artifacts` is discarded at `cli.py:214` and `518` but echoed at `agent_add`.

**C10.
Library code prints, and text encoding is left to the platform.** Low, pre-2.0 if you support Windows.
- `check._uv_preflight` prints to stderr (`check.py:85, 91`).
  Put the message on the `CheckResult` and let the CLI echo it.
- About half the `read_text()`/`write_text()` calls pass no encoding (for example `core.py:137`, `catalog.py:61`, `claude.translate_agent`, `skills.py:91`); the others pass `utf-8`.
  Bundled content contains `—`, `…` and `→`.
  On Windows with Python 3.12 that gets decoded as cp1252, which garbles the text.
- Fix: add `PLW1514` to ruff `select` and let it list every site.

**C11.
Status reporting is pre-formatted strings with ad hoc verbs.** Low, 2.x.
- Examples: `"  skill   x"`, `"  hooks   would add N to …"`, `"  [dry-run] replace X (confirmation required)"`, and both `"(overwrite requires --force)"` and `"(left untouched)"` for a declined overwrite.
- `sync.SyncResult` is the only structured result.
- Fix: `@dataclass Outcome(action: Literal["wrote","unchanged","skipped","removed",…], path: Path, reason: str | None)`, rendered in one place in the CLI. That makes a "N skipped" summary and a future `--json` free.


## 2.
Structure

**S1.
The problem is wrong boundaries, not the flat layout.** Medium, 2.x.
- Eighteen modules is not too many.
  The problems are:
  - `cli.py` holds domain logic (C7).
  - `core.py` is a junk drawer: paths, the integration list, Copilot writers, MCP merging, and OpenCode's MCP translation (`core.py:172-200`).
  - `generate.py` mixes ownership policy, filesystem operations and interactive prompting through questionary (`generate.py:24, ~113`).
  - Every module reads `repo_root()` (`core.py:93`), which is `Path.cwd()` behind a function call.
    That is a hidden global, and it is why `tests/conftest.py:13` has to `monkeypatch.chdir`.
- The integrations are dispatched through a dict of tuples (`cli.py:308`) that must be kept in sync with `SUPPORTED_INTEGRATIONS` (`core.py:38`) by hand.

**Target layout (2.x):**

```
src/tara/
  __init__.py            docstring only, no re-exports
  __main__.py            from tara.cli import main; main()
  errors.py              TaraError and all subclasses
  layout.py              every repo-relative path, data_path(), Repo(root) context
  config.py              STAYS. Schema + load(path) + dump. No repo_root() inside.
  markdown_lint.py       STAYS AT THIS PATH (public, see P2)
  cli/
    __init__.py          app, main() with the TaraError handler
    options.py           DryRun, ForceOpt, IntegrationsOpt, ...
    render.py            Outcome/Section -> echo
    prompts.py           questionary adapters (checkbox, confirm_takeover UI)
    setup.py             init, rebuild, integrations, sync, hidden aliases
    artifacts.py         add, list, skill *, agent *
    quality.py           check, audit, standards
    scaffold.py          new
  core/                  pure: no typer, no questionary, no cwd
    instructions.py      <- core.assemble_instructions
    mcp.py               <- core merge/load/render, cli MCP ownership helpers
    frontmatter.py       <- frontmatter.py (unchanged content)
    catalog.py           <- catalog discovery, CatalogItem, ArtifactKind
    rebuild.py           <- cli.py:1060-1238
    audit.py  standards.py  check.py  review.py   (decide/compare only)
  fs/
    write.py             unsafe_reason, write_text, copy_tree, remove -> Outcome
    ownership.py         MARKER, generated.json, mirror_skills  <- generate.py
    formats.py           TOML/JSON read+write raising TaraError
  sources/               anything that leaves the process
    git.py               <- skills._git/_clone
    skills.py            <- skills.py manifest/lock/add/update
    library_skills.py    <- sync.py
    llms.py              <- docs.py
    runners.py           uv / copilot subprocess  <- standards._run_uv, check, review
  integrations/
    __init__.py          Integration Protocol, REGISTRY
    _common.py           shared port/remove loops (C3)
    tools.py             Copilot tool -> capability table (C4)
    copilot.py           write_instructions, write_mcp (the source)
    claude.py  claude_hooks.py (<- hooks.py)  opencode.py (+ core.py:172-200)
```

The integration contract replaces `_GENERATORS`:

```python
class Integration(Protocol):
    name: str            # "claude"
    label: str           # "Claude Code"
    def port(self, repo: Repo, opts: WriteOptions) -> list[Section]: ...
    def remove(self, repo: Repo, opts: WriteOptions) -> list[Outcome]: ...

REGISTRY = {i.name: i for i in (Claude(), OpenCode())}
SUPPORTED_INTEGRATIONS = (COPILOT, *REGISTRY)   # one source, can't drift
```

Inject `Repo(root: Path)` and a `Confirm = Callable[[Path, str], bool]` from the CLI. The fs layer never imports questionary, and tests stop calling `chdir`.

**What needs no change:**
- The content of `frontmatter.py`.
- `audit.py`'s rule functions.
- `hooks.merge`.
- `markdown_lint.py` and its path.
- The `config.py` schema.
- The whole `data/` tree.
- `scripts/gen_cli_docs.py`, as long as `tara.cli` still exports `app`.

**How to migrate:**
- Tag 2.0.0 first.
- Then one PR per subpackage, each with `git mv` and only import changes, so the diff is reviewable and blame survives.
- `tests/test_cli_docs.py` already snapshots the whole CLI help, which is your guard against breaking the CLI surface.

**Cheaper alternative if you only get one refactor:** do just the `cli/` package, the `integrations/` package with the Protocol, and a single `fs.py`.
That is most of the value for about a third of the churn.


## 3.
Content, config and library separation

**D1.
Starter commands are hardcoded, duplicated, and partly wrong.** Medium.
The content fix is pre-2.0; moving it to data is 2.x.
- They are defined in `claude.py:114` and `opencode.py:72`.
- The `check` body hardcodes `ruff` plus `pytest`.
  It ignores `.tara/checks.toml` and Tara's own gate, which also runs `ty` and `uv audit` (`check.py:21`).
- The `review` body points the agent at `gilfoyle`, which exists only if the user installed that catalog agent.
- Pre-2.0 fix: make the check body `` !`uv run tara check` `` and make the review body agent-neutral.
- 2.x fix: ship them as `data/catalog/prompts/check.prompt.md` so they go through the normal port path, then delete both `_STARTER_COMMANDS` tables and their special cases.

**D2.
`tara new` content is split between Python and data.** Low, 2.x.
- The prompt and agent scaffolds are inline strings (`cli.py:1003-1020`), while every other kind uses `data/templates`.
- `_TEMPLATE_MAP` (`cli.py:934`) and `_KIND_HELP` (`cli.py:947`) are two tables with the same keys that must be kept in sync.
- Fix: add `data/templates/copilot/{prompt,agent}.md` and one `data/templates/index.toml` with `template`, `dest`, `filename` and `help` per kind.

**D3.
The config option docs repeat the model defaults as string literals.** Low, pre-2.0.
`_OPTION_DOCS` (`config.py:47`) restates the `StandardsConfig` defaults (`config.py:65-71`).
Change one and the commented example lies.
Fix: render the commented example from `StandardsConfig().model_dump()`.

**D4.
Paths and constants are scattered.** Medium, 2.x.
- `.github/{agents,prompts,skills,instructions}` is defined in `claude.py:37-39`, `opencode.py:34-36`, `catalog.py:253-257`, `cli.py:1133-1137`, `audit.py:321-330` and `cli.list_` (`cli.py:~429+`).
- `.tara/*` paths are defined in `config.py:20`, `generate.py:31`, `skills.py:28-29`, `sync.py:36`, `check.py:22`, `core.py:~127, ~140` and `audit.MCP_CONFIGS`.
- The literal `".mcp.json"` appears at `catalog.py:375` even though `core.MCP_CONFIG` exists.
- The default stack `"python"` is hardcoded in `config.py` (twice), `check.py:23` and `cli.py` (StackArg, and `stack or "python"` in `init`).
  As a result `tara check` never reads the configured `stack`.
- Fix: put Copilot and `.tara` paths in `layout.py`.
  Each integration owns its own destination paths.
  The default stack lives in one place.

**D5.
Config is loaded by the code that uses it instead of passed in.** Medium, 2.x.
- `TaraConfig.load()` reads `repo_root()` itself (`config.py:139`).
- `StandardsConfig.load()` re-parses `config.toml` on every call, and `standards.py` calls it three times per report.
  That is three parses plus three unhandled `ConfigError` sites (C1).
- Fix: `TaraConfig.load(path)`.
  The CLI loads once and passes `cfg.standards` and `cfg.stack` down.
- The schema itself is clean.
  Don't touch it.

**D6.
Code is stored as data.** Low, 2.x.
`sync._DISCOVER_SCRIPT` (`sync.py:38`) is about 30 lines of Python in a string, so ruff and ty never see it.
Fix: ship it as `tara/_discover_skills.py` and run `uv run python <path>`.

**D7.
Bundled catalog content has no validity test.** Medium, pre-2.0.
The frontmatter fail-open bug in the other review makes a broken bundled file a security issue.
Make sure a test parses every `data/catalog/**/*.md` with non-empty frontmatter and runs the audit rules over it with zero errors.
I didn't read the test bodies, so check whether one already exists.


## 4.
Package readiness

**P1.
The package metadata is still 1.x.** High, pre-2.0.
- `pyproject.toml:2-4` still has `name = "tara"`, `version = "1.1.0"` and a Copilot-only description.
- `classifiers`, `keywords`, `authors` and `Changelog`/`Documentation` URLs are missing.
- The Typer help at `cli.py:61` has the same stale text.
- The rename to `tara-dev` is a runbook step, and the `--version` lookup bug is in the other review, so neither is repeated here.
  A static version in pyproject read through `importlib.metadata` is the right single source, so keep it.

**P2.
The public surface is undeclared, and part of it is not obvious.** Medium, pre-2.0.
- Your actual contracts are the `tara` CLI, the `.tara/config.toml` schema, and `python -m tara.markdown_lint`.
  That last one is run in users' repos by the bundled standard (`data/standards/python/pre-commit-config.yaml:45`), so its module path is API. Any restructure that moves it breaks every user's pre-commit.
- Fix: state in the README that there is no Python API and every module is internal.
- Do not add `__all__` across internals.
  Do not ship `py.typed`, because it promises a typed API you don't intend to maintain.
- Add config fixture tests: a 1.0 config (`tool = "all"`), a 1.x config (`tools = [...]`) and a 2.0 config must all load to the expected model.

**P3.
Package data inclusion is assumed, not verified.** Medium, pre-2.0.
- `uv_build` includes everything under `src/tara`, so `data/` ships.
  Nothing checks it.
- Fix: a CI job that runs `uv build`, installs the wheel into a clean venv, then runs `tara --version`, `tara init --dry-run` in a temp dir, and `python -m tara.markdown_lint README.md`.
  That one job catches the whole class of bug that the version-name issue belongs to.
- `data_path()` (`core.py:89`) uses `Path(str(resources.files(...)))`.
  That works for installed wheels and breaks for zip imports.
  It's acceptable; just know it.

**P4.
Dependencies are lean but have a cost for users.** Low.
- The four runtime dependencies are all used, and `pyyaml` is justified because YAML frontmatter is mandated.
- Because the bundled pre-commit hook runs `uv run python -m tara.markdown_lint`, Tara must be a dev dependency of every user project. pydantic, typer, questionary and prompt_toolkit then land in their resolver.
  Keep the lower bounds only and add nothing new without a reason.
- `packaging`, for C6, is the one addition worth making.
- questionary is imported eagerly through `generate.py:24`, so even `tara check` in CI loads prompt_toolkit.
  Fix: one lazy import in `cli/prompts.py`.

**P5.
Tests mirror the modules, with two gaps.** Low, 2.x.
- The test files mirror the modules 1:1, except that `docs.py` and `review.py` have no tests.
- `docs.py` calls `urllib.request.urlopen` directly with nothing injected, so it can't be tested as written.
  Inject a fetcher.
- `review.build_prompt` is pure and takes three lines to test.
- After the restructure, mirror `tests/` to the new tree and drop the `chdir` fixture in favour of passing `Repo(tmp_path)`.

**P6.
`__init__.py` is fine.** It is a docstring only.
Keep it that way.


## What is fine

- `frontmatter.Frontmatter` with `extra="forbid"` and `yaml.safe_dump` is the right way to write agent files.
  Leave the design alone; the parse side's fail-open behaviour is the other review's finding.
- `hooks.merge` is pure, append-only, returns a count and makes no I/O decisions.
  It is what the rest of the package should look like.
- `audit.py` and `markdown_lint.find_violations` are pure rule functions behind thin I/O.
- `config.py`: the models, `_explain` and the legacy key migration are clean.
- `sync.SyncResult` is the only structured result in the package.
  Copy it everywhere (C11).
- `scripts/gen_cli_docs.py` plus `test_cli_docs.py` amount to a CLI-surface snapshot test.
  It's the most useful guard you have for the "don't break the CLI" requirement.
- Generating Claude commands that `@`-import the Copilot prompts instead of copying them is the right call.


## Prioritised actions

**Before 2.0.0:**
1. Add `errors.py` with `TaraError` and a `main()` handler.
   Route `add`, `standards` and the hook installs in `rebuild` through it, and replace both `except Exception` (C1).
2. Propagate the `deep_review` exit code (C2).
3. Update the pyproject metadata, and add the clean-venv wheel smoke test (P1, P3).
4. Declare the public surface: the CLI, the config schema and `python -m tara.markdown_lint`.
   Add the 1.0, 1.x and 2.0 config fixture tests (P2).
5. Fix the starter command content and add the bundled-catalog validity test (D1, D7).
6. One-line fixes: quote the skill manifest TOML key, move the dry-run return above the prompts, delete dead code.
   Enable `PLW1514` if Windows is supported (C6, C5, C9, C10).

**2.x:**

7. Move rebuild and sync orchestration out of `cli.py` into library modules that return `Outcome`s, then split `cli/` (C7, C11).
8. Create the `integrations/` package with the `Integration` Protocol, shared port loops and one tool-capability table (C3, C4, S1).
9. Use one `fs` write path, inject `Repo` and `Confirm`, and remove the `repo_root()` global (C5, S1, D4, D5).
10. Use one parser per file format with Pydantic models and an `ArtifactKind` enum (C6, C8).
