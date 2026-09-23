Created: 2026 July 29

```yaml
prompt_info:
  id: "prompt-a2f9c4d1"
  task_type: "debug"
  source_ref: "change-a2f9c4d1"
  date: "2026-07-29"
  iteration: 1
  coupled_docs:
    change_ref: "change-a2f9c4d1"
    change_iteration: 1

context:
  purpose: >
    Attach work-summary.txt persistence to worker-phase termination rather than
    to the single final-response exit, and stop treating a productive worker
    phase that exhausted its tool-call budget as fatal. Without this, three of
    four run_phase exits leave deliverables on disk with no manifest, silently
    voiding the read-evidence, syntax and pytest gates; and correct work is
    discarded when the budget runs out.
  integration: >
    ai/ael/src/orchestrator.py — module-level helpers near _validate_write_scope;
    run_phase (local state initialisation, tool dispatch loop, and the
    wall-clock, work-complete and iteration-exhaustion exits).
  constraints:
    - "Do not write a summary on the BLOCKED exit"
    - "Never overwrite an existing work-summary.txt"
    - "Write nothing when no successful non-state file writes were observed"
    - "Do not change review-phase behaviour — guard all synthesis on is_worker_phase"
    - "Do not change the F13 final-response path"
    - "Reuse _WRITE_TOOLS and write_state; add no new imports"
    - "Verify no syntax errors after edit"

specification:
  description: >
    Record successful write-tool targets during a worker phase; synthesise
    work-summary.txt from them at the three non-blocked exits when the worker
    did not write one; return 0 rather than 1 from the iteration-exhaustion
    exit when the phase produced deliverables.
  requirements:
    functional:
      - "Add _synthesize_work_summary(state_dir, written_paths, reason, log) -> bool"
      - "Return False without writing if work-summary.txt already exists"
      - "Return False without writing if written_paths is empty, or if no member survives filtering"
      - "Filter out paths inside state_dir, and paths that are not files at synthesis time"
      - "Body must be headed ORCHESTRATOR-GENERATED SUMMARY, name the exit reason, state that it records what was written and not why, and list the surviving paths sorted"
      - "Initialise a phase-scoped _written_paths set alongside _read_counts in run_phase"
      - "In the tool dispatch loop, record os.path.abspath of the path/file_path/destination argument of any _WRITE_TOOLS call that produced no scope error, no audit-report error and no MCP error"
      - "Call the helper, guarded by is_worker_phase, at the wall-clock cap exit, the work-complete exit and the iteration-exhaustion exit"
      - "At the iteration-exhaustion exit return 0 when a manifest is present after synthesis, else 1"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Preserve existing logging and console output conventions"
        - "Reuse existing state-file helpers"

design:
  architecture: "New module-level helper plus targeted edits to run_phase local state, dispatch loop and three exit paths"
  components:
    - name: "_synthesize_work_summary"
      type: "function"
      purpose: "Reconstruct a deliverable manifest from observed writes"
      logic:
        - "Return False if work-summary.txt exists"
        - "Return False if written_paths empty"
        - "Filter to paths outside state_dir that are files; return False if none remain"
        - "Write the headed body via write_state; log at WARNING; return True"
    - name: "run_phase"
      type: "function"
      purpose: "Track writes and synthesise at termination"
      logic:
        - "Initialise _written_paths alongside _read_counts"
        - "Record successful write-tool targets after the P3 duplicate-read tracking block"
        - "Synthesise at the wall-clock, work-complete and exhaustion exits when is_worker_phase"
        - "Condition the exhaustion return code on manifest presence"
  dependencies:
    internal:
      - "_WRITE_TOOLS, write_state, _is_mcp_error"
    external: []

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py in place"
    - "Run py_compile on the edited file"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "Work-summary synthesis and exhaustion return-code change per design"

success_criteria:
  - "A worker phase that writes deliverables then exhausts its budget produces a synthesised work-summary.txt and returns 0"
  - "A worker phase that writes nothing and exhausts its budget produces no summary and returns 1"
  - "An existing work-summary.txt is never overwritten"
  - "State-directory signal files are never listed as deliverables"
  - "The BLOCKED exit produces no summary"
  - "Review-phase behaviour is unchanged"
  - "The F13 final-response path is unchanged"
  - "ai/ael/src/orchestrator.py has no syntax errors"

tactical_brief: |
  File: ai/ael/src/orchestrator.py. Read run_phase fully before editing.
  Defect 1: work-summary.txt is written only at the final-response exit (F13, ~1069). The wall-clock (~952), work-complete (~1267) and exhaustion (~1272) exits skip it, so _extract_deliverables returns empty and the read-evidence, syntax and pytest gates no-op.
  Defect 2: exhaustion returns rc=1 and run_loop aborts on non-zero work-phase rc (~1765), discarding correct work.
  Add _synthesize_work_summary(state_dir, written_paths, reason, log) near _validate_write_scope: no-op if work-summary.txt exists, if written_paths is empty, or if nothing survives the state-dir and isfile filters; otherwise write an ORCHESTRATOR-GENERATED SUMMARY listing the sorted survivors.
  Add _written_paths set beside _read_counts; populate it in the dispatch loop for _WRITE_TOOLS calls with no scope error, no report error and no MCP error.
  Call the helper guarded by is_worker_phase at the three non-blocked exits. At the exhaustion exit return 0 if a manifest is present after synthesis, else 1.
  Constraints: no synthesis on BLOCKED; never overwrite; no review-phase change; no F13 change; no new imports; verify py_compile.

notes: >
  Execution: Claude Desktop (Opus 5), direct implementation via Filesystem MCP
  at William Watson's instruction — not delegated to Claude Code or AEL. This
  document is retained for governance triple compliance and as the
  specification of record. P08 strategic audit by an independent session
  remains outstanding and is required before closure; the implementer cannot
  supply it.
```
