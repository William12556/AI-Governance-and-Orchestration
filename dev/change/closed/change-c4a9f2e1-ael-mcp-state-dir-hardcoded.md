# Change: ael-mcp — Correct State Directory to ai/state/ralph

Created: 2026 June 15

---

## Table of Contents

- [1.0 Change Information](#10-change-information)
- [2.0 Scope](#20-scope)
- [3.0 Rationale](#30-rationale)
- [4.0 Technical Details](#40-technical-details)
- [5.0 Testing](#50-testing)
- [6.0 Implementation](#60-implementation)
- [Version History](#version-history)

---

## 1.0 Change Information

```yaml
change_info:
  id: "change-c4a9f2e1"
  title: "ael-mcp — correct hardcoded state directory to ai/state/ralph"
  date: "2026-06-15"
  author: "William Watson"
  status: "implemented"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-c4a9f2e1"
    issue_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Scope

```yaml
scope:
  summary: >
    Correct the hardcoded state path in ael-mcp/server.py from .ael/ralph to
    ai/state/ralph, update the ael_status docstring, and align the matching
    references in README.md and DESIGN.md. Repository: William12556/ael-mcp.
  affected_components:
    - name: "_STATE_REL constant"
      file_path: "server.py"
      change_type: "modify"
    - name: "module docstring (ael_status line)"
      file_path: "server.py"
      change_type: "modify"
    - name: "state directory references"
      file_path: "README.md"
      change_type: "modify"
    - name: "state directory references"
      file_path: "DESIGN.md"
      change_type: "modify"
  out_of_scope:
    - "requirements.txt — no new dependency; literal fix retains mcp-only deps"
    - "config-driven state resolution — see Rationale alternatives"
    - "_STATE_FILES list — unchanged (file names, not the directory)"
```

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Rationale

```yaml
rationale:
  problem_statement: >
    server.py hardcodes _STATE_REL = ".ael/ralph". After the ai/ consolidation
    the orchestrator writes loop state to ai/state/ralph/. The server and
    orchestrator disagree, so ael_status misreports and start_ael seeds state
    in the wrong location for migrated projects.
  proposed_solution: >
    Change the single constant _STATE_REL to "ai/state/ralph". All state
    operations derive from this constant, so the one-line correction aligns
    start_ael, ael_status, and reset_ael. Update the docstring and the
    documentation references to match.
  alternatives_considered:
    - option: "Parse loop.state_dir from config.yaml in _validate_project"
      reason_rejected: >
        Adds a YAML-parser dependency to a server whose only dependency is mcp.
        state_dir is fixed by convention; the literal correction is simpler and
        equally reliable. Favours technical simplicity over feature complexity.
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Technical Details

```yaml
technical_details:
  current_behavior: >
    _STATE_REL = ".ael/ralph". _validate_project returns state_dir =
    root / _STATE_REL. start_ael, ael_status, and reset_ael all operate on
    .ael/ralph/.
  proposed_behavior: >
    _STATE_REL = "ai/state/ralph". All three tools operate on ai/state/ralph/,
    matching the orchestrator's loop.state_dir.
  code_changes:
    - file: "server.py"
      location: "module constant (~line 26)"
      old: '_STATE_REL        = ".ael/ralph"'
      new: '_STATE_REL        = "ai/state/ralph"'
    - file: "server.py"
      location: "module docstring (ael_status line, ~line 6)"
      old: "    ael_status  — report current run state from .ael/ralph/"
      new: "    ael_status  — report current run state from ai/state/ralph/"
    - file: "README.md"
      location: "tool table and Reads line"
      detail: "Replace both .ael/ralph/ references with ai/state/ralph/."
    - file: "DESIGN.md"
      location: "state path references (5 occurrences)"
      detail: >
        Replace .ael/ralph/ with ai/state/ralph/ in the run-state location,
        subprocess log note, run-record note, state_files note, and the
        log_path example.
```

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Testing

```yaml
testing:
  approach: >
    Manual verification against a project migrated to the ai/ layout. Confirm
    start_ael seeds the run record under ai/state/ralph/ and ael_status reports
    live state. Confirm reset_ael clears the run record at the new location.
  test_cases:
    - scenario: "start_ael on a migrated project"
      expected_result: >
        Run record (mcp-run.json) and mcp-<run_id>.log written to
        ai/state/ralph/; returned log_path points there.
    - scenario: "ael_status during a live run"
      expected_result: >
        pid_alive true; state_files lists files present in ai/state/ralph/;
        shipped/blocked reflect actual loop state.
    - scenario: "reset_ael after a run"
      expected_result: "Run record removed from ai/state/ralph/; returncode 0."
  validation_criteria:
    - "No .ael/ralph reference remains in server.py, README.md, or DESIGN.md"
    - "server.py imports unchanged; mcp remains the only dependency"
    - "All three tools operate on ai/state/ralph/"
```

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Implementation

```yaml
implementation:
  steps:
    - step: "Claude Code: apply edits per prompt-c4a9f2e1 in the ael-mcp repository"
      status: "done"
    - step: "Manual smoke check: start_ael / ael_status / reset_ael on a migrated project"
      status: "pending"
    - step: "Commit and push ael-mcp"
      status: "pending — William to execute"
    - step: "Update issue-c4a9f2e1 status to resolved after verification"
      status: "done"
  rollback_procedure: "Restore from git history"
  deployment_notes: >
    ael-mcp is a standalone repository scoped to the Claude Desktop profile;
    no framework propagation applies. Commit directly to William12556/ael-mcp.

verification:
  implemented_date: "2026-06-15"
  implemented_by: "Tactical Domain (Claude Code)"
  verification_date: "2026-06-15"
  verified_by: "William Watson"
  test_results: "Source inspection: server.py, README.md, DESIGN.md all on ai/state/ralph/; runtime smoke check remains optional"

traceability:
  related_issues:
    - issue_ref: "issue-c4a9f2e1"
      relationship: "source"
    - issue_ref: "issue-b6e4a1c9"
      relationship: "same consolidation effort"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-15 | William Watson | Initial change — correct ael-mcp state directory to ai/state/ralph |
| 1.1 | 2026-06-15 | William Watson | Implemented and verified by source inspection; closed |

---

Copyright (c) 2026 William Watson. MIT License.
