---
name: managing-epics-roadmap
description: "Build and maintain a product roadmap as initiatives and functional epics in one markdown source document, review changes through proposal documents, and publish them to GitHub issues and a project board with a script. Use when: creating or restructuring the epics/initiatives of a repo, splitting an epic or app into its own initiative, remapping epic codes, syncing the epics document to GitHub, or setting issue types and board fields in bulk."
---

# Epics roadmap: document first, then board

One markdown document is the source of truth for all initiatives and epics.
GitHub issues are generated from it.
Never hand-edit issue bodies on GitHub; change the document and republish.

## Structure

- Initiative: a group of epics for one component or application. One `##` section in the document.
- Epic: a functional component or goal the product owner understands. One `###` heading with a code, for example `### C3 Alle data loopt via de datacatalogus`.
- Story: a technical issue under an epic. Only titles in the epic's Scope; created later.
- Codes: a short prefix per initiative plus a number (`C`, `D`, `AN`, `PH`). Codes are unique across the document. A prefix never collides with a word used in prose.
- Split an application into its own initiative once it has more than one functional goal. Its epics get the application's product on the board.
- Keep work that is not started yet as one epic in an existing initiative, and record when it is split.

## Source document

Location: `.agents/plan/YYYYMMDDHHMM_epics-<repo>.md`. Layout:

```markdown
# Epics <repo>

## Uitgangspunten
- Design rules that every epic follows.
| Sectie | Epics | Waar het over gaat |

## <Initiative name>
Intro paragraph. Becomes the initiative body.

### <CODE> <Functional title>
#### Omschrijving
Als <actor> wil ik <capability>, zodat <benefit>.
Na afronding van deze epic <what works>.
Stand van zaken: <current state>.
#### Scope
Wel:
- Spike: <decision to make> (first item when no ADR exists)
- <story title>
Niet:
- <excluded item> (<CODE of the epic that owns it>)
#### Requirements
- <testable requirement>
#### Relatie met andere epics
- Besluit: <ADR or "geen ADR, de eerste story is een spike">.
- Vereist <CODES>.
- Bestaand werk: #<n>.

## Werkt al, controleren      (not published)
## Features per epic          (feature -> CODE table)
## Bestaande epics op GitHub  (old epic -> what happened)
## Open punten
```

Rules:

- One sentence per line. The script reflows paragraphs for GitHub.
- Every `Niet` item names the epic that owns it. Every dependency is a code.
- Every feature from the source docs (ADRs, feature lists, old issues) appears in the "Features per epic" table. A missing row is a gap.
- Every existing issue that is replaced appears in "Bestaande epics op GitHub".

## Change workflow

1. Gather sources: ADRs, design docs, architecture, existing issues (`gh issue list`), and the user's brain dump. Read them before proposing anything.
2. Write a proposal: `.agents/plan/YYYYMMDDHHMM_<topic>-voorstel.md`. Include new or changed epic texts, a table of existing issues (now / becomes), reference remapping, and open questions. Add a row to `.agents/plan/index.md`.
3. Stop. The user reviews the proposal by hand. Ask decisions with `ask_user`. Record each decision as `Besluit:` in the proposal.
4. Consistency sweep before publishing: every dependency exists, no scope item is owned by two epics, every `Niet` points to an owner, requirements do not contradict across epics, and no feature lacks an epic.
5. Apply to the source document with a Python script that asserts each old string occurs exactly once before replacing. Afterwards grep for leftover old codes; the result must be empty.
6. Publish (see below). Verify on GitHub.
7. Update the proposal status line, `.agents/plan/index.md` (counts and issue range) and a hand-off note in `.agents/memory/`. Never commit.

## Publish

Script: `.github/skills/managing-epics-roadmap/scripts/publish_epics.py`.
Config: copy `scripts/epics-config.example.json` next to the source document or into the session folder. State is written to `<config>.state.json` (code -> issue number). Keep the state outside git if the repo is public.

Discover IDs once and put them in the config:

```bash
gh project list --owner <org> --format json
gh project field-list <number> --owner <org> --format json   # field and option IDs
gh api graphql -f query='{organization(login:"<org>"){issueTypes(first:20){nodes{id name}}}}'
```

Commands:

```bash
S=.github/skills/managing-epics-roadmap/scripts/publish_epics.py
python $S cfg.json preview "<section>"   # check titles and bodies, no writes
python $S cfg.json create "<section>"... # idempotent: creates missing initiative/epics, sets type and fields, links sub-issues
python $S cfg.json relink                # rewrite all epic bodies, codes become #numbers
python $S cfg.json initiatives           # rewrite all initiative bodies
```

- Always run `preview` before `create`.
- Run `relink` and `initiatives` after every create or document change, because cross-references change.
- Per-section board fields (for example Product) go in `sections.<name>.fields` and override `default_fields`.
- Issue type (Initiative, Epic, Story) uses the organisation issue type, set with `updateIssueIssueType`. Do not use a project field for the level.

## Restructuring existing issues

Reuse issues instead of closing and recreating them, so links and history stay intact.

| Change | How |
|:---|:---|
| Rename | `gh issue edit <n> --title "..."` |
| Epic becomes initiative | Change type with `updateIssueIssueType`, set the product, then `gh sub-issue remove <old-parent> --sub-issue-number <n>` |
| Move under another parent | `gh sub-issue add <parent> --sub-issue-number <n> --replace-parent` |
| Order sub-issues | GraphQL `reprioritizeSubIssue(input:{issueId, subIssueId, afterId})` |
| New code for an existing issue | Edit the state file: remove the old code and its `LINK:` key, add the new code with the same number |
| Rename an initiative section | Edit the state file: rename the `INIT:<name>` key |

Before changing an issue, read its current type, parent, status and product with GraphQL, so nothing is overwritten unintentionally.

## Writing rules

- Functional titles, no tech jargon in the title. Technology goes in Scope and Requirements.
- Full, moderate-length sentences. No em dashes.
- A list is always a markdown list with bullets.
- Never link with `Closes #n`; link issues via the project's Development field.
- Ask the product owner open questions as a comment on the epic, tagging the owners.
