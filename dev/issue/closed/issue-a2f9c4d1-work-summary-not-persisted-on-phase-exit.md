Created: 2026 July 29

```yaml
issue_info:
  id: "issue-a2f9c4d1"
  title: "Worker phase discards work-summary.txt on non-final-response exits; iteration exhaustion aborts the run before review"
  date: "2026-07-29"
  reporter: "William Watson"
  status: "closed"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-a2f9c4d1"
    change_iteration: 1

source:
  origin: "live_execution"
  test_ref: "dev/smoke run fc55ecf7 (2026-07-29 07:19), run 30a648c7 (2026-07-29 07:47)"
  description: >
    Two live Ralph Loop runs against dev/smoke were executed to validate the
    full ael-mcp path. In both, the worker produced a correct implementation of
    the task deliverable (src/split.py) and the run nonetheless terminated with
    rc=1 having shipped nothing. Root cause is two independent defects in
    run_phase and run_loop, both centred on work-summary.txt.

    run_phase persists work-summary.txt at exactly one of its four exits: the
    normal final-response path (F13, line ~1069). The wall-clock cap exit (line
    ~952), the work-complete.txt detection exit (line ~1267), and the iteration
    exhaustion exit (line ~1272) all return without writing it. Because
    _extract_deliverables reads work-summary.txt to build the deliverable set,
    a phase exiting by any of those three routes leaves real deliverables on
    disk with no manifest — silently disabling the read-evidence gate, the
    syntax gate, and the pytest gate, all of which key on that set.

    Separately, iteration exhaustion returns rc=1, and run_loop aborts on any
    non-zero work-phase rc (line ~1765). A worker that produced correct,
    complete deliverables but ran out of its tool-call budget therefore never
    reaches the review phase at all.

affected_scope:
  components:
    - name: "orchestrator (run_phase, run_loop)"
      file_path: "ai/ael/src/orchestrator.py"
  designs: []
  version: "current"

reproduction:
  prerequisites: "Ralph Loop (--mode loop), any task whose worker phase exits by iteration exhaustion, wall-clock cap, or work-complete detection."
  steps:
    - "Seed a project with a task requiring one or more file writes"
    - "Set loop.phase_max_iterations low enough that the worker writes deliverables but does not reach a final response"
    - "Run --mode loop"
    - "Observe: deliverables exist on disk; work-summary.txt is absent; run exits rc=1 without a review phase"
  frequency: "always"
  reproducibility_conditions: "Independent of model. Observed with Devstral-2512-8bit worker at phase_max_iterations 20 and 8."
  preconditions: ""
  test_data: "dev/smoke — split_into_chunks task"
  error_output: |
    2026-07-29 07:50:38,350 WARNING max iterations 8 reached
    2026-07-29 07:50:38,350 INFO work phase rc=1
    2026-07-29 07:50:38,351 INFO AEL end rc=1

behavior:
  expected: >
    A worker phase that produced deliverables presents a manifest to the review
    phase regardless of how the phase terminated, and the reviewer adjudicates
    the work. Iteration exhaustion is a budget boundary, not a failure — the
    reviewer decides whether the work is complete.
  actual: >
    work-summary.txt is written only on the final-response exit. On the other
    three exits the manifest is absent, so all deliverable-keyed gates no-op.
    On iteration exhaustion the run additionally aborts before review.
  impact: >
    Correct, complete work is discarded. Worse, on the two exits that do reach
    review (wall-clock cap, work-complete), the review proceeds with an empty
    deliverable set, so the read-evidence, syntax and pytest gates pass
    vacuously — a SHIP can be accepted with no gate having examined anything.
  workaround: "Raise phase_max_iterations until the worker reaches a final response. Unreliable — run fc55ecf7 had 12 spare iterations and still never wrote the summary."

environment:
  python_version: "3.11"
  os: "macOS 14+ / Apple Silicon"
  dependencies: []
  domain: "tactical"

analysis:
  root_cause: >
    Two defects. (1) The work-summary.txt persistence step is attached to a
    single exit path rather than to phase termination, so three of four exits
    bypass it. (2) Iteration exhaustion is classified as a phase failure
    (rc=1) rather than a budget boundary, and run_loop treats any non-zero
    work-phase rc as fatal.
  technical_notes: >
    ralph-work.yaml PROCEDURE step 6 instructs the worker to write
    work-summary.txt itself, and a compliant worker reaching a final response
    makes the F13 fallback redundant. Both observed runs show the instruction
    is not reliably followed: run fc55ecf7 received an explicit REVISE naming
    the missing file and still did not write it across a further twelve
    iterations. This is the project's standing instruction-is-not-enforcement
    pattern, and the remedy follows the established precedent — deterministic
    orchestrator-side handling rather than stronger recipe wording.

    Synthesis must be conservative to avoid masking genuine failure: never
    overwrite an existing summary, and write nothing when no successful
    non-state writes were observed, so a phase that produced nothing still
    presents no manifest and still fails.
  related_issues:
    - issue_ref: "issue-e2b8046c"
      relationship: "related — signal files excluded from the deliverable list"
    - issue_ref: "issue-d7f4a1c8"
      relationship: "related — read-evidence gate consumes the deliverable set this issue leaves empty"
    - issue_ref: "issue-5bdc2d9b"
      relationship: "related — pytest gate consumes the same deliverable set"

resolution:
  assigned_to: "Claude Desktop (Opus 5) — direct implementation"
  target_date: "2026-07-29"
  approach: "Orchestrator-side work-summary synthesis at all non-blocked exits; reclassify productive iteration exhaustion as rc=0"
  change_ref: "change-a2f9c4d1"
  resolved_date: "2026-07-29"
  resolved_by: "Claude Desktop (Opus 5)"
  fix_description: >
    Implemented under change-a2f9c4d1 (_synthesize_work_summary; write-target
    tracking; synthesis at the wall-clock, work-complete and exhaustion exits;
    conditional exhaustion rc). Completed by change-f5c28a04 (per-cycle
    manifest clear, phase-own exhaustion rc, move/rename destination) and
    change-d1f4a83b (observed-write manifest at the final-response exit).

verification:
  verified_date: "2026-09-23"
  verified_by: "Claude (Cowork, Opus 5.5) — static verification only"
  test_results: >
    ai/ael/src/orchestrator.py compiles. Source inspection confirms all five
    implementation steps of change-a2f9c4d1 are present in their corrected
    form: helper at line 151, _written_paths at 1162, write-target recording
    at 1384, synthesis at the wall-clock (1192), work-complete (1544) and
    exhaustion (1563) exits, each guarded by is_worker_phase; the exhaustion
    rc is derived from this phase's own synthesis or manifest write.
  closure_notes: >
    Closed at William Watson's direction on 2026-09-23, consistent with the
    operator closures of successors f5c28a04 and d1f4a83b on 2026-07-29. Not
    verified end-to-end: no live SHIP has been observed, and the unexercised
    test cases carried by change-f5c28a04 remain unexercised. These are
    recorded in dev/backlog.md, not represented as satisfied.

prevention:
  preventive_measures: >
    Live Ralph Loop execution surfaced both defects immediately; neither was
    visible to inline source review across prior audits. Live smoke testing
    should precede closure for gate-related changes.
  process_improvements: ""

verification_enhanced:
  verification_steps: []
  verification_results: ""

traceability:
  design_refs: []
  change_refs:
    - "change-a2f9c4d1"
  test_refs:
    - "dev/smoke"

notes: >
  Discovered during the dev/smoke harness validation that also produced the
  reviewer-model comparison. Three unrelated defects were logged in the same
  session and are not addressed here: bin/propagate.sh excludes the stale path
  ael/state/ rather than state/, and does not exclude ai/context.md; and the
  deployed ael-mcp build resolves state to .ael/ralph rather than
  ai/state/ralph, breaking ael_status.

  Update (2026-07-29, P08 audit audit-p08-20260729): change-a2f9c4d1 as
  implemented did not fully close this issue. The manifest it introduced was
  cleared only once per run rather than once per cycle, so from loop cycle 2
  onward a manifest left by a prior cycle suppressed synthesis and was
  re-presented to the gates as though it were current — live-confirmed in run
  a2d10058, which contains exactly one write call, in cycle 1, yet returned
  rc=0 in cycle 2 with zero writes. A related defect (move/rename deliverables
  recorded at their pre-move location) was found in the same review. Both are
  addressed by change-f5c28a04, which narrows work-summary.txt's lifetime to a
  single cycle and derives the exhaustion return code from the phase's own
  outcome rather than file presence. This issue remains open pending
  end-to-end verification of change-f5c28a04, which is itself blocked on
  change-3b9e6d72 (no reviewer verdict was reachable as SHIP before that fix).

loop_context:
  was_loop_execution: true
  blocked_at_iteration: 8
  failure_mode: "work phase rc=1 on iteration exhaustion; no review phase reached"
  last_review_feedback: "REVISE: Missing work-summary.txt. Worker must describe their outputs."

version_history:
  - version: "1.0"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Initial issue from live dev/smoke runs fc55ecf7 and 30a648c7"
  - version: "1.1"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "P08 audit audit-p08-20260729 found change-a2f9c4d1 incompletely closed this issue (stale-manifest and move/rename recording defects); corrective change-f5c28a04 implemented; issue remains open pending that change's end-to-end verification, itself blocked on change-3b9e6d72"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Closed at operator direction after static verification; status investigating -> closed; resolution and verification recorded; end-to-end verification debt carried to dev/backlog.md"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.3"
  schema_type: "t03_issue"
```
