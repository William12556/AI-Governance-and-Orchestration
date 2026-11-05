Created: 2026 October 23

# Task List

Open work for extending AI-G&O. Rules: `dev/README.md` §4.0. Replaces
`dev/todo.md` and `dev/backlog.md` (v1.34), retired 2026-10-23; their
history is in git. The previous register, closed 2026-09-23, is
`dev/reports/closed/task-2026-09-23.md`.

Status keywords: `Active`, `Planned`, `Open — not raised`, `Deferred`, `Parked`.

| ID | Item | Status | References |
| --- | --- | --- | --- |
| — | Operator: review and delete retired framework files in the downstream `ai-local/` folders: `ai-local/src/` (old Overwatch, all four projects) and `ai-local/retired-5bcd46ad/` where present. Labels in each `ai-local/RELOCATED.md` | Active — operator | `5bcd46ad`, `14cf601f`; propagation 2026-11-04 |
| — | Operator: remove the `ael-mcp` entry from the Claude Desktop MCP configuration; archive the `ael-mcp` repository and the `~/mcp-ael` install | Active — operator | `audit-5bcd46ad` L-10 |
| — | `audit-5e8aea4f` F-01 to F-04 (all low): `_validate_audit_report_write` crashes `run_phase` on a non-string write path in an audit run (F-01); `loop.mcp_timeout_seconds` near 8.64e13 s removes every server, and integers beyond the float range raise `OverflowError` (F-02); no test for the `anthropic` secret wiring, the Anthropic API readiness redaction or `BaseException` from `MCPClient.close` (F-03); T16 and T20 lack `isolated_engine_logger` (F-04). One triple | Open — not raised | `audit-5e8aea4f` §8.4 |
| `b8a6c445` | Propagate engine, Overwatch and governance 12.8 (change-b8a6c445, `run.json`) to the four downstream projects with `bin/propagate.sh` | Planned | `change-b8a6c445` (closed) |
| `86c958dd` | Run record and status follow-up: `audit-b8a6c445` F-01 (recorded rc), F-02 (decided: a marker counts only when not older than the run's start), F-03 (decided: FR-02-06 only while running), F-04 (path case), F-05 (test gaps), F-08; live-check observations P-01 (HTTP 404 retried) and P-02 (`manifest.yaml` version 12.2). F-07 optional, not raised | Active — issue raised 2026-11-05; change not yet drafted | `issue-86c958dd`; `audit-b8a6c445` §11.0 |
| `caab2052` | Audit remediation group 3, governance checkers: M-03, L-11, tests for `linter.py` and `protocol_checker.py`. Decided: retire the numeric `schema_type` prefix; templates emit the class word; checkers accept the class word and all 14 numbered values as aliases and warn on an unknown value; governance Appendix A.5 updated | Open — not raised | `audit-caab2052` §10.0, §14.0; audit-eb782f83 F-04 |
| `caab2052` | Audit remediation group 4, approval and tracking: L-04, L-05, L-06 | Open — not raised | `audit-caab2052` §10.0 |
| `caab2052` | Audit remediation group 5, scope and gate hardening: L-01, L-02, L-12; a syntax FAIL overrides SHIP (OQ-01, FR-03-04 v1.8); a collection-only pass over `tests/` in the pytest gate, so a worker helper file that fails on import fails the gate (GTach run 1e00fd66, work item 72f95f73; operator decision 2026-11-05) | Open — not raised | `audit-caab2052` §10.0, §14.0; `change-bdc6820f` |
| `caab2052` | Audit remediation group 6, hygiene and structure: L-10, L-13, L-14, L-16, L-17, L-18, L-19 (L-17 and L-18 with `ai/core/`) | Open — not raised | `audit-caab2052` §10.0 |
| `caab2052` | Audit remediation group 7, test coverage gaps | Open — not raised | `audit-caab2052` §8.0 |
| `14e05e35` | Operator: read the Mistral "Included API usage" meter | Active — operator | `design-14e05e35` DI-04; `report-14e05e35-live-verification` O-02 |
| `14e05e35` | DI-05: record the error Mistral returns when the included allowance is exhausted with pay-as-you-go off; then treat it as non-retryable so the run ends BLOCKED naming the provider. Needs T06 once the error is known | Deferred — awaits observation | `design-14e05e35` DI-05; `report-14e05e35-mistral-api-hypothesis`; `report-14e05e35-live-verification` O-02 |
| — | Mistral Vibe manual profile `ai/profiles/mistral-vibe.md`, alongside `claude-code.md`. Standalone documentation task; requires current facts on Vibe installation, custom providers and MCP | Planned | `proposal-5bcd46ad` OQ-01, D-16 |
| — | Document layout conformance (README.md v4.5): bulleted Table of Contents of H2 sections only, GitHub heading anchors, Return to Table of Contents links. 23 active documents still list ToC entries without bullets, including both `primer.md` copies, both `guide-audit-loop.md` copies, `workflow.md`, `skills/validation/run-tests.md`, `ai/core/README.md`, `dev/README.md`, active requirements, design, proposal, audit and report documents. Records under `closed/` are historical and excluded; `task.md` is exempt | Planned | README.md v4.5; `report-c0cbceb9` |
| — | Validate the REVISE → fix → SHIP convergence path. REVISE and the gate FAIL branch observed live, but no SHIP after a genuine fix (Run B2 `ael_20260924-154002`; run 4870846d does not count). Next attempt needs a different worker model or a smaller defect; copy the fixture without its header comment | Open — not raised | `change-c37198be` (closed) |
| — | Reviewer false negatives not corrected by gate evidence: Magistral REVISE on correct work (solax-modbus `engine_20260929-131551`; Phase 2 replay, five false REVISE, stall BLOCKED). mistral-medium-2604 shipped the same work in one cycle. Decided 2026-11-05: bind the reviewer to mistral-medium-2604 by configuration; an engine change (PASS gate results and a deliverable diff for the reviewer) only if a local reviewer is required | Active — operator configuration | `report-14e05e35-live-verification` OB-01 |
| — | `run_phase`: normalise (abspath) `read_paths` on the F28 wall-clock-cap early return. No observed impact | Deferred — T06 not raised | `d7f4a1c8` P08 review |
| — | `bin/bootstrap.sh`: refuse, with a clear message, a release tarball without `ai/engine/` | Deferred — T06 not raised | `audit-5bcd46ad` H-01 option |
| — | Pre-existing defects: `audit-review.yaml` tests for `.complete` containing `DURATION_LIMIT`, which the orchestrator never writes; `ai/profiles/README.md` links to the gitignored `docs/claude/project_information.md` | Deferred — T06 not raised | `audit-5bcd46ad` L-12 |
| — | Config validation (NFR-04 gaps): missing `loop:` block or `loop.state_dir` gives `KeyError`; non-numeric `max_tokens` gives `ValueError`; gate `timeout_seconds` not validated; missing config file gives a traceback. Validate and report file and field | Deferred — T06 not raised | `audit-14e05e35` L-08 |
| — | `propagate.sh` creates workspace folders on the up-to-date path before confirmation and the plan-error check; its awk parser ignores flow-style `workspace_folders` lists; `migrate-layout.sh` warns on a single-quoted `'ai/state'` | Deferred — T06 not raised | `audit-14e05e35` L-10 |
| — | Stage scan does not report a completed status in an active folder after closure (design §8.1 narrowed in v1.6); implement if wanted | Deferred — T06 not raised | `audit-14e05e35` L-11 |
| — | `approve.py` accepts an `accept` approval before any loop run; require loop completion (`.complete` or a SHIP record) first | Deferred — T06 not raised | `audit-14e05e35` L-14 |
| — | A prompt path in `ai/workspace/` that is not a regular file (directory, FIFO) is classified as untracked; the CLI run starts with the path string as task text and project-root write scope; the warning wrongly says "outside ai/workspace/". Treat as tracked and refuse with exit 3 when no bytes were read; correct the warning; add a test | Deferred — T06 not raised | `audit-14e05e35` follow-up F5-01 |
| — | Log unremovable state entries before writing `BLOCKED.md`; add tests for a real unremovable entry, the `reset_state` return value 1 and the loop-start BLOCKED | Deferred — T06 not raised | `audit-14e05e35` follow-up §6.0 notes 1, 3 |
| — | Context-window resolution order: tier 2 (live oMLX query) precedes tier 3 (`context.model_context_windows`), so no setting gives Devstral 262144 and Magistral 40960 together. Decided 2026-11-05: a per-model entry is used before the live query. Replaces the context-window half of the former "engine per project" row; its interpreter half is met by `gates.python` | Open — not raised | O-03 propagation, 2026-10-02; solax-modbus pilot preparation, 2026-09-29 |
| — | Terminal status (for example `superseded`) for a test document whose target was removed: T04 template, `linter.py` `t05_test`, `protocol_checker.py` `_TERMINAL_STATUS`, governance P00.14.3; consider for T05. Propagate afterwards | Deferred — T06 not raised | Found in GTach, 2026-10-08 |
| — | Check that validates protocol citations in source comments | Deferred | `issue-e36a35d3` analysis |
| — | Author the five reserved protocols: P05 Continuous Integration, P16 Execution, P17 Release, P18 Deployment and Propagation, P19 Observability | Deferred | `proposal-eb782f83` §5.3 |
| — | `.github/workflows` CI running `linter.py`, `protocol_checker.py` and pytest on push, plus a check that `docs/claude/primer.md` equals `ai/governance/software-engineering/primer.md`. Governed by P05 once authored; until then sync the primer copy manually | Deferred | gap G1; decision 7.1 |
| — | Tests remaining with P05 CI: `bin/migrate-layout.sh`, `bin/propagate.sh` end to end | Deferred | `audit-5bcd46ad` L-08 |
| — | Phase 3: second governance model (document authoring), installed under `ai/governance/<name>/`; shows which parts of `governance.md` are shared | Deferred — Phase 3 | `proposal-5bcd46ad` (Phase 3 not started); `requirements-14e05e35` out-of-scope table |
| — | Evaluate splitting `governance.md` | Deferred — Phase 3 | `proposal-5bcd46ad` OQ-03 |
| — | Phase 4: central web GUI for managing governance models and their engines; `ai/webui/` is its component. Scope undecided; Overwatch FR-02–FR-10 to be reconsidered within it | Deferred — Phase 4 | `proposal-5bcd46ad`; `requirements-14e05e35` out-of-scope table; `report-14cf601f` |
| — | Planner client integration for open-weight models: profiles or setup guidance for MCP-capable clients (Goose, Cherry Studio, BoltAI, Open WebUI, Codex CLI, OpenCode, Mistral Vibe) | Deferred — not scheduled | `proposal-5bcd46ad` OQ-05 |
| — | Live check of the native Anthropic provider against the Anthropic API: strict tools, prompt caching and Models API readiness. Run one loop with an `ANTHROPIC_API_KEY`; set `strict_tools: false` if a schema is rejected | Deferred — no API key | `requirements-14e05e35` V-04; `change-43091424` |
| — | Speculative decoding or prefill acceleration for prefill-heavy loops; current models incompatible, needs a compatible draft model | Deferred | `report-omlx-ael-efficiency-2026-07-15` §5.0 item 6 |
| — | External MCP servers `mcp-ripgrep`, `mcp-git`, `mcp-sed-awk`: check for the JSON Schema draft-07 `outputSchema` declaration that breaks MCP tools in Cowork sessions; emit 2020-12 or omit `$schema` | Deferred — external | observed 2026-09-23 |
| — | Live oMLX context-window query enhancement | Parked | — |
| `0c6aedee` | Project Overwatch FR-02–FR-10; several items are SE-specific, to be reconsidered in the Phase 4 web GUI design. OQ-07 remains open by design | Parked | `design-project-overwatch` §9.2; `proposal-5bcd46ad` D-12 |

---

Copyright (c) 2026 William Watson. MIT License.
