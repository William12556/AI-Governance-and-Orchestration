Created: 2026 September 23

```yaml
change_info:
  id: "change-b170cf6a"
  title: "propagate.sh: back up local modifications; exact names; self-computed preview; re-plan after prompt; exit-contract fixes"
  date: "2026-09-23"
  author: "William Watson"
  status: "implemented"
  priority: "medium"
  iteration: 3
  coupled_docs:
    issue_ref: "issue-b170cf6a"
    issue_iteration: 3
    prompt_ref: "prompt-b170cf6a"

source:
  type: "issue"
  reference: "issue-b170cf6a"
  description: "Remediate follow-up audit findings N-01 to N-08."

scope:
  summary: "bin/propagate.sh; governance 10.5 P10.6; two guides."
  affected_components:
    - name: "propagate"
      file_path: "bin/propagate.sh"
      change_type: "modify"
    - name: "governance"
      file_path: "ai/governance.md"
      change_type: "modify"
    - name: "user guides"
      file_path: "docs/guide-install.md, docs/guide-getting-started.md"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "A directory at a declared file name (ai/context.md/) is emptied into ai-local/ and then seeded (N-07 part); no content lost; unchanged"
    - "Interrupt between log row and action: row is now written first, so an interrupted action leaves a row without a move (safe direction)"

rational:
  problem_statement: "See issue-b170cf6a."
  proposed_solution: >
    N-01: before the copy, copy each regular target file at a framework path
    whose content differs from the source and is not a framework version at
    that path to ai-local/ as 'local modification'. After an interactive
    confirmation, re-plan and refuse (exit 3) if the plan changed while the
    prompt was open. N-02: path existence is decided by exact byte comparison
    of directory entries, component by component. N-03: the preview and the
    up-to-date gate are computed with find and cmp; rsync output is not parsed.
    N-04: dirname -- throughout. N-05: RELOCATED.md reserved; suffix loops with
    timestamp, index and counter until free; a non-regular log path refuses
    before any change; droppings inside a type-conflict directory are relocated
    and empty blocking directories removed; a failed copy exits 4 with a
    message. N-06: labels use branches, tags, remotes and HEAD only. N-07: a
    candidate symlink that holds a declared path (ai/ael) refuses before any
    change; relative symlinks are noted in the log. N-08: every non-directory
    entry type is enumerated, so a FIFO at a framework path is relocated;
    control characters are replaced in displayed paths.
  alternatives_considered:
    - option: "Record N-01 as accepted behaviour"
      reason_rejected: "Operator decision 2026-09-23: back up edits."
  benefits:
    - "No project content lost, including local edits to framework files"
    - "No dependence on rsync output text"
  risks:
    - risk: "Backups of intentionally discarded edits accumulate in ai-local/"
      mitigation: "Labelled 'local modification'; deleted by the human after review"

technical_details:
  current_behavior: "Iteration 3 of change-c5270084."
  proposed_behavior: "As proposed_solution."
  implementation_approach: "plan() computes cands, backups and updates as NUL lists; records carry kind, path, destination, label, ignore flag and note."
  code_changes:
    - component: "propagate"
      file: "bin/propagate.sh"
      change_summary: "N-01 to N-08"
      functions_affected:
        - "plan, fingerprint, exact_exists, ancestor_conflict, dest_for, add_rec, disp (new); same_type, is_framework_version"
      classes_affected: []
  data_changes: []
  interface_changes:
    - "Preview lines 'add', 'update', 'relocate', 'backup'"
    - "Exit 3 when the target changes during the prompt or ai/ael is a symlink; exit 4 when the copy fails"
    - "RELOCATED.md label 'local modification'"

dependencies:
  internal:
    - component: "change-c5270084"
      impact: "Extends iteration 3"
  external:
    - "git, rsync, find, cmp"
  required_changes: []

testing_requirements:
  test_approach: "Follow-up audit experiments X1-X13 re-run on throwaway targets in the Cowork Linux VM."
  test_cases:
    - scenario: "X1 9.16 target with special names and a type conflict, LC_ALL=C"
      expected_result: "7 retired and 9 project entries relocated; T01-T08 present; exit 0"
    - scenario: "X2 local edit to primer.md; X2b older framework primer.md"
      expected_result: "Edit backed up then overwritten; older version not backed up"
    - scenario: "X3 file created at a framework path or a new path during the prompt"
      expected_result: "Exit 3, nothing applied, created files intact"
    - scenario: "X4 FIFO at workflow.md; X5 directory holding notes and droppings at workflow.md"
      expected_result: "Relocated; framework workflow.md in place; exit 0"
    - scenario: "X6 declared symlinks and logs/; X6b symlinked ai/ael holding config.yaml"
      expected_result: "Untouched; exit 3 before any change"
    - scenario: "X7 relocated .gitignore; X8 stash-only blob"
      expected_result: "Three warnings; label 'project content'"
    - scenario: "X9c RELOCATED.md candidate; X9d log path is a directory; X9e suffix exists"
      expected_result: "Suffixed; exit 3 before any change; next free suffix"
    - scenario: "X10 guards and empty ai/; X11 rsync output shim; X13 '-x.md' and '--'"
      expected_result: "Exit 2 / initialize; update applied; relocated, exit 0"
  regression_scope:
    - "change-07087e91 and change-c5270084 behaviour"
  validation_criteria:
    - "All test cases pass; bash -n passes"

implementation:
  effort_estimate: "small"
  implementation_steps:
    - step: "Claude (Cowork) implements directly at William Watson's instruction, 2026-09-23"
      owner: "Claude (Cowork, Opus 5.5)"
  rollback_procedure: "git revert of the implementing commit"
  deployment_notes: "Final re-check limited to iteration 2 and the macOS procedure (follow-up audit §8.0 plus ai/Templates/ and ai/Context.md cases) before the next downstream propagation."

iteration_2:
  source: "dev/audit/audit-b170cf6a-recheck-2026-09-23.md (A1-A7; operator decision 2026-09-23: fix causes, one final re-check limited to iteration 2 plus macOS procedure; close if nothing medium or higher)"
  changes:
    - "A1, A3, A4: the path-list re-plan is replaced by a snapshot of ai/ (declared paths included) and ai-local/ — names, symlink targets, file checksums — taken before the prompt and compared after; any difference exits 3 with nothing applied"
    - "A2: find runs to a file with its exit status checked; any enumeration error exits 3 before any change; declared directories (workspace, state, logs) are pruned and never read"
    - "A3: backups are written no-clobber (mktemp in the destination directory, cp, mv -n, verified); an existing file or symlink at the destination fails the run with exit 3"
    - "A5: labels and the local-modification test use only the history of the framework's checked-out HEAD"
    - "A6: a symlink at ai/context.md or ai/task.md refuses before any change; seeding never overwrites an existing file"
    - "A7: a candidate whose path differs from a declared path (or ael/) only by letter case refuses before any change"
  accepted:
    - "N-08 residual: C1 control bytes (0x80-0x9F) are not masked in displayed paths; effect depends on the terminal"
    - "A7 residual: a case-variant framework directory (e.g. ai/Templates/) on a case-insensitive file system causes its framework files to be relocated on every run; no content lost; documented in guide-install"
    - "Performance: ~11 s for 1,500 files in one non-declared directory under bash 5.1 (quadratic exact-name check); acceptable for current projects"

iteration_3:
  source: "dev/audit/audit-b170cf6a-final-2026-09-23.md (B1 medium, B2-B4 low); scope limited to snapshot(), its call site and the A6 refusal"
  b1_option: >
    Snapshot through the link. Every other step (-d guard, list0, rsync,
    seeding) already follows a symlinked ai/, and iterations 1 and 2 supported
    that layout; refusing it would remove a supported layout, which is outside
    the stated scope. The link target is also recorded, so retargeting ai/
    during the prompt is detected.
  changes:
    - "B1: snapshot() records the ai/ link target and then snapshots the linked directory; the -L record-only branch remains for ai-local/ (refused by check_dir_chain)"
    - "B2: in interactive mode (no --yes, stdin a terminal) SNAP_BEFORE is taken before plan; the non-TTY check uses the same INTERACTIVE flag"
    - "B3: snapshot() writes to a work file, checks every step (find, sort -z, readlink, cksum) and returns non-zero on failure; both call sites exit 3 via snapshot_failed with nothing applied; errors are no longer discarded"
    - "B4: context.md or task.md is refused only when it is a symlink with no regular file behind it (dangling, or pointing to a non-regular file); a symlink to an existing regular file is preserved; header comment and guide-install §3.3 updated; exit-code header notes the snapshot failure"
  behaviour_notes:
    - "Audit P-B2 as written (cksum shim editing on the first call) now edits before the baseline and before plan; the edit is backed up as 'local modification', exit 0, no loss."
  out_of_scope:
    - "Nested empty-directory exit 4 (P-N3); orphan .propagate-tmp file; accepted residuals (C1 bytes, ai/Templates/, performance)"
  open_findings:
    - id: "B5"
      raised_by: "Operator decision 2026-09-23 (previously a behaviour note of iteration 3)"
      location: "bin/propagate.sh snapshot() and its call sites"
      description: >
        Consequence of the B3 fail-closed snapshot: an interactive run exits 3
        before any change when any directory under ai/ or ai-local/ cannot be
        read, including one inside a declared path (audit case F3: mode 000
        state/x). Iteration 2 proceeded with exit 0. --yes runs are unchanged
        (proceed, exit 0).
      proposed_severity: "low (safe direction: nothing applied, no content lost; --yes works around it)"
      severity: "low (assigned by dev/audit/audit-b170cf6a-closure-2026-09-23.md)"
      disposition: "fixed"
      fix: >
        Fixed directly at operator instruction (2026-09-23), without a separate
        issue/change/prompt, using the closure audit's minimal form. In
        snapshot(), ai/workspace, ai/state and ai/logs are recorded by entry and
        type (dir, symlink and target, other, absent) and pruned from the name,
        symlink and checksum walks, as list0 prunes them; the script never writes
        them. ai-local/ and the declared files (context.md, task.md,
        ael/config.yaml, dashboard-alerts.md) remain fully snapshotted.
        Side effect: P-N4 resolved (a write inside ai/state during the prompt no
        longer refuses). Residual: unreadable content in ai-local/ still makes an
        interactive run exit 3 (kept: the A3 guard depends on ai-local/). I1 (FIFO
        at ai-local) unchanged. guide-install §3.3 prompt-guard wording updated.
      fix_test_results: >
        Cowork Linux VM (GNU bash 5.1.16), throwaway targets; iteration 3 as
        audited run side by side. bash -n passes. Interactive, mode 000:
        state/x dir (update and up to date), state/f file, workspace/y dir,
        logs/z file: it3 exit 3, fix exit 0 (up to date: "up to date", exit 0);
        ai-local/z dir: exit 3 both (residual); framework file: exit 3 both;
        --yes: unchanged in every case. Guard edges during the prompt: write in
        state/ exit 0 and applied; state/ replaced by a symlink, workspace/
        renamed, logs/ created, ael/config.yaml edited, dashboard-alerts.md
        created: exit 3. Symlinked ai/: edit exit 3, write in real-ai/state
        exit 0. Regressions: prompt-race edit on a real ai/, P-A1, P-B1, P-B2
        (cmp shim), P-B3a (target byte-identical), A6 dangling, A3 no-clobber:
        exit 3; P-B4, S-A1, up to date, declined: exit 0; non-TTY: exit 2.
        Not covered by the closure audit (which examined 51611db); macOS and
        bash 3.2 not exercised.
  test_results: >
    Cowork Linux VM (GNU bash 5.1.16, rsync 3.2.7, GNU sort), throwaway targets
    from git archive HEAD ai; iteration 2 (HEAD 1b7f068) run side by side.
    bash -n passes. P-B1 (symlinked ai/, older framework primer.md, edit during
    prompt): it2 exit 0, edit lost; it3 exit 3, edit intact. ai/ link
    retargeted during prompt: exit 3. P-B2 (cmp shim edits primer.md after it
    is planned as update): it2 exit 0, edit lost; it3 exit 3, edit intact.
    P-B3 (sort shim rejects -z from the start): it2 exit 0; it3 exit 3 before
    the prompt, target byte-identical. P-B3 (rejects -z after the prompt, edit
    during prompt): it3 exit 3, edit intact. P-B4 (context.md -> existing file):
    it2 exit 3; it3 exit 0, link preserved; same for task.md with --yes.
    Regressions: prompt-race edit on a real ai/ exit 3; P-A1 exit 3 and S-A1
    not seeded, exit 0; A3 cp shim at the backup destination exit 3, user file
    intact; A6 dangling symlink exit 3, nothing created; symlink to a directory
    exit 3; up to date exit 0; declined prompt exit 0; plain apply exit 0;
    non-TTY without --yes exit 2. macOS and bash 3.2 not exercised.
  macos_results: >
    Operator run on macOS, commit 51611db, throwaway targets under /tmp,
    script invoked as bin/propagate.sh (interpreter from /usr/bin/env bash;
    version not captured in this run). (1) Real ai/, older framework
    primer.md planned as update, EDIT appended to ai/workflow.md during the
    prompt: "changed while the prompt was open", rc=3, edit intact. (2) ai/
    symlinked to real-ai/, EDIT appended to real-ai/primer.md during the
    prompt: rc=3, edit intact (B1). (3) printf 'b\0a\0' | LC_ALL=C
    /usr/bin/sort -z | od -c printed "a \0 b \0": sort -z supported (B3).

verification:
  implemented_date: "2026-09-23"
  implemented_by: "Claude (Cowork, Opus 5.5)"
  verification_date: "2026-09-23"
  verified_by: "Claude (Cowork, Opus 5.5) — implementing session"
  test_results: >
    Iteration 2, Cowork Linux VM (GNU bash 5.1, rsync 3.2.7). bash -n passes.
    Prompt-window mutations via pty: context.md created, declared state file
    created, file created in ai-local/, ai-local symlink created, retired
    candidate edited — each exit 3, nothing applied, mutation intact; no
    mutation — applied, exit 0. Unlistable ai/templates with an edited file:
    exit 3, edit intact. Unlistable declared state/ subdirectory: proceeds.
    Existing file at the backup destination: suffixed, user file intact.
    Blob only on a non-default framework branch: backed up. Dangling symlink at
    context.md: exit 3. ai/Context.md: exit 3. Regressions (X1, X2, X4, X5,
    X6b, X13, guards, empty ai/, up to date) pass. N-02/A7 not exercisable on a
    case-sensitive file system; bash 3.2 not run in the VM.
  macos_results: >
    Operator run on macOS 27.0, /bin/bash 3.2.57, /usr/bin/rsync = openrsync
    (protocol 29), commit 45ac716, throwaway targets under /tmp
    (/tmp/macos-check.out). (1) openrsync --itemize-changes printed nothing for
    a changed file: confirms the audit's N-03 concern; the script no longer
    parses that output. (2) Stale workflow.md: backed up as local
    modification, updated, rc=0. (3) Primer.md beside a framework primer.md:
    relocated to ai-local/Primer.md with PROJECT TEXT; ai/primer.md is the
    framework file; N-02 resolved on APFS. (4) 9.16 -> 10.5: 7 retired, 2
    project content, rc=0. (5) ai/Context.md: rc=3, file intact (A7).
    (6) ai/Templates/: 8 framework files relocated as project content, rc=0,
    directory keeps its case; accepted behaviour as documented.
  issues_found: []

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-c5270084"
      relationship: "extends"
  related_issues:
    - issue_ref: "issue-b170cf6a"
      relationship: "resolves"

notes: >
  Implemented by the Strategic Domain at operator instruction. Independent
  re-check required before closure (operator decision 2026-09-23).

version_history:
  - version: "1.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Initial change document; implemented"
  - version: "2.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Iteration 2 after re-check audit-b170cf6a: A1-A7 remediated or accepted (iteration_2 block)"
  - version: "2.1"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "macOS results recorded (bash 3.2, openrsync, APFS)"
  - version: "3.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Iteration 3 after final re-check audit-b170cf6a: B1-B4 remediated in snapshot(), its call site and the A6 refusal (iteration_3 block)"
  - version: "3.1"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Iteration 3 macOS results recorded (prompt race on real and symlinked ai/; sort -z)"
  - version: "3.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "B5 raised as an open finding (operator decision): interactive refusal on an unreadable directory under a declared path"
  - version: "3.3"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "B5 severity low (closure audit); fixed directly in snapshot() at operator instruction: declared directories recorded by entry and type only"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
