---
applyTo: "**/*.md,**/*.mdx,**/*.qmd"
description: "Markdown prose rules: no em dashes, full sentences, no AI tics, one sentence per line."
---

# Markdown conventions

The general writing style lives in `.github/copilot-instructions.md`.
For how to document (audience, structure, docstrings, diagrams, keeping docs current), use the `writing-documentation` skill.
Markdown files add:

- Write functional, precise prose; focus on content, not decoration.
- Use headings and lists to structure content.
- Document the why; don't restate what the code already shows.
- In non-English docs, keep code and technical terms in English (class, metric, feature).
- Never use em dashes. Use a comma, period, colon, or parentheses instead.
- Write full sentences. Don't glue short fragments together with commas where a period belongs.
- Don't collapse a sentence into a colon followed by a noun-phrase fragment, as in `X: a direction, not a task, something that...`. Write the full clause instead.
- Avoid the "not X, but Y" and "not just X" contrastive tic. Say the thing directly.
- Don't overuse bold, italics, or emoji.
- Write one sentence per source line, however long.
  Never hard-wrap a sentence across lines at a column width.
  The `markdown-wrap` pre-commit hook (installed via `tara standards`) enforces this.
- Check the site config (`mkdocs.yml`, `zensical.toml`, or equivalent) before suggesting formatting or structure for files under `docs/`.

To enforce the prose rules on writes, install the `prose-style` hooks (`tara add`, kind `hooks`).
They block a write that introduces an em dash or one of the fragment constructions.
