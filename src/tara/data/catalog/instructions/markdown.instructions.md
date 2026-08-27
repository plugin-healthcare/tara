---
applyTo: "**/*.md"
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
- Hard-wrap one sentence per line, not at a character column, so a diff touches only the
  sentence that changed. Skill files and agent-only instruction files (this file included)
  wrap at a character column instead, since that helps a reader estimate token cost at a
  glance.
