Created: 2026 July 29

```yaml
change_info:
  id: "change-e4b1a7c3"
  title: "Correct propagate.sh state exclude; protect and seed ai/context.md"
  date: "2026-07-29"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-e4b1a7c3"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-e4b1a7c3"
  description: >
    Stop propagating the source repository's AEL runtime state, and stop
    overwriting downstream project context.md files, without regressing
    new-project provisioning.

scope:
  summary: >
    Three edits to bin/propagate.sh. Replace the stale --exclude='ael/state/'
    with the anchored post-restructure path /state/. Add /context.md to the
    exclude list. Add a second rsync pass, --ignore-existing, that seeds
    ai/context.md only when the target does not already have one.
  affected_components:
    - name: "propagate.sh"
      file_path: "bin/propagate.sh"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "Aligning config.yaml to the same seeding pattern — its plain exclusion works as intended and manual migration is established practice"
    - "Auditing GTach, solax-modbus and e-Paper-IP-Display for prior damage — recorded in issue-e4b1a7c3 notes as follow-up"
    - "bin/sync-skel.sh — retired deprecation stub, unaffected"
    - "The deployed ael-mcp stale-path defect — different repository, separate triple"

rational:
  problem_statement: >
    Propagation copies live Ralph state into every target and silently replaces
    any filled-in downstream context.md with the framework placeholder
    template. A propagated work-summary.txt suppresses change-a2f9c4d1's
    synthesis path; a propagated audit-index.md would switch recipe selection.
  proposed_solution: >
    Correct the exclude to the current path and treat context.md as
    project-specific. Seed rather than overwrite, so a newly provisioned
    project still receives the template.
  alternatives_considered:
    - option: "Exclude context.md with no seeding pass"
      reason_rejected: >
        Regresses new-project provisioning — the target would never receive
        the template, and ralph-work.yaml PROCEDURE step 1 directs the worker
        to read a file that would not exist.
    - option: "Unanchored 'state/' exclude"
      reason_rejected: >
        Matches at any depth, so a future ai/<component>/state/ that ought to
        propagate would be silently dropped. Anchoring to /state/ targets the
        one canonical location.
    - option: "Leave 'ael/state/' in place alongside the new pattern"
      reason_rejected: >
        The path has not existed since the 2026-06-16 restructure. Retaining
        it implies a location that is gone and invites the same confusion again.
  benefits:
    # Correction (2026-07-29, change-8c1a4f5e): the original wording here read
    # "Removes the manual post-propagation repair step the dev/smoke harness
    # currently requires." True in general, but the seeding pass this change
    # added was itself unreachable when context.md was the target's only
    # outstanding difference from source — precisely the state a project is in
    # immediately after a propagation that copied everything else. Found by
    # P08 audit audit-p08-20260729 (F4); fixed by change-8c1a4f5e.
    - "Runtime state no longer crosses the propagation boundary"
    - "Downstream project context is preserved across framework updates"
    - "New projects still receive the context.md template, except in the narrow case corrected by change-8c1a4f5e (F4)"
    - "Removes the manual post-propagation repair step the dev/smoke harness currently requires"
  risks:
    - risk: "A target relying on receiving an updated context.md template will no longer get one"
      mitigation: "Intended — context.md is project-specific. Template changes are consumed by new projects; existing projects update deliberately."
    - risk: "Seeding pass adds a second rsync invocation"
      mitigation: "Single file, --ignore-existing, negligible cost; runs only after the main pass succeeds."
    - risk: "Anchored /state/ misses a non-canonical state location"
      mitigation: "state_dir is configurable, but ai/state/ralph is the documented default and the only location in the framework tree. Non-default layouts remain the operator's responsibility."

technical_details:
  current_behavior: >
    EXCLUDES contains --exclude='ael/state/', a pre-restructure path matching
    nothing. ai/state/ therefore propagates. context.md is not excluded and
    overwrites the target's copy on every run.
  proposed_behavior: >
    EXCLUDES contains --exclude='/state/' and --exclude='/context.md'. After
    the main rsync, a second pass copies ai/context.md with --ignore-existing.
  implementation_approach: >
    1. Replace the ael/state/ entry with '/state/', comment updated to name
    the post-restructure path.
    2. Add '/context.md' to EXCLUDES with a comment classifying it alongside
    config.yaml.
    3. After the main rsync, run
    rsync -av --ignore-existing "${AI_SRC}/context.md" "${PROJECT_AI}/"
    and report whether it seeded or left an existing file alone.
  code_changes:
    - component: "propagate.sh"
      file: "bin/propagate.sh"
      change_summary: >
        EXCLUDES corrected and extended; context.md seeding pass added after
        the main propagation.
      functions_affected: []
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal: []
  external:
    - library: "rsync"
      version_change: "none — --ignore-existing is long-standing"
      impact: "none"
  required_changes: []

testing_requirements:
  test_approach: >
    Live propagation to dev/smoke with a populated source ai/state/ and a
    filled-in target context.md, plus bash -n syntax validation.
  test_cases:
    - scenario: "Source has ai/state/ralph/ populated"
      expected_result: "Target receives no ai/state/ directory"
    - scenario: "Target has a filled-in ai/context.md"
      expected_result: "Target context.md unchanged after propagation"
    - scenario: "Target has no ai/context.md"
      expected_result: "Template seeded by the second pass"
    - scenario: "Target ai/ael/config.yaml present"
      expected_result: "Unchanged — existing exclusion behaviour"
    - scenario: "Framework source files changed"
      expected_result: "Propagated normally; preview and confirmation flow unchanged"
  regression_scope:
    - "Preview/confirmation flow unchanged"
    - "config.yaml, workspace/, dashboard-alerts.md exclusions unchanged"
    - "set -euo pipefail behaviour unchanged"
  validation_criteria:
    - "bash -n reports no syntax errors"
    - "No ai/state/ in target after propagation"
    - "Filled-in target context.md survives propagation"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Claude Desktop implements directly via Filesystem MCP per William Watson's instruction, 2026-07-29"
      owner: "Claude Desktop (Opus 5)"
  rollback_procedure: "git revert bin/propagate.sh to prior version"
  deployment_notes: >
    Takes effect on the next propagation. Downstream projects should be
    checked for prior damage per issue-e4b1a7c3 notes.

verification:
  implemented_date: "2026-07-29"
  implemented_by: "Claude Desktop (Opus 5)"
  verification_date: "2026-07-29"
  verified_by: "Claude (Cowork remediation session, Opus 5) — independent of the implementing session"
  test_results: >
    bash -n clean and set -euo pipefail present, both re-checked. All five test
    cases and all three validation criteria exercised live against a synthetic
    source tree carrying a populated ai/state/, an ai/ael/config.yaml, an
    ai/workspace/ and an ai/dashboard-alerts.md.

    Source ai/state/ populated: the pre-change script transferred state/leak.txt
    into the target; the current script excludes it. Corroborated in the
    framework's own use — propagation to dev/smoke transferred only
    ai/ael/src/orchestrator.py and created no ai/state in the target.

    Filled-in target ai/context.md: retained byte-for-byte, with the script
    reporting "context.md: existing project copy preserved."

    Target with no ai/context.md: seeded byte-identical to the template. The
    narrow case audit finding F4 identified as failing here is supplied by
    change-8c1a4f5e, independently verified and closed alongside this change.

    Target ai/ael/config.yaml: unchanged. Framework source files changed:
    propagated normally, with the preview and confirmation flow unaltered and
    declining at the prompt producing neither transfer nor seed.
  issues_found: []

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-a2f9c4d1"
      relationship: "related — propagated stale state suppresses its synthesis path"
    - change_ref: "change-8c1a4f5e"
      relationship: "corrective successor — closes F4 (seeding pass unreachable in its own use case) and two style findings from audit-p08-20260729"
  related_issues:
    - issue_ref: "issue-e4b1a7c3"
      relationship: "resolves"

notes: >
  Implemented directly by the Strategic Domain at William Watson's
  instruction. P08 strategic audit by an independent session remains
  outstanding and is required before closure.

version_history:
  - version: "1.0"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Initial change document — approved for direct implementation"
  - version: "1.1"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Corrected an overstated benefit per P08 audit audit-p08-20260729 finding F4 (seeding pass unreachable when context.md was the target's only outstanding difference); delivered by change-8c1a4f5e"
      - "Added change-8c1a4f5e to traceability.related_changes as the corrective successor"
  - version: "1.2"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Independently verified live in the Cowork remediation session; all five test cases and all three validation criteria re-derived, including a pre-change/post-change comparison of the state leak; change-8c1a4f5e closed F4; status closed"
  - version: "1.3"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised closed -> verified: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction; asserts no verification beyond what this document already records."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
