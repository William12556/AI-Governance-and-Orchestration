Created: 2026 June 10

# Prompt: Implement govwatch Governance Monitoring Tool

---

## Table of Contents

- [1.0 Prompt Information](#10-prompt-information)
- [2.0 Context](#20-context)
- [3.0 Specification](#30-specification)
- [4.0 Design](#40-design)
- [5.0 Error Handling](#50-error-handling)
- [6.0 Testing](#60-testing)
- [7.0 Deliverable](#70-deliverable)
- [8.0 Tactical Brief](#80-tactical-brief)
- [9.0 Success Criteria](#90-success-criteria)
- [10.0 Element Registry](#100-element-registry)
- [Version History](#version-history)

---

## 1.0 Prompt Information

```yaml
prompt_info:
  id: "prompt-7c1d9e02"
  task_type: "code_generation"
  source_ref: "change-7c1d9e02"
  date: "2026-06-10"
  iteration: 1
  coupled_docs:
    change_ref: "change-7c1d9e02"
    change_iteration: 1
```

Tactical Domain: Claude Code. The authoritative specification is
`dev/design/design-govwatch.md` v0.1; read it in full before coding. This
prompt operationalises that design and is not a substitute for it.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Context

```yaml
context:
  purpose: >
    Implement govwatch, a standalone read-only governance monitoring TUI for
    downstream framework projects.
  integration: >
    Single module at framework/ai/src/govwatch.py. Propagates to skel and
    downstream via the standard rsync scripts. Run from a downstream project
    root: python ai/src/govwatch.py. No dependency on AEL modules.
  knowledge_references: []
  constraints:
    - "Read-only except dashboard-alerts.md in the project root (CON-07)"
    - "Dependencies limited to textual and rich (CON-04)"
    - "Python 3.11+"
    - "No network, no server, no subprocess during polling"
    - "Reference design-govwatch.md for all component, parsing, and check detail"
```

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Specification

```yaml
specification:
  description: >
    A polling textual App that scans the project filesystem into an immutable
    snapshot each cycle, infers workflow phase, runs a two-tier compliance
    scan, lists open documents by UUID, and writes an alert summary to the
    clipboard (C key) and to dashboard-alerts.md (each scan, overwrite).
  requirements:
    functional:
      - "Workflow State panel: phase, AEL status + iteration, budget status (design §6, §7.3)"
      - "Compliance Alerts panel: Tier 1 + Tier 2 checks, colour by severity, counts, scan time (design §7)"
      - "Document Registry panel: open docs grouped by UUID; open-issue to-do list (design §5.1, §9.1)"
      - "C copies alert summary to clipboard; R refreshes; Q quits (design §8.2)"
      - "dashboard-alerts.md overwritten each scan (design §8.3)"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Comprehensive error handling; no unhandled exception from a single document (NFR-04)"
        - "Filesystem reads only; no subprocess during polling (NFR-03)"
        - "Professional docstrings"
        - "textual + rich only"
  performance:
    - target: "under 2 seconds"
      metric: "startup time (NFR-02)"
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Design

```yaml
design:
  architecture: >
    Passive polling observer with a textual presentation layer. Data flow:
    filesystem -> Scanner -> Snapshot -> {PhaseInference, ComplianceEngine}
    -> panels + AlertWriter -> dashboard-alerts.md / clipboard. See design §3.
  components:
    - name: "Scanner"
      type: "class"
      purpose: "Produce a Snapshot from the filesystem; read-only. design §5.1"
    - name: "PhaseInference"
      type: "class"
      purpose: "Derive workflow phase by precedence. design §6.0"
    - name: "ComplianceEngine"
      type: "class"
      purpose: "Tier 1 (filename/structure) then Tier 2 (content) checks. design §7"
    - name: "AlertWriter"
      type: "class"
      purpose: "Render payload; overwrite dashboard-alerts.md; clipboard on C. design §5.4, §8.3"
    - name: "GovwatchApp"
      type: "class"
      purpose: "textual.App: layout, polling timer, key bindings, startup validation. design §5.5"
  dependencies:
    internal: []
    external:
      - "textual"
      - "rich"
```

Parsing contract (design §9): documents embed fields inside fenced ```yaml
blocks. Extract every yaml block, parse each, select the block containing the
relevant root key (`change_info` / `issue_info` / `prompt_info`). Filename UUID
is authoritative. `tactical_brief` is valid only when a yaml block holds a
non-empty `tactical_brief` root key not beginning with `#`. Class `issue` maps
to folder `issues/`; masters (`<class>-<name>-master.md`) are exempt from UUID
and coupling checks.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Error Handling

```yaml
error_handling:
  strategy: >
    Per-document try/except yields a WARNING alert, never an exception (NFR-04).
    Absent .ael/ralph/ -> AEL Idle (NFR-05). Absent context-budget.md ->
    budget unknown. dashboard-alerts.md write failure -> in-TUI WARNING, app
    continues. Invalid project root at startup -> clear message, exit non-zero
    before the TUI (FR-05-04). See design §10.
  logging:
    level: "WARNING"
    format: "in-TUI alert entries"
```

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Testing

```yaml
testing:
  unit_tests: []   # none this iteration; validation is manual (change-7c1d9e02 §5)
  edge_cases:
    - "Malformed yaml block in a document"
    - "Master document present (must be exempt from coupling/UUID checks)"
    - "Absent .ael/ralph/ and absent context-budget.md"
    - "Empty workspace (Idle phase)"
  validation:
    - "Three panels render without error"
    - "No write outside dashboard-alerts.md"
    - "Phase inference matches design §6.0 precedence"
```

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Deliverable

```yaml
deliverable:
  format_requirements:
    - "Write generated code directly to the specified paths"
  files:
    - path: "framework/ai/src/govwatch.py"
      content: ""   # single module per design §12.0 element registry
    - path: "framework/ai/src/requirements-govwatch.txt"
      content: ""   # textual, rich
```

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Tactical Brief

```yaml
tactical_brief: |
  Implement framework/ai/src/govwatch.py: a read-only governance monitoring
  TUI (textual + rich, Python 3.11). Read dev/design/design-govwatch.md in
  full first; it is authoritative.
  Build, in one module:
    - dataclasses: ProjectPaths, DocumentRecord, AelState, BudgetState, Alert,
      Snapshot.
    - Scanner.scan() -> Snapshot: walk workspace/<dir>/ (exclude closed/),
      parse filename + first matching ```yaml block per document; read
      .ael/ralph/ state files; read context-budget.md. CLASS_DIRS maps class
      to folder (issue -> issues/). Reads only.
    - PhaseInference.infer(snapshot): precedence per design §6.0.
    - ComplianceEngine.evaluate(snapshot) -> list[Alert]: Tier 1 filename/
      coupling, then Tier 2 content (design §7). tactical_brief valid only if a
      yaml block has a non-empty tactical_brief key not starting with '#'.
    - AlertWriter: payload() text; write() overwrites dashboard-alerts.md (sole
      write target); copy to clipboard on C.
    - GovwatchApp(textual.App): three panels (design §9.2 layout), poll timer
      (--interval, default 5), bindings C/R/Q, startup validate_project().
    - CLI: --project (default cwd), --interval (default 5).
  Constraints: write nothing except dashboard-alerts.md; no subprocess during
  polling; a malformed document yields a WARNING, never an exception; absent
  .ael/ralph/ -> Idle.
  Also create framework/ai/src/requirements-govwatch.txt listing textual and rich.
```

[Return to Table of Contents](#table-of-contents)

---

## 9.0 Success Criteria

```yaml
success_criteria:
  - "framework/ai/src/govwatch.py created with no syntax errors"
  - "framework/ai/src/requirements-govwatch.txt created listing textual and rich"
  - "All classes and functions in design §12.0 element registry are present"
  - "Tool writes only dashboard-alerts.md; no other file is created or modified"
  - "Runs from a project root and renders three panels; C/R/Q operate"
  - "Absent .ael/ralph/ and malformed documents are handled without exception"
```

[Return to Table of Contents](#table-of-contents)

---

## 10.0 Element Registry

```yaml
element_registry:
  source: "dev/design/design-govwatch.md §12.0"
  entries:
    modules:
      - name: "govwatch"
        path: "framework/ai/src/govwatch.py"
    classes:
      - name: "ProjectPaths"
        module: "govwatch"
      - name: "DocumentRecord"
        module: "govwatch"
      - name: "AelState"
        module: "govwatch"
      - name: "BudgetState"
        module: "govwatch"
      - name: "Alert"
        module: "govwatch"
      - name: "Snapshot"
        module: "govwatch"
      - name: "Scanner"
        module: "govwatch"
      - name: "PhaseInference"
        module: "govwatch"
      - name: "ComplianceEngine"
        module: "govwatch"
      - name: "AlertWriter"
        module: "govwatch"
      - name: "GovwatchApp"
        module: "govwatch"
    functions:
      - name: "validate_project"
        module: "govwatch"
        signature: "validate_project(paths: ProjectPaths) -> bool"
      - name: "parse_filename"
        module: "govwatch"
        signature: "parse_filename(name: str) -> tuple"
      - name: "parse_document"
        module: "govwatch"
        signature: "parse_document(path: str) -> DocumentRecord"
      - name: "main"
        module: "govwatch"
        signature: "main() -> None"
    constants:
      - name: "CLASS_DIRS"
        module: "govwatch"
        type: "dict[str, str]"
      - name: "DEFAULT_INTERVAL"
        module: "govwatch"
        type: "int"
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-10 | William Watson | Initial prompt — govwatch implementation for Claude Code, coupled to change-7c1d9e02 |

---

Copyright (c) 2026 William Watson. MIT License.
