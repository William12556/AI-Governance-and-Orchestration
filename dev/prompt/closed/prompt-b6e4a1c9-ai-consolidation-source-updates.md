# Prompt: Align Source and Scripts with ai/-Consolidated Layout

Created: 2026 June 15

---

## Table of Contents

- [1.0 Prompt Information](#10-prompt-information)
- [2.0 Context](#20-context)
- [3.0 Specification](#30-specification)
- [4.0 Deliverable](#40-deliverable)
- [5.0 Testing](#50-testing)
- [6.0 Tactical Brief](#60-tactical-brief)
- [7.0 Success Criteria](#70-success-criteria)
- [Version History](#version-history)

---

## 1.0 Prompt Information

```yaml
prompt_info:
  id: "prompt-b6e4a1c9"
  task_type: "code_modification"
  source_ref: "change-b6e4a1c9"
  date: "2026-06-15"
  iteration: 1
  coupled_docs:
    change_ref: "change-b6e4a1c9"
    change_iteration: 1
```

Tactical Domain: Claude Code. This prompt operationalises change-b6e4a1c9.
Read each target file before editing and apply only the path edits specified.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Context

```yaml
context:
  purpose: >
    Align source code and provisioning scripts with the ai/-consolidated
    layout established in Phase 1 (workspace/ -> ai/workspace/, loop state
    .ael/ralph/ -> ai/state/ralph/, govwatch output -> ai/dashboard-alerts.md).
  integration: >
    Edits apply to framework/ and bin/ only. skel/ai mirrors and downstream
    copies update later via sync-skel.sh and propagate.sh. No behavioural
    change; path references only.
  knowledge_references: []
  constraints:
    - "Modify only the paths and strings specified; do not refactor surrounding logic"
    - "Read each file before editing"
    - "Do not edit skel/ or downstream copies; the propagation chain handles those"
    - "Preserve existing code style and formatting"
```

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Specification

```yaml
specification:
  description: >
    Four files. govwatch path constructors and two cosmetic strings; two
    script exclude lists; one regression test's skeleton-layout assertions.
  edits:
    - file: "framework/ai/src/govwatch.py"
      changes:
        - "In main(), ProjectPaths: workspace = root / 'ai' / 'workspace'"
        - "In main(), ProjectPaths: ael_state = root / 'ai' / 'state' / 'ralph'"
        - "In main(), ProjectPaths: alerts_file = root / 'ai' / 'dashboard-alerts.md'"
        - "Startup validation message naming the expected subdirectory: 'workspace/' -> 'ai/workspace/'"
        - "Relative-path display anchor: ensure the displayed document path remains correct under ai/workspace/ (anchor on 'ai/workspace' if the current code keys on the literal 'workspace')"
    - file: "bin/sync-skel.sh"
      changes:
        - "Add --exclude='state/' to the rsync exclude list"
        - "Add --exclude='dashboard-alerts.md' to the rsync exclude list"
    - file: "bin/propagate.sh"
      changes:
        - "Add --exclude='state/' to the rsync exclude list"
        - "Add --exclude='dashboard-alerts.md' to the rsync exclude list"
    - file: "framework/ai/ael/tests/test_regression.py"
      changes:
        - "Replace skel/workspace/ path assertions with skel/ai/workspace/"
        - "Replace any .ael/ralph reference with ai/state/ralph"
        - "Leave self-contained temporary-tree fixtures unchanged"
  technical:
    language: "Python and bash"
    version: "Python 3.11"
    standards:
      - "No behavioural change; paths and strings only"
      - "Preserve formatting and comments"
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Deliverable

```yaml
deliverable:
  format_requirements:
    - "Apply edits in place to the existing files"
  files:
    - path: "framework/ai/src/govwatch.py"
    - path: "bin/sync-skel.sh"
    - path: "bin/propagate.sh"
    - path: "framework/ai/ael/tests/test_regression.py"
```

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Testing

```yaml
testing:
  approach: >
    Run pytest over framework/ai/ael/tests/. Optionally run govwatch against a
    project whose documents live under ai/workspace/ and confirm it renders and
    writes ai/dashboard-alerts.md.
  validation:
    - "pytest suite passes, including updated test_regression.py"
    - "govwatch.py imports and runs without path errors"
    - "Both scripts contain the new exclude entries"
```

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Tactical Brief

```yaml
tactical_brief: |
  Apply path-only edits to four files; read each before editing; change nothing
  else.
  1. framework/ai/src/govwatch.py — in main(), the ProjectPaths construction:
       workspace   = root / "ai" / "workspace"
       ael_state   = root / "ai" / "state" / "ralph"
       alerts_file = root / "ai" / "dashboard-alerts.md"
     Update the startup validation message that names the expected subdirectory
     from "workspace/" to "ai/workspace/". If the relative-path display logic
     keys on the literal substring "workspace", re-anchor it on "ai/workspace"
     so displayed document paths remain correct.
  2. bin/sync-skel.sh — add to the rsync exclude list:
       --exclude='state/'  and  --exclude='dashboard-alerts.md'
  3. bin/propagate.sh — add the same two excludes to its rsync exclude list.
  4. framework/ai/ael/tests/test_regression.py — change skel/workspace/
     assertions to skel/ai/workspace/, and any .ael/ralph reference to
     ai/state/ralph. Leave fixtures that build their own temporary workspace
     trees unchanged.
  Do not edit skel/ or downstream copies. Run pytest framework/ai/ael/tests/
  and confirm it passes.
```

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Success Criteria

```yaml
success_criteria:
  - "govwatch.py ProjectPaths point to ai/workspace, ai/state/ralph, ai/dashboard-alerts.md"
  - "govwatch.py startup validation message names ai/workspace/"
  - "bin/sync-skel.sh and bin/propagate.sh both exclude state/ and dashboard-alerts.md"
  - "test_regression.py asserts the skel/ai/workspace/ layout"
  - "pytest framework/ai/ael/tests/ passes with no errors"
  - "No file under skel/ or any downstream project was modified"
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-15 | William Watson | Initial prompt — source and script path alignment, coupled to change-b6e4a1c9 |

---

Copyright (c) 2026 William Watson. MIT License.
