Created: 2026 October 23

# Task List

Open work for extending AI-G&O. Rules: `dev/README.md` §4.0. Replaces
`dev/todo.md` and `dev/backlog.md` (v1.34), retired 2026-10-23; their
history is in git. The previous register, closed 2026-09-23, is
`dev/reports/closed/task-2026-09-23.md`.

Status keywords: `Active`, `Planned`, `Open — not raised`, `Deferred`, `Parked`.

| ID | Item | Status | References |
| --- | --- | --- | --- |
| `5bcd46ad` | Downstream migration to the new layout: e-Paper-IP-Display and pi-netconfig remain. Procedure: `bin/migrate-layout.sh <root>` (dry run), `--apply`, `bin/propagate.sh --allow-major <root>`; update old paths in CLAUDE.md / AGENTS.md / .gitignore; pin `@j0hanz/filesystem-mcp@2.5.0` in `ai/config.yaml`; add `reviewer_model`; gitignore `.claude/settings.local.json`. GTach `ai-local/retired-5bcd46ad/` (framework files only) may be deleted after review | Active — solax-modbus and GTach done | `proposal-5bcd46ad`; GTach `f67d797` onwards |
| — | Operator: remove the `ael-mcp` entry from the Claude Desktop MCP configuration; archive the `ael-mcp` repository and the `~/mcp-ael` install | Active — operator | `audit-5bcd46ad` L-10 |
| — | Release v0.2.0 (`bin/release.sh v0.2.0`) | Active | Phase 2 follow-up (`requirements-14e05e35`) |
| `caab2052` | Audit remediation group 1, loop robustness: M-01 (tool error reply for non-object arguments), M-02, M-06 (timeouts 300 s model, 120 s MCP; SDK retries 0), L-03, L-09, with `audit-14e05e35` L-09 (HTTP 400/401/403 not retried). Follow-up audit required | Active — change `711a57d5` implemented (c328dfb); live oMLX run and follow-up audit outstanding | `audit-caab2052` §14.0; `issue-711a57d5`, `change-711a57d5`, `prompt-711a57d5` |
| `caab2052` | Audit remediation group 2, status accuracy: M-04, M-05, L-07, L-08, L-15 | Open — not raised | `audit-caab2052` §10.0 |
| `caab2052` | Audit remediation group 3, governance checkers: M-03, L-11, tests for `linter.py` and `protocol_checker.py`; relates to the `schema_type` retirement row | Open — not raised | `audit-caab2052` §10.0 |
| `caab2052` | Audit remediation group 4, approval and tracking: L-04, L-05, L-06 | Open — not raised | `audit-caab2052` §10.0 |
| `caab2052` | Audit remediation group 5, scope hardening: L-01, L-02, L-12 | Open — not raised | `audit-caab2052` §10.0 |
| `caab2052` | Audit remediation group 6, hygiene and structure: L-10, L-13, L-14, L-16, L-17, L-18, L-19 (L-17 and L-18 with `ai/core/`) | Open — not raised | `audit-caab2052` §10.0 |
| `caab2052` | Audit remediation group 7, test coverage gaps | Open — not raised | `audit-caab2052` §8.0 |
| `caab2052` | Operator decisions OQ-01 (syntax gate authority), OQ-02 (Overwatch read-only basis), OQ-03 (AEL baseline currency), OQ-04 ("run type's own paths") | Open — not raised | `audit-caab2052` §11.0 |
| `14e05e35` | Propagate governance 12.x with `--allow-major` to solax-modbus, GTach, e-Paper-IP-Display and pi-netconfig; then `bin/migrate-terms.py --scan` per project and re-record approvals for tracked work items with `approve.py` | Active | `report-14e05e35-live-verification` O-03 |
| `14e05e35` | Operator: read the Mistral "Included API usage" meter | Active — operator | `design-14e05e35` DI-04; `report-14e05e35-live-verification` O-02 |
| — | Mistral Vibe manual profile `ai/profiles/mistral-vibe.md`, alongside `claude-code.md`. Standalone documentation task; requires current facts on Vibe installation, custom providers and MCP | Planned | `proposal-5bcd46ad` OQ-01, D-16 |
| — | Validate the REVISE → fix → SHIP convergence path. REVISE and the gate FAIL branch observed live, but no SHIP after a genuine fix (Run B2 `ael_20260924-154002`; run 4870846d does not count). Next attempt needs a different worker model or a smaller defect; copy the fixture without its header comment | Open — not raised | `change-c37198be` (closed) |
| — | Reviewer false negatives not corrected by gate evidence: Magistral REVISE on correct work (solax-modbus `engine_20260929-131551`; Phase 2 replay, five false REVISE, stall BLOCKED). mistral-medium-2604 shipped the same work in one cycle. Options: present a PASS gate plus a deliverable diff to the reviewer, or change the reviewer model | Open — not raised | `report-14e05e35-live-verification` OB-01 |
| — | Worker helper files under writable `tests/` (GTach run 1e00fd66, work item 72f95f73): `tests/test_changes.py` exits at import; the pytest gate ran only its target and the reviewer shipped. Options: report untracked non-deliverable files to the reviewer and in `awaiting-approval.md`; run the full suite or a collection-only pass in the pytest gate; narrow `writable_paths`. Needs T06/T07/T03 | Open — not raised | `change-bdc6820f` (write scope); `change-7d953510` |
| — | `run_phase`: normalise (abspath) `read_paths` on the F28 wall-clock-cap early return. No observed impact | Deferred — T06 not raised | `d7f4a1c8` P08 review |
| — | `bin/bootstrap.sh`: refuse, with a clear message, a release tarball without `ai/engine/` | Deferred — T06 not raised | `audit-5bcd46ad` H-01 option |
| — | Pre-existing defects: `audit-review.yaml` tests for `.complete` containing `DURATION_LIMIT`, which the orchestrator never writes; `ai/profiles/README.md` links to the gitignored `docs/claude/project_information.md` | Deferred — T06 not raised | `audit-5bcd46ad` L-12 |
| — | Config validation (NFR-04 gaps): missing `loop:` block or `loop.state_dir` gives `KeyError`; non-numeric `max_tokens` gives `ValueError`; gate `timeout_seconds` not validated; missing config file gives a traceback. Validate and report file and field | Deferred — T06 not raised | `audit-14e05e35` L-08 |
| — | Strict-schema rejections and Anthropic authentication errors are retried. Treat HTTP 400/401/403 as non-retryable, or amend design §11.0 (relates to DI-05) | Active — implemented in `711a57d5`; row removed at closure | `audit-14e05e35` L-09 |
| — | `propagate.sh` creates workspace folders on the up-to-date path before confirmation and the plan-error check; its awk parser ignores flow-style `workspace_folders` lists; `migrate-layout.sh` warns on a single-quoted `'ai/state'` | Deferred — T06 not raised | `audit-14e05e35` L-10 |
| — | Stage scan does not report a completed status in an active folder after closure (design §8.1 narrowed in v1.6); implement if wanted | Deferred — T06 not raised | `audit-14e05e35` L-11 |
| — | `approve.py` accepts an `accept` approval before any loop run; require loop completion (`.complete` or a SHIP record) first | Deferred — T06 not raised | `audit-14e05e35` L-14 |
| — | A prompt path in `ai/workspace/` that is not a regular file (directory, FIFO) is classified as untracked; the CLI run starts with the path string as task text and project-root write scope; the warning wrongly says "outside ai/workspace/". Treat as tracked and refuse with exit 3 when no bytes were read; correct the warning; add a test | Deferred — T06 not raised | `audit-14e05e35` follow-up F5-01 |
| — | Log unremovable state entries before writing `BLOCKED.md`; add tests for a real unremovable entry, the `reset_state` return value 1 and the loop-start BLOCKED | Deferred — T06 not raised | `audit-14e05e35` follow-up §6.0 notes 1, 3 |
| — | Context-window resolution order: tier 2 (live oMLX query) precedes tier 3 (`context.model_context_windows`), so a per-model entry never overrides the live value for kind `omlx`; no setting gives Devstral 262144 and Magistral 40960 together. Decide the fix with the operator | Deferred — T06 not raised | O-03 propagation, 2026-10-02 |
| — | Terminal status (for example `superseded`) for a test document whose target was removed: T04 template, `linter.py` `t05_test`, `protocol_checker.py` `_TERMINAL_STATUS`, governance P00.14.3; consider for T05. Propagate afterwards | Deferred — T06 not raised | Found in GTach, 2026-10-08 |
| — | Check that validates protocol citations in source comments | Deferred | `issue-e36a35d3` analysis |
| — | Author the five reserved protocols: P05 Continuous Integration, P16 Execution, P17 Release, P18 Deployment and Propagation, P19 Observability | Deferred | `proposal-eb782f83` §5.3 |
| — | `.github/workflows` CI running `linter.py`, `protocol_checker.py` and pytest on push, plus a check that `docs/claude/primer.md` equals `ai/governance/software-engineering/primer.md`. Governed by P05 once authored; until then sync the primer copy manually | Deferred | gap G1; decision 7.1 |
| — | Tests remaining with P05 CI: `bin/migrate-layout.sh`, `bin/propagate.sh` end to end | Deferred | `audit-5bcd46ad` L-08 |
| — | Retire the numeric `schema_type` prefix in favour of the class word | Deferred | audit F-04; governance Appendix A A.5 |
| — | Evaluate splitting `governance.md` | Deferred — Phase 3 | `proposal-5bcd46ad` OQ-03 |
| — | Engine per project: make the pytest gate command or interpreter configurable (gate runs `sys.executable -m pytest`); resolve the context window per role (Magistral 40960 vs Devstral 262144) | Deferred | solax-modbus pilot preparation, 2026-09-29 |
| — | Planner client integration for open-weight models: profiles or setup guidance for MCP-capable clients (Goose, Cherry Studio, BoltAI, Open WebUI, Codex CLI, OpenCode, Mistral Vibe) | Deferred — not scheduled | `proposal-5bcd46ad` OQ-05 |
| — | Live check of the native Anthropic provider against the Anthropic API: strict tools, prompt caching and Models API readiness. Run one loop with an `ANTHROPIC_API_KEY`; set `strict_tools: false` if a schema is rejected | Deferred — no API key | `requirements-14e05e35` V-04; `change-43091424` |
| — | Speculative decoding or prefill acceleration for prefill-heavy loops; current models incompatible, needs a compatible draft model | Deferred | `report-omlx-ael-efficiency-2026-07-15` §5.0 item 6 |
| — | External MCP servers `mcp-ripgrep`, `mcp-git`, `mcp-sed-awk`: check for the JSON Schema draft-07 `outputSchema` declaration that breaks MCP tools in Cowork sessions; emit 2020-12 or omit `$schema` | Deferred — external | observed 2026-09-23 |
| — | Live oMLX context-window query enhancement | Parked | — |
| `0c6aedee` | Project Overwatch FR-02–FR-10; several items are SE-specific, to be reconsidered in the Phase 4 web GUI design. OQ-07 remains open by design | Parked | `design-project-overwatch` §9.2; `proposal-5bcd46ad` D-12 |

---

Copyright (c) 2026 William Watson. MIT License.
