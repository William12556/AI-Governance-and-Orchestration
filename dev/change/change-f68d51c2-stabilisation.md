Created: 2026 November 18

```yaml
change_info:
  id: "change-f68d51c2"
  title: "Stabilisation M2: exclusive temporary files, escaped provider text, config blocks, bootstrap cleanup, YAML loader robustness, two one-liners"
  date: "2026-11-18"
  status: "implemented"  # operator approval 2026-11-18; implemented and merged 2026-11-18 (3703cf8); verification audit open
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-f68d51c2"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-f68d51c2"
  description: "Milestone M2 of dev/task.md (2026-11-18): the findings selected by the operator for release v0.3.0."

scope:
  summary: >
    (A, d4f527e7 F-01) The three atomic write helpers create their
    temporary file with tempfile.mkstemp in the target directory and set
    the mode before os.replace. (B, bae631c7 F-02) The retry console line
    escapes the provider error text. (C, bae631c7 F-03) A null context: or
    execution: block is read as empty; any other non-mapping is a
    configuration error before any state is written. (D, 541f5c58 F-01)
    bootstrap.sh removes its temporary directory on every exit and removes
    a partial ai/ when extraction fails. (E, 9377f9b9-followup F-01, F-02)
    The YAML readers catch ValueError, TypeError, OverflowError and
    RecursionError and report them as each site reports invalid YAML today.
    (F1, bae631c7 F-01) '[y/N]' is escaped in the continuation prompt.
    (F2, 541f5c58 F-02) workspace_folders_of accepts a block list indented
    at column 0 and strips a trailing carriage return.
  affected_components:
    - { name: "engine orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }  # A, B, C, E, F1
    - { name: "approval recorder", file_path: "ai/engine/src/approve.py", change_type: "modify" }  # A
    - { name: "Overwatch", file_path: "ai/webui/src/overwatch.py", change_type: "modify" }  # A
    - { name: "linter", file_path: "ai/engine/src/linter.py", change_type: "modify" }  # E
    - { name: "manifest loader", file_path: "ai/engine/src/manifest.py", change_type: "modify" }  # E
    - { name: "stage tracking", file_path: "ai/engine/src/stages.py", change_type: "modify" }  # E
    - { name: "write scope", file_path: "ai/engine/src/scope.py", change_type: "modify" }  # E
    - { name: "bootstrap script", file_path: "bin/bootstrap.sh", change_type: "modify" }  # D, F2
    - { name: "propagation script", file_path: "bin/propagate.sh", change_type: "modify" }  # F2
    - { name: "tests", file_path: "tests/engine/, tests/webui/", change_type: "modify" }
    - { name: "engine design", file_path: "dev/design/design-14e05e35-engine-generalisation.md", change_type: "modify" }  # planner after review: §11.0
    - { name: "orchestrator design", file_path: "dev/design/design-ael-orchestrator.md", change_type: "modify" }  # planner after review: §4.1
    - { name: "operations guide", file_path: "ai/engine/doc/guide-engine-operations.md", change_type: "modify" }  # planner after review: §3.0
  affected_designs:
    - { design_ref: "design-14e05e35", sections: ["§11.0 configuration row"] }
    - { design_ref: "design-ael-orchestrator", sections: ["§4.1 state file writes"] }
    - { design_ref: "guide-engine-operations", sections: ["§3.0 configuration errors"] }
  out_of_scope:
    - "All rows of dev/task.md marked 'Deferred — post-release', including the test gaps of row 6 (a) other than the continuation prompt text"
    - "Other BLOCKED.md log order sites (audit-d4f527e7 F-06), archive numbering (F-05), refusal text (F-07)"
    - "MCP error text redaction (audit-bae631c7 F-05)"
    - "Other quoted-name forms of the workspace_folders parser (multi-line flow lists, aliases, quoted names holding ',', ']' or '#')"
    - "A shared module for the three write helpers (ai/core/ stays reserved)"
    - "Any change to governance.md or the templates"

rational:
  problem_statement: "See issue-f68d51c2."
  proposed_solution: "Local, minimal fixes at each site named in issue-f68d51c2 analysis.root_cause, each with one or two tests and a mutation that the tests kill."
  alternatives_considered:
    - option: "One shared write helper in ai/core/"
      reason_rejected: "ai/core/ is reserved; three small local helpers keep the component boundaries; consistency is checked by the same tests"
    - option: "O_NOFOLLOW with the predictable name"
      reason_rejected: "Still fails on a planted directory and on two writers; mkstemp removes both"
    - option: "except Exception in the YAML readers"
      reason_rejected: "Hides programming errors (audit-9377f9b9-followup X12)"
    - option: "Defer E and F to after the release"
      reason_rejected: "Operator decision 2026-11-18: include them to close the work out"
  benefits:
    - "The atomic write protection holds for the temporary name as well as the target name"
    - "No configuration, provider text or YAML input ends a run or a check with a traceback"
    - "A failed bootstrap can be repeated without manual cleanup"
  risks:
    - risk: "A new file written by a helper gets a different mode from before"
      mitigation: "The mode is set to 0666 masked by the process umask, which is what open() gave; a test asserts it"
    - risk: "load_yaml now raises ConfigError where it raised a YAML exception"
      mitigation: "Each caller is checked; a caller that does not report ConfigError is a recorded deviation"

technical_details:
  current_behavior: "See issue-f68d51c2 behavior.actual and analysis.root_cause."
  proposed_behavior: >
    (A) In orchestrator._write_atomic, overwatch._write_text_atomic and
    approve._write_atomic: fd, tmp = tempfile.mkstemp(dir=<directory of
    the target>, prefix='.' + <target basename> + '.', suffix='.tmp');
    write through os.fdopen(fd, ...) with the encoding each helper uses
    today; set the mode with os.fchmod (or os.chmod on tmp) before
    os.replace: the permission bits of an existing regular file at the
    target (lstat; a symlink or other type is not a regular file), else
    0o666 & ~umask, the umask read with os.umask and restored at once;
    os.replace(tmp, target); on BaseException remove tmp and re-raise.
    Target resolution is unchanged: orchestrator replaces the name,
    overwatch and approve resolve the path first. (B) _completion_with_retry
    retry branch prints {escape(err_text)}. (C) A check of the config
    blocks runs in main_async before the first read of config['context']
    or config['execution'] and before any state is written, in the modes
    that read them: a None value is replaced by {} in config; any other
    non-dict raises ConfigError('<key>: must be a mapping'), reported as
    'configuration error (<file>): <key>: must be a mapping', exit 1, no
    state written. (D) bootstrap.sh: trap 'rm -rf "${TMPWORK}"' EXIT
    directly after mktemp; when tar extraction fails, rm -rf
    "${PROJECT_AI}" (it did not exist before the run, checked at :32),
    print an error to stderr and exit 1. (E) Each YAML reader also catches
    ValueError, TypeError, OverflowError and RecursionError (not
    Exception): linter._parse_yaml_block gives (None, first line of
    str(e)) or 'nesting too deep'; manifest.load_manifest raises
    ManifestError('<path>: invalid YAML: <first line of str(e)>');
    stages._status and scope.extract_deliverable_paths return what they
    return today for a yaml.YAMLError; stages.parse_approvals returns {}
    (fail closed); orchestrator.load_yaml raises ConfigError('<path>:
    invalid YAML: <problem>'); orchestrator._load_config raises
    ConfigError('invalid YAML: <first line of str(e)>'). (F1) '\\[y/N]'
    at both continuation-prompt sites. (F2) In workspace_folders_of of
    both scripts the block branch stays open on a line that starts with
    '-' at column 0, and every extracted name has a trailing '\r'
    removed (block and flow branches).
  implementation_approach: "Claude Code cloud session per prompt-f68d51c2 after operator approval, on a session branch. The planner reviews the branch and updates the three documents in affected_designs after review. Verification audit (governance P02.10.1) by an independent session."
  code_changes:
    - { component: "orchestrator", file: "ai/engine/src/orchestrator.py", change_summary: "A, B, C, E, F1", functions_affected: ["_keep_mode", "_write_atomic", "_completion_with_retry", "load_yaml", "_load_config", "main_async", "run_loop (continuation prompt)"] }
    - { component: "approve", file: "ai/engine/src/approve.py", change_summary: "A", functions_affected: ["_write_atomic"] }
    - { component: "overwatch", file: "ai/webui/src/overwatch.py", change_summary: "A", functions_affected: ["_write_text_atomic"] }
    - { component: "linter", file: "ai/engine/src/linter.py", change_summary: "E", functions_affected: ["_parse_yaml_block"] }
    - { component: "manifest", file: "ai/engine/src/manifest.py", change_summary: "E", functions_affected: ["load_manifest"] }
    - { component: "stages", file: "ai/engine/src/stages.py", change_summary: "E", functions_affected: ["parse_approvals", "_status"] }
    - { component: "scope", file: "ai/engine/src/scope.py", change_summary: "E", functions_affected: ["extract_deliverable_paths"] }
    - { component: "bootstrap", file: "bin/bootstrap.sh", change_summary: "D, F2", functions_affected: ["main body", "workspace_folders_of"] }
    - { component: "propagate", file: "bin/propagate.sh", change_summary: "F2", functions_affected: ["workspace_folders_of"] }
  interface_changes:
    - { interface: "ai/config.yaml context:, execution:", change_type: "behavior", details: "null read as empty; other non-mapping refused as a configuration error", backward_compatible: "yes for valid configurations" }
    - { interface: "orchestrator.load_yaml", change_type: "behavior", details: "invalid YAML raises ConfigError", backward_compatible: "yes for valid recipes" }

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "Standard library, PyYAML and Rich only" }

testing_requirements:
  test_approach: "pytest offline, in the existing module beside each site's change-d4f527e7, change-bae631c7, change-541f5c58 or change-9377f9b9 tests."
  test_cases:
    - { scenario: "A1: each helper with a symlink planted at '.<name>.<pid>.tmp' pointing to a victim file", expected: "victim unchanged; target is a regular file with the new content" }
    - { scenario: "A2: each helper with a directory planted at the same name", expected: "write succeeds" }
    - { scenario: "A3: a new file; a symlink at the name of a state file", expected: "mode 0o666 & ~umask in both cases" }
    - { scenario: "B: a provider error containing '[/x]' on the first attempt, success on the second", expected: "no MarkupError; two attempts; the error text printed literally" }
    - { scenario: "C: context: and execution: each null, a list and a string, in loop mode", expected: "null proceeds past the check; list and string exit 1 with 'configuration error (<file>): <key>: must be a mapping' and no state directory" }
    - { scenario: "D1: bootstrap.sh with a failing download (curl stand-in exits 22)", expected: "non-zero exit; TMPDIR holds no directory from the run" }
    - { scenario: "D2: bootstrap.sh with a tarball that holds ai/engine/ and a '..' member", expected: "non-zero exit; no ai/ in the project; no temporary directory left" }
    - { scenario: "E: an unquoted invalid date at each of the seven readers; a 5,000-level nesting at the readers that do not yet catch RecursionError", expected: "the per-site result in proposed_behavior (E); no traceback" }
    - { scenario: "F1: the continuation prompt, non-interactive and interactive", expected: "rendered text contains '[y/N]'" }
    - { scenario: "F2: a manifest with '- a' and '- b' at column 0 under workspace_folders, and an indented block list with CRLF line ends, in both scripts", expected: "folders a and b created; no name ends in a carriage return" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline; macOS suite run by the operator"
    - "Mutations M1 to M12 of prompt-f68d51c2 each fail a named test"
    - "linter.py dev and protocol_checker.py dev: 0 errors"
    - "bash -n passes for both scripts"
    - "Verification audit by an independent session (governance P02.10.1)"

implementation:
  effort_estimate: "3-4 hours"
  implementation_steps:
    - { step: "Source and tests (prompt-f68d51c2)", owner: "Claude Code cloud" }
    - { step: "Planner review of the session branch; design-14e05e35 §11.0, design-ael-orchestrator §4.1, guide-engine-operations §3.0", owner: "planner" }
    - { step: "macOS suite", owner: "operator" }
    - { step: "Verification audit (P02.10.1)", owner: "independent session" }
  rollback_procedure: "Revert the implementation commits."
  deployment_notes: "Released as v0.3.0 and propagated to GTach and solax-modbus (milestone M3, dev/task.md row 8e)."

traceability:
  related_changes:
    - { change_ref: "change-d4f527e7", relationship: "corrects (audit-d4f527e7 F-01)" }
    - { change_ref: "change-bae631c7", relationship: "follows up (audit-bae631c7 F-01 to F-03)" }
    - { change_ref: "change-541f5c58", relationship: "follows up (audit-541f5c58 F-01, F-02)" }
    - { change_ref: "change-9377f9b9", relationship: "follows up (audit-9377f9b9-followup F-01, F-02)" }
  related_issues:
    - { issue_ref: "issue-f68d51c2", relationship: "source" }

notes: "Operator decision 2026-11-18: M2 holds the four selected low findings, YAML loader robustness and the one-liners. Under governance P02.11, the verification audit may raise only an unmet criterion, a regression or a defect introduced on the changed lines; at most one remediation round."

version_history:
  - version: "1.0"
    date: "2026-11-18"
    changes: ["Initial change record for milestone M2"]
  - version: "1.1"
    date: "2026-11-18"
    changes: ["Approved by the operator as drafted, with the planner decisions confirmed: new-file mode 0666 masked by the umask; three local write helpers; load_yaml raises ConfigError; parse_approvals fails closed; observations only, no fixes outside FR-01 to FR-08. Implementation per prompt-f68d51c2"]
  - version: "1.2"
    date: "2026-11-18"
    changes:
      - "Implemented in Claude Code cloud on branch claude/wonderful-rubin-pjutl1 from 76bac3a: engine b643021, webui c4e27b7, scripts 2a683f0, tests 92fa6d1, report and prompt move 3703cf8 (report-f68d51c2 v1.0). Merged fast-forward into main at 3703cf8. Status implemented"
      - "Session (Linux): 858 passed, 4 skipped at baseline; 894 passed, 4 skipped after (36 new cases). Mutations M1 to M13 fail their named tests. Operator macOS suite after the merge: 898 passed"
      - "Planner review: diff limited to the prompt scope; source read against FR-01 to FR-08; the 18 new cases of the linter, manifest, stages, bin-script and Overwatch modules re-run on Linux (pass); M12 repeated against bootstrap.sh (killed)"
      - "Report deviations: D-01 (the recipe caller of load_yaml does not catch ConfigError; pre-existing traceback) deferred post-release under P02.11; D-02 and D-03 accepted. Observations: no action"
      - "Planner updates: design-14e05e35 v1.34 §11.0; design-ael-orchestrator v0.15 §4.1; guide-engine-operations v1.36 §3.0"
      - "Open: verification audit (governance P02.10.1)"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "change"
```

Copyright (c) 2026 William Watson. MIT License.
