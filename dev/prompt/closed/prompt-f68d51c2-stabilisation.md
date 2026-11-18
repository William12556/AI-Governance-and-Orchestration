Created: 2026 November 18

```yaml
prompt_info:
  id: "prompt-f68d51c2"
  task_type: "debug"
  source_ref: "change-f68d51c2"
  target_profile: "claude_code"  # Claude Code cloud session
  date: "2026-11-18"
  iteration: 1
  coupled_docs:
    change_ref: "change-f68d51c2"
    change_iteration: 1

context:
  purpose: >
    Milestone M2 (stabilisation before release v0.3.0): close the selected
    low findings of the follow-up audits of 2026-11-16 and the YAML loader
    robustness item, with one test per behaviour. Remediates
    issue-f68d51c2. This is the last change before the release; keep to
    the stated scope exactly.
  integration: >
    Line numbers are at main e07476d; locate code by the quoted text if
    lines have moved.
    ai/engine/src/orchestrator.py: _keep_mode (:734-741, lstat; chmod only
    for a regular file); _write_atomic (:744-764, tmp_path
    '.{basename}.{os.getpid()}.tmp' opened with open(tmp_path, 'w'),
    _keep_mode, os.replace, BaseException cleanup); write_state (:767-769);
    _write_run_record (about :772-795, NamedTemporaryFile pattern, not
    changed); _completion_with_retry (:485-563; retry console line
    :542-545 'retrying in {backoff:.1f}s: {err_text}[/yellow]');
    load_yaml (:630-632, yaml.safe_load, used for recipes); _load_config
    (:635-659, ConfigError for OSError, MarkedYAMLError, YAMLError,
    RecursionError, non-mapping top level); _validate_context_windows
    (:662-681, returns for a non-dict context); resolve_context_window
    (about :858, ctx_cfg = config.get('context', {})); the continuation
    prompt (:2242-2244 non-interactive, :2249 interactive, both contain
    '[y/N]' inside Rich markup); main_async (about :2805-2830: timeout
    check, _validate_context_windows call, exec_cfg =
    config.get('execution', {}) :2815, ctx_cfg = config.get('context', {})
    :2821, archive_prior_logs, setup_logging). Configuration errors are
    printed as 'configuration error (<file>): <message>' with exit 1.
    ai/webui/src/overwatch.py: _write_text_atomic (:421-443; resolves the
    path, copies the mode, os.replace). ai/engine/src/approve.py:
    _write_atomic (:35-58; resolves the path; locale encoding).
    ai/engine/src/linter.py: _parse_yaml_block (:166). ai/engine/src/
    manifest.py: load_manifest (:119). ai/engine/src/stages.py:
    parse_approvals (:99), _status (:173). ai/engine/src/scope.py:
    extract_deliverable_paths (:123). bin/bootstrap.sh: PROJECT_AI (:30),
    'ai/ already exists' check (:32-36), TMPWORK=$(mktemp -d) (:64),
    listing check (:70-81, removes TMPWORK at :79), extraction 'tar -xz
    -C "${PROJECT_ROOT}" -f "${TARBALL}"' (:86), workspace_folders_of
    (:101-126, block-end rule 'f && /^[^[:space:]#]/ { f = 0 }' at :117),
    final removal of TMPWORK (:146). bin/propagate.sh:
    workspace_folders_of (:118-143, the same rule at :134).
  knowledge_references:
    - "dev/change/change-f68d51c2-stabilisation.md (scope, proposed_behavior A to F2)"
    - "dev/issue/issue-f68d51c2-stabilisation.md"
    - "dev/audit/closed/audit-d4f527e7-followup-2026-11-16.md F-01, §4.1"
    - "dev/audit/closed/audit-bae631c7-followup-2026-11-16.md F-01 to F-03, §4.2, §4.3, §4.5"
    - "dev/audit/closed/audit-541f5c58-followup-2026-11-16.md F-01, F-02, §4.2, §4.3"
    - "dev/audit/closed/audit-9377f9b9-followup-2026-11-07.md F-01, F-02, §4.1, §4.6"
    - "dev/task.md rows M2 and 'YAML loader robustness'"
    - "CLAUDE.md"
  constraints:
    - "Execution environment: Claude Code cloud (Linux container, repository clone). No network other than package installation."
    - "Source changes are limited to the nine files in change-f68d51c2 code_changes: ai/engine/src/orchestrator.py, approve.py, linter.py, manifest.py, stages.py, scope.py; ai/webui/src/overwatch.py; bin/bootstrap.sh; bin/propagate.sh."
    - "Test changes are limited to adding cases to tests/engine/test_tracking_state_hygiene.py, test_runtime_hygiene.py, test_stages.py, test_linter.py, test_manifest_gates.py, test_write_scope.py, test_bin_scripts.py and tests/webui/test_overwatch.py. Other existing tests may change only where an assertion depends on behaviour changed by an FR below; record each such change in the report."
    - "Governance changes are limited to creating the report named in deliverable.files and moving this prompt to dev/prompt/closed/. Do not edit any other document, any closed/ directory, governance.md, manifest.yaml, the templates, ai/engine/doc/, dev/design/, README files or dev/task.md; the planner updates the designs and the guide after review."
    - "No new dependencies and no new modules. Standard library, PyYAML and Rich only. Scripts stay compatible with bash 3.2 and the BSD tools of macOS (no mapfile, associative arrays, sed -i, grep -P, readlink -f)."
    - "Do not use 'except Exception' in the YAML readers; catch the named exception types."
    - "Keep every existing message unchanged except where an FR states new text."
    - "Do not fix anything outside FR-01 to FR-08, even if you notice it. Record such observations in report §6.0 in one line each (governance P02.10.1)."
    - "Git (CLAUDE.md §4.0): work on your session branch. Record the starting commit before any edit. Commit to the session branch and push it; do not merge into main, open a pull request, force-push or rewrite history."
    - "Stop condition: if an FR conflicts with existing code or tests, or needs a file outside the scope, implement the unaffected FRs, record the conflict in report §5.0 and §6.0, and stop."
    - "Stop condition: if the baseline suite has failures, do not fix them; record them and judge the final run against the baseline."
    - "Stop condition: if either checker reports an error on dev/ after the change, do not edit dev/; record the findings in report §4.0 and §6.0 and stop."

specification:
  description: "Eight changes, FR-01 to FR-08, with the tests listed under testing.unit_tests."
  requirements:
    functional:
      - "FR-01 (A; audit-d4f527e7 F-01) In orchestrator._write_atomic, overwatch._write_text_atomic and approve._write_atomic, create the temporary file with tempfile.mkstemp(dir=<directory of the target>, prefix='.' + <target basename> + '.', suffix='.tmp') and write through os.fdopen(fd, ...) with the mode ('w' or 'wb') and encoding each helper uses today. Before os.replace set the temporary file's permission bits: those of an existing regular file at the target (os.lstat; any other file type, including a symlink, counts as absent), else 0o666 & ~umask, the umask read with 'u = os.umask(0); os.umask(u)'. On BaseException remove the temporary file and re-raise, as today. Keep the existing target resolution: orchestrator replaces the name itself; overwatch and approve resolve the path first. In orchestrator, adjust _keep_mode or replace it so that the mode rule above holds. Comment at each site: change-f68d51c2 (audit-d4f527e7 F-01)."
      - "FR-02 (B; audit-bae631c7 F-02) In the retry branch of _completion_with_retry, interpolate escape(err_text) instead of err_text into the Rich console line (rich.markup.escape is already imported in orchestrator.py; import it if not). The log record and the BLOCKED.md text are unchanged. Comment: change-f68d51c2 (audit-bae631c7 F-02)."
      - "FR-03 (C; audit-bae631c7 F-03) Add a check of the configuration blocks in orchestrator.py, called in main_async at the call site of _validate_context_windows (before it), in every mode that calls _validate_context_windows. For each key in ('context', 'execution'): a value of None is replaced by {} in config; any other value that is not a dict raises ConfigError(f'{key}: must be a mapping'). It is reported through the existing ConfigError path as 'configuration error (<file>): <key>: must be a mapping', exit 1, before any state is written. Confirm that no read of config['context'] or config['execution'] in main_async precedes the check; if one does, move the check before it and record this in the report. Comment: change-f68d51c2 (audit-bae631c7 F-03)."
      - "FR-04 (D; audit-541f5c58 F-01) In bin/bootstrap.sh, directly after TMPWORK=\"$(mktemp -d)\", add trap 'rm -rf \"${TMPWORK}\"' EXIT. Run the extraction as 'if ! tar -xz -C \"${PROJECT_ROOT}\" -f \"${TARBALL}\"; then rm -rf \"${PROJECT_AI}\"; echo \"Error: extraction failed; ai/ removed\" >&2; exit 1; fi'. PROJECT_AI did not exist before the run (:32-36), so its removal cannot lose user data. The existing explicit removals of TMPWORK may stay. Comment: change-f68d51c2 (audit-541f5c58 F-01)."
      - "FR-05 (E; audit-9377f9b9-followup F-01, F-02) Each YAML reader also catches ValueError, TypeError, OverflowError and, where not caught today, RecursionError: linter._parse_yaml_block returns (None, <first line of str(e)>) for the first three and keeps 'nesting too deep' for RecursionError; manifest.load_manifest raises ManifestError(f'{path}: invalid YAML: <first line of str(e)>'), and keeps its existing RecursionError text; stages._status and scope.extract_deliverable_paths return exactly what they return today for a yaml.YAMLError; stages.parse_approvals returns {} (fail closed: no approvals); orchestrator.load_yaml raises ConfigError(f'{path}: invalid YAML: <first line of str(e)>') for these types and for yaml.YAMLError, and 'nesting too deep' for RecursionError; orchestrator._load_config raises ConfigError(f'invalid YAML: <first line of str(e)>') for the first three. A module-level tuple of the exception types per module is allowed; no shared module. Check every caller of load_yaml: each must report a ConfigError as a configuration error naming the file without a traceback; if a caller does not, record it as a deviation. Comment at each site: change-f68d51c2 (audit-9377f9b9-followup F-01 or F-02)."
      - "FR-06 (F1; audit-bae631c7 F-01) At both continuation-prompt sites write '\\\\[y/N]' (an escaped Rich tag) so that '[y/N]' is shown. Comment: change-f68d51c2 (audit-bae631c7 F-01)."
      - "FR-07 (F2; audit-541f5c58 F-02) In workspace_folders_of of bin/bootstrap.sh and bin/propagate.sh (identical functions): the block branch does not end on a line whose first character is '-' (a block item at column 0), so the end rule becomes 'a line that starts with a character other than whitespace, # or -'; and every extracted name, in the block and the flow branch, has a trailing carriage return removed. Keep the two functions identical. Comment in each: change-f68d51c2 (audit-541f5c58 F-02)."
      - "FR-08 (tests) Add the cases under testing.unit_tests to the test modules named in constraints, beside the existing tests of the change each FR corrects. Docstrings name change-f68d51c2."
    technical:
      language: "Python; bash"
      version: "Python 3.11+; bash 3.2+"
      standards:
        - "PEP 8; type hints on changed signatures; docstrings in the existing module style"
        - "Comments referencing change-f68d51c2 and the finding ID at each change site"

design:
  architecture: "No new modules. Local edits at the sites listed in context.integration."
  components:
    - name: "atomic write helpers (orchestrator, overwatch, approve)"
      type: "function"
      purpose: "Write a file so that a reader sees the old or the new content, never a partial file, and never follow an entry planted at the temporary name"
      interface:
        inputs: [{ name: "path, content", type: "str or Path, str or bytes", description: "unchanged signatures" }]
        outputs: { type: "None", description: "unchanged" }
        raises: ["OSError and BaseException re-raised after removing the temporary file"]
      logic: ["mkstemp in the target directory", "write through the descriptor", "mode: existing regular file's bits, else 0o666 & ~umask", "os.replace", "cleanup on failure"]
    - name: "configuration block check (orchestrator)"
      type: "function"
      purpose: "Normalise null context/execution blocks and refuse other non-mappings before any state is written"
      interface:
        inputs: [{ name: "config", type: "dict", description: "loaded ai/config.yaml" }]
        outputs: { type: "None", description: "config updated in place" }
        raises: ["ConfigError('<key>: must be a mapping')"]
      logic: ["None -> {}", "non-dict -> ConfigError"]
  dependencies:
    internal: ["orchestrator", "approve", "overwatch", "linter", "manifest", "stages", "scope"]
    external: ["os", "stat", "tempfile", "yaml", "rich"]

testing:
  unit_tests:
    - { scenario: "T1 (FR-01): for each of the three helpers, a symlink created at the former name '.<basename>.<os.getpid()>.tmp' beside the target, pointing to a victim file with known content; then a write", expected: "victim content and mode unchanged; the target is a regular file (not a symlink) with the new content" }
    - { scenario: "T2 (FR-01): for each of the three helpers, a directory created at the same former name; then a write", expected: "the write succeeds; the target has the new content" }
    - { scenario: "T3 (FR-01): orchestrator write_state to a new file, and to a name that holds a symlink; overwatch and approve to a new file", expected: "mode == 0o666 & ~umask for each" }
    - { scenario: "T4 (FR-02): _completion_with_retry with a provider stand-in that raises an error whose text contains '[/v1/chat/completions]' on the first call and succeeds on the second", expected: "no exception; two calls made; the captured console output contains '[/v1/chat/completions]'" }
    - { scenario: "T5 (FR-03): ai/config.yaml with context: null, and with execution: null, in loop mode", expected: "no AttributeError; the run passes the configuration check (assert on the next observable step, as the existing T4/T5 tests of change-bae631c7 do)" }
    - { scenario: "T6 (FR-03): context: and execution: each set to a list and to a string, in loop mode (parametrised)", expected: "exit 1; output 'configuration error (<file>): <key>: must be a mapping'; no state directory created" }
    - { scenario: "T7 (FR-04): bootstrap.sh with the existing curl stand-in made to exit 22, TMPDIR pointed at an empty directory", expected: "non-zero exit; TMPDIR empty afterwards; no ai/ in the project" }
    - { scenario: "T8 (FR-04): bootstrap.sh with a tarball that holds ai/engine/ and a member '../escaped.txt' (built with Python tarfile), TMPDIR pointed at an empty directory", expected: "exit 1; stderr names the extraction failure; no ai/ in the project; TMPDIR empty afterwards" }
    - { scenario: "T9 (FR-05): an unquoted invalid date 'created: 2026-11-31' in the first YAML block, at each reader: linter.run on a workspace; manifest.load_manifest; stages._status; stages.parse_approvals; scope.extract_deliverable_paths; orchestrator.load_yaml; orchestrator._load_config", expected: "linter: the existing 'YAML block does not parse: ...' finding; manifest: ManifestError naming the path and 'invalid YAML'; _status and extract_deliverable_paths: the same value as for 'key: [' (a YAMLError); parse_approvals: {}; load_yaml and _load_config: ConfigError with 'invalid YAML'; no other exception" }
    - { scenario: "T10 (FR-05): a 5,000-level nested block at stages._status, stages.parse_approvals, scope.extract_deliverable_paths and orchestrator.load_yaml", expected: "the per-site results of T9, with 'nesting too deep' for load_yaml" }
    - { scenario: "T11 (FR-06): the continuation prompt in the non-interactive and the interactive path (stdin stand-in answering 'n')", expected: "captured console text contains '[y/N]'" }
    - { scenario: "T12 (FR-07): for bootstrap.sh and propagate.sh (the existing helper that extracts workspace_folders_of), a manifest with 'workspace_folders:' followed by '- a' and '- b' at column 0 and then another top-level key; and an indented block list with CRLF line ends", expected: "names a and b exactly, in both cases; no name ends in '\\r'" }
  edge_cases:
    - "Use tmp_path; no network."
    - "Create symlinks and directories with os.symlink and os.mkdir in the test; skip a symlink test only where os.symlink is unavailable."
    - "Build deeply nested YAML in the test ('[' * 5000 + ']' * 5000), not in a stored file."
    - "Keep the curl stand-in and tarball helpers of tests/engine/test_bin_scripts.py; extend them rather than adding new ones."
  validation:
    - "Baseline before any edit: python3 -m pytest tests/engine tests/webui -q; python3 ai/engine/src/linter.py dev; python3 ai/engine/src/protocol_checker.py dev; bash -n bin/bootstrap.sh bin/propagate.sh; record counts."
    - "After the change: the same commands; no new failures; all new tests pass; both checkers 0 errors on dev/; bash -n passes."
    - "Mutation check (not committed), each on a temporary copy, full offline suite: (M1) orchestrator helper back to the predictable name opened with open(..., 'w'): T1 fails; (M2) the same in overwatch: T1 fails; (M3) the same in approve: T1 fails; (M4) no mode set for a new file (mkstemp 0600 kept): T3 fails; (M5) escape removed in the retry line: T4 fails; (M6) None not replaced by {}: T5 fails; (M7) non-dict accepted: T6 fails; (M8) EXIT trap removed: T7 fails; (M9) ai/ not removed on extraction failure: T8 fails; (M10) ValueError not caught in linter._parse_yaml_block: T9 fails; (M11) parse_approvals returns None or raises for ValueError: T9 fails; (M12) the column-0 end rule restored in propagate.sh: T12 fails; (M13) '[y/N]' unescaped at the non-interactive site: T11 fails. Record each result and the first failing test."

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute the full pytest suite on completion; report pass/fail summary"
    - "Setup if needed: pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest (pip may need --break-system-packages)"
    - "Close this prompt with git mv dev/prompt/prompt-f68d51c2-stabilisation.md dev/prompt/closed/; leave the issue and change documents active"
    - "Commits: Conventional Commits; engine and webui source as fix(engine) or fix(webui), scripts as fix(bin), tests as test, report and prompt move as docs(dev)"
  files:
    - { path: "ai/engine/src/orchestrator.py", content: "modified (FR-01, FR-02, FR-03, FR-05, FR-06)" }
    - { path: "ai/engine/src/approve.py", content: "modified (FR-01)" }
    - { path: "ai/webui/src/overwatch.py", content: "modified (FR-01)" }
    - { path: "ai/engine/src/linter.py", content: "modified (FR-05)" }
    - { path: "ai/engine/src/manifest.py", content: "modified (FR-05)" }
    - { path: "ai/engine/src/stages.py", content: "modified (FR-05)" }
    - { path: "ai/engine/src/scope.py", content: "modified (FR-05)" }
    - { path: "bin/bootstrap.sh", content: "modified (FR-04, FR-07)" }
    - { path: "bin/propagate.sh", content: "modified (FR-07)" }
    - { path: "tests/engine/test_tracking_state_hygiene.py", content: "modified (FR-08)" }
    - { path: "tests/engine/test_runtime_hygiene.py", content: "modified (FR-08)" }
    - { path: "tests/engine/test_stages.py", content: "modified (FR-08)" }
    - { path: "tests/engine/test_linter.py", content: "modified (FR-08)" }
    - { path: "tests/engine/test_manifest_gates.py", content: "modified (FR-08)" }
    - { path: "tests/engine/test_write_scope.py", content: "modified (FR-08)" }
    - { path: "tests/engine/test_bin_scripts.py", content: "modified (FR-08)" }
    - { path: "tests/webui/test_overwatch.py", content: "modified (FR-08)" }
    - path: "dev/reports/report-f68d51c2-stabilisation.md"
      content: >
        New file in Obsidian-compatible GitHub Flavored Markdown, laid out as
        README.md: unnumbered H1 title followed by the line 'Created: <year>
        <month> <day>'; unnumbered '## Table of Contents' as a bulleted list
        of the H2 sections linked by GitHub heading slugs (for example
        [1.0 Summary](#10-summary)); numbered sections; '---' between
        sections; '[Return to Table of Contents](#table-of-contents)' at the
        end of each section except Version History; Version History table;
        final '---' and the line 'Copyright (c) 2026 William Watson. MIT
        License.'. Sections: 1.0 Summary; 2.0 Files changed (with
        functions); 3.0 Test results (baseline and final counts, new test
        names, mutation results M1 to M13); 4.0 Governance checks (both
        checkers on dev/ before and after; bash -n); 5.0 Deviations from
        this prompt (or 'None'); 6.0 Observations (pre-existing defects
        noticed in passing, one line each, not fixed) and open points for
        the planner; 7.0 Session branch, starting commit and commit hashes.

success_criteria:
  - "FR-01 to FR-08 implemented as specified; all new tests present and passing"
  - "Mutations M1 to M13 fail their named tests"
  - "Full suite: no failures beyond the recorded baseline"
  - "Both checkers report 0 errors on dev/; bash -n passes for both scripts"
  - "git diff <starting commit>..HEAD touches only the files in deliverable.files and the prompt move, plus recorded assertion updates"
  - "Commits pushed to the session branch, not merged; report §7.0 lists the branch, starting commit and commit hashes"

notes: "The planner reviews the session branch before the operator merges it into main, then updates design-14e05e35 §11.0, design-ael-orchestrator §4.1 and guide-engine-operations §3.0. A verification audit by an independent session follows (governance P02.10.1); it checks the acceptance criteria, regressions and defects introduced on the changed lines only. This change is the last before release v0.3.0 (dev/README.md §7.0)."
```

Copyright (c) 2026 William Watson. MIT License.
