# Todo

Deferred work is held in `dev/backlog.md`. Move an item here when work on it starts.

## Active

Paused 2026-09-25. Resume by reading this section, then `dev/backlog.md` §5.0, then `dev/change/change-c37198be-ael-runtime-verification.md`.

1. change-c37198be (issue-c37198be): implemented and committed (13bb533); independent review pending, then closure.
2. Backlog §5.0 item 2 (REVISE → fix → SHIP): open. Retry with a different worker model or a smaller defect; copy the fixture without its header (`grep -v '^#' ../smoke-fixtures/split_defective.py > src/split.py`). Run from `dev/smoke` with `~/.venvs/ael/bin/python`.
3. Backlog §5.0 item 7: worker writes unrequested helper scripts; decide whether to restrict worker writes to declared deliverables.
4. Downstream: propagate the c37198be changes (`bin/propagate.sh`) and pin `@j0hanz/filesystem-mcp@2.5.0` in each project's own `ai/ael/config.yaml` (not propagated).

## Planned

## Parked
