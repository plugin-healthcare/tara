---
applyTo: "**/*.md,**/*.mdx,**/*.qmd"
---

# Markdown conventions

The general writing style lives in `.github/copilot-instructions.md`. For how to
document audience, structure, diagrams, and keeping docs current, use the
`writing-documentation` skill.

- Write functional, precise prose. Focus on content, not decoration.
- Use headings and lists to structure content.
- Document the why. Do not restate what the code already shows.
- In non-English docs, keep code and technical terms in English.
- Never use em dashes. Use a comma, period, colon, or parentheses.
- Write full sentences. Do not glue fragments together with commas.
- Do not collapse a sentence into a colon followed by a noun-phrase fragment.
- Avoid the "not X, but Y" and "not just X" contrastive tic.
- Do not overuse bold, italics, or emoji.
- Write one sentence per source line. Skills and agent-only instruction files may
  wrap at a character column to make token cost easier to estimate.
- Check the site configuration before suggesting structure under `docs/`.
