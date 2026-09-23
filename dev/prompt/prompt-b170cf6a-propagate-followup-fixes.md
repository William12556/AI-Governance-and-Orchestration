Created: 2026 September 23

```yaml
prompt_info:
  id: "prompt-b170cf6a"
  task_type: "debug"
  source_ref: "change-b170cf6a"
  date: "2026-09-23"
  iteration: 1
  coupled_docs:
    change_ref: "change-b170cf6a"
    change_iteration: 1

context:
  purpose: "Remediate c5270084 follow-up audit findings N-01 to N-08 in bin/propagate.sh."
  integration: "bin/propagate.sh — plan, destinations, preview, confirmation, relocation, copy."
  constraints:
    - "Never delete a file; never overwrite in ai-local/"
    - "Do not parse rsync output"
    - "bash 3.2 compatible; bash -n must pass"

specification:
  description: "Backups, exact names, self-computed preview, re-plan, exit contract."
  requirements:
    functional:
      - "Back up locally modified framework files to ai-local/ as 'local modification' before the copy"
      - "Re-plan after an interactive confirmation; exit 3 if the plan changed"
      - "Decide path existence by exact directory-entry comparison"
      - "Compute add/update preview lines with find and cmp"
      - "Use 'dirname --'; reserve RELOCATED.md; unique suffixes; refuse a non-regular log path"
      - "Relocate droppings inside type-conflict directories; remove empty blocking directories; exit 4 on copy failure"
      - "Label from branches, tags, remotes and HEAD only"
      - "Refuse a candidate symlink that holds a declared path; note relative symlinks"
      - "Enumerate all non-directory entry types; replace control characters in displayed paths"
    technical:
      language: "bash"
      version: "3.2+"
      standards:
        - "set -euo pipefail; NUL-delimited paths"

design:
  architecture: "plan() returns NUL lists; records drive preview and apply"
  components:
    - name: "plan"
      type: "function"
      purpose: "Compute candidates, backups and updates"
      logic:
        - "Target walk: declared skip; droppings only under type conflicts; same_type via exact_exists; backups via cmp and is_framework_version"
        - "Source walk: add/update via exact_exists and cmp"
  dependencies:
    internal: []
    external:
      - "git, rsync, find, cmp"

deliverable:
  format_requirements:
    - "Edit bin/propagate.sh in place"
  files:
    - path: "bin/propagate.sh"
      content: "N-01 to N-08 remediation"

success_criteria:
  - "All change-b170cf6a test cases pass"
  - "bash -n passes"

notes: >
  Execution: Claude (Cowork, Opus 5.5), direct implementation at William
  Watson's instruction. This document is the specification of record.

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.10"
  schema_type: "t04_prompt"
```
