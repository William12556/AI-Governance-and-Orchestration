Created: 2026 October 23

# Task List

Open work for extending AI-G&O. Rules: `dev/README.md` §4.0. Replaces
`dev/todo.md` and `dev/backlog.md` (v1.34), retired 2026-10-23; their
history is in git. The previous register, closed 2026-09-23, is
`dev/reports/closed/task-2026-09-23.md`.

Status keywords: `Active`, `Planned`, `Open — not raised`, `Deferred`, `Parked`.

Rows are in Stage C order, work items 1 to 8 (2026-11-06). Goal: a stable
state before `design-63c98596`. Items that concept reshapes were transferred
to `design-63c98596` §10.2 on 2026-11-06. Work items 1 (change-b8c75bac)
and 2 (change-86c958dd) closed 2026-11-06; work items 3 (change-e4428fd5)
and 4 (change-4b0a5592) closed 2026-11-07. Work item 5 was split
into 5A, 5B-1, 5B-2 and 5C; the parts of 5 implemented by change-9377f9b9
((g) for the checkers and `load_manifest`, (j), (k), (l)) and work item 6 (d)
were removed from rows 5 and 6 on 2026-11-14 (`report-b3a503a2`). Work item 5A
(change-9377f9b9), 5B-1 (change-bae631c7) and 5B-2 (change-d4f527e7) closed 2026-11-14.

| ID | Item | Status | References |
| --- | --- | --- | --- |
| `541f5c58` | **5C. Scripts and documents** (work item 5 parts (a) L-19, (b), (d), (e)). (a) L-19: design-14e05e35 §4.1 names `context_window(model)` and `await_ready(...) -> bool` with `poll`; the code has `live_context_window` and `await_ready(...) -> None` with `interval` and `echo`; amend the design. (b) `audit-review.yaml` tests for `.complete` containing `DURATION_LIMIT`, which the orchestrator never writes (it writes `.timeout` with `TIMEOUT: iteration N`); `guide-engine-operations.md` §5.0 states the same `.complete` content (found 2026-11-14); `ai/profiles/README.md` links to the gitignored `docs/claude/project_information.md`. (d) `bin/bootstrap.sh`: refuse, with a clear message, a release tarball without `ai/engine/`. (e) `propagate.sh` creates workspace folders on the up-to-date path before confirmation and the plan-error check; its awk parser ignores flow-style `workspace_folders` lists; `migrate-layout.sh` warns on a single-quoted `'ai/state'` | Active — issue-541f5c58 raised 2026-11-14; change-541f5c58 approved (operator, one-time session exemption) | `audit-caab2052` L-19; `audit-5bcd46ad` L-12, H-01 option; `audit-14e05e35` L-10 |
| `6d40f0dd` | **6. Test coverage gaps**: change-6d40f0dd implemented (tests `0c7595c`); under review | Active — issue-6d40f0dd resolved; change-6d40f0dd implemented 2026-11-14 | `issue-6d40f0dd`; `report-6d40f0dd` |
| `caab2052` | **6 (a). Remaining test coverage gaps** after the re-measurement of 2026-11-14 (`report-6d40f0dd` §4.0): `parser.py` format 2 sanitising of a malformed JSON string; the context-budget abort path in `run_phase` and `write_context_report`; `--duration` exit code 2 with `.timeout`, and the max-iterations continuation prompt; the audit-run scope lock and SHIP coverage override; `strict_tools` given as a string; `stages.py` `main` output (`--json`, `--task-check`); Overwatch `PhaseInference`, the `ComplianceEngine` rules other than FR-02-06 and `_read_budget`. Not taken as optional: `audit-b8c75bac` X03, X09; `audit-86c958dd` X03, X06. Work item 6 parts (b), (c), (e), (f) closed with change-6d40f0dd | Open — not raised | `audit-caab2052` §8.0, §14.0; `report-6d40f0dd` §4.0, §7.0 |
| — | **7a. Document layout conformance** (README.md v4.5): bulleted Table of Contents of H2 sections only, GitHub heading anchors, Return to Table of Contents links. 23 active documents still list ToC entries without bullets, including both `primer.md` copies, both `guide-audit-loop.md` copies, `workflow.md`, `skills/validation/run-tests.md`, `ai/core/README.md`, `dev/README.md`, active requirements, design, proposal, audit and report documents. Records under `closed/` are historical and excluded; `task.md` is exempt | Planned | README.md v4.5; `report-c0cbceb9` |
| — | **8a. Operator:** review and delete retired framework files in the downstream `ai-local/` folders: `ai-local/src/` (old Overwatch, all four projects) and `ai-local/retired-5bcd46ad/` where present. Labels in each `ai-local/RELOCATED.md` | Active — operator | `5bcd46ad`, `14cf601f`; propagation 2026-11-04 |
| — | **8b. Operator:** remove the `ael-mcp` entry from the Claude Desktop MCP configuration; archive the `ael-mcp` repository and the `~/mcp-ael` install | Active — operator | `audit-5bcd46ad` L-10 |
| `14e05e35` | **8c. Operator:** read the Mistral "Included API usage" meter | Active — operator | `design-14e05e35` DI-04; `report-14e05e35-live-verification` O-02 |
| — | **8d. Operator:** reviewer false negatives not corrected by gate evidence: Magistral REVISE on correct work (solax-modbus `engine_20260929-131551`; Phase 2 replay, five false REVISE, stall BLOCKED). mistral-medium-2604 shipped the same work in one cycle. Decided 2026-11-05: bind the reviewer to mistral-medium-2604 by configuration; an engine change (PASS gate results and a deliverable diff for the reviewer) only if a local reviewer is required. dev/smoke comparison 2026-11-05: both reviewers converged in two rounds; mistral-medium-2604 took 5 s per review with accurate feedback, Magistral 34–61 s with wrong supporting figures, and Magistral echoed its input in an earlier run. Record the configuration in each project, then close | Active — operator configuration | `report-14e05e35-live-verification` OB-01; `report-2ad46c76-smoke-convergence` |
| `b8a6c445` | **8e. Propagation**, once, after work item 6: engine, Overwatch and governance (change-b8a6c445, `run.json`; change-a5bd4fe1, scope and gate hardening; work items 1 to 6) to the four downstream projects with `bin/propagate.sh`. Before propagating, run `<gates python> -m pytest --collect-only -q tests` in each project: an existing collection error would fail every pytest gate. Also run `linter.py` and `protocol_checker.py` on each downstream `ai/workspace/`: since change-e4428fd5, an active T03 prompt is checked, and one without `design.components` or `deliverable.files` fails `protocol_checker.py` (`audit-e4428fd5` §5.0) | Planned — on hold for operator decision | `change-b8a6c445` (closed) |
| `14e05e35` | DI-05: record the error Mistral returns when the included allowance is exhausted with pay-as-you-go off; then treat it as non-retryable so the run ends BLOCKED naming the provider. Needs T06 once the error is known | Deferred — awaits observation | `design-14e05e35` DI-05; `report-14e05e35-mistral-api-hypothesis`; `report-14e05e35-live-verification` O-02 |
| — | Live check of the native Anthropic provider against the Anthropic API: strict tools, prompt caching and Models API readiness. Run one loop with an `ANTHROPIC_API_KEY`; set `strict_tools: false` if a schema is rejected | Deferred — no API key; not planned (API access is not included in the Pro plan) | `requirements-14e05e35` V-04; `change-43091424`; `design-63c98596` §10.2 note |
| — | External MCP servers `mcp-ripgrep`, `mcp-git`, `mcp-sed-awk`: check for the JSON Schema draft-07 `outputSchema` declaration that breaks MCP tools in Cowork sessions; emit 2020-12 or omit `$schema` | Deferred — external | observed 2026-09-23 |

---

Copyright (c) 2026 William Watson. MIT License.
