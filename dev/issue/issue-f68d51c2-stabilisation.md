Created: 2026 November 18

```yaml
issue_info:
  id: "issue-f68d51c2"
  title: "Stabilisation M2: predictable temporary names, unescaped provider text, null config blocks, bootstrap cleanup, YAML loader robustness, two one-liners"
  date: "2026-11-18"
  status: "resolved"  # change-f68d51c2 implemented 2026-11-18
  severity: "low"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-f68d51c2"
    change_iteration: 1

source:
  origin: "code_review"  # follow-up audits of 2026-11-16 and audit-9377f9b9-followup-2026-11-07
  description: >
    Milestone M2 of dev/task.md (2026-11-18): one stabilisation change for
    the findings the operator selected for the release (governance 12.13
    P02.11). audit-d4f527e7 F-01 (security-relevant low); audit-bae631c7
    F-01, F-02, F-03; audit-541f5c58 F-01, F-02; audit-9377f9b9-followup
    F-01, F-02 (dev/task.md row "YAML loader robustness").

affected_scope:
  components:
    - { name: "engine orchestrator", file_path: "ai/engine/src/orchestrator.py" }
    - { name: "approval recorder", file_path: "ai/engine/src/approve.py" }
    - { name: "Overwatch", file_path: "ai/webui/src/overwatch.py" }
    - { name: "linter", file_path: "ai/engine/src/linter.py" }
    - { name: "manifest loader", file_path: "ai/engine/src/manifest.py" }
    - { name: "stage tracking", file_path: "ai/engine/src/stages.py" }
    - { name: "write scope", file_path: "ai/engine/src/scope.py" }
    - { name: "bootstrap script", file_path: "bin/bootstrap.sh" }
    - { name: "propagation script", file_path: "bin/propagate.sh" }
  designs:
    - { design_ref: "design-14e05e35 §3.0, §11.0" }
    - { design_ref: "design-ael-orchestrator §4.1" }
    - { design_ref: "requirements-14e05e35 NFR-04" }
  version: "main e07476d; governance 12.13"

reproduction:
  prerequisites: "main e07476d"
  steps:
    - "(A) create a symlink at <state_dir>/.BLOCKED.md.<engine pid>.tmp pointing to a writable file, then let the engine write BLOCKED.md; the same for the Overwatch outputs and ai/approvals.yaml"
    - "(B) a provider error whose text contains '[/v1/chat/completions]' during _completion_with_retry"
    - "(C) ai/config.yaml with 'context:' or 'execution:' empty (null), a list or a string; run --mode loop, worker or reviewer"
    - "(D) bin/bootstrap.sh with a download that fails, or a tarball whose extraction fails after the listing check (a '..' member)"
    - "(E) a governance document or manifest.yaml with an unquoted invalid date (2026-11-31) or time (25:00:00); a deeply nested or invalid-date YAML block read by stages._status, stages.parse_approvals, scope.extract_deliverable_paths, orchestrator.load_yaml or orchestrator._load_config"
    - "(F1) the max-iterations continuation prompt, interactive and non-interactive"
    - "(F2) a manifest whose workspace_folders block list is indented at column 0, or has CRLF line ends; run bootstrap.sh or propagate.sh"
  frequency: "always, under the stated condition"
  error_output: "(B) rich.errors.MarkupError; (C) AttributeError: '<type>' object has no attribute 'get'; (E) ValueError or RecursionError with a traceback"

behavior:
  expected: >
    (A) A planted entry at a temporary name is never followed or moved
    into place. (B) A provider error is retried and ends BLOCKED after the
    bounded retries, whatever its text. (C) A null block is read as empty;
    any other non-mapping is a configuration error naming the file and the
    key, before any state is written. (D) A failed bootstrap leaves no
    temporary directory and no partial ai/. (E) No YAML content ends a
    checker, the manifest load, the stage scan, the scope extraction or a
    configuration load with a traceback. (F1) The prompt shows '[y/N]'.
    (F2) Every block list valid for manifest.py gives its folders, without
    carriage returns.
  actual: >
    (A) The helpers open '.<name>.<pid>.tmp' with open(..., 'w'): a symlink
    there is followed and then moved onto the name; a directory there
    blocks the write. (B) err_text is interpolated into Rich markup
    unescaped. (C) config.get(key, {}) returns the null or other value and
    the next .get raises. (D) set -e ends the script without removing
    TMPWORK; a failed extraction leaves a partial ai/ and the next run
    stops at 'ai/ already exists'. (E) Only yaml.YAMLError (and in places
    RecursionError) is caught; PyYAML's timestamp constructor raises
    ValueError. (F1) Rich reads '[y/N]' as a style tag and drops it.
    (F2) The awk block branch ends at a line starting with '-' at column 0
    and keeps a trailing '\r'.
  impact: "(A) An actor that can create a symlink in the state directory can make the engine overwrite a file it can write; (B), (C), (E) runs end with a traceback instead of a retry, BLOCKED or a configuration error; (D) manual cleanup; (F) cosmetic and missing folders."
  workaround: "None needed for normal operation; avoid the stated inputs."

environment:
  os: "platform-independent (scripts: bash 3.2 and BSD tools on macOS; GNU on Linux)"

analysis:
  root_cause: >
    Line numbers at main e07476d. (A) orchestrator.py:744-764
    _write_atomic, :734-741 _keep_mode; overwatch.py:421-443
    _write_text_atomic; approve.py:35-58 _write_atomic. (B)
    orchestrator.py:542-545. (C) orchestrator.py:2815 exec_cfg, :2821
    ctx_cfg, :858 resolve_context_window; _validate_context_windows
    (:662-681) returns for a non-mapping context. (D) bootstrap.sh:64
    mktemp, :86 extraction, :79 and :146 the only removals; no trap.
    (E) linter._parse_yaml_block (:166), manifest.load_manifest (:119),
    stages.parse_approvals (:99), stages._status (:173),
    scope.extract_deliverable_paths (:123), orchestrator.load_yaml (:630),
    orchestrator._load_config (:635-659). (F1) orchestrator.py:2242-2244,
    :2249. (F2) bootstrap.sh:117, propagate.sh:134.
  technical_notes: >
    The run record writer _write_run_record already uses a random,
    exclusively created temporary file (NamedTemporaryFile); the three
    newer helpers do not. tempfile.mkstemp creates the file with mode
    0600, so a new file needs the mode open() would give (0666 masked by
    the umask) set explicitly. No module of the engine or Overwatch uses
    threads, so reading the umask by setting and restoring it is safe.

resolution:
  approach: "To be defined in change-f68d51c2."
  change_ref: "change-f68d51c2"

traceability:
  design_refs: ["design-14e05e35 §3.0, §11.0", "design-ael-orchestrator §4.1", "requirements-14e05e35 NFR-04"]
  change_refs: ["change-f68d51c2"]

notes: "References: audit-d4f527e7-followup-2026-11-16 F-01 (and F-03, removed by the same fix); audit-bae631c7-followup-2026-11-16 F-01 to F-03; audit-541f5c58-followup-2026-11-16 F-01, F-02; audit-9377f9b9-followup-2026-11-07 F-01, F-02; all in dev/audit/closed/. dev/task.md row M2."

version_history:
  - version: "1.0"
    date: "2026-11-18"
    changes: ["Initial issue for milestone M2"]
  - version: "1.1"
    date: "2026-11-18"
    changes: ["Status resolved: change-f68d51c2 implemented and merged (3703cf8); verification audit open"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "issue"
```

Copyright (c) 2026 William Watson. MIT License.
