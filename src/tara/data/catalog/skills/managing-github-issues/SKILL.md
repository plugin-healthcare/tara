---
name: managing-github-issues
description: "Use when executing approved GitHub issue or project operations: bulk issue creation, sub-issue links, project item insertion, project field updates, or linking existing work. Do not use to draft or refine epic/story content; use writing-epics-stories for that."
---

# Managing GitHub issues and project boards

The `writing-epics-stories` skill decides what an epic or story says. This skill is the
mechanics of getting that into GitHub: issue creation, parent and child links, and
project board fields, all through the `gh` CLI.

Never hardcode an ID. Project, field, and option IDs differ per project and per repo, so
every run starts with discovery.

Discovery commands may run immediately. Before running `gh issue create`,
`gh sub-issue add`, `gh project item-add`, `gh project item-edit`, `gh label create`, or
installing an extension, show the planned mutations and obtain explicit developer
confirmation. Without confirmation, output the commands and payloads only.

## Prerequisites

- `gh` authenticated (`gh auth status`).
- The sub-issue extension for hierarchy: `gh extension install github/gh-sub-issue`.
- The repo owner and name, and the project number from the project URL.

## Step 0: discover the project metadata

```bash
OWNER="<org-or-user>"

gh project list --owner "$OWNER" --format json | jq '.projects[] | {number, title, id}'
gh project field-list <PROJECT_NUMBER> --owner "$OWNER" --format json \
  | jq '.fields[] | {name, id, type, options}'
```

Save that output for the rest of the session. The project node ID (`PVT_...`), each
field ID (`PVTSSF_...`), and each single-select option ID all appear here.

## Order of operations

Create in dependency order so cross-references can use real issue numbers:

1. Create the epics, and note the number each one gets.
2. Link each epic to its parent initiative:
   `gh sub-issue add <PARENT> --issue-number <EPIC> --repo "$OWNER/$REPO"`.
3. Create the stories, replacing any `E2` or `S3.5` style reference in the body with the
   `#<number>` of the issue that now exists.
4. Link each story to its epic with the same `gh sub-issue add` call.
5. Add every issue to the project and set its fields.

```bash
gh issue create --repo "$OWNER/$REPO" --title "<title>" --body "<body>"

ITEM_ID=$(gh project item-add <PROJECT_NUMBER> --owner "$OWNER" \
  --url "https://github.com/$OWNER/$REPO/issues/<NUMBER>" \
  --format json | jq -r '.id')

gh project item-edit --project-id "<PROJECT_NODE_ID>" --id "$ITEM_ID" \
  --field-id "<FIELD_ID>" --single-select-option-id "<OPTION_ID>"

gh project item-edit --project-id "<PROJECT_NODE_ID>" --id "$ITEM_ID" \
  --field-id "<FIELD_ID>" --number 5
```

A project item ID is not an issue number. Field edits always need the item ID that
`item-add` returns.

## Bulk creation

For more than a handful of issues, write a throwaway script in a temporary directory
outside the repo rather than pasting commands one at a time. The pattern that survives a
rerun:

1. Represent each issue as one record with a stable source key, title, body, parent key,
   and fields. Persist the returned issue URL and number against that key.
2. Phase 1 creates epics and captures their numbers.
3. Phase 2 links epics to the initiative.
4. Phase 3 creates stories.
5. Phase 4 links stories to their epic.
6. Phase 5 adds everything to the project and sets fields.

Never use the title alone as identity because GitHub permits duplicate titles. Before
linking, query the current parent relationship and skip an existing link. On a secondary
rate limit, stop and retry with bounded exponential backoff, honoring `Retry-After` when
present. Do not continue issuing mutations after a rate-limit error.

## Linking work to an issue

Link a branch or pull request through the issue's Development sidebar, so the issue
closes when the linked PR merges. Do not put `Closes #<n>`, `Fixes #<n>`, or
`Resolves #<n>` in a PR body: it bypasses the project board's own status automation and
duplicates a link GitHub already models.

## Useful checks

```bash
gh issue list --repo "$OWNER/$REPO" --limit 100 --json number,title,state
gh sub-issue list <PARENT_NUMBER> --repo "$OWNER/$REPO"
gh label create "epic" --repo "$OWNER/$REPO" --color "0E8A16" --description "Epic-level issue"
```

Never commit or push. You draft the issues and the links; the developer reviews.
