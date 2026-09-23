Created: 2026 September 22

```yaml
change_info:
  id: "change-9b8f1c47"
  title: "Remediate the fourteen findings of the eb782f83 strategic audit"
  date: "2026-09-22"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-9b8f1c47"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-9b8f1c47"
  description: >
    Correct the governance record, Appendix A, the migration instrument's
    rollback and gate logic, and the recorded figures. The migrated corpus is
    not reopened.

scope:
  summary: >
    Fourteen findings in one change, at the operator's direction. The migrated
    identifiers, citations and structure are untouched: every edit here is to a
    record, to an appendix that describes the record, or to tooling. The single
    exception is Appendix A itself, which is part of the migrated corpus and is
    corrected under P04 rather than silently, as the audit recommends.
  affected_components:
    - name: "Appendix A — scope statement, version-history rule, schema_type exception, bare-identifier column"
      file_path: "ai/governance.md"
      change_type: "modify"
    - name: "Version history entry 10.0 — substitution total"
      file_path: "ai/governance.md"
      change_type: "modify"
    - name: "FR-07-04, V-05, V-06, V-14 reproducibility"
      file_path: "dev/requirements/requirements-eb782f83-protocol-template-reordering.md"
      change_type: "modify"
    - name: "OQ-7 and acceptance criteria"
      file_path: "dev/proposals/proposal-eb782f83-protocol-template-reordering.md"
      change_type: "modify"
    - name: "rollback() and evaluate_gates()"
      file_path: "dev/tools/migrate_identifiers.py"
      change_type: "modify"
    - name: "refuse_paths, exclude_paths comment accuracy"
      file_path: "dev/tools/mapping.yaml"
      change_type: "modify"
    - name: "Reopened link item, new deferred items"
      file_path: "dev/todo.md"
      change_type: "modify"
    - name: "Clause-count and tool-output comparison commands, retained"
      file_path: "dev/tools/verify_migration.py"
      change_type: "modify"
  affected_designs:
    - "dev/design/design-eb782f83-protocol-template-reordering.md"
  out_of_scope:
    - "Reverting the eight Category A template links. They are correct; only the record is wrong. The audit is explicit that reverting to restore conformance would be the wrong repair."
    - "Retiring the numeric schema_type prefix. Recorded as a named exception here; the retirement is its own change, because it touches the linter's validation keys and every document in the frozen corpus carries them."
    - "Re-running or amending the migration. No identifier, citation or structural heading changes."
    - "The propagate.sh defects, already on dev/todo.md, except to note that F-03 and F-10 must be resolved with them before D5 propagation."
    - "The 102 linter and 38 protocol-checker pre-existing errors."

rational:
  problem_statement: >
    The migrated corpus is functionally correct and independently verified. The
    governance record around it is not: four documents state a decision that
    delivery reversed, Appendix A misdirects on two classes of content, the
    rollback path is incomplete, and three figures do not reconcile. This
    framework exists to keep the record, so a defective record is the defect
    that matters most here.
  proposed_solution: >
    One change, at the operator's direction, covering all fourteen findings.
    Grouped by nature rather than by severity, because the grouping determines
    the risk: record corrections cannot break anything, the Appendix A edit
    touches the migrated corpus, and the tooling edits change behaviour that has
    never been exercised.
  alternatives_considered:
    - option: "Four sequenced changes as originally recommended"
      reason_rejected: >
        Operator directed a single change. The sequencing was for reviewability,
        not for safety; nothing here depends on anything else here.
    - option: "Revert the Category A links to satisfy FR-07-04"
      reason_rejected: >
        Would make the artefact worse to satisfy a document. The audit
        recommends amending the document, and the links are correct.
    - option: "Revert the widened audit scope in P02.3"
      reason_rejected: >
        The prior text excluded P10 Requirements, which existed; the range was
        never updated when that protocol was added. 'All protocols' is what was
        evidently intended. Recorded as an intended CON-08 exception instead,
        at the operator's ruling.

remediation:
  - finding: "F-01"
    action: >
      Amend FR-07-04 and OQ-7 to the decision actually taken. Reopen the closed
      dev/todo.md item and reclassify it: the eight links were repaired, not
      discharged. Record the reversal as a CON-08 exception in the proposal.
      Correct V-14's rationale, which currently contradicts FR-07-04.
  - finding: "F-02"
    action: >
      rollback() computes the set of files present under the write set but absent
      from the manifest, and refuses to proceed while listing them. Until a
      subsequent change makes removal safe, the documented rollback procedure is
      git checkout of pre-eb782f83, with the snapshot used only for
      docs/claude/project_information.md. Recorded in the design.
  - finding: "F-03"
    action: >
      evaluate_gates() fails with a distinct exit code when the marker file does
      not exist at its configured path, rather than reading its absence as an
      unmigrated corpus.
  - finding: "F-04"
    action: >
      Record the schema_type namespace in Appendix A as a named exception, with
      the reason the numeric prefix cannot be migrated: the linter keys its
      validation rules on these strings and every document in the frozen corpus
      carries them, so migrating the namespace would require editing frozen
      documents or breaking their validation, and CON-04 forecloses both. Defer
      retirement in favour of the class word to its own change.
  - finding: "F-05"
    action: >
      Record both clause edits as CON-08 exceptions in the proposal, with their
      commit and their placement before the baseline tag stated. Record the
      widened audit scope as intended. Note in the design that a baseline tag
      must precede the first edit of any kind, not merely the first mechanical
      one.
  - finding: "F-06"
    action: >
      Correct Appendix A's scope statement: name dev/smoke/ai/ and the eb782f83
      document set as current-scheme.
  - finding: "F-07"
    action: >
      State in Appendix A that version-history sections throughout the corpus are
      read under the scheme in force at the time of the entry.
  - finding: "F-08"
    action: >
      Correct 614 to 654 in the governance v10.0 version-history entry and
      wherever else it appears.
  - finding: "F-09"
    action: >
      Correct the renamed-template count to seven, T08 being a fixed point.
  - finding: "F-10"
    action: >
      Add bin/ to refuse_paths as a decision, with the reason recorded: it holds
      executable shell, not corpus, and bin/propagate.sh is subject to its own
      deferred change.
  - finding: "F-11"
    action: >
      Correct the exclude_paths comment in mapping.yaml: the gitignore rule is
      ai/state/ralph/, not ai/state/. The exclusion of ai/state/ remains correct
      and is now argued on its own terms rather than on the ignore rule.
  - finding: "F-12"
    action: >
      Record in the design that an untracked file in the write set has no
      version-controlled rollback path, and that the snapshot must be preserved
      until the change closes.
  - finding: "F-13"
    action: >
      Retain the V-05 and V-06 comparison as a script rather than ad-hoc
      commands, so the criterion is reproducible.
  - finding: "F-14"
    action: >
      Retain the clause-count comparison as a script, with its extraction rule
      explicit, so the 1086 figure is reproducible.

validation:
  criteria:
    - "Appendix A names dev/smoke/ai/ and the eb782f83 document set as current-scheme, states the version-history rule, records the schema_type exception, and carries a bare-identifier column in A.2"
    - "No occurrence of 614 remains as a substitution total; 654 reconciles with C0 60 + C1 140 + C2 185 + C3 225 + C4 44"
    - "FR-07-04, OQ-7, V-14 and the todo item agree with the delivered table of contents"
    - "rollback() refuses and lists when files exist under the write set that the manifest does not record, demonstrated on a scratch copy"
    - "evaluate_gates() returns a distinct exit code for a missing marker file, demonstrated with a wrong --root"
    - "bin/ is named in refuse_paths"
    - "The clause-count and tool-output comparisons run from a retained script and reproduce 1086 and byte-identical output respectively"
    - "git diff of ai/ contains no identifier, citation or heading change outside Appendix A and the version history"
  method: >
    The last criterion is decisive: it proves the migrated corpus was not
    reopened. Everything else is checked by reading the amended documents against
    the audit findings.

traceability:
  requirements:
    - "CON-01 — the widened audit scope is recorded as an exception, not concealed"
    - "CON-04 — the frozen corpus remains untouched; it is the reason schema_type cannot be migrated"
    - "CON-08 — three exceptions now recorded explicitly rather than argued away"
    - "NFR-04 — reversibility, which F-02 shows was not achieved"
  related_documents:
    - "dev/audit/audit-eb782f83-strategic-2026-09-22.md"

implementation_record:
  date: "2026-09-22"
  files_changed:
    - "ai/governance.md — Appendix A regenerated with corrected scope, version-history rule, A.5 schema_type exception and identifier columns in A.2; v10.0 entry 614 to 654"
    - "dev/tools/migrate_identifiers.py — rollback() refuses when the manifest cannot account for the write set; gate 5 distinguishes an absent marker file; clean failure for a missing mapping; appendix generator emits the corrected text"
    - "dev/tools/mapping.yaml — bin/ added to refuse_paths; exclude_paths rationale restated on its own terms"
    - "dev/tools/compare_migration.py — new; retains the V-05, V-06 and clause-count comparisons"
    - "dev/tools/verify_migration.py — unchanged this iteration; V-17 bounding was already applied under d60a8b9"
    - "dev/requirements/... v0.7 — FR-07-04, V-14, V-05, V-06"
    - "dev/proposals/... v1.7 — §6.3 CON-08 exception register; OQ-7"
    - "dev/design/... v0.5 — §8.5 rollback procedure; §5.4.1 baseline-tag rule; §12.0 three boundary conditions"
    - "dev/todo.md — link item reclassified; six items deferred from the audit"
    - "dev/audit/audit-eb782f83-brief.md v1.1 — errata recorded, text left as the auditor read it"
  verification:
    - "git diff of the migrated corpus touches ai/governance.md only, and only within Appendix A and the version history"
    - "verify_migration.py --until-ref b3369f5: 10 passed, 0 failed"
    - "compare_migration.py: linter and protocol_checker byte-identical; clause lines 986 = 986, differences are the nineteen table-of-contents entries"
    - "migrate_identifiers.py --self-test: 13/13"
    - "generate_alias_appendix() reproduces the delivered Appendix A exactly, so FR-05-03 holds again"
  notes:
    - >
      The clause-count figure is 986, not the 1086 previously recorded. Both are
      correct counts of different things: the retained extraction rule now
      discards version-history sections on both sides, because that section is a
      protected region, was deliberately not migrated, and accretes entries
      afterwards — the governance v10.0 entry alone made the two sides differ by
      one. 986 is the reproducible figure and the one the claim is about.
    - >
      Two defects were found while remediating. Appendix A was hand-edited first,
      which contradicted FR-05-03; the generator was updated and the appendix
      regenerated from it, and the two now agree byte for byte. The generator's
      own hazard list included P00, a fixed point that resolves to itself and is
      therefore harmless; corrected to name the five identifiers that genuinely
      resolve to a different protocol.
    - >
      A wrong --root failed with an unhandled FileNotFoundError rather than a
      message, found while demonstrating the F-03 fix. Corrected in the same
      change.

version_history:
  - version: "1.1"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Verified and closed. Operator accepted the remediation on 2026-09-22 and directed closure on 2026-09-23. Verification per implementation_record: migrated corpus untouched outside Appendix A and the version history; 10 of 10 checks; comparisons reproduce; self-test 13/13."
  - version: "1.0"
    date: "2026-09-22"
    author: "William Watson"
    changes:
      - "Initial change document covering all fourteen findings in one change, at operator direction"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
