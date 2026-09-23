Created: 2026 September 23

```yaml
prompt_info:
  id: "prompt-51f1aef0"
  task_type: "debug"
  source_ref: "change-51f1aef0"
  date: "2026-09-23"
  iteration: 1
  coupled_docs:
    change_ref: "change-51f1aef0"
    change_iteration: 1

context:
  purpose: "Stop linter.py reporting errors on documents that conform to the current templates and conventions."
  integration: "ai/ael/src/linter.py — VALID_CLASSES, _ENUMS['t03_issue'], check_structure, run."
  constraints:
    - "No new checks; no change to WARN-level rules"
    - "Keep the YAML ID pattern check and iteration-mismatch check unchanged"
    - "Add no new imports"
    - "Verify no syntax errors after edit"

specification:
  description: "Five rule corrections."
  requirements:
    functional:
      - "check_structure: pass when a 'version history' heading or a line-anchored 'version_history:' key is present"
      - "check_structure: skip the version-history check for files whose class is prompt"
      - "VALID_CLASSES: add 'proposal' and 'report'"
      - "_ENUMS['t03_issue']['issue_info.type']: add 'enhancement' and 'requirement_change'"
      - "run: register every NORMAL_RE governance filename in doc_index as '<class>-<uuid>' (setdefault) so prose documents resolve as coupling targets"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Preserve existing code style and Finding messages"

design:
  architecture: "Local edits to existing functions and constants"
  components:
    - name: "check_structure"
      type: "function"
      purpose: "Structure rules"
      logic:
        - "Add fname parameter; derive class from NORMAL_RE or MASTER_RE"
        - "Require version history unless class is prompt; accept heading or key"
    - name: "run"
      type: "function"
      purpose: "Build coupling index"
      logic:
        - "After the governance-doc guard, setdefault doc_index['<class>-<uuid>'] from the filename"
  dependencies:
    internal: []
    external: []

deliverable:
  format_requirements:
    - "Edit ai/ael/src/linter.py in place"
    - "Run py_compile on the edited file"
  files:
    - path: "ai/ael/src/linter.py"
      content: "Five rule corrections per specification"

success_criteria:
  - "All change-51f1aef0 test cases pass"
  - "dev/ errors reduced to those of the 4 gitignored probe files"
  - "ai/workspace remains at 0 errors"
  - "linter.py compiles"

notes: >
  Execution: Claude (Cowork, Opus 5.5), direct implementation at William
  Watson's instruction. This document is the specification of record.

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.10"
  schema_type: "t04_prompt"
```
