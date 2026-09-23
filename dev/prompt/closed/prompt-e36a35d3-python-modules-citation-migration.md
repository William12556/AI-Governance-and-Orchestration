Created: 2026 September 22

```yaml
prompt_info:
  id: "prompt-e36a35d3"
  task_type: "refactor"
  source_ref: "change-e36a35d3"
  date: "2026-09-22"
  iteration: 1
  target_profile: "human"
  coupled_docs:
    change_ref: "change-e36a35d3"
    change_iteration: 1

context:
  purpose: >
    Authorise the portion of the eb782f83 migration run that modifies the five
    Python modules under ai/. Their module docstrings and inline comments cite
    the retired positional protocol scheme; after the migration those citations
    name identifiers that either no longer exist or, in the P03/P04
    transposition, name a different protocol than intended.
  integration: >
    No separate implementation. The five files lie inside the migration set and
    are processed by stage 5 of dev/tools/migrate_identifiers.py during the
    eb782f83 run, under the same two-pass sentinel substitution as the rest of
    the corpus.
  constraints:
    - "No hand editing. The protocol namespace overlaps its own image; manual substitution is the failure mode the sentinel algorithm exists to prevent."
    - "No executable line may change. The diff must contain comments and docstrings only."
    - "Do not reorder, rename or restructure any function, class, constant or module"
    - "Do not alter the content of the tactical_brief guidance strings; only their citations change"
    - "Do not add citation validation for source comments — a real gap, deferred to dev/todo.md"
    - "These five files have no independent rollback path; reverting them alone would reintroduce a mixed scheme"

design:
  reference: "dev/design/design-eb782f83-protocol-template-reordering.md"
  components:
    - name: "protocol_checker — module docstring and six check-section banners"
      file_path: "ai/ael/src/protocol_checker.py"
      element_type: "comments"
    - name: "linter — module docstring, check banners, enum constraint comment"
      file_path: "ai/ael/src/linter.py"
      element_type: "comments"
    - name: "orchestrator — tactical_brief guidance strings and extraction docstrings"
      file_path: "ai/ael/src/orchestrator.py"
      element_type: "comments"
    - name: "govwatch — tactical brief detection comment"
      file_path: "ai/src/govwatch.py"
      element_type: "comments"
    - name: "overwatch — tactical brief detection comment"
      file_path: "ai/src/overwatch.py"
      element_type: "comments"
  mapping_source: "dev/tools/mapping.yaml"
  algorithm: >
    Two-pass sentinel substitution, design §5.3. Token classes C0 (combined
    'Pnn §1.x.y'), C2 (bare positional citation), C1 (bare protocol identifier),
    C3 and C4 (template identifier and filename). Protected regions do not
    apply to .py files.

deliverable:
  files:
    - path: "ai/ael/src/protocol_checker.py"
      type: "modified"
    - path: "ai/ael/src/linter.py"
      type: "modified"
    - path: "ai/ael/src/orchestrator.py"
      type: "modified"
    - path: "ai/src/govwatch.py"
      type: "modified"
    - path: "ai/src/overwatch.py"
      type: "modified"

specification:
  description: >
    Convert every protocol and template citation in the five modules from the
    retired positional form to the dotted fully-qualified form, as part of the
    whole-corpus migration run.
  affected_files:
    - "ai/ael/src/protocol_checker.py"
    - "ai/ael/src/linter.py"
    - "ai/ael/src/orchestrator.py"
    - "ai/src/govwatch.py"
    - "ai/src/overwatch.py"
  requirements:
    functional:
      - "Every occurrence of the combined form 'Pnn §1.x.y' collapses to a single dotted citation"
      - "Every bare positional citation '§1.x.y' becomes '<new identifier>.x.y'"
      - "Every bare protocol identifier is remapped per mapping.yaml"
      - "Protected regions do not apply: these are .py files, where a leading '#' opens a comment, not a heading"
    prohibited:
      - "Any change to an executable statement, expression, signature or default"
      - "Any change to a regular expression, enum membership or constant value"

execution:
  option: "A — human executes the command directly"
  command: |
    cd ~/Documents/GitHub/LLM-Governance-and-Orchestration
    python3 dev/tools/migrate_identifiers.py --dry-run
    # review the diff for the five modules, then:
    python3 dev/tools/migrate_identifiers.py
  note: >
    This prompt authorises the five-module portion only. The run as a whole is
    authorised by the approved eb782f83 design, under the initial-implementation
    forward path.

validation:
  criteria:
    - "git diff for the five files shows changes confined to comment and docstring lines"
    - "All five modules parse: ast.parse succeeds on each"
    - "AST equivalence with docstrings stripped is identical before and after — the decisive check"
    - "linter.py and protocol_checker.py produce byte-identical output on the same corpus state"
    - "govwatch.py and overwatch.py each complete one scan cycle without traceback"
    - "No positional citation remains in any of the five files (verify_migration.py V-02)"
  command: |
    python3 dev/tools/verify_migration.py
  ast_check: >
    Implemented as V-15 in dev/tools/verify_migration.py, run by the validation
    command above. For each module it compares the AST skeleton with docstrings
    removed and every string constant blanked, then compares the string
    constants pairwise: each difference must equal the result of running the
    migration substitution on the original string. A structural change, a change
    in the number of string constants, or a string that changed beyond the
    migration all fail the check.
  expected_result: >
    One string constant changes, in orchestrator.py: the guidance block written
    into context-budget.md, which names the prompt template. All other changes
    are docstrings and comments.

traceability:
  requirements:
    - "CON-09"
    - "FR-04-06"
    - "NFR-07"
    - "V-15"
  documents:
    - "dev/issue/closed/issue-e36a35d3-python-modules-retired-citations.md"
    - "dev/change/closed/change-e36a35d3-python-modules-citation-migration.md"
    - "dev/design/design-eb782f83-protocol-template-reordering.md"

version_history:
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Closed with its coupled issue and change. Coupling paths updated to closed/. Prompts carry no terminal status field."
  - version: "1.1"
    date: "2026-09-22"
    author: "William Watson"
    changes:
      - "ast_check replaced by V-15 in verify_migration.py; expected_result records the single legitimate string-constant change in orchestrator.py"
  - version: "1.0"
    date: "2026-09-22"
    author: "William Watson"
    changes:
      - "Initial prompt document"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```
