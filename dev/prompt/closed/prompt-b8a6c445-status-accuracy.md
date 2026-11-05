Created: 2026 November 5

```yaml
prompt_info:
  id: "prompt-b8a6c445"
  task_type: "debug"
  source_ref: "change-b8a6c445"
  target_profile: "claude_code"  # Claude Code cloud session
  date: "2026-11-05"
  iteration: 1
  coupled_docs:
    change_ref: "change-b8a6c445"
    change_iteration: 1

context:
  purpose: >
    Make Overwatch's engine status and prompt match correct by having the
    engine write a run record, run.json, at the start and end of every run,
    and fix three small Overwatch defects. Remediates audit-caab2052 M-04,
    M-05, L-07, L-08, L-15 and the OQ-02 citation (operator decisions of
    2026-11-05, audit-caab2052 §14.0).
  integration: >
    main_async (orchestrator.py) validates configuration, calls
    setup_logging, then runs everything inside one try whose finally logs
    'engine end rc=N' and closes the MCP client (change-711a57d5 FR-G).
    write_state writes state files; reset_state removes the files listed in
    _RESET_FILES. scope.SIGNAL_FILES lists the state files a worker may not
    write. Overwatch (ai/webui/src/overwatch.py) builds a Snapshot in
    Scanner.scan: documents per CLASS_DIRS entry, then
    _read_engine_state; PhaseInference.infer and ComplianceEngine.evaluate
    use it; AlertWriter writes ai/dashboard-alerts.md; HtmlRenderer writes
    overwatch.html. Line numbers below are at 695ad06; locate code by the
    quoted text if lines have moved.
  knowledge_references:
    - "dev/change/change-b8a6c445-status-accuracy.md (approved scope)"
    - "dev/issue/issue-b8a6c445-status-accuracy.md"
    - "dev/audit/audit-caab2052-static-code-2026-10-27.md §5.1 (M-04, M-05, L-07, L-08), §5.4 (L-15), §11.0 (OQ-02), §14.0"
    - "dev/requirements/requirements-0c6aedee-project-overwatch.md (CON-01, NFR-01 v0.6, NFR-05)"
    - "dev/design/design-14e05e35-engine-generalisation.md §7.0"
    - "CLAUDE.md; ai/governance/software-engineering/governance.md"
  constraints:
    - "Execution environment: Claude Code cloud (Linux container, repository clone). No oMLX, no model, no API key, no MCP server binaries. Do not start the engine against a real endpoint, do not start engine-mcp, and do not call any network endpoint other than package installation."
    - "Code changes are limited to ai/engine/src/orchestrator.py, ai/engine/src/scope.py, ai/webui/src/overwatch.py, the new tests/engine/test_run_record.py and tests/webui/test_overwatch.py. Other existing test files may change only where an assertion depends on behaviour changed by an FR below; record each such change in the report."
    - "Governance changes are limited to: creating the report named in deliverable.files, and moving this prompt to dev/prompt/closed/."
    - "Do not edit the issue, change, audit, requirements or design documents, ai/config.yaml, ai/engine/config.template.yaml, ai/engine/doc/, ai/engine/mcp/, ai/profiles/, README files or dev/task.md; the planner updates those after review."
    - "No new dependencies. Standard library only for new code; Overwatch keeps its pyyaml-only footprint (requirements-0c6aedee NFR-07)."
    - "Keep every existing message, log line, state file and BLOCKED.md text unchanged except where an FR states new text."
    - "FR-08-05 must hold: a run refused before setup_logging writes no state directory and no file. Do not move setup_logging, archive_prior_logs or the binding-record replay."
    - "Overwatch stays read-only for project content (requirements-0c6aedee CON-01, NFR-01 v0.6): it writes only overwatch.html and ai/dashboard-alerts.md. Testing whether a pid is alive with os.kill(pid, 0) sends no signal and is permitted."
    - "Git (CLAUDE.md §4.0): work on your session branch. Record the starting commit before any edit. Commit to the session branch and push it; do not merge into main, open a pull request, force-push or rewrite history."
    - "Stop condition: if any FR conflicts with existing code or tests, or needs a file outside the scope, implement the unaffected FRs, record the conflict in report §5.0 and §6.0, and stop."
    - "Stop condition: if the baseline suite has failures, do not fix them; record them and judge the final run against the baseline."

specification:
  description: "Six changes, FR-A to FR-F, with tests R1 to R6 in tests/engine/test_run_record.py and O1 to O6 in tests/webui/test_overwatch.py."
  requirements:
    functional:
      - "FR-A (M-04, M-05; engine run record) In orchestrator.py: (1) module constant _RUN_RECORD = 'run.json'. (2) Helper _write_run_record(state_dir: str, record: dict) -> None that writes json.dumps(record, indent=2) + '\\n' to a temporary file created in state_dir (tempfile.NamedTemporaryFile or mkstemp, delete=False) and moves it into place with os.replace; on any exception the temporary file is removed and the exception re-raised. (3) In main_async, the first statement inside the try that follows setup_logging (the try introduced by change-711a57d5 FR-G, after 'rc = 1' and 'mcp = None') builds _run_record = {'mode': args.mode, 'task_file': os.path.abspath(args.task) if _task_bytes is not None else None, 'pid': os.getpid(), 'started': <now>, 'ended': None, 'rc': None}, where <now> is datetime.datetime.now().astimezone().isoformat(timespec='seconds'), and writes it with _write_run_record. Set a local flag _run_record_written = True only after a successful write. Initialise _run_record = None and _run_record_written = False before the try. (4) In the finally, before the existing log.info('engine end rc=%d', rc): if _run_record_written, set _run_record['ended'] to <now> and _run_record['rc'] = rc and write it again. (5) Every exception from either write is caught (except Exception), logged with log.warning('run record not written: %s', e) and otherwise ignored; neither write changes rc or the control flow. (6) Add 'run.json' to _RESET_FILES. Comment at each site: change-b8a6c445 (audit-caab2052 M-04, M-05)."
      - "FR-B (worker protection) In scope.py, add 'run.json' to SIGNAL_FILES. The existing parametrised test_worker_cannot_write_signal_files then covers it; do not change that test."
      - "FR-C (M-04; Overwatch status) In overwatch.py: (1) EngineState gains task_file: Optional[str] = None and rc: Optional[int] = None; update the status docstring to 'idle | running | ship | blocked | ended | unknown'. (2) _read_engine_state reads <state_dir>/run.json with json.loads. A record is valid when it is a dict whose 'pid' is an int (not bool) and whose 'ended' is None or a str; otherwise, or when the file cannot be read or parsed, treat it as invalid. A valid record is live when 'ended' is None and the pid is alive: os.kill(pid, 0) succeeds; ProcessLookupError means not alive; PermissionError means alive (the process exists); any other OSError means not alive. (3) Status precedence, first match wins: valid and live record -> 'running'; BLOCKED.md present -> 'blocked'; .complete present -> 'ship'; valid record (ended, or not live) -> 'ended'; invalid record present, or task.md present without run.json -> 'unknown'; otherwise 'idle'. (4) For a valid record set task_file to its 'task_file' when that is a str, else None, and rc to its 'rc' when that is an int (not bool), else None. (5) task_ref becomes os.path.basename(task_file) when task_file is set, 'text task' for a valid record without task_file, and None otherwise; task.md is no longer read for task_ref. iteration and blocked_detail keep their current sources. (6) PhaseInference.infer rule 2 also applies when status is 'ended': eng.status in ('idle', 'ship', 'ended'); update its docstring. (7) In the stylesheet, add .status-ended to the existing .status-warn rule. (8) AlertWriter.payload: when status is 'ended' and rc is not None, engine_str becomes 'ENDED rc=<rc>' before the iteration suffix. Comment: change-b8a6c445 (audit-caab2052 M-04)."
      - "FR-D (M-05; FR-02-06) In ComplianceEngine.evaluate, replace the FR-02-06 block (overwatch.py:702-717, 'if eng.task_ref:') with: evaluate only when the state directory held a valid run record (add has_run_record: bool = False to EngineState, set True for a valid record in FR-C) and at least one open non-master prompt exists; matched is True when task_file is set and os.path.realpath(task_file) equals os.path.realpath(doc.path) for some open prompt; when not matched append Alert(severity='warning', code='FR-02-06', message='engine run task is not an open prompt document', document=None). Comment: change-b8a6c445 (audit-caab2052 M-05)."
      - "FR-E (L-07, L-08; scan) In Scanner.scan: (1) a file found under a class directory is skipped when it lies inside another CLASS_DIRS directory nested within that class directory (for example a file under test/result/ is scanned for result, not for test); derive the nested set from CLASS_DIRS, do not hard-code test/result. (2) Replace the closed/ test 'if \"closed\" in filepath.parts' with a test on filepath.relative_to(self.paths.workspace).parts. Comments: change-b8a6c445 (audit-caab2052 L-07, L-08)."
      - "FR-F (L-15, OQ-02; text) In AlertWriter: the heading line becomes f'# Overwatch alerts — {project_name}'; the class docstring citation '(CON-07 / NFR-01, design §3.1 clarification)' becomes '(CON-01 / NFR-01, design §3.1 clarification)'. No other docstring or historical govwatch reference changes."
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "PEP 8; type hints on new or changed signatures; docstrings in the existing module style"
        - "Comments referencing change-b8a6c445 and the finding ID at each change site"

design:
  architecture: "One new engine state file; no new modules in ai/; Overwatch reads one more file."
  components:
    - name: "_write_run_record"
      type: "function"
      purpose: "Atomic write of the run record"
      interface:
        inputs:
          - { name: "state_dir", type: "str", description: "engine state directory" }
          - { name: "record", type: "dict", description: "mode, task_file, pid, started, ended, rc" }
        outputs: { type: "None", description: "run.json replaced in one step" }
        raises: ["OSError and serialisation errors; callers catch them (FR-A 5)"]
      logic: ["temporary file in state_dir; json.dump; os.replace; remove the temporary file on failure"]
    - name: "Scanner._read_engine_state"
      type: "method"
      purpose: "Engine status from run.json, BLOCKED.md and .complete"
      interface:
        inputs: []
        outputs: { type: "EngineState", description: "status, iteration, blocked_detail, task_ref, task_file, rc, has_run_record" }
        raises: []
      logic: ["FR-C precedence table"]
  dependencies:
    internal: ["scope.SIGNAL_FILES"]
    external: ["json", "os", "tempfile", "datetime"]

error_handling:
  strategy: "Run-record writes never affect a run; an unreadable record is shown as 'unknown', never as an exception."
  logging:
    level: "WARNING for a failed run-record write; no new Overwatch log output"

testing:
  unit_tests:
    - { scenario: "R1 (FR-A) main_async with a text task (args.task None) that returns at the no-task check after setup_logging; legacy config, readiness stubbed, fake MCPClient and isolated engine logger as in tests/engine/test_loop_robustness.py _run_without_task (import or copy those helpers)", expected: "rc 1; run.json is valid JSON with mode 'loop', task_file None, pid os.getpid(), started and ended non-empty ISO strings, rc 1" }
    - { scenario: "R2 (FR-A) main_async with --task pointing to an existing file under the project and Manifest.recipe_paths raising ManifestError (test_t15 pattern)", expected: "rc 1; run.json task_file equals os.path.abspath of the task path; rc 1" }
    - { scenario: "R3 (FR-A) as R1 with orchestrator._write_run_record replaced by a function raising OSError", expected: "rc 1 as in R1; a WARNING record containing 'run record not written'; last log line contains 'engine end rc=1'" }
    - { scenario: "R4 (FR-A) reset_state on a state directory containing run.json", expected: "run.json removed; return value 0" }
    - { scenario: "R5 (FR-A, FR-08-05) main_async with loop.mcp_timeout_seconds 0", expected: "returns 1; no state directory created, hence no run.json" }
    - { scenario: "R6 (FR-A) _write_run_record with os.replace wrapped by a recording spy; then with os.replace raising OSError", expected: "first: os.replace called once with a source in state_dir and target run.json; second: OSError propagates and no file other than pre-existing ones remains in state_dir" }
    - { scenario: "O1 (FR-C) _read_engine_state over fixture state directories: (a) none; (b) run.json ended null, pid os.getpid(); (c) run.json ended null, pid of a finished child process (start sys.executable -c pass, wait); (d) run.json ended set, rc 2; (e) (d) plus BLOCKED.md; (f) (d) plus .complete; (g) (b) plus BLOCKED.md; (h) task.md only; (i) run.json containing 'not json'", expected: "(a) idle; (b) running; (c) ended, rc None; (d) ended, rc 2; (e) blocked; (f) ship; (g) running; (h) unknown; (i) unknown" }
    - { scenario: "O2 (FR-D) workspace with one open prompt prompt-<uuid>-x.md; run.json task_file set to that prompt's path, to another path, and None", expected: "no FR-02-06 alert; FR-02-06 alert with the new message; FR-02-06 alert" }
    - { scenario: "O3 (FR-E) one result document under ai/workspace/test/result/", expected: "Scanner.scan lists it once, with cls 'result'" }
    - { scenario: "O4 (FR-E) project created under tmp_path / 'closed' / 'proj' with one open prompt; and one prompt under ai/workspace/prompt/closed/", expected: "the open prompt is listed; the closed one is not" }
    - { scenario: "O5 (FR-C, FR-F) AlertWriter.payload for a snapshot with status 'ended' and rc 2", expected: "first line '# Overwatch alerts — <project name>'; a line 'engine: ENDED rc=2'" }
    - { scenario: "O6 (FR-C) PhaseInference.infer with status 'ended' and an open prompt", expected: "'Awaiting prompt execution'" }
  edge_cases:
    - "Use tmp_path and monkeypatch only; no network, no real engine run."
    - "Restore the 'engine' logger after tests that call setup_logging, as test_loop_robustness.py does."
    - "The existing snapshot fixture in tests/webui/test_overwatch.py constructs EngineState(status='running', iteration=4, task_ref='task'); new fields have defaults, so it must keep working unchanged."
  validation:
    - "Baseline before any edit: python3 -m pytest tests/engine tests/webui -q; record counts (expected on Linux as root: 383 passed, 1 skipped)."
    - "After the change: same command; no new failures; R1 to R6 and O1 to O6 pass."
    - "Mutation check (not committed), each on a temporary copy: (M1) remove the end write in the finally: R1 fails; (M2) restore task.md presence as the 'running' test in _read_engine_state: O1 (h) fails; (M3) restore the first-line task_ref match in FR-02-06: O2 fails; (M4) remove the nested-directory skip: O3 fails; (M5) restore the absolute-path closed test: O4 fails; (M6) remove 'run.json' from SIGNAL_FILES: test_worker_cannot_write_signal_files no longer has a run.json case (record that the parametrised case disappears rather than fails). Record results."
    - "python3 ai/engine/src/linter.py dev and python3 ai/engine/src/protocol_checker.py dev; record results; fix new findings caused by this work only."

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
    - "Setup if needed: pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest (pip may need --break-system-packages)"
    - "Close this prompt with git mv dev/prompt/prompt-b8a6c445-status-accuracy.md dev/prompt/closed/; leave the issue and change documents active"
    - "Commits: Conventional Commits; source as fix(engine) and fix(webui), tests as test, report and prompt move as docs(dev)"
  files:
    - { path: "ai/engine/src/orchestrator.py", content: "modified (FR-A)" }
    - { path: "ai/engine/src/scope.py", content: "modified (FR-B)" }
    - { path: "ai/webui/src/overwatch.py", content: "modified (FR-C to FR-F)" }
    - { path: "tests/engine/test_run_record.py", content: "new (R1 to R6)" }
    - { path: "tests/webui/test_overwatch.py", content: "modified (O1 to O6 added)" }
    - path: "dev/reports/report-b8a6c445-status-accuracy.md"
      content: >
        New file in Obsidian-compatible GitHub Flavored Markdown, laid out as
        README.md: unnumbered H1 title followed by the line 'Created: <year>
        <month> <day>'; unnumbered '## Table of Contents' as a bulleted list
        of the H2 sections linked by GitHub heading slugs (for example
        [1.0 Summary](#10-summary)); numbered sections; '---' between
        sections; '[Return to Table of Contents](#table-of-contents)' at the
        end of each section except Version History; Version History table;
        final '---' and the line 'Copyright (c) 2026 William Watson. MIT
        License.'. Sections: 1.0 Summary; 2.0 Files changed (with functions);
        3.0 Test results (baseline and final counts, new test names, mutation
        results); 4.0 Governance checks; 5.0 Deviations from this prompt (or
        'None'); 6.0 Open points for the planner, including that no live run
        was possible; 7.0 Session branch, starting commit and commit hashes.

success_criteria:
  - "FR-A to FR-F implemented as specified; R1 to R6 and O1 to O6 present and passing"
  - "Mutations M1 to M5 fail their named tests; M6 recorded"
  - "Full suite: no failures beyond the recorded baseline"
  - "git diff <starting commit>..HEAD touches only the files in deliverable.files and the prompt move"
  - "No existing message changed except the FR-02-06 message, the alert heading and the AlertWriter docstring citation"
  - "Commits pushed to the session branch, not merged; report §7.0 lists the branch, starting commit and commit hashes"

notes: "The planner reviews the session branch before the operator merges it fast-forward into main. A follow-up audit by an independent session is required before closure (P02.8.2). The planner updates design-14e05e35, design-project-overwatch, requirements-0c6aedee FR-01-01 and FR-01-02, and the operations guide after review."
```

Copyright (c) 2026 William Watson. MIT License.
