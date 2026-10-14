# Rebuild Tara-managed setup from configuration

Date: 2026-09-09
Branch: `feat/claude-code-support`

## Goal

Make upgrades repeatable with `tara rebuild`: reconstruct the configured core setup,
catalog selections, standards scaffolding, agent docs, and derived integrations without
silently replacing user-authored files.

## Plan

1. Extend `.tara/config.toml` with explicit catalog artifact lists and preserve legacy
   configuration loading.
2. Record successful `tara init`, `tara add`, direct catalog-agent, and package-triggered
   installations in the manifest.
3. Discover recognized installed artifacts when an older config has no artifact table,
   then persist that migration during rebuild.
4. Add ownership-safe rebuild writers with dry-run and explicit-force behavior.
5. Reinstall desired catalog artifacts, restore core files and agent-doc scaffolding,
   apply standards scaffolding, and regenerate configured integrations.
6. Cover migration, persistence, reconstruction, dry-run, and collision safety in tests;
   update README, CLI docs, changelog, and handover.

## Implementation status

Completed on 2026-09-09. The artifact manifest preserves legacy `None` semantics,
records selections without rewriting unrelated comments, and migrates only installed
catalog content Tara can match to its source. `tara rebuild` restores the configured
setup, supports dry-run and force modes, and protects unowned files and MCP entries.
