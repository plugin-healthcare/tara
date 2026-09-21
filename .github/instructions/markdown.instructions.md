---
applyTo: "**/*.md"
---

# Markdown conventions

The general writing style (avoid typical AI formulation: no em dashes, emoji, hype, or filler) lives in `.github/copilot-instructions.md`.
For how to document (audience, structure, docstrings, diagrams, keeping docs current), use the `writing-documentation` skill.
Markdown files add:

- Write functional, precise prose; focus on content, not decoration.
- Use headings and lists to structure content.
- Write one sentence per source line, however long.
  Never hard-wrap a sentence across lines at a column width.
  The `markdown-wrap` pre-commit hook (installed via `tara standards`) enforces this.
- Document the why, not the what; don't restate what the code already shows.
- In non-English docs, keep code and technical terms in English (class, metric, feature).
