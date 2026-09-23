Created: 2026 July 29

```yaml
issue_info:
  id: "issue-d1f4a83b"
  title: "Worker final response persisted as a manifest without naming any deliverable; write-scope validation stops at the first path argument; leading-token strip applied to verdict-free feedback; non-interactive continue prompt blocks forever"
  date: "2026-07-29"
  reporter: "William Watson"
  status: "closed"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-d1f4a83b"
    change_iteration: 1

source:
  origin: "live_execution"
  test_ref: "dev/smoke runs e73caef0 and 8c2040d3 (2026-07-29 12:31 and 12:37)"
  description: >
    Four defects observed or derived while independently verifying
    change-3b9e6d72, change-f5c28a04 and change-8c1a4f5e in a separate session.
    None is a defect of those three changes; N1 and N2 are adjacent conditions
    those changes reasoned about but did not close, N3 is a residual of
    change-3b9e6d72's stated benefit, and N4 is pre-existing and only observable
    when the orchestrator is launched detached.

    (N1) Final response persisted as a manifest. F13 writes the worker's final
    message verbatim to work-summary.txt on the normal-completion path, on the
    assumption that a worker finishing deliberately has produced the manifest
    ralph-work.yaml PROCEDURE step 6 requests. The assumption does not hold. In
    run 8c2040d3 cycle 1 the worker wrote src/split.py and test_manual.py, then
    concluded with the single sentence "Let me run the manual test to verify the
    implementation:". That sentence became work-summary.txt.
    _extract_deliverables returned the empty set, and the syntax, pytest and
    read-evidence gates all no-opped. The reviewer, reading the manifest,
    reported that split.py "was not found in the expected location" — of a file
    that existed. This is the vacuous-pass condition change-a2f9c4d1 set out to
    close, reached through the one worker exit that change did not touch.
    change-f5c28a04's _manifest_written flag is set unconditionally on this
    path, so the exhaustion exit's freshness test would also be satisfied by a
    non-manifest. Observed twice in one run (cycles 1 and 3).

    (N2) Write-scope validation stops at the first path argument.
    _validate_write_scope extracts `path or file_path or destination` and tests
    that one value. For a move or rename supplying its source as `path` and its
    destination as `destination` or `new_path`, only the source is tested, so a
    call relocating a file out of the project root passes the gate. F4's
    containment guarantee does not hold for the move/rename members of
    _WRITE_TOOLS. change-f5c28a04 examined this exact argument ordering and
    corrected the manifest-construction side of it only.

    (N3) Leading-token strip applied to verdict-free feedback. _strip_verdict
    falls back to dropping the message's first whitespace-delimited token when
    no isolated verdict line is present. That fallback is correct for the
    'REVISE: ...' form, but it also fires for a reviewer message containing no
    verdict at all — which still reaches the path, because _normalize_verdict
    defaults to REVISE. The next worker then reads feedback with an ordinary
    word of prose removed. change-3b9e6d72 claims REVISE bodies are "no longer
    mangled by an inapplicable leading-token strip"; that holds only when a
    verdict is present.

    (N4) Non-interactive continue prompt blocks forever. On reaching
    max_iterations without SHIP, run_loop calls input() to offer another block
    of iterations, guarded only against EOFError and KeyboardInterrupt. Launched
    through ael-mcp the process is detached and its stdin is neither a terminal
    nor closed, so input() blocks indefinitely. Run 8c2040d3 logged "max
    iterations 3 reached without SHIP" at 12:53:26 and never reached "AEL end";
    ael_status reported pid_alive true thereafter, with the MCP servers still
    held open.

affected_scope:
  components:
    - name: "orchestrator (run_phase F13 exit, _validate_write_scope, _strip_verdict, run_loop continue prompt)"
      file_path: "ai/ael/src/orchestrator.py"
  designs: []
  version: "current"

reproduction:
  prerequisites: "Ralph Loop against dev/smoke; oMLX with Devstral 8-bit worker and Magistral 8-bit reviewer; ael-mcp for the detached-launch condition."
  steps:
    - "N1: run --mode loop; observe a cycle whose worker writes deliverables and then ends on a final response that names none of them"
    - "N1: observe '_extract_deliverables: 0 files from work-summary.txt' and 'pytest gate: no deliverables — gate is no-op' in the same cycle"
    - "N1: observe the reviewer reporting the deliverable absent"
    - "N2: call _validate_write_scope('move_file', {'path': '<inside>', 'destination': '<outside>'}, project_root) and observe None"
    - "N3: call _strip_verdict on a message containing no verdict token and observe the first word removed"
    - "N4: launch via ael-mcp with max_iterations small enough to exhaust; observe no 'AEL end' line and pid_alive true indefinitely"
  frequency: "N1 twice in three cycles of one run; N2/N3 deterministic; N4 always, on any detached run reaching max_iterations"
  reproducibility_conditions: >
    N1 requires the worker to end on a final response rather than the
    work-complete signal or budget exhaustion, and that response not to name its
    own output. N4 requires a non-terminal stdin, which is the ael-mcp launch
    condition and not the terminal launch condition.
  preconditions: ""
  test_data: "dev/smoke, dev/smoke-n1"
  error_output: |
    2026-07-29 12:42:00,637 INFO  work phase rc=0
    2026-07-29 12:42:00,638 DEBUG _extract_deliverables: 0 files from work-summary.txt
    2026-07-29 12:42:00,638 DEBUG pytest gate: no deliverables — gate is no-op
    2026-07-29 12:42:31,391 DEBUG verdict from reviewer final message: 'REVISE: The required file `split.py` was not found in the ex' -> 'REVISE'
    2026-07-29 12:53:26,510 WARNING max iterations 3 reached without SHIP
    (no further log lines; process alive)

behavior:
  expected: >
    (N1) The reviewer and the three gates receive a manifest of this cycle's
    actual output at every non-blocked worker exit, including the
    final-response exit.
    (N2) Every path a write tool touches is inside project_root, or the call is
    rejected.
    (N3) Feedback text is altered only where a verdict declaration is actually
    removed.
    (N4) A detached run terminates on its own budget rather than waiting on a
    terminal that is not there.
  actual: >
    (N1) A one-sentence final response becomes the manifest; all three gates
    no-op; the reviewer is misinformed about what exists.
    (N2) A move out of the project root passes scope validation.
    (N3) A verdict-free message loses its first word.
    (N4) The process blocks in input() and never exits.
  impact: >
    N1 is the governance-integrity concern: gates that appear to have passed on
    the current cycle's work have in fact examined nothing, and the reviewer
    adjudicates against a manifest that contradicts the filesystem. It is also
    the proximate reason no SHIP was reached in either run of this session.
    N2 defeats F4 containment for four of the tools in _WRITE_TOOLS. N3 degrades
    feedback quality in a minority of cycles. N4 leaves orphaned processes
    holding MCP servers and makes ael_status's pid_alive meaningless as a
    completion signal.
  workaround: >
    N1: none within the loop; the operator must read the log rather than the
    manifest. N4: kill the orphaned pid manually.

environment:
  python_version: "3.11"
  os: "macOS 14+ / Apple Silicon"
  dependencies: []
  domain: "tactical"

analysis:
  root_cause: >
    N1: F13 conflates two different artefacts — the worker's account of its
    reasoning and the machine-readable manifest the gates consume — and
    persists the first as though it were the second. change-a2f9c4d1 added
    synthesis at the three exits where no summary existed, and correctly
    declined to overwrite one that did; the final-response exit is the case
    where a summary exists but is not a manifest, which neither change
    considered.
    N2: an `or` chain returns one value, but containment is an obligation on
    every path in the call. The chain was adequate while every write tool
    carried exactly one meaningful path.
    N3: the fallback was carried over unchanged from the pre-3b9e6d72 code,
    where it was the only extraction rule and the leading token was assumed to
    be the verdict. With the isolated-line pass ahead of it, the fallback is
    now reached in a case it was never written for.
    N4: the guard anticipates a closed stdin, not an open one that never
    produces a line. Detached execution via ael-mcp postdates the prompt.
  technical_notes: >
    N1 was not visible to the P08 audit because the one surviving log at that
    time (run a2d10058) reached its exits by budget exhaustion, where synthesis
    fires. It became observable only once phase_max_iterations was raised
    enough for the worker to finish deliberately.
  related_issues:
    - issue_ref: "issue-a2f9c4d1"
      relationship: "extends — closes the vacuous-gate condition at the one worker exit a2f9c4d1 did not cover"
    - issue_ref: "issue-f5c28a04"
      relationship: "related — N1 defeats the per-cycle manifest guarantee that change completes; N2 is the unexamined half of the argument ordering it corrected"
    - issue_ref: "issue-3b9e6d72"
      relationship: "related — N3 is a residual of that change's stated benefit"
    - issue_ref: "issue-c7e9a1b3"
      relationship: "related — worker tool-call inefficiency is the other reason no SHIP was reached; out of scope here"

resolution:
  assigned_to: "Claude (Cowork session, Opus 5) — direct implementation"
  target_date: "2026-07-29"
  approach: >
    Append rather than replace at the F13 exit; validate every path argument;
    condition the leading-token strip on the token being a verdict; prompt only
    when stdin is a terminal.
  change_ref: "change-d1f4a83b"
  resolved_date: "2026-07-29"
  resolved_by: "Claude (Cowork session, Opus 5)"
  fix_description: >
    New _append_observed_manifest appends an observed-write manifest to
    work-summary.txt after the F13 write, only when deliverables were observed
    and the worker's own text names none of them. _validate_write_scope now
    tests every present value among path, file_path, destination and new_path.
    _strip_verdict drops the leading token only when that token normalises to a
    verdict. run_loop's continue prompt is taken only when sys.stdin.isatty().

verification:
  verified_date: "2026-07-29"
  verified_by: "Claude (Cowork session, Opus 5) — implementer and verifier are the same session"
  test_results: >
    Recorded in change-d1f4a83b. Isolated execution of all four changed units
    against synthetic inputs, plus live run 7135e75d against dev/smoke-n1.
  closure_notes: >
    Left open at the time of self-verification. Implementer and verifier were
    the same session, and N1 is a governance-integrity fix in the same code
    region that had produced defects on three consecutive review passes.
    Closed at William Watson's explicit instruction on 2026-07-29 (dev/audit
    review), overriding the stated independent-verification precondition; see
    change-d1f4a83b operator_closure_2026_07_29. N1 remains unconfirmed live
    and is recorded in dev/task.md.

prevention:
  preventive_measures: >
    Every defect in this issue was found by exercising a path no prior run had
    reached, not by re-reading the diff. The exits of run_phase should be
    enumerated and each one exercised at least once before any change to
    manifest handling is closed.
  process_improvements: ""

verification_enhanced:
  verification_steps: []
  verification_results: ""

traceability:
  design_refs: []
  change_refs:
    - "change-d1f4a83b"
  test_refs:
    - "dev/smoke"
    - "dev/smoke-n1"

notes: >
  Raised during the autonomous remediation session of 2026-07-29 described in
  dev/cowork-remediation-prompt-2026-07-29.md §7.0. Evidence is recorded in
  dev/audit/report-2026-07-29-cowork-remediation.md.

loop_context:
  was_loop_execution: true
  blocked_at_iteration: 3
  failure_mode: "max iterations 3 reached without SHIP; process then blocked in input()"
  last_review_feedback: "no verdict source — defaulting to REVISE"

version_history:
  - version: "1.0"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Initial issue from independent verification of change-3b9e6d72, change-f5c28a04 and change-8c1a4f5e"
  - version: "1.1"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Closed at operator instruction (dev/audit review); closure_notes updated to record the operator closure decision and the items (N1 live confirmation) still outstanding"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised resolved -> closed: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.3"
  schema_type: "t03_issue"
```
