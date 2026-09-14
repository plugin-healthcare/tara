---
applyTo: "**/*.md,**/*.mdx,**/*.qmd"
description: "Markdown prose rules: no em dashes, full sentences, no AI tics, one sentence per line."
---

# Markdown conventions

The general writing style (avoid typical AI formulation: no em dashes, emoji, hype, or
filler) lives in `.github/copilot-instructions.md`. For how to document (audience,
structure, docstrings, diagrams, keeping docs current), use the `writing-documentation`
skill. Markdown files add:

- Write functional, precise prose; focus on content, not decoration.
- Use headings and lists to structure content; keep lines readable.
- Document the why, not the what; don't restate what the code already shows.
- In non-English docs, keep code and technical terms in English (class, metric, feature).
- No em dashes, ever. Not "sparingly", never. Use a comma, period, colon, or
  parentheses instead.
- Write full sentences. Don't glue short fragments together with commas where a period
  belongs.
- Don't collapse a sentence into a colon followed by a noun-phrase fragment, as in
  `X: a direction, not a task, something that...`. Write the full clause instead. This
  construction is a distinctive AI-writing tell and reads as evasive even when the
  content is fine.
- Avoid the "not X, but Y" and "not just X" contrastive tic as a stylistic habit. Say
  the thing directly instead of setting up a contrast to knock down.
- Don't overuse bold, italics, or emoji.
- Hard-wrap one sentence per line, not at a character column, so a diff touches only the
  sentence that changed. Markdown collapses single newlines inside a paragraph, so this
  changes diffs, never rendering. Skill files and agent-only instruction files (this
  file included) wrap at a character column instead, since that helps a reader estimate
  token cost at a glance.
- Check the site config (`mkdocs.yml`, `zensical.toml`, or equivalent) before suggesting
  formatting or structure for files under `docs/`.

To have the first four prose rules enforced rather than merely written down, install the
`prose-style` hooks (`tara add`, kind `hooks`). They block a write that introduces an em
dash or one of the fragment constructions.
