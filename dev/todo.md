# Todo

Deferred work is held in `dev/backlog.md`. Move an item here when work on it starts.

## Active

Phase 1 of proposal-5bcd46ad closed 2026-09-29 (change-5bcd46ad, change-c37198be, issue-c37198be and audit-5bcd46ad in `closed/`). Remaining follow-ups:

1. Downstream migration: the solax-modbus pilot is confirmed. Its live engine run on prompt-c8e760ee was accepted on 2026-09-29 (`ee495f4`), and `ai-local/retired-5bcd46ad/` was removed (`74ebcbc`). GTach was migrated and corrected on 2026-09-29/30 (`f67d797` onwards). Its `ai-local/retired-5bcd46ad/` holds only framework files (29 files, checked 2026-09-29) and may be deleted after review. Remaining: e-Paper-IP-Display and pi-netconfig. Procedure: `bin/migrate-layout.sh <root>` (dry run), `--apply`, `bin/propagate.sh --allow-major <root>`; update old paths reported in CLAUDE.md / AGENTS.md / .gitignore; pin `@j0hanz/filesystem-mcp@2.5.0` in `ai/config.yaml`; add `reviewer_model`; gitignore `.claude/settings.local.json`.
2. Operator: remove the `ael-mcp` entry from the Claude Desktop MCP configuration (audit L-10); archive the `ael-mcp` repository and the `~/mcp-ael` install.
3. Phase 2 closed 2026-10-01: requirements-14e05e35 v1.4 (§6.1 Verification Results; V-03 deviation and V-04 Anthropic partial accepted), design-14e05e35 v1.11, live report v1.3, audit-14e05e35 with five follow-ups, all change records in `closed/`. Remaining Phase 2 follow-ups:
    - Release v0.2.0 (`bin/release.sh v0.2.0`).
    - Downstream propagation of governance 12.2 with `--allow-major` to solax-modbus, GTach, e-Paper-IP-Display and pi-netconfig; then `bin/migrate-terms.py --scan` per project and re-recording of approvals for tracked work items with `approve.py` (live report O-03).
    - Operator: read the Mistral "Included API usage" meter (design DI-04, live report O-02).
    - Deferred: live Anthropic API check (backlog §2.0 item 12); audit residuals (backlog §3.0 items 6–12).

## Planned

- Mistral Vibe manual profile `ai/profiles/mistral-vibe.md`, alongside `claude-code.md` (proposal-5bcd46ad OQ-01, D-16). Standalone documentation task, outside Phase 2; requires current facts on Vibe installation, custom providers and MCP.

## Parked
