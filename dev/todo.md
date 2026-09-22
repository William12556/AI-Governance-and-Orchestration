# Todo

## Active
- [ ] Project Overwatch: FR-01 (monitoring panel) shipped 2026-08-21 (prompt-19819f2e); FR-02–FR-10 remaining (design-project-overwatch.md §9.2). OQ-09 side-by-side validation vs govwatch TUI still required before any retirement decision.

## Planned
- [ ] Live Ralph Loop smoke test of the pytest SHIP gate (change-5bdc2d9b) against a project with an existing tests/ directory
- [ ] Validate REVISE→fix→SHIP convergence path at runtime
- [ ] Propagate current orchestrator to GTach
- [ ] Propagate current orchestrator to e-Paper-IP-Display
- [ ] AEL MCP teardown (a3f1c7d9) — Option B, awaiting Claude Code execution
- [ ] Confirm Magistral reviewer tool-calling on first real review phase (a7d3f8b1)
- [ ] Normalize (abspath) read_paths on the F28 phase wall-clock-cap early return in run_phase for consistency with the other return sites (minor, found in d7f4a1c8 P08 review; no observed impact)

### Deferred from eb782f83 (protocol/template reordering)

Scope-excluded from the migration; see `dev/proposals/proposal-eb782f83-protocol-template-reordering.md`
and `dev/reports/report-eb782f83-pre-migration-baseline.md`.

- [ ] Repair the 8 `ai/governance.md` template links — bare filenames missing the `templates/` path segment (baseline §4.1, OQ-7). **After eb782f83**, since the filenames change in it.
- [ ] Repair 9 further pre-existing broken links unrelated to numbering (baseline §4.2–§4.4): `governance.md` → `claude-code.md` missing `profiles/`; `ai/profiles/README.md` → nonexistent `claude-desktop-instructions.md` and stale `claude.md`; 6 profile setup-guide links using `../../../docs/` where `../../docs/` is correct. Independent of eb782f83.
- [ ] Author the five reserved protocols (Change 2): `P05` Continuous Integration, `P16` Execution, `P17` Release, `P18` Deployment and Propagation, `P19` Observability. Slots reserved by eb782f83; content deliberately deferred (proposal §5.3).
- [ ] Add `.github/workflows` CI running `linter.py`, `protocol_checker.py` and pytest on push (gap G1). Governed by `P05` once authored.
- [ ] Propagate governance v10.0 to downstream repositories — GTach, solax-modbus, e-Paper-IP-Display, pi-netconfig, certmon. All pinned at v9.16 by decision D5 until this is done. Distinct from the orchestrator propagation items above.
- [ ] Decide whether `docs/claude/primer.md` should continue to exist as a file copy once `ai/primer.md` is canonical, or be replaced by a pointer. A maintained duplicate is how it drifted three revisions behind.
- [ ] Evaluate splitting `governance.md`. It is 1233 lines before the alias appendix is added (OQ-1).
- [ ] Decide whether `dev/backup/` is git-tracked or ignored (OQ-4). Proposal §7.5 assumes tracked.

### Repository hygiene

- [ ] Resolve whether `tests/overwatch/test_overwatch.py` and `ai/src/requirements-overwatch.txt` are tracked or ignored. Both were untracked as of 2026-09-16; ignoring them leaves the Overwatch test suite unversioned and its dependencies unreproducible. Decision pending.
- [ ] Check `mcp-ripgrep`, `mcp-git` and `mcp-sed-awk` for the JSON Schema draft-07 `outputSchema` declaration that makes the Anthropic Filesystem MCP server unusable in Cowork sessions. Emit `2020-12`, or omit `$schema` entirely.

## Parked
- [ ] Live oMLX context-window query enhancement
