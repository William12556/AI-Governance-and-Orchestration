Created: 2026 March 20

# Issue: P04 — Strategic Domain Does Not Verify Deployment Entry Point Before Naming Target Files

---

## Table of Contents

- [Issue](#issue)
- [Source](#source)
- [Affected Scope](#affected-scope)
- [Reproduction](#reproduction)
- [Behavior](#behavior)
- [Environment](#environment)
- [Analysis](#analysis)
- [Resolution](#resolution)
- [Prevention](#prevention)
- [Traceability](#traceability)
- [Version History](#version-history)

---

## Issue

```yaml
issue_info:
  id: "issue-c3e5b7d9"
  title: "P04 — Strategic Domain does not verify deployment entry point before naming target files"
  date: "2026-03-20"
  reporter: "William Watson"
  status: "resolved"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null
```

[Return to Table of Contents](#table-of-contents)

---

## Source

```yaml
source:
  origin: "code_review"
  test_ref: ""
  description: >
    Observed during post-mortem of e-Paper-IP-Display project AEL test.
    The Strategic Domain created issue-3f7e9a2b specifying
    'src/epaper_ip_display.py' as the target file without first verifying
    the deployment entry point defined in pyproject.toml [project.scripts].
    The actual entry point was 'epaper_ip_display.main:main', resolving to
    'src/epaper_ip_display/main.py'. Every subsequent document (change,
    prompt) and every AEL run inherited the wrong target. The pipeline
    produced code that was never deployed.
```

[Return to Table of Contents](#table-of-contents)

---

## Affected Scope

```yaml
affected_scope:
  components:
    - name: "P04 Issue Protocol"
      file_path: "framework/ai/governance.md"
    - name: "P03 Change Protocol"
      file_path: "framework/ai/governance.md"
    - name: "P09 Prompt Protocol"
      file_path: "framework/ai/governance.md"
  designs:
    - design_ref: ""
  version: "8.1"
```

[Return to Table of Contents](#table-of-contents)

---

## Reproduction

```yaml
reproduction:
  prerequisites: >
    A Python project using pyproject.toml [project.scripts] console entry
    points, where the entry point module path differs from a top-level
    source file of a similar name.
  steps:
    - "Strategic Domain identifies a source file requiring modification by name inference."
    - "Strategic Domain creates T03 issue with file_path set to the inferred file."
    - "Strategic Domain does not read pyproject.toml [project.scripts] to verify."
    - "All downstream documents (T02 change, T04 prompt) inherit the wrong target."
    - "AEL modifies the wrong file; the deployed entry point remains unchanged."
  frequency: "always"
  reproducibility_conditions: >
    Occurs whenever the project has a non-trivial entry point and the
    Strategic Domain names a target file without reading the project
    configuration first.
  error_output: >
    No error at document creation time. Failure manifests only at
    runtime on target hardware after build and deployment.
```

[Return to Table of Contents](#table-of-contents)

---

## Behavior

```yaml
behavior:
  expected: >
    Strategic Domain verifies the deployment entry point in pyproject.toml
    [project.scripts] before specifying any target file path in a T03 issue
    or T04 prompt document.
  actual: >
    Strategic Domain names target files by inspection of the source tree
    without cross-referencing project configuration. Wrong file is targeted.
    AEL modifies dead code. Feature is never deployed.
  impact: >
    Complete pipeline failure: all AEL work is applied to a file outside the
    deployment path. The error is silent at governance level and only detected
    at runtime on target hardware. Multiple AEL runs, document cycles, and
    human review effort are wasted.
  workaround: >
    Human post-mortem review of deployed source tree and pyproject.toml after
    observing unexpected runtime behaviour.
```

[Return to Table of Contents](#table-of-contents)

---

## Environment

```yaml
environment:
  python_version: "3.x"
  os: "any"
  dependencies:
    - library: "pyproject.toml"
      version: "PEP 517/518"
  domain: "domain_1"
```

[Return to Table of Contents](#table-of-contents)

---

## Analysis

```yaml
analysis:
  root_cause: >
    P04 §1.5.1 directs the Strategic Domain to create issue documents from
    test results and to specify affected components and file paths. It does
    not require verification of those file paths against the project's
    deployment configuration (pyproject.toml [project.scripts], setup.py
    entry_points, or equivalent). The omission allows the Strategic Domain
    to name a plausible but incorrect target file with no governance check.
  technical_notes: >
    In Python projects the executed file at runtime is determined by the
    console_scripts entry point, not by file name proximity. A file named
    'src/epaper_ip_display.py' and a package entry at
    'src/epaper_ip_display/main.py' are entirely distinct. The Strategic
    Domain must read [project.scripts] before asserting any file_path in
    a T03 or T04 document. This applies equally to setup.cfg entry_points,
    Makefile targets, or any other project-specific dispatch mechanism.
  related_issues: []
```

[Return to Table of Contents](#table-of-contents)

---

## Resolution

```yaml
resolution:
  assigned_to: "William Watson"
  target_date: ""
  approach: >
    Add a mandatory verification directive to P04 §1.5.1 and P09 §1.10.2
    requiring the Strategic Domain to read the project entry point
    configuration before specifying any target file path in a T03 issue
    or T04 prompt document.
  change_ref: "n/a — governance change, §1.4.11 exempt"
  resolved_date: "2026-03-20"
  resolved_by: "William Watson"
  fix_description: "Added entry point verification directive to P04 §1.5.1 and P09 §1.10.2 in framework/ai/governance.md and skel/ai/governance.md (v8.2). Strategic Domain must read project entry point configuration before specifying any target file_path."
```

[Return to Table of Contents](#table-of-contents)

---

## Prevention

```yaml
prevention:
  preventive_measures: >
    Mandatory entry point verification step in P04 and P09: before naming
    any source file as a target, the Strategic Domain reads the project's
    deployment configuration (pyproject.toml [project.scripts] or
    equivalent) and confirms the named file is in the execution path.
  process_improvements: >
    P04 §1.5.1: add directive — Strategic Domain reads pyproject.toml
    [project.scripts] (or equivalent) and verifies target file_path is
    in the deployment path before creating the issue document.
    P09 §1.10.2: add directive — Strategic Domain confirms deliverable
    file path against project entry point configuration before authoring
    the T04 prompt.
```

[Return to Table of Contents](#table-of-contents)

---

## Traceability

```yaml
traceability:
  design_refs: []
  change_refs: []
  test_refs: []
notes: >
  Observed in e-Paper-IP-Display project, issues 3f7e9a2b and a1c4e7f2.
  Both issue cycles targeted src/epaper_ip_display.py. Deployment entry
  point was epaper_ip_display.main:main (src/epaper_ip_display/main.py).
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-03-20 | William Watson | Initial |
| 1.1 | 2026-03-20 | William Watson | Resolved: governance.md v8.2 — directive added to P04 §1.5.1 and P09 §1.10.2 |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
