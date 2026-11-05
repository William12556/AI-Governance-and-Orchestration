Created: 2026 November 5

```yaml
change_info:
  id: "change-b8a6c445"
  title: "Status accuracy: engine run record and Overwatch status (audit-caab2052 group 2)"
  date: "2026-11-05"
  status: "approved"  # operator, 2026-11-05
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-b8a6c445"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-b8a6c445"
  description: "Remediate audit-caab2052 M-04, M-05, L-07, L-08, L-15 and the OQ-02 citation, with the run record decided by the operator on 2026-11-05 (audit-caab2052 §14.0)."

scope:
  summary: >
    (A) The engine writes a run record, run.json, in the state directory:
    at the start of the run and again at its end, in the existing final
    finally of main_async. It is written atomically, protected from worker
    writes and removed by reset. (B) Overwatch derives the engine status
    from run.json: running only while the recorded process is alive; a new
    status 'ended' for a run that ended without SHIP or BLOCKED, shown with
    its exit code; 'unknown' for task.md without a run record or an
    unreadable record. (C) FR-02-06 compares the run's task file with the
    open prompts by resolved path. (D) L-07: each document is scanned once.
    (E) L-08: the closed/ filter applies to paths inside the workspace only.
    (F) L-15 and OQ-02: alert heading and docstring citation corrected.
    Tests R1 to R6 and O1 to O6 (prompt-b8a6c445).
  affected_components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }
    - { name: "scope", file_path: "ai/engine/src/scope.py", change_type: "modify" }
    - { name: "overwatch", file_path: "ai/webui/src/overwatch.py", change_type: "modify" }
    - { name: "engine tests", file_path: "tests/engine/test_run_record.py", change_type: "add" }
    - { name: "overwatch tests", file_path: "tests/webui/test_overwatch.py", change_type: "modify" }
    - { name: "engine design", file_path: "dev/design/design-14e05e35-engine-generalisation.md", change_type: "modify" }  # planner
    - { name: "overwatch design", file_path: "dev/design/design-project-overwatch.md", change_type: "modify" }  # planner
    - { name: "overwatch requirements", file_path: "dev/requirements/requirements-0c6aedee-project-overwatch.md", change_type: "modify" }  # planner
    - { name: "operations guide", file_path: "ai/engine/doc/guide-engine-operations.md", change_type: "modify" }  # planner
  affected_designs:
    - { design_ref: "design-14e05e35", sections: ["§7.0 signal files", "§11.0 Error Handling (run-record write failure)", "Version History"] }
    - { design_ref: "design-project-overwatch", sections: ["§4.0 Data Model (EngineState)", "§5.0 Components (Scanner, ComplianceEngine no longer unmodified)", "§7.1", "§8.4", "Version History"] }
  out_of_scope:
    - "engine-mcp engine_status and mcp-run.json; engine-mcp keeps its pid check"
    - "Clearing a stale BLOCKED.md at loop start"
    - "Atomic writes of the other state files and of Overwatch's outputs (audit-caab2052 L-10, group 6)"
    - "Overwatch FR-02 to FR-10 (parked)"
    - "Showing run start and end times in the HTML page; the record carries them for later use"

rational:
  problem_statement: "See issue-b8a6c445: Overwatch reports RUNNING after runs that ended, warns on every prompt run, doubles result documents, hides projects under a 'closed' ancestor, and names a retired tool."
  proposed_solution: "One engine-written record of each run (task file, pid, start, end, exit code), read by Overwatch; three small Overwatch scan and text fixes."
  alternatives_considered:
    - option: "Write BLOCKED.md or another marker on every non-SHIP exit, and parse the task path from the run log"
      reason_rejected: "Several write sites and log parsing; the operator chose the run record (2026-11-05)"
    - option: "Overwatch reads mcp-run.json"
      reason_rejected: "Only engine-mcp writes it; CLI runs would stay wrong"
    - option: "Defer to the Phase 4 web interface"
      reason_rejected: "Overwatch is in use now, and the Phase 4 interface needs the same record"
    - option: "Overwatch infers the end from the last log line 'engine end rc=N'"
      reason_rejected: "Requires locating and parsing the newest log; the record is one small JSON file"
  benefits:
    - "Correct engine status for CLI and engine-mcp runs, including crashed processes"
    - "FR-02-06 meaningful again"
    - "Correct document counts"
    - "A run record the Phase 4 interface can reuse"
  risks:
    - risk: "A recycled pid makes a crashed run look alive"
      mitigation: "Accepted; the window is small on a single-user machine, and a new engine run overwrites the record"
    - risk: "A run-record write failure stops a run"
      mitigation: "Write failures are logged as warnings and never change the run's exit code"
    - risk: "A stale BLOCKED.md from an earlier run outranks an ended run"
      mitigation: "Accepted as before; a live run outranks it, and reset clears it"

technical_details:
  current_behavior: "See issue-b8a6c445 behavior.actual and analysis.root_cause."
  proposed_behavior: >
    (A) run.json holds {mode, task_file, pid, started, ended, rc}; task_file
    is the absolute path of the task file or null for a text task; started
    and ended are ISO 8601 local times with offset; ended and rc are null
    until the end. The start record is written as the first statement of
    the try that follows setup_logging, so a run refused before
    setup_logging writes none (FR-08-05) and every later exit writes the
    end record in the finally. (B) Precedence: live run record → running;
    BLOCKED.md → blocked; .complete → ship; run record ended or process not
    alive → ended (rc from the record, null when the process died without
    an end record); task.md without a run record, or an unreadable record →
    unknown; otherwise idle. (C) FR-02-06 fires when a valid run record
    exists, at least one prompt is open, and no open prompt has the same
    resolved path as task_file (a text task never matches). (D) A file is
    scanned only for the most specific class directory that contains it.
    (E) closed is tested in the path relative to ai/workspace/.
  implementation_approach: "Claude Code cloud session per prompt-b8a6c445; planner updates designs, requirements and the guide after review."
  code_changes:
    - component: "orchestrator"
      file: "ai/engine/src/orchestrator.py"
      change_summary: "A: _RUN_RECORD constant, _write_run_record helper, start and end writes in main_async, run.json in _RESET_FILES"
      functions_affected: ["main_async", "reset_state (file list)"]
    - component: "scope"
      file: "ai/engine/src/scope.py"
      change_summary: "A: run.json in SIGNAL_FILES"
      functions_affected: ["SIGNAL_FILES"]
    - component: "overwatch"
      file: "ai/webui/src/overwatch.py"
      change_summary: "B to F"
      functions_affected: ["EngineState", "Scanner.scan", "Scanner._read_engine_state", "PhaseInference.infer", "ComplianceEngine.evaluate (FR-02-06)", "AlertWriter.payload", "AlertWriter docstring", "HtmlRenderer stylesheet"]
  interface_changes:
    - interface: "<state_dir>/run.json"
      change_type: "addition"
      details: "Engine-written run record; protected from worker writes; removed by reset"
      backward_compatible: "yes"
    - interface: "Overwatch engine status values"
      change_type: "contract"
      details: "Adds 'ended' and 'unknown' to idle, running, ship, blocked; EngineState gains task_file, rc and has_run_record"
      backward_compatible: "yes for readers of the four existing values"

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "Standard library only (json, os, tempfile)" }

testing_requirements:
  test_approach: "pytest, no network, no model (NFR-06). Engine tests drive main_async with fakes, as tests/engine/test_loop_robustness.py does. Overwatch tests build fixture projects in tmp_path."
  test_cases:
    - { scenario: "R1: main_async with a text task that returns early after setup_logging", expected: "run.json: mode loop, task_file null, pid os.getpid(), started and ended set, rc 1" }
    - { scenario: "R2: main_async with a task file that ends at a manifest error", expected: "task_file equals the absolute task path; rc 1" }
    - { scenario: "R3: run-record write raising OSError", expected: "warning logged; same return code; 'engine end' logged" }
    - { scenario: "R4: reset", expected: "run.json removed" }
    - { scenario: "R5: refused run (invalid loop.mcp_timeout_seconds)", expected: "no run.json" }
    - { scenario: "R6: atomic write", expected: "os.replace used; no temporary file left in the state directory" }
    - { scenario: "O1: status precedence table (nine fixtures)", expected: "idle, running, ended, ended with rc, blocked, ship, running over stale BLOCKED.md, unknown for task.md only, unknown for invalid JSON" }
    - { scenario: "O2: FR-02-06 with matching, non-matching and text tasks", expected: "no warning, warning, warning" }
    - { scenario: "O3: result document under test/result/", expected: "listed once, class result" }
    - { scenario: "O4: project under a directory named closed", expected: "documents listed" }
    - { scenario: "O5: alert payload", expected: "heading '# Overwatch alerts — <project>'; 'ENDED rc=2' for an ended run" }
    - { scenario: "O6: phase inference with status ended and an open prompt", expected: "Awaiting prompt execution" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline"
    - "Live: one engine run per path (SHIP, BLOCKED, and an early return) in a downstream project, with Overwatch showing ship, blocked and ended"
    - "Follow-up audit by an independent session (P02.8.2)"

implementation:
  effort_estimate: "3-5 hours"
  implementation_steps:
    - { step: "Source and tests (prompt-b8a6c445)", owner: "Claude Code cloud" }
    - { step: "Planner review of the session branch", owner: "planner" }
    - { step: "design-14e05e35 §7.0, §11.0; design-project-overwatch §4.0, §5.0, §7.1, §8.4; requirements-0c6aedee FR-01-01, FR-01-02; guide-engine-operations state files", owner: "planner" }
    - { step: "Live check", owner: "operator" }
    - { step: "Follow-up audit (P02.8.2)", owner: "independent session" }
  rollback_procedure: "Revert the implementation commits; run.json files left in state directories are ignored by earlier versions."
  deployment_notes: "Propagate with bin/propagate.sh after verification; no configuration change."

traceability:
  related_changes:
    - { change_ref: "change-711a57d5", relationship: "builds on (single final finally in main_async)" }
    - { change_ref: "prompt-19819f2e", relationship: "modifies (Overwatch FR-01 port; no change document exists)" }
  related_issues:
    - { issue_ref: "issue-b8a6c445", relationship: "source" }

notes: "Operator decisions of 2026-11-05 (audit-caab2052 §14.0: M-04, M-05, OQ-02). File name run.json as decided; distinct from engine-mcp's mcp-run.json."

version_history:
  - version: "1.0"
    date: "2026-11-05"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-11-05"
    changes: ["Approved by the operator as drafted, including the statuses 'ended' and 'unknown', the pid liveness check with os.kill(pid, 0), and the out-of-scope items (engine-mcp unchanged, stale BLOCKED.md not cleared, other atomic writes in group 6)"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

Copyright (c) 2026 William Watson. MIT License.
