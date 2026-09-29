# Todo

Deferred work is held in `dev/backlog.md`. Move an item here when work on it starts.

## Active

Phase 1 of proposal-5bcd46ad closed 2026-09-29 (change-5bcd46ad, change-c37198be, issue-c37198be and audit-5bcd46ad in `closed/`). Remaining follow-ups:

1. Downstream pilot: solax-modbus migrated and committed 2026-09-25; its `ai-local/retired-5bcd46ad/` holds only framework files (29 files, checked 2026-09-29) and may be deleted after review. Remaining: a live engine run on real work there. GTach, e-Paper-IP-Display and pi-netconfig follow only after the pilot is confirmed working (operator decision 2026-09-25). Procedure: `bin/migrate-layout.sh <root>` (dry run), `--apply`, `bin/propagate.sh --allow-major <root>`; update old paths reported in CLAUDE.md / AGENTS.md / .gitignore; pin `@j0hanz/filesystem-mcp@2.5.0` in `ai/config.yaml`.
2. Operator: remove the `ael-mcp` entry from the Claude Desktop MCP configuration (audit L-10); archive the `ael-mcp` repository and the `~/mcp-ael` install.

## Planned

- Phase 2 requirements (proposal-5bcd46ad §7.0; inputs in `dev/backlog.md` §2.0 items 8–9 and §5.0 items 7–8).

## Parked
