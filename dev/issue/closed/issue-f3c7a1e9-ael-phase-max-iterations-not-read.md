Created: 2026 March 24

# Issue: AEL Orchestrator — max_iterations Applied to Both Outer Loop and Inner Phase

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
  id: "issue-f3c7a1e9"
  title: "AEL Orchestrator — max_iterations applied to both outer loop and inner phase; phase_max_iterations never read"
  date: "2026-03-24"
  reporter: "William Watson"
  status: "resolved"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-f3c7a1e9"
    change_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## Source

```yaml
source:
  origin: "user_report"
  test_ref: ""
  description: >
    Discovered during GTach project AEL execution of prompt-e1f2a3b4-1
    (Comm Transport Abstraction — New Files). With config.yaml
    loop.max_iterations set to 5, the work phase exhausted all 5 iterations
    without completing the task. The work phase required a minimum of ~9
    tool calls (read task, read iteration, list directory, 4 file writes,
    write work-summary.txt, write work-complete.txt). The 5-iteration limit
    was insufficient to complete those operations, causing WORK PHASE FAILED.
    Investigation revealed that orchestrator.py passes max_iterations to
    run_phase() as its iteration limit, meaning it governs both the outer
    Ralph Loop cycle count and the inner tool-call limit. The config.yaml
    field phase_max_iterations: 20 is defined but never read by the
    orchestrator, making it a no-op. The two limits cannot be set
    independently.
```

[Return to Table of Contents](#table-of-contents)

---

## Affected Scope

```yaml
affected_scope:
  components:
    - name: "orchestrator.py"
      file_path: "skel/ai/ael/src/orchestrator.py"

  designs:
    - design_ref: "governance.md §1.1.11 AEL"

  version: "governance v8.2 / AEL orchestrator current"
```

[Return to Table of Contents](#table-of-contents)

---

## Reproduction

```yaml
reproduction:
  prerequisites: >
    AEL configured with config.yaml loop.max_iterations set to a low value
    (e.g. 5). Task requires more tool calls than max_iterations permits
    (e.g. creating 4 files requires ~9+ tool calls).

  steps:
    - "Set loop.max_iterations: 5 in config.yaml"
    - "Submit a task requiring 4+ file writes"
    - "Run: python ai/ael/src/orchestrator.py --mode loop --task <prompt>"
    - "Observe: [ael] max iterations (5) reached; WORK PHASE FAILED"

  frequency: "always"

  reproducibility_conditions: >
    Any task where the number of required tool calls exceeds max_iterations.
    Typical code generation tasks require 8-15 tool calls minimum
    (reads + writes + state file updates).

  error_output: |
    [ael] max iterations (5) reached
    ✗ WORK PHASE FAILED
```

[Return to Table of Contents](#table-of-contents)

---

## Behavior

```yaml
behavior:
  expected: >
    config.yaml provides two independent controls:
    - loop.max_iterations: governs the number of outer Ralph Loop cycles
      (worker + reviewer passes). A value of 3-5 is appropriate.
    - loop.phase_max_iterations: governs the number of tool-call iterations
      within a single work or review phase. A value of 15-20 is appropriate
      for non-trivial code generation tasks.
    run_loop() uses max_iterations for outer cycle limit.
    run_phase() uses phase_max_iterations for inner tool-call limit.

  actual: >
    orchestrator.py passes max_iterations to run_phase() as the
    phase iteration limit. phase_max_iterations is read from config.yaml
    but never passed to any function. Both limits are identical in effect,
    making it impossible to have a low outer cycle count and a high inner
    tool-call budget simultaneously.

  impact: >
    With max_iterations set to a governance-appropriate outer loop value
    (3-5), any non-trivial code generation task fails immediately in the
    work phase. The only workaround is to inflate max_iterations to a value
    sufficient for inner phase completion (15-20), which also inflates the
    outer loop limit unnecessarily.

  workaround: >
    Set loop.max_iterations to 20 in config.yaml. This gives the inner
    phase sufficient tool-call budget at the cost of allowing up to 20
    outer Ralph Loop cycles. Applied in GTach project as a temporary
    measure.
```

[Return to Table of Contents](#table-of-contents)

---

## Environment

```yaml
environment:
  python_version: "3.x"
  os: "macOS (Apple Silicon)"
  dependencies:
    - library: "openai"
      version: "current"
  domain: "AEL orchestrator"
```

[Return to Table of Contents](#table-of-contents)

---

## Analysis

```yaml
analysis:
  root_cause: >
    In orchestrator.py main_async(), the variable max_iter is read from
    config["loop"]["max_iterations"]. This single value is passed to
    run_loop() as its max_iterations argument, and run_loop() in turn
    passes the same value to every run_phase() call as its max_iterations
    argument. The config.yaml key phase_max_iterations is loaded into the
    config dict but is never referenced in code.

    Relevant code path:
      max_iter = args.max_iterations or config["loop"]["max_iterations"]
      rc = await run_loop(..., max_iter, ...)
        -> rc = await run_phase(..., max_iterations, ...)  # same value

  technical_notes: >
    Fix requires two changes to orchestrator.py:
    1. Read phase_max_iterations separately:
         phase_max_iter = config["loop"].get("phase_max_iterations", max_iter)
    2. Pass phase_max_iter to run_phase() instead of max_iter:
         rc = await run_phase(..., phase_max_iter, ...)
    run_loop() continues to receive max_iter as its outer cycle limit.
    No changes required to config.yaml, recipes, or governance documents.
    The fix is confined to a single function (main_async) and is both
    trivial and surgical.

  related_issues: []
```

[Return to Table of Contents](#table-of-contents)

---

## Resolution

```yaml
resolution:
  assigned_to: "William Watson"
  change_ref: "change-f3c7a1e9"
  resolved_date: "2026-03-24"
  resolved_by: "William Watson"
  fix_description: >
    GTach orchestrator.py: worker and reviewer mode run_phase() calls updated
    to pass phase_max_iter instead of max_iter (2 lines). solax-modbus
    orchestrator.py: phase_max_iter read added to main_async(); run_loop()
    signature extended with phase_max_iterations parameter; all run_phase()
    and run_loop() call sites updated. solax-modbus config.yaml:
    max_iterations reduced to 5; phase_max_iterations: 20 added.
    framework/ and skel/ orchestrators already correct — no changes required.
```

[Return to Table of Contents](#table-of-contents)

---

## Prevention

```yaml
prevention:
  governance_update: >
    None required. The config.yaml structure already expresses the intent
    correctly via the two separate fields. The defect is purely in the
    orchestrator implementation.
  testing: >
    Add an AEL integration test: configure max_iterations=3 and
    phase_max_iterations=15; submit a task requiring 10+ tool calls;
    verify it completes in one outer cycle rather than failing.
```

[Return to Table of Contents](#table-of-contents)

---

## Traceability

```yaml
traceability:
  governance_ref: "governance.md §1.1.11 AEL — Loop control boundary conditions"
  project_ref: "GTach change-e1f2a3b4 — workaround applied (max_iterations: 20)"
  related_changes:
    - "change-f3c7a1e9"
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2026-03-24 | William Watson | Resolved: change-f3c7a1e9 — phase_max_iter wired to run_phase() in GTach and solax-modbus |
| 1.0 | 2026-03-24 | William Watson | Initial issue document |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
