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
- [ ] Rename the three `dev/requirements/` documents to the UUID convention of P00 §1.1.10 — `ael-requirements.md`, `requirements-govwatch.md`, `requirements-project-overwatch.md` — and update every reference to them. Their current names are an oversight.
- [ ] Record in governance v10.0 that `dev/` documents are authored in prose with FR/NFR/CON tables. The YAML `T07` template applies to downstream project requirements only, where a local model consumes it.

### Compliance tooling defects

Pre-existing; found while baselining eb782f83. See `dev/reports/report-eb782f83-pre-migration-baseline.md` §7.0.

- [ ] Resolve the linter/template contradiction producing 81 of the 102 `dev/` linter errors: `linter.py` requires a markdown `## Version History` heading, while the `T02`, `T03` and `T04` templates are pure YAML carrying a `version_history:` key. Either the linter accepts the YAML key for YAML-schema documents, or the templates gain a markdown section. Every issue, change and prompt document in the repository currently fails this check.
- [ ] Add `proposal` and `report` to the linter's known document classes (9 errors). Both are established `dev/` classes.
- [ ] Correct 31 `protocol_checker` lifecycle errors — documents in `closed/` whose status field is non-terminal — and 7 status-consistency errors where an issue and its coupled change disagree.
- [ ] Correct 10 linter enum violations and 2 dangling coupling references in existing `dev/` documents.
- [ ] Consider a check that validates protocol citations embedded in source comments. Nothing currently does; `linter.py` and `protocol_checker.py` validate documents, not docstrings. Named in `issue-e36a35d3` analysis.

### Repository hygiene

- [ ] Check `mcp-ripgrep`, `mcp-git` and `mcp-sed-awk` for the JSON Schema draft-07 `outputSchema` declaration that makes the Anthropic Filesystem MCP server unusable in Cowork sessions. Emit `2020-12`, or omit `$schema` entirely.

## Parked
- [ ] Live oMLX context-window query enhancement
