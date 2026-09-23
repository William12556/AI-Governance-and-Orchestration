Created: 2026 September 23

```yaml
prompt_info:
  id: "prompt-c5270084"
  task_type: "debug"
  source_ref: "change-c5270084"
  date: "2026-09-23"
  iteration: 2
  coupled_docs:
    change_ref: "change-c5270084"
    change_iteration: 2

context:
  purpose: "Stop bin/propagate.sh deleting project files; move them out of ai/ instead (governance P10.6)."
  integration: "bin/propagate.sh — Classify section before Preview; Relocate section before the rsync apply."
  constraints:
    - "Never delete a file whose content is not a blob in the framework repository"
    - "Never overwrite in ai-local/"
    - "Keep change-07087e91 behaviour otherwise unchanged"
    - "bash 3.2 compatible; bash -n must pass"

specification:
  description: "Content classification and relocation."
  requirements:
    functional:
      - "Obtain the files rsync --delete would remove (dry run, '*deleting' lines; expand directories to files)"
      - "Delete-class: git hash-object --no-filters of the target file exists in the framework repo (git cat-file -e)"
      - "Relocate-class: everything else, including symlinks and unreadable files"
      - "Preview lines: 'delete <path> (unmodified framework file)' and 'relocate <path> -> ai-local/<path> (project content)'"
      - "Before the apply, move relocate-class files to <project-root>/ai-local/<path>; on collision append .relocated-<timestamp>; exit 3 if a move fails"
      - "Append a row per move to ai-local/RELOCATED.md, creating it with a header if absent"
      - "Warn when a file ignored at ai/<path> is not ignored at its new path"
      - "Remove the iteration-1 protect rules and .propagate-keep handling"
    technical:
      language: "bash"
      version: "3.2+"
      standards:
        - "Keep set -euo pipefail"

design:
  architecture: "Two new sections; rsync apply unchanged apart from removal of protect rules"
  components:
    - name: "Classify"
      type: "script section"
      purpose: "Split deletion candidates into delete and relocate lists"
      logic:
        - "is_framework_blob: regular file, hash-object, cat-file -e in REPO_ROOT"
    - name: "Relocate"
      type: "script section"
      purpose: "Move project content to ai-local/ and log it"
      logic:
        - "mv -n; verify source gone; check-ignore before and after; append log row"
  dependencies:
    internal: []
    external:
      - "git, rsync"

deliverable:
  format_requirements:
    - "Edit bin/propagate.sh in place"
  files:
    - path: "bin/propagate.sh"
      content: "Classify and Relocate sections per specification"

success_criteria:
  - "All change-c5270084 iteration 2 test cases pass"
  - "bash -n passes"

notes: >
  Execution: Claude (Cowork, Opus 5.5), direct implementation at William
  Watson's instruction. This document is the specification of record.

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.10"
  schema_type: "t04_prompt"
```
