Created: 2026 September 23

```yaml
prompt_info:
  id: "prompt-c5270084"
  task_type: "debug"
  source_ref: "change-c5270084"
  date: "2026-09-23"
  iteration: 3
  coupled_docs:
    change_ref: "change-c5270084"
    change_iteration: 3

context:
  purpose: "Remediate audit-c5270084 with a design in which bin/propagate.sh never deletes a file."
  integration: "bin/propagate.sh — rewritten section by section; interface preserved."
  constraints:
    - "No rsync --delete; no rm of target files anywhere"
    - "Never overwrite in ai-local/; check destinations before the first move"
    - "Keep --yes, --allow-major, non-TTY and seeding behaviour"
    - "bash 3.2 compatible; bash -n must pass"

specification:
  description: "No-delete propagation with labelled relocation."
  requirements:
    functional:
      - "Enumerate target files and symlinks with find -print0; skip declared paths; candidate when the source lacks an entry of the same type"
      - "Label: non-empty blob at the same path in git log --all --raw of ai/ (and historic framework/ai/, skel/ai/) -> 'retired framework file'; else 'project content'"
      - "Record gitignore status of every candidate before any move; warn after all moves; warn when a .gitignore is relocated"
      - "Pre-check that ai-local/ and each existing destination directory component is a real directory; otherwise exit 3 before any change"
      - "Relocate before the copy; log each move; any failure exits 3 before the copy"
      - "Remove only empty directories that block a source file"
      - "Absent or unparseable target version -> 'unknown', treated as major; accept x.y and x.y.z"
      - "Excludes without trailing slash; add /logs"
      - "Set the executable bit"
    technical:
      language: "bash"
      version: "3.2+"
      standards:
        - "set -euo pipefail; NUL-delimited path handling"

design:
  architecture: "Enumerate, label, plan, preview, confirm, relocate, copy, seed"
  components:
    - name: "Enumerate/Label/Plan"
      type: "script sections"
      purpose: "Build a NUL-delimited plan of (path, destination, label, ignored)"
      logic:
        - "find -print0 over target ai/; is_declared; same_type"
        - "label_of via hash-object and the reachable blob list"
        - "check_dir_chain on each destination directory"
  dependencies:
    internal: []
    external:
      - "git, rsync, find"

deliverable:
  format_requirements:
    - "Replace bin/propagate.sh"
  files:
    - path: "bin/propagate.sh"
      content: "No-delete propagation per specification"

success_criteria:
  - "All change-c5270084 iteration 3 test cases pass"
  - "bash -n passes; no deletion code path"

notes: >
  Execution: Claude (Cowork, Opus 5.5), direct implementation at William
  Watson's instruction. This document is the specification of record.

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.10"
  schema_type: "t04_prompt"
```
