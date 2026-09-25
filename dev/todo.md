# Todo

Deferred work is held in `dev/backlog.md`. Move an item here when work on it starts.

## Active

change-5bcd46ad (layout and terminology migration; proposal-5bcd46ad Phase 1). Implemented 2026-09-25; folds in change-c37198be.

1. Operator verification on the Mac, engine environment (`~/.venvs/ael`):
   - `python -m pytest tests/engine tests/overwatch -v` (62 tests passed offline with a stub harness; confirm with real pytest).
   - Smoke run: `dev/smoke/ai/` is a gitignored propagated copy in the old layout — remove it, create an empty `dev/smoke/ai/`, run `bin/propagate.sh --allow-major dev/smoke`, copy `dev/smoke/config.reference.yaml` to `dev/smoke/ai/config.yaml`, then run `--mode loop` from `dev/smoke` to SHIP. Doubles as the backlog §5.0 item 2 retry.
   - engine-mcp: repoint the Claude Desktop entry to `ai/engine/mcp/server.py` with the engine interpreter; exercise `start_engine`, `engine_status`, `reset_engine` against `dev/smoke`.
2. Independent review (one review covering change-5bcd46ad and change-c37198be); then close both triples.
3. Downstream pilot: solax-modbus only — `bin/migrate-layout.sh <root>` (dry run), `--apply`, then `bin/propagate.sh --allow-major <root>`; update old paths reported in CLAUDE.md / AGENTS.md / .gitignore; pin `@j0hanz/filesystem-mcp@2.5.0` in `ai/config.yaml`. GTach, e-Paper-IP-Display and pi-netconfig follow only after the pilot is confirmed working (operator decision 2026-09-25).
4. Archive the `ael-mcp` repository and the `~/mcp-ael` install.

## Planned

## Parked
