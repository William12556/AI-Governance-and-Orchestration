Created: 2026 September 23

```yaml
prompt_info:
  id: "prompt-c5270084"
  task_type: "debug"
  source_ref: "change-c5270084"
  date: "2026-09-23"
  iteration: 1
  coupled_docs:
    change_ref: "change-c5270084"
    change_iteration: 1

context:
  purpose: "Stop bin/propagate.sh deleting project-local files."
  integration: "bin/propagate.sh — new Protect section before Preview; both rsync calls."
  constraints:
    - "Never use --delete-excluded"
    - "Keep change-07087e91 behaviour otherwise unchanged"
    - "bash 3.2 compatible; bash -n must pass"

specification:
  description: "Protect rules for untracked files and a per-project keep list."
  requirements:
    functional:
      - "If the target is a git work tree, add --filter='P /<rel>' for every path from git ls-files --others run in the target ai/"
      - "If <project>/ai/.propagate-keep exists, add a P rule per non-comment line; exclude the file from transfer"
      - "If the target is not a git work tree, add --filter='P *'"
      - "List protected paths absent from the source in the preview, omitting workspace/, state/ and interpreter droppings"
    technical:
      language: "bash"
      version: "3.2+"
      standards:
        - "Keep set -euo pipefail; guard empty-array expansion"

design:
  architecture: "One new section; array appended to the two existing rsync invocations"
  components:
    - name: "Protect section"
      type: "script section"
      purpose: "Build rsync protect rules before the preview"
      logic:
        - "Read .propagate-keep lines into P rules"
        - "If git work tree: P rule per git ls-files --others path; else P *"
        - "Collect preview lines for protected paths absent from the source"
  dependencies:
    internal: []
    external:
      - "git, rsync"

deliverable:
  format_requirements:
    - "Edit bin/propagate.sh in place"
  files:
    - path: "bin/propagate.sh"
      content: "Protect section per specification"

success_criteria:
  - "All change-c5270084 test cases pass"
  - "bash -n passes"

notes: >
  Execution: Claude (Cowork, Opus 5.5), direct implementation at William
  Watson's instruction. This document is the specification of record.

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.10"
  schema_type: "t04_prompt"
```
