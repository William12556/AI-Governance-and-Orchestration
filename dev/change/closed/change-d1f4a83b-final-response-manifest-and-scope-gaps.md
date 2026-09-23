Created: 2026 July 29

```yaml
change_info:
  id: "change-d1f4a83b"
  title: "Append an observed-write manifest at the final-response exit; validate every write-tool path argument; strip only an actual verdict token; skip the continue prompt when stdin is not a terminal"
  date: "2026-07-29"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-d1f4a83b"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-d1f4a83b"
  description: >
    Close the vacuous-gate condition at the one worker exit change-a2f9c4d1 did
    not cover, and three smaller defects found in the same region during
    independent verification.

scope:
  summary: >
    Four edits to orchestrator.py. (1) After the F13 final-response write,
    append an observed-write manifest to work-summary.txt when the worker's own
    text names none of the files it wrote. (2) Validate every path argument a
    write tool carries, not only the first present. (3) Drop the leading token
    in _strip_verdict only when it is itself a verdict. (4) Take the
    max-iterations continue prompt only when stdin is a terminal.
  affected_components:
    - name: "orchestrator (_append_observed_manifest, new)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "orchestrator (run_phase F13 final-response exit)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "orchestrator (_validate_write_scope)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "orchestrator (_strip_verdict)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "orchestrator (run_loop continue prompt)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "Worker tool-call efficiency — issue-c7e9a1b3, the other reason no SHIP was reached; explicitly out of scope for this remediation"
    - "Reviewer criterion-6 calibration — a recipe-design judgment for William Watson"
    - "ralph-work.yaml PROCEDURE wording — the orchestrator is being made robust to what workers emit, not the instruction tightened"
    - "Grammar-constrained decoding — deferred under change-3b9e6d72"
    - "The deployed ael-mcp build's .ael/ralph state resolution — a separate repository and an operational redeploy"

rational:
  problem_statement: >
    F13 persists the worker's final message verbatim as work-summary.txt.
    _extract_deliverables then parses that message for paths, and the syntax,
    pytest and read-evidence gates act on the result. A final message that is a
    sentence rather than a manifest yields no deliverables, so all three gates
    no-op while appearing to have run, and the reviewer is shown a manifest that
    contradicts the filesystem. change-a2f9c4d1 closed this condition at the
    wall-clock, work-complete and exhaustion exits by synthesising a manifest
    where none existed; the final-response exit is the case where one exists but
    is not a manifest, and it was not considered. Three smaller defects sit in
    the same region: scope validation tests only the first path argument
    present, so a move out of the project root is admitted; _strip_verdict's
    fallback removes the first word of a message that carries no verdict at all;
    and the max-iterations continue prompt blocks forever when stdin is not a
    terminal, which is the ael-mcp launch condition.
  proposed_solution: >
    Extend rather than replace at the final-response exit. The worker's own
    account is a governance artefact in its own right and is preserved
    unaltered; a machine-generated section is appended below it, and only when
    the worker's text names none of the observed deliverables, so a worker that
    did write a proper manifest is untouched. The other three are each a
    one-condition correction at the point the wrong assumption is made.
  alternatives_considered:
    - option: "Replace the final response with a synthesised manifest when it names no files"
      reason_rejected: >
        Destroys the worker's account of its reasoning, which the reviewer reads
        and which change-a2f9c4d1 was careful to protect. Appending obtains the
        manifest without that loss.
    - option: "Call _synthesize_work_summary at the final-response exit"
      reason_rejected: >
        It declines to overwrite an existing work-summary.txt by design, so at
        this exit it would always no-op. Loosening that guard would reintroduce
        the destruction the guard exists to prevent.
    - option: "Require the worker to write work-summary.txt before its final response, enforced by rejecting the final response otherwise"
      reason_rejected: >
        Converts a recoverable condition into a BLOCKED phase, and makes loop
        termination depend on instruction-following by a 24B quantised model —
        the dependency this framework has repeatedly found unreliable.
    - option: "Detect the missing manifest at the gates instead, treating an empty deliverable set as a gate failure"
      reason_rejected: >
        An empty deliverable set is legitimate in a cycle that genuinely
        produced nothing. The gates cannot distinguish the two cases; the phase
        that observed the writes can.
    - option: "For N2, validate only the destination for move/rename tools"
      reason_rejected: >
        The source is also a containment obligation — a move can read from
        outside the project. Testing every path present is both simpler and
        stricter.
  benefits:
    - "The syntax, pytest and read-evidence gates receive this cycle's actual output at every non-blocked worker exit"
    - "The reviewer is no longer told a deliverable is absent when it exists"
    - "F4 containment holds for the move and rename members of _WRITE_TOOLS"
    - "REVISE feedback is altered only where a verdict declaration is actually removed"
    - "A detached run terminates on its own budget instead of leaving an orphaned process holding MCP servers"
  risks:
    - risk: "The basename test suppresses the append when the worker mentions a filename incidentally"
      mitigation: >
        Deliberately conservative in that direction: a mention is weak evidence
        the worker described its output, and a false suppression leaves
        behaviour exactly as it is today, whereas a false append would duplicate
        a manifest the worker did supply.
    - risk: "Appending changes the byte content of work-summary.txt that the reviewer reads"
      mitigation: >
        The section is plainly labelled ORCHESTRATOR-APPENDED MANIFEST, in the
        same register as the ORCHESTRATOR-GENERATED SUMMARY change-a2f9c4d1
        introduced, so the reviewer does not mistake it for the worker's account.
    - risk: "Validating every path argument rejects a call that previously succeeded"
      mitigation: >
        Only calls with a second path outside the project root are newly
        rejected. That is the defect being closed, not a regression.
    - risk: "isatty() misreports under an unusual launcher and a human is denied the prompt"
      mitigation: >
        The declined branch is the documented default answer, and the decision
        is logged. A terminal run is unaffected.

technical_details:
  current_behavior: >
    run_phase's F13 branch writes the worker's final message to work-summary.txt
    and sets _manifest_written, with no test of the content.
    _validate_write_scope evaluates `path or file_path or destination` and tests
    that single value. _strip_verdict falls back to dropping the first
    whitespace-delimited token whenever no isolated verdict line is present.
    run_loop calls input() on reaching max_iterations, guarded against EOFError
    and KeyboardInterrupt only.
  proposed_behavior: >
    The F13 branch additionally calls _append_observed_manifest, which appends a
    labelled file list when deliverables were observed outside state_dir and the
    worker's text contains none of their basenames. _validate_write_scope tests
    every present value among path, file_path, destination and new_path and
    rejects on the first outside project_root. _strip_verdict returns the text
    unchanged when no verdict line was removed and the leading token is not
    itself a verdict. run_loop prompts only when sys.stdin.isatty(), logging and
    declining otherwise.
  implementation_approach: >
    1. New _append_observed_manifest(state_dir, written_paths, content, log) ->
    bool, placed after _synthesize_work_summary and filtering written_paths by
    the same two rules (outside state_dir, isfile).
    2. Call it in run_phase's F13 is_worker_phase branch, after write_state.
    3. _validate_write_scope: build a list of present string path arguments and
    loop, rather than short-circuiting on an `or` chain.
    4. _strip_verdict: guard the leading-token fallback with _is_verdict_line.
    5. run_loop: branch the continue prompt on sys.stdin.isatty().
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: >
        _append_observed_manifest added and called from the F13 exit;
        _validate_write_scope tests every path argument; _strip_verdict's
        fallback conditioned on the leading token being a verdict; continue
        prompt conditioned on an interactive stdin.
      functions_affected:
        - "_append_observed_manifest (new)"
        - "run_phase"
        - "_validate_write_scope"
        - "_strip_verdict"
        - "run_loop"
      classes_affected: []
  data_changes:
    - "work-summary.txt may carry an appended ORCHESTRATOR-APPENDED MANIFEST section following the worker's own final response"
  interface_changes:
    - "A non-interactive run reaching max_iterations now exits 1 rather than blocking; no configuration change"

dependencies:
  internal:
    - component: "_extract_deliverables and the read-evidence, syntax and pytest gates"
      impact: "Unchanged; now receive a populated deliverable set at the final-response exit"
    - component: "_is_verdict_line"
      impact: "Reused by _strip_verdict's fallback guard"
    - component: "change-f5c28a04 _manifest_written tracking"
      impact: "Unchanged. The flag still records that a summary was written; N1 corrects what that summary contains, not whether it exists"
  external: []
  required_changes: []

testing_requirements:
  test_approach: >
    Isolated execution of each changed unit against synthetic inputs, then a
    live Ralph Loop run against a scratch harness reaching the F13 exit and the
    max-iterations exit.
  test_cases:
    - scenario: "Worker writes src/split.py, final response names no file"
      expected_result: "Manifest section appended; _extract_deliverables non-empty; gates act"
    - scenario: "Worker writes src/split.py, final response says 'I wrote src/split.py'"
      expected_result: "No append; worker's manifest left as-is"
    - scenario: "No observed writes outside state_dir"
      expected_result: "No append"
    - scenario: "Only state_dir writes observed"
      expected_result: "No append"
    - scenario: "move_file with path inside and destination outside project_root"
      expected_result: "Scope violation returned"
    - scenario: "rename_file with path inside and new_path outside project_root"
      expected_result: "Scope violation returned"
    - scenario: "move_file wholly inside project_root; write inside; non-write tool outside"
      expected_result: "Allowed"
    - scenario: "_strip_verdict on a message with no verdict token"
      expected_result: "Text returned unchanged"
    - scenario: "_strip_verdict on 'REVISE: fix the import' and on a trailing isolated REVISE"
      expected_result: "Unchanged from change-3b9e6d72 behaviour"
    - scenario: "Detached loop reaching max_iterations"
      expected_result: "Declines non-interactively, logs the reason, exits 1"
  regression_scope:
    - "The worker's own final response is written verbatim and never altered"
    - "_synthesize_work_summary and the three exits it serves are untouched"
    - "_normalize_verdict is untouched"
    - "Non-write tools remain unvalidated for scope"
    - "A terminal-launched run still receives the continue prompt"
  validation_criteria:
    - "ai/ael/src/orchestrator.py has no syntax errors"
    - "No previously-allowed write call inside project_root is newly rejected"
    - "No previously-correct feedback body is newly altered"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Claude implements directly via file tools (no Claude Code, no AEL) per dev/cowork-remediation-prompt-2026-07-29.md §7.0"
      owner: "Claude (Cowork session, Opus 5)"
  rollback_procedure: "git revert the commit."
  deployment_notes: >
    Downstream propagation via bin/propagate.sh, together with change-3b9e6d72
    and change-f5c28a04. N1 should reach downstream projects before any further
    AEL run there, as it governs whether the SHIP gates evaluate anything at all.

verification:
  implemented_date: "2026-07-29"
  implemented_by: "Claude (Cowork session, Opus 5)"
  verification_date: "2026-07-29"
  verified_by: "Claude (Cowork session, Opus 5) — implementer and verifier are the same session"
  test_results: >
    python3 -m py_compile clean. Isolated execution via AST extraction of
    _append_observed_manifest, _validate_write_scope, _strip_verdict and
    _is_verdict_line against synthetic inputs: all ten cases above pass at unit
    level, including the two scope violations that returned None before this
    change and the two _strip_verdict forms that must remain unchanged. The
    twenty-two-case _normalize_verdict suite was re-run and is unaffected.

    Live, run 1df4e55d against dev/smoke-n1 (max_iterations 1,
    phase_max_iterations 20): N4 confirmed. The run completed one cycle with
    four deliverables, syntax gate PASS, _extract_deliverables 4 files,
    [TEST GATE: PASS] and a REVISE verdict, then logged "max iterations 1
    reached without SHIP", "max iterations reached, stdin is not a terminal —
    declining to continue" and "AEL end rc=1". Run 8c2040d3 produced the first
    of those lines at 12:53:26 and never produced the third. No regression was
    observed in the synthesis path, the three gates or verdict resolution.
  issues_found:
    - "N1 is not confirmed live. In every run since the fix the worker exhausted its iteration budget rather than ending on a final response, so _synthesize_work_summary fired and _append_observed_manifest was never reached. The remediation rests on isolated execution of the helper across its four decision branches plus source reading of the call site."
    - "N2 and N3 cannot be reached by a live run: no worker used a move or rename tool in any run, and every reviewer verdict took the leading-token form. Both rest on isolated execution."
    - "Verified by the implementing session only. Independent verification is outstanding, and is the stated precondition for closure."
    - "Observation, not a defect of this change: in run 1df4e55d the reviewer issued REVISE on the grounds that 'the worker did not write work-summary.txt' when a synthesised manifest was present and had been read. If the reviewer objects to an orchestrator-supplied manifest on principle, N1's appended section will meet the same objection. This is reviewer-recipe calibration, out of scope here."

operator_closure_2026_07_29:
  closed_by: "William Watson"
  basis: >
    Closed at William Watson's explicit instruction on 2026-07-29, review of
    dev/audit. The document's own stated precondition for closure —
    independent verification, distinct from the implementing session — was not
    met at the time of writing. This is an operator closure decision overriding
    that stated precondition, not a claim that independent verification was
    subsequently performed. N1 in particular remains unconfirmed live; recorded
    in dev/task.md rather than represented as resolved.

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-a2f9c4d1"
      relationship: "extends — closes the vacuous-gate condition at the fourth worker exit"
    - change_ref: "change-f5c28a04"
      relationship: "completes — N1 restores the per-cycle manifest guarantee at the final-response exit; N2 closes the half of the argument ordering that change did not correct"
    - change_ref: "change-3b9e6d72"
      relationship: "corrects — N3 is a residual of that change's stated benefit"
  related_issues:
    - issue_ref: "issue-d1f4a83b"
      relationship: "resolves"

notes: >
  Authored and implemented during the autonomous remediation session of
  2026-07-29. Left open deliberately: the implementer is the verifier, and N1
  sits in the code region that has produced defects on three consecutive review
  passes (a2f9c4d1 -> f5c28a04 -> d1f4a83b). Independent verification before
  closure is the standard this project has applied to every predecessor in that
  chain.

version_history:
  - version: "1.0"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Initial change document — implemented from issue-d1f4a83b findings N1-N4"
  - version: "1.1"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Closed at operator instruction (dev/audit review); status implemented -> closed; operator_closure_2026_07_29 recorded, naming N1's live confirmation as still outstanding at closure"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised closed -> verified: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction; asserts no verification beyond what this document already records."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
