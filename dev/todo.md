# Todo

Deferred work is held in `dev/backlog.md`. Move an item here when work on it starts.

## Active

change-5bcd46ad (layout and terminology migration; proposal-5bcd46ad Phase 1) and change-c37198be: verified 2026-09-29 (audit-5bcd46ad, accept with remediation; pytest 62 passed; release v0.1.0). Remediation done except the items below.

1. Operator: accept audit-5bcd46ad; then close change-5bcd46ad, change-c37198be and issue-c37198be (move to `closed/`), record acceptance in the audit §8.0, and move the audit to `dev/audit/closed/`. Follow-up audit waivable (P02.8.2): remediation changed only the `migrate-layout.sh` log label (P04.12).
2. Downstream pilot: solax-modbus migrated and committed 2026-09-25; its `ai-local/retired-5bcd46ad/` holds only framework files (29 files, checked 2026-09-29) and may be deleted after review. Remaining: a live engine run on real work there. GTach, e-Paper-IP-Display and pi-netconfig follow only after the pilot is confirmed working (operator decision 2026-09-25). Procedure: `bin/migrate-layout.sh <root>` (dry run), `--apply`, `bin/propagate.sh --allow-major <root>`; update old paths reported in CLAUDE.md / AGENTS.md / .gitignore; pin `@j0hanz/filesystem-mcp@2.5.0` in `ai/config.yaml`.
3. Operator: remove the `ael-mcp` entry from the Claude Desktop MCP configuration (audit L-10); archive the `ael-mcp` repository and the `~/mcp-ael` install.

## Planned

- Phase 2 requirements (proposal-5bcd46ad §7.0; inputs in `dev/backlog.md` §2.0 items 8–9 and §5.0 items 7–8).

## Parked
