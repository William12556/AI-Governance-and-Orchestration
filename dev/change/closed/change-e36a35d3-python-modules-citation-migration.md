Created: 2026 September 22

```yaml
change_info:
  id: "change-e36a35d3"
  title: "Migrate protocol citations in five Python modules to the eb782f83 scheme"
  date: "2026-09-22"
  author: "William Watson"
  status: "verified"
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-e36a35d3"
    issue_iteration: 1
    prompt_ref: "prompt-e36a35d3"
    prompt_iteration: 1

source:
  type: "issue"
  reference: "issue-e36a35d3"
  description: >
    Convert every protocol and template citation in the five affected Python
    modules from the retired positional scheme to the migrated dotted scheme,
    touching comments and docstrings only.

scope:
  summary: >
    The conversion is performed by dev/tools/migrate_identifiers.py, the same
    instrument that migrates the rest of the corpus, in the same run. The five
    modules lie within ai/ and therefore within the migration set already; this
    change document exists to govern that portion of the run under the
    src/-change rule, not to introduce a separate mechanism. Hand editing is
    prohibited.
  affected_components:
    - name: "protocol_checker (docstring, check banners)"
      file_path: "ai/ael/src/protocol_checker.py"
      change_type: "modify"
    - name: "linter (docstring, check banners, enum comment)"
      file_path: "ai/ael/src/linter.py"
      change_type: "modify"
    - name: "orchestrator (guidance strings, extraction docstrings)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "govwatch (tactical brief comment)"
      file_path: "ai/src/govwatch.py"
      change_type: "modify"
    - name: "overwatch (tactical brief comment)"
      file_path: "ai/src/overwatch.py"
      change_type: "modify"
  affected_designs:
    - "dev/design/design-eb782f83-protocol-template-reordering.md"
  out_of_scope:
    - "Any executable line. The diff must contain comments and docstrings only."
    - "Adding validation of citations embedded in source comments — a real gap named in the issue analysis, deferred to dev/todo.md"
    - "The tactical_brief guidance strings' content; only their citations change"
    - "Renaming or restructuring any function, constant or module"

rational:
  problem_statement: >
    These modules annotate each check with the governance clause it implements.
    After eb782f83 those annotations cite a retired scheme, and the identifiers
    P03 and P04, having exchanged meanings, make some annotations misleading
    rather than merely stale.
  proposed_solution: >
    Migrate them mechanically with the rest of the corpus. The modules are
    already inside the migration set, the substitution rules apply to comments
    and docstrings identically to prose, and the two-pass sentinel algorithm
    protects the overlapping identifiers that make hand editing hazardous.
  alternatives_considered:
    - option: "Exclude the five modules from the migration set and edit them later"
      reason_rejected: >
        Leaves the live corpus in a mixed scheme for an indefinite period, and
        requires a second migration run configured differently from the first.
    - option: "Treat comment-only edits as documentation and skip the triple"
      reason_rejected: >
        Requires an exemption clause in governance, which is itself a governance
        change and larger than the thing it would exempt.
    - option: "Hand-edit the five files"
      reason_rejected: >
        The protocol identifier namespace overlaps its own image: P01 through
        P04 and P10 are each both a source and a target of different mappings,
        and P03 and P04 form a transposition. Manual substitution is precisely
        the failure mode the sentinel algorithm exists to prevent.

implementation:
  approach: >
    No separate implementation. The files are processed by stage 5 of
    migrate_identifiers.py during the eb782f83 run.
  sequence:
    - "The eb782f83 migration runs; the five modules are substituted with the rest of ai/"
    - "The diff for these five files is reviewed separately from the prose diff, to confirm no executable line changed"
    - "V-15 executes: all five import; linter.py and protocol_checker.py run clean; govwatch.py and overwatch.py each complete one scan cycle"
  rollback: >
    Covered by the eb782f83 snapshot and the pre-eb782f83 tag. These five files
    have no independent rollback path and must not be reverted in isolation,
    which would reintroduce a mixed scheme.

validation:
  criteria:
    - "All five modules parse"
    - "The AST skeleton, with docstrings removed and every string constant blanked, is identical before and after"
    - "Every string constant that differs, differs by exactly what the migration would produce, verified by re-running the substitution on the original"
    - "linter.py and protocol_checker.py produce byte-identical output on the same input corpus state"
    - "govwatch.py and overwatch.py complete one scan cycle with no traceback"
  method: >
    Implemented as V-15 in dev/tools/verify_migration.py. The skeleton
    comparison proves no executable construct changed; the per-string
    comparison permits a citation inside a string literal to change while
    proving it changed only in the way the migration defines.
  criterion_history: >
    Version 1.0 required plain AST equivalence with docstrings stripped. The
    rehearsal showed that criterion to be inconsistent with this document's own
    scope, which permits the citations inside the tactical_brief guidance
    strings to change. orchestrator.py writes a guidance block into
    context-budget.md naming the prompt template; after migration that template
    is T03, so leaving the string at T04 would emit wrong instructions at
    runtime. One string in one file changes. Plain AST equivalence would have
    forbidden the only string change the change itself requires.

traceability:
  requirements:
    - "CON-09"
    - "FR-04-06"
    - "NFR-07"
    - "V-15"
  related_changes: []
  related_documents:
    - "dev/design/design-eb782f83-protocol-template-reordering.md"
    - "dev/reports/closed/report-eb782f83-pre-migration-baseline.md"

version_history:
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Verified and closed. Approved by the operator on 2026-09-22 when the live run was authorised; implemented in b3369f5; verified by V-15 (AST skeleton identical, one string constant changed exactly as the migration defines) and confirmed independently by the strategic audit, claim C5. Status passes directly from proposed to verified because the approval and implementation were recorded in the eb782f83 documents rather than here — noted rather than back-filled."
  - version: "1.1"
    date: "2026-09-22"
    author: "William Watson"
    changes:
      - "Validation criterion replaced: plain AST equivalence was inconsistent with this document's own scope, which permits citations inside the tactical_brief guidance strings to change. Replaced with the blanked-skeleton comparison plus per-string verification, implemented as V-15."
  - version: "1.0"
    date: "2026-09-22"
    author: "William Watson"
    changes:
      - "Initial change document"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
