Created: 2026 September 23

```yaml
prompt_info:
  id: "prompt-07087e91"
  task_type: "debug"
  source_ref: "change-07087e91"
  date: "2026-09-23"
  iteration: 1
  coupled_docs:
    change_ref: "change-07087e91"
    change_iteration: 1

context:
  purpose: "Make bin/propagate.sh carry renames and run safely without a terminal."
  integration: "bin/propagate.sh — argument validation, preview, confirmation, apply."
  constraints:
    - "Exclude list unchanged; excluded paths must never be deleted (no --delete-excluded)"
    - "Seeding of context.md and task.md unchanged"
    - "Interactive default remains No"
    - "bash -n must pass"

specification:
  description: "Mirror, flags, version guard."
  requirements:
    functional:
      - "Accept --yes and --allow-major in any position; reject other options with exit 1"
      - "Use rsync --delete in both preview and apply; show '*deleting' lines in the preview"
      - "Read governance version from the last Version History row of source and target governance.md; print both"
      - "On a major version difference print a warning; with --yes and without --allow-major exit 2 before applying"
      - "Without --yes and with a non-TTY stdin, exit 2 with a message before applying"
    technical:
      language: "bash"
      version: "3.2+ (macOS default)"
      standards:
        - "Keep set -euo pipefail"

design:
  architecture: "Local edits within the existing script structure"
  components:
    - name: "gov_version"
      type: "function"
      purpose: "Extract governance version"
      logic:
        - "grep the last '| N.N |' table row; sed out the version"
  dependencies:
    internal: []
    external:
      - "rsync"

deliverable:
  format_requirements:
    - "Edit bin/propagate.sh in place"
  files:
    - path: "bin/propagate.sh"
      content: "Mirror, flags and version guard per specification"

success_criteria:
  - "All change-07087e91 test cases pass"
  - "bash -n passes"

notes: >
  Execution: Claude (Cowork, Opus 5.5), direct implementation at William
  Watson's instruction. This document is the specification of record.

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.10"
  schema_type: "t04_prompt"
```
