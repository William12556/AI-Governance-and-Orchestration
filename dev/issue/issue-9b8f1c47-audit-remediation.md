Created: 2026 September 22

```yaml
issue_info:
  id: "issue-9b8f1c47"
  title: "Strategic audit of eb782f83 recorded fourteen findings requiring remediation"
  date: "2026-09-22"
  reporter: "William Watson"
  status: "resolved"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-9b8f1c47"
    change_iteration: 1

source:
  origin: "audit"
  reference: "dev/audit/audit-eb782f83-strategic-2026-09-22.md"
  description: >
    An independent strategic audit of commit b3369f5 against baseline 9a1767f
    adjudicated twelve claims — five confirmed, six refuted, one unverifiable —
    and recorded fourteen findings: two high, five medium, seven low. The
    migrated corpus is functionally correct; the defects are concentrated in the
    governance record, in the migration instrument's rollback and gate logic, and
    in a fourth identifier namespace that was never in scope.

affected_scope:
  components:
    - name: "Appendix A scope statement and template alias table"
      file_path: "ai/governance.md"
    - name: "Governance version history, entry 10.0"
      file_path: "ai/governance.md"
    - name: "Requirements FR-07-04, V-05, V-06, V-14"
      file_path: "dev/requirements/requirements-eb782f83-protocol-template-reordering.md"
    - name: "Proposal OQ-7 and acceptance criteria"
      file_path: "dev/proposals/proposal-eb782f83-protocol-template-reordering.md"
    - name: "Rollback and idempotence gate"
      file_path: "dev/tools/migrate_identifiers.py"
    - name: "Exclusion and refusal path lists"
      file_path: "dev/tools/mapping.yaml"
    - name: "Discharged link item and deferred work"
      file_path: "dev/todo.md"
  version: "governance v10.0"

findings:
  high:
    - id: "F-01"
      summary: >
        A ratified decision was reversed during execution and recorded as a
        discharge rather than a change. OQ-7 and FR-07-04 state that the eight
        Category A template links are renamed but not repaired; the delivered
        table of contents emits the repaired, path-qualified form. The delivered
        artefact does not satisfy its own requirements baseline, and V-14 now
        contradicts FR-07-04 directly. The links are correct; the record is not.
    - id: "F-02"
      summary: >
        --rollback does not restore the pre-migration state. It copies manifest
        entries back but never removes a file the migration created. The seven
        renamed templates are absent from the manifest, so a rollback would leave
        fifteen files in ai/templates/ and a restored table of contents pointing
        at the seven originals while the new files sit beside them unreferenced.
  medium:
    - id: "F-03"
      summary: >
        The idempotence gate conflates an absent scheme marker with an absent
        marker file, so a mistaken --root presents as an unmigrated corpus.
    - id: "F-04"
      summary: >
        A fourth identifier namespace exists and was never in scope. schema_type
        carries numeric template prefixes — t01_design, t02_change, t03_issue —
        which the substitution patterns cannot match, because the underscore is a
        word character. T02-design.md now declares schema_type t01_design.
    - id: "F-05"
      summary: >
        Two protocol clauses changed meaning in 7b47345, one commit before the
        pre-eb782f83 tag, and therefore outside every window in which CON-01 was
        measured. 'Protocol compliance: All protocols P00-P09' became 'All
        protocols', replacing a closed enumerated set with an open one and
        widening audit scope onto Requirements and every future protocol.
    - id: "F-06"
      summary: >
        Appendix A's scope statement is false in a document declared immutable.
        It claims the corpus in dev/ cites the retired scheme; the entire
        eb782f83 document set and the regenerated dev/smoke/ai/ tree are
        current-scheme, and the overlapping identifiers are exactly those the
        rule mis-resolves.
    - id: "F-07"
      summary: >
        Ninety-five positional citations survive in live version histories by
        design, but nothing in the live corpus records that version histories are
        read under the scheme in force at the time of the entry.
  low:
    - id: "F-08"
      summary: >
        The substitution total does not reconcile with its own breakdown. The
        components sum to 654; 614 was recorded, and is now in the permanent
        governance v10.0 version-history entry.
    - id: "F-09"
      summary: "'Templates renamed: 8' overstates by one; T08 was not renamed."
    - id: "F-10"
      summary: >
        bin/ appears in neither migration_set nor refuse_paths. Its absence from
        the write set is an omission rather than a decision.
    - id: "F-11"
      summary: >
        The gitignore rule is ai/state/ralph/, not ai/state/, so C7's evidence
        for the exclusion is narrower than stated.
    - id: "F-12"
      summary: >
        The only rollback path for docs/claude/project_information.md is the
        snapshot, which is itself untracked and gitignored.
    - id: "F-13"
      summary: >
        The restated V-05 and V-06 criteria are already unreproducible: they
        compare tool output before and after, but the comparison was performed
        with ad-hoc commands that were not retained.
    - id: "F-14"
      summary: >
        The '1086 clause lines each side' figure cannot be reproduced from the
        artefacts, because the extraction rule was not recorded.

behavior:
  expected: >
    The governance record states what was actually decided and delivered; the
    migration instrument can restore the pre-migration state; Appendix A resolves
    every identifier a reader will encounter; recorded figures reconcile.
  actual: >
    Four documents state a decision that was reversed in delivery, Appendix A
    misdirects on two classes of content, rollback is incomplete, and three
    recorded figures are wrong or unreproducible.
  impact: >
    No impact on the migrated corpus, which is functionally correct and verified.
    The impact is on the governance record, on the ability to reverse the change
    safely, and on any future maintainer resolving a retired identifier.

analysis:
  root_cause: >
    Three distinct causes. First, decisions taken under time pressure during
    execution were recorded as discharges rather than as reversals requiring a
    change document. Second, the migration instrument was designed for one
    repository with a known layout and was never exercised in reverse. Third,
    the scope of the identifier survey was set by pattern-matching on documents,
    which cannot see a namespace whose tokens are embedded in identifiers.
  contributing_factors:
    - "The baseline tag was placed after the range-expression edits, so every verification window excluded two clause changes (F-05)"
    - "Verification tooling shares its token patterns with the migration tooling by direct import, so a blind spot in one is a blind spot in both"
    - "schema_type was never listed as a namespace in the design, so no rule was written for it"

resolution_criteria:
  - "Appendix A states its true scope and the version-history resolution rule"
  - "The governance v10.0 version-history entry carries a figure that reconciles"
  - "FR-07-04, OQ-7 and the closed todo item state the decision actually taken, with the reversal recorded as a CON-08 exception"
  - "The widened audit scope is recorded as an intended CON-08 exception or reverted"
  - "rollback() either removes created files or refuses and lists them"
  - "The idempotence gate distinguishes an absent marker from an absent marker file"
  - "bin/ appears in migration_set or refuse_paths as a decision"
  - "The schema_type namespace is recorded as a named exception, with its retirement deferred"
  - "V-05, V-06 and the clause-count comparison are reproducible from a retained command"

traceability:
  related_documents:
    - "dev/audit/audit-eb782f83-strategic-2026-09-22.md"
    - "dev/audit/audit-eb782f83-brief.md"
    - "dev/proposals/proposal-eb782f83-protocol-template-reordering.md"
    - "dev/requirements/requirements-eb782f83-protocol-template-reordering.md"
    - "dev/design/design-eb782f83-protocol-template-reordering.md"

version_history:
  - version: "1.1"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status open to resolved, following implementation under change-9b8f1c47 (097d6ea). protocol_checker.py flagged the mismatch: change implemented while its coupled issue remained open."
  - version: "1.0"
    date: "2026-09-22"
    author: "William Watson"
    changes:
      - "Initial issue document consolidating all fourteen audit findings"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
