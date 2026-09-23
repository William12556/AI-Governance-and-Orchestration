Created: 2026 July 29

```yaml
change_info:
  id: "change-8c1a4f5e"
  title: "Evaluate the context.md seed condition before the preview early exit; anchor path-specific excludes; drop redundant --ignore-existing"
  date: "2026-07-29"
  author: "William Watson"
  status: "verified"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-8c1a4f5e"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-8c1a4f5e"
  description: >
    Make the context.md seeding pass reachable in the case it exists to serve,
    and tidy two adjacent latent defects in the same region of the script.

scope:
  summary: >
    Compute NEEDS_SEED before the preview's change detection and include it in
    the early-exit condition, so a target differing only by a missing
    ai/context.md is recognised as work to be done. Report the pending seed in
    the preview. Key the seeding branch on NEEDS_SEED and drop the
    --ignore-existing flag rendered redundant by that guard. Anchor config.yaml,
    workspace/ and dashboard-alerts.md to the transfer root.
  affected_components:
    - name: "propagate.sh (EXCLUDES array)"
      file_path: "bin/propagate.sh"
      change_type: "modify"
    - name: "propagate.sh (preview and early exit)"
      file_path: "bin/propagate.sh"
      change_type: "modify"
    - name: "propagate.sh (seeding pass)"
      file_path: "bin/propagate.sh"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "Aligning config.yaml to the same seed-when-absent treatment as context.md — deliberately left as plain exclusion with manual migration, per issue-e4b1a7c3"
    - "The confirmation prompt and the main rsync invocation — unchanged"
    - "Remediating downstream projects whose ai/context.md is the unfilled template — an operational task, not a script defect"

rational:
  problem_statement: >
    CHANGES is computed with EXCLUDES, which contains /context.md. A target
    differing from the framework only by a missing context.md therefore reports
    no changes and exits before the seeding pass — the exact state a project
    occupies after a propagation that copied everything else. The pass is
    unreachable in its own use case.
  proposed_solution: >
    Decide the seed condition from the file's presence in the target, which is
    the actual precondition, and evaluate it before the early exit rather than
    after it. Surface it in the preview so the operator sees what will happen
    before confirming.
  alternatives_considered:
    - option: "Compute CHANGES without the /context.md exclusion"
      reason_rejected: >
        The dry run would then list context.md as a pending transfer on every
        target with a filled-in copy, which is precisely what the change would
        not do — a preview that misreports the action is worse than the defect.
    - option: "Move the seeding pass above the early exit"
      reason_rejected: >
        Would seed before the operator confirms, and before the main transfer,
        inverting the script's order of consent and action.
    - option: "Drop the early exit entirely"
      reason_rejected: >
        It is useful: it distinguishes a no-op run from one requiring
        confirmation. Only its condition was incomplete.
  benefits:
    - "New projects reliably receive the context.md template regardless of how current their other framework files are"
    - "The preview states the pending seed, so the operator confirms what will actually occur"
    - "Anchored excludes match only their intended files rather than any same-named file at any depth"
    - "One redundant flag removed"
  risks:
    - risk: "Anchoring workspace/ newly propagates into a downstream ai/doc/workspace/ or similar"
      mitigation: >
        Intended: only ai/workspace/ is project-local governance. No downstream
        project currently has a nested directory of that name; verified against
        GTach, solax-modbus and e-Paper-IP-Display.
    - risk: "Anchoring config.yaml to /ael/config.yaml misses a config.yaml elsewhere under ai/"
      mitigation: "ai/ael/config.yaml is the only one in the framework tree. Confirmed by inspection."
    - risk: "The preview now prints a seed line that is not rsync itemize output and may confuse parsing"
      mitigation: "The preview is read by a human at a confirmation prompt; nothing parses it."

technical_details:
  current_behavior: >
    EXCLUDES anchors /context.md and /state/ but not config.yaml, workspace/ or
    dashboard-alerts.md. CHANGES is computed with EXCLUDES; an empty CHANGES
    exits 0 with 'Target is up to date'. The seeding pass sits after the main
    rsync and tests for the file's presence, using rsync --ignore-existing
    inside the absence branch.
  proposed_behavior: >
    NEEDS_SEED is computed from the target's context.md before CHANGES. The
    early exit requires both an empty CHANGES and NEEDS_SEED false. The preview
    prints the file list when non-empty, a '(no framework files differ)' note
    otherwise, and a seed line when NEEDS_SEED is true. The seeding branch is
    keyed on NEEDS_SEED and copies without --ignore-existing. The three
    path-specific excludes are anchored, with a comment recording why the
    remaining unanchored patterns stay that way.
  implementation_approach: >
    1. Anchor config.yaml to /ael/config.yaml, workspace/ to /workspace/ and
    dashboard-alerts.md to /dashboard-alerts.md; add a comment distinguishing
    path-specific from genuinely depth-independent patterns.
    2. Before the CHANGES computation, set NEEDS_SEED true or false from
    [[ -f "${PROJECT_AI}/context.md" ]].
    3. Change the early exit to require -z CHANGES and NEEDS_SEED false.
    4. Print CHANGES when non-empty, otherwise a note; print a seed line when
    NEEDS_SEED is true.
    5. Key the seeding branch on NEEDS_SEED, drop --ignore-existing, and extend
    the seeded message to prompt the operator to fill the template in.
  code_changes:
    - component: "propagate.sh"
      file: "bin/propagate.sh"
      change_summary: >
        NEEDS_SEED computed before the preview; early exit conditioned on both
        signals; preview reports the pending seed; seeding branch keyed on
        NEEDS_SEED without --ignore-existing; three excludes anchored.
      functions_affected: []
      classes_affected: []
  data_changes: []
  interface_changes:
    - "A run whose only pending action is the context.md seed now prompts for confirmation rather than exiting 0 silently"

dependencies:
  internal:
    - component: "change-e4b1a7c3 exclude list and seeding pass"
      impact: "Both retained; the seed condition is relocated and the exclude list anchored"
  external:
    - "rsync"
  required_changes: []

testing_requirements:
  test_approach: >
    bash -n, then execution against three scratch targets covering the defect
    case, the no-op case and the new-project case, plus an idempotency re-run.
  test_cases:
    - scenario: "Target current except ai/context.md absent"
      expected_result: "Preview reports '(no framework files differ)' and a pending seed; on confirmation context.md is written identically to the template"
    - scenario: "Target fully current including context.md"
      expected_result: "'Target is up to date. No changes to apply.', exit 0"
    - scenario: "Empty target"
      expected_result: "Full file list plus pending seed; both applied on confirmation"
    - scenario: "Re-run immediately after seeding"
      expected_result: "Up to date; nothing further applied"
    - scenario: "Declining at the confirmation prompt"
      expected_result: "'Aborted.'; neither transfer nor seed occurs"
  regression_scope:
    - "Main rsync invocation and confirmation flow unchanged"
    - "/state/ and /context.md exclusions unchanged"
    - "An existing filled-in downstream context.md is still never overwritten"
  validation_criteria:
    - "bash -n reports no syntax errors"
    - "set -euo pipefail preserved"
    - "A filled-in target context.md survives propagation unchanged"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Claude Desktop implements directly via file tools (no Claude Code, no AEL) per William Watson's instruction, 2026-07-29"
      owner: "Claude Desktop (Opus 5)"
  rollback_procedure: "git revert the commit."
  deployment_notes: >
    This script is the propagation mechanism itself and is not propagated.
    It should be committed before the next downstream propagation so that
    change-3b9e6d72 and change-f5c28a04 reach targets under corrected excludes.

verification:
  implemented_date: "2026-07-29"
  implemented_by: "Claude Desktop (Opus 5)"
  verification_date: "2026-07-29"
  verified_by: "Claude (Cowork remediation session, Opus 5) — independent of the implementing session"
  test_results: >
    Verified independently and live, re-derived against the script rather than
    accepted from the implementing session's record. bash -n clean;
    set -euo pipefail present.

    Case (a), the F4 precondition proper — target identical to source with
    timestamps preserved so the dry run yields no changes, and context.md
    absent: preview prints "(no framework files differ)" and
    "seed         context.md (absent in target)", and on confirmation writes a
    context.md byte-identical to the template. The same input run against a
    reconstructed e4b1a7c3-only script prints "Target is up to date. No changes
    to apply." and exits without seeding, so the defect and its correction are
    demonstrated on identical input.

    Case (b) fully current: up to date, exit 0, target context.md left with its
    downstream content. Case (c) empty target: full file list plus the seed
    line, both applied. Case (d) re-run after (a): up to date. Case (e)
    declining: "Aborted.", neither transfer nor seed occurs.

    Anchoring, previously inspection-only: the synthetic source carried
    ai/doc/config.yaml and ai/doc/workspace/note.md alongside ai/ael/config.yaml
    and ai/workspace/gov.md. Case (c) transferred the two nested files and
    excluded the two anchored ones — the behavioural difference anchoring exists
    to produce. ai/state/ and ai/dashboard-alerts.md excluded in the same run.

    Live in the framework's own use: propagation to dev/smoke transferred only
    ai/ael/src/orchestrator.py, preserved the target's filled-in context.md, and
    created no ai/state in the target.
  issues_found: []

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-e4b1a7c3"
      relationship: "corrects — that change introduced the exclusion and the seeding pass whose interaction was defective"
  related_issues:
    - issue_ref: "issue-8c1a4f5e"
      relationship: "resolves"

notes: >
  Implemented directly by the Strategic Domain at William Watson's instruction.
  Remediation backlog §1.4, §4.3 and §4.4.

version_history:
  - version: "1.0"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Initial change document — implemented directly from dev/remediation-2026-07-29.md §1.4, §4.3, §4.4"
  - version: "1.1"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Independently verified live in the Cowork remediation session; the anchoring criterion recorded as inspection-only at implementation is now demonstrated behaviourally; issues_found cleared; status closed"
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
