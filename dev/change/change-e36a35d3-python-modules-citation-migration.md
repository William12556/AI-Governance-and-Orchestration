Created: 2026 September 22

```yaml
change_info:
  id: "change-e36a35d3"
  title: "Migrate protocol citations in five Python modules to the eb782f83 scheme"
  date: "2026-09-22"
  author: "William Watson"
  status: "proposed"
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
    - "git diff --stat for the five files shows changes confined to comment and docstring lines"
    - "python -c 'import ast, pathlib; [ast.parse(p.read_text()) for p in paths]' succeeds for all five"
    - "The abstract syntax tree of each module, with docstrings stripped, is identical before and after"
    - "linter.py and protocol_checker.py produce byte-identical output on the same input corpus state"
    - "govwatch.py and overwatch.py complete one scan cycle with no traceback"
  method: >
    The AST comparison is the decisive check. It proves mechanically that no
    executable construct changed, which manual diff review can only assert.

traceability:
  requirements:
    - "CON-09"
    - "FR-04-06"
    - "NFR-07"
    - "V-15"
  related_changes: []
  related_documents:
    - "dev/design/design-eb782f83-protocol-template-reordering.md"
    - "dev/reports/report-eb782f83-pre-migration-baseline.md"

version_history:
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
