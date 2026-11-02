---
name: publish-html-hatch
description: Use when publishing a self-contained HTML page or explorable to a public URL with the Hatch MCP: pairing a workspace, creating a hatch, updating it, and sharing or reviewing the roost URL.
---


# Publish HTML with Hatch

Hatch hosts static HTML at a public "roost" URL (`https://{slug}.{apex}`). See `references/hatch-flow.md` for tool-by-tool detail.

## Steps
1. **Build** a self-contained page: inline CSS; any assets in one folder.
2. **Pair** (only for workspace-scoped actions): `whoami` → `get_pairing_code` → a human approves the code → `poll_pairing`. Never print session or refresh tokens.
3. **Check first**: `list` or `lookup` so you don't create a duplicate site.
4. **Hatch once per site**: pass `html` for a single page, or a `manifest` (paths + sizes) and `curl -T` each file to the returned presigned PUT URLs. Choose `tier` (free sites expire; paid tiers persist), optional `preferredSlug`/`apex`. **Save the returned hatch id.**
5. **Update** with `upload` + manifest. Never call `hatch` again for the same site.
6. **Adjust** with `convert`: rename slug, gallery listing, custom domain.
7. **Share/review** (optional): `auth` for a shared password, `share` for an expiring guest link, `await_decision` / `poll_decision` / `continue_decision` for human review on the live page.
8. **Paid upgrades**: `catalog` → `checkout` → `poll_checkout`, only with explicit human approval.

## Rules
- Never put tokens, workspace IDs, or hatch IDs in shared files or posts.
- A human approves anything public or paid.
