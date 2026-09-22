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

- [x] Repair the 8 `ai/governance.md` template links — **done by eb782f83, not discharged by it.** The migration emits them at their correct `templates/` paths. The strategic audit (F-01) found this reversed OQ-7 and FR-07-04, which said the paths would not be repaired; recorded as CON-08 exception E-3 in the proposal §6.3 rather than closed as a discharge. Broken links fell from 17 to 9.
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

### propagate.sh defects

Found while regenerating `dev/smoke/ai/` after the eb782f83 migration. Both
gate the downstream propagation item above.

- [ ] `bin/propagate.sh` cannot handle renames. It rsyncs without `--delete`, so a renamed file leaves its old name behind in the target. Propagating v10.0 as it stands would leave every downstream project with fifteen template files: the eight current names plus the seven retired ones. Either add `--delete` with the existing exclude list acting as protection, or enumerate and remove superseded names explicitly.
- [ ] `bin/propagate.sh` cannot run non-interactively. Line 117 is `read -r -p "Apply changes? [y/N] "`, and under `set -euo pipefail` a non-TTY stdin causes exit 1 *after* the preview and *before* the apply — so it reports what it would do and then silently does nothing. Add a `--yes` flag, or detect a non-TTY and fail loudly rather than exiting as though complete.
- [ ] Consider whether `propagate.sh` should refuse to run when the target's governance version differs from the source by a major version, since that is exactly when renames occur.

### Deferred from the eb782f83 strategic audit (change-9b8f1c47)

- [ ] Retire the numeric `schema_type` prefix in favour of the class word — `issue`, `change`, `design` (audit F-04). Recorded as a permanent exception in governance Appendix A A.5 for now. The prefix cannot be migrated in isolation: `linter.py` keys validation rules, enums, id patterns and coupling paths on these strings and every frozen document carries them, so CON-04 forecloses it. Retiring the numeric component removes the coupling altogether, which is the same correction this migration made to protocol citations.
- [ ] Decide whether `rollback()` should remove files the manifest does not record, or continue to refuse and defer to `git checkout` (audit F-02). It currently refuses, which is safe but leaves the tool unable to do the thing its name claims.
- [ ] Exercise `--rollback` against a real snapshot on a scratch clone. It has still never been run in anger (brief §5.1.3), and the refusal path added under change-9b8f1c47 is now the only path it takes.
- [ ] Resolve `bin/propagate.sh`'s two defects together with audit F-03 and F-10 before any D5 propagation. The audit is right that these are one problem seen from three sides: the instrument was built for one repository with a known layout, and propagation is the first use that breaks those assumptions.
- [ ] Search the corpus for prose that refers to a protocol by position — "the following protocol", "as described above". Never performed; named as untested in the audit brief §5.1.1 and still the most likely place for a genuine CON-01 violation.
- [ ] Run the AEL once against the migrated corpus. The recipes were in the write set and no Ralph Loop has executed since (brief §5.1.4).

### Repository hygiene

- [ ] Check `mcp-ripgrep`, `mcp-git` and `mcp-sed-awk` for the JSON Schema draft-07 `outputSchema` declaration that makes the Anthropic Filesystem MCP server unusable in Cowork sessions. Emit `2020-12`, or omit `$schema` entirely.

## Parked
- [ ] Live oMLX context-window query enhancement
