Created: 2026 November 5

```yaml
prompt_info:
  id: "prompt-a5bd4fe1"
  task_type: "debug"
  source_ref: "change-a5bd4fe1"
  target_profile: "claude_code"  # Claude Code cloud session
  date: "2026-11-05"
  iteration: 1
  coupled_docs:
    change_ref: "change-a5bd4fe1"
    change_iteration: 1

context:
  purpose: >
    Harden the engine's write scope and gates: classify MCP tools fail
    closed, refuse unresolvable write paths, stop py_compile from writing
    bytecode beside checked files and from compiling paths outside the
    project, let a syntax FAIL override SHIP, and add a collection-only pass
    over tests/ to the pytest gate. Remediates audit-caab2052 L-01, L-02,
    L-12 and OQ-01, with the operator decisions of 2026-11-05.
  integration: >
    scope.py classifies tools (is_write_tool, is_readonly_tool) and checks
    each worker tool call before dispatch (check). The classification is
    also used by orchestrator.py (_dispatch_refusal, write tracking in
    run_phase, the post-write syntax check) and by mcp_client.py (the
    read-only tool filter for the review phase). gates.py holds the built-in
    syntax gate (syntax_check), the pytest target mapping (pytest_targets)
    and the command gate runner (run_command_gate). orchestrator.py wraps
    them in _run_syntax_gate and _run_pytest_gate, runs them in run_loop
    before the review phase, and applies the SHIP override after a reviewer
    SHIP. py_compile also runs in run_phase (edit-failure and post-write
    checks) and in run_preflight_check. The engine runs with the project
    root as its working directory. Line numbers below are at c5d582d; locate
    code by the quoted text if lines have moved.
  knowledge_references:
    - "dev/change/change-a5bd4fe1-scope-gate-hardening.md (approved scope)"
    - "dev/issue/issue-a5bd4fe1-scope-gate-hardening.md"
    - "dev/audit/audit-caab2052-static-code-2026-10-27.md §5 (L-01, L-02, L-12), §11.0 and §14.0 (OQ-01)"
    - "dev/requirements/requirements-14e05e35-engine-generalisation.md FR-03-02, FR-03-04 (v1.8), FR-05-01"
    - "dev/design/design-14e05e35-engine-generalisation.md §6.0, §7.0, §11.0"
    - "CLAUDE.md; ai/governance/software-engineering/governance.md"
  constraints:
    - "Execution environment: Claude Code cloud (Linux container, repository clone). No oMLX, no model, no API key, no MCP server binaries. Do not start the engine against a real endpoint, do not start engine-mcp, and do not call any network endpoint other than package installation."
    - "Code changes are limited to ai/engine/src/scope.py, ai/engine/src/gates.py, ai/engine/src/orchestrator.py and the new tests/engine/test_scope_gate_hardening.py. Other existing test files may change only where an assertion depends on behaviour changed by an FR below; record each such change in the report."
    - "Governance changes are limited to: creating the report named in deliverable.files, and moving this prompt to dev/prompt/closed/."
    - "Do not edit the issue, change, audit, requirements or design documents, ai/config.yaml, ai/engine/config.template.yaml, ai/engine/doc/, ai/engine/mcp/, ai/engine/src/mcp_client.py, ai/governance/, ai/profiles/, README files or dev/task.md; the planner updates those after review."
    - "No new dependencies. Standard library only."
    - "Keep every existing message, log line, state file and BLOCKED.md text unchanged except where an FR states new text."
    - "Keep every subprocess bounded as change-711a57d5 (audit-caab2052 L-03) made it: py_compile calls keep their timeouts and their current timeout handling at each call site."
    - "Git (CLAUDE.md §4.0): work on your session branch. Record the starting commit before any edit. Commit to the session branch and push it; do not merge into main, open a pull request, force-push or rewrite history."
    - "Stop condition: if any FR conflicts with existing code or tests, or needs a file outside the scope, implement the unaffected FRs, record the conflict in report §5.0 and §6.0, and stop."
    - "Stop condition: if the baseline suite has failures, do not fix them; record them and judge the final run against the baseline."

specification:
  description: "Five changes, FR-A to FR-E, with tests S1 to S4, C1 to C4, D1 to D2 and E1 to E4 in tests/engine/test_scope_gate_hardening.py."
  requirements:
    functional:
      - "FR-A (L-01; fail-closed classification) In scope.py: (1) READONLY_TOOL_PATTERNS gains r'^diff' and r'^count'. (2) is_readonly_tool(name) returns False when the name is in WRITE_TOOLS or contains a WRITE_NAME_PATTERNS verb, otherwise True when it matches a READONLY_TOOL_PATTERNS entry, otherwise False (unchanged logic, with the new patterns). (3) is_write_tool(name) returns not is_readonly_tool(name): every tool that is not recognised as read-only is a write tool. (4) Update the module docstring and both function docstrings: classification is fail-closed; a tool is read-only only when its name matches a read-only pattern and contains no write verb. check() keeps its early return 'if not is_write_tool(tool_name): return None'. Do not change mcp_client.py; it already delegates to is_readonly_tool. Comment: change-a5bd4fe1 (audit-caab2052 L-01)."
      - "FR-B (L-02; unresolvable path) In scope.check, replace 'continue  # malformed path: left to the MCP server' (scope.py:213) with: return Violation(target, 'unresolvable path', f\"write refused: path '{target}' cannot be resolved\"). Comment: change-a5bd4fe1 (audit-caab2052 L-02)."
      - "FR-C (L-12; bytecode and project paths) (1) In gates.py add compile_file(path: str, timeout: float = SYNTAX_TIMEOUT_SECONDS) -> subprocess.CompletedProcess: inside 'with tempfile.TemporaryDirectory(prefix=\"engine-pyc-\") as cache:' run subprocess.run([sys.executable, '-m', 'py_compile', path], capture_output=True, text=True, timeout=timeout, env={**os.environ, 'PYTHONPYCACHEPREFIX': cache}) and return the result; subprocess.TimeoutExpired and other exceptions propagate to the caller. (2) syntax_check(state_dir, log, project_root: str | None = None): root is os.path.realpath(project_root or os.getcwd()); a candidate .py path that exists but whose os.path.realpath(os.path.abspath(path)) is not root or below it is skipped with log.warning('syntax gate: %s is outside the project; not checked', path) and appears neither in the count nor in the block; every checked path uses compile_file. (3) orchestrator._run_syntax_gate gains a project_root parameter passed to syntax_check; run_loop passes its project_root. (4) The edit-failure check (orchestrator.py:1535) and the post-write check (:1610) call G.compile_file(path, timeout=_SUBPROCESS_TIMEOUT_SECONDS) in place of subprocess.run, keeping their except branches. (5) run_preflight_check's 'no syntax' criterion (:1740) uses G.compile_file with the same timeout; a path that does not resolve inside os.getcwd() gives the line '  [{i}] UNCHECKED  {criterion} (outside the project)' and counts as unchecked. Comments: change-a5bd4fe1 (audit-caab2052 L-12)."
      - "FR-D (OQ-01; syntax FAIL blocks SHIP) In run_loop's SHIP override for the non-audit path (orchestrator.py:2335-2386), after the read-evidence check and before the command gate loop: when _read_gate_pass is still True, 'syntax' is in gate_list and G.gate_status(_syntax_result) == 'FAIL', set _read_gate_pass = False, log.warning('syntax SHIP gate: FAIL — overriding SHIP'), print '[yellow][engine] syntax SHIP gate: FAIL — overriding SHIP to REVISE[/yellow]' and write review-feedback.txt with 'Syntax gate failed.\\n\\n' + _syntax_result. The audit path is unchanged. Comment: change-a5bd4fe1 (audit-caab2052 OQ-01; FR-03-04 v1.8)."
      - "FR-E (collection-only pass) When _run_pytest_gate runs the pytest command (at least one target) and os.path.join(project_root, 'tests') is a directory, the gate also runs argv [python, '-m', 'pytest', '--collect-only', '-q', os.path.join(project_root, 'tests')], where python is spec['python'] or sys.executable, with the gate's cwd (project_root), timeout (spec timeout_seconds or DEFAULT_TIMEOUT_SECONDS) and scrub_env handling as run_command_gate. A custom spec['command'] does not apply to this step. Step status: exit 0 or 5 PASS, any other exit FAIL, an exception (including a timeout) UNCHECKED. The gate status is the worst of the target run and the collection step in the order UNCHECKED, FAIL, PASS. The [TEST GATE] block keeps its format and its first line carries the combined status; before '[END TEST GATE]' it adds 'The orchestrator ran a collection-only pass: <argv joined with shlex.quote>' and 'Collection output:\\n<output>', with the output truncated as the main output is. Log the step with log.info('pytest gate: collection-only pass, status=%s', status). Put the step's logic in gates.py; _run_pytest_gate keeps its signature. Comment: change-a5bd4fe1 (operator decision 2026-11-05)."
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "PEP 8; type hints on new or changed signatures; docstrings in the existing module style"
        - "Comments referencing change-a5bd4fe1 and the finding ID at each change site"

design:
  architecture: "No new modules in ai/; one new function in gates.py for compiles and one for the collection step."
  components:
    - name: "gates.compile_file"
      type: "function"
      purpose: "Bounded py_compile with a temporary bytecode cache"
      interface:
        inputs:
          - { name: "path", type: "str", description: ".py file to compile" }
          - { name: "timeout", type: "float", description: "seconds, default SYNTAX_TIMEOUT_SECONDS" }
        outputs: { type: "subprocess.CompletedProcess", description: "result of python -m py_compile" }
        raises: ["subprocess.TimeoutExpired and other subprocess errors; callers keep their handling"]
      logic: ["TemporaryDirectory; PYTHONPYCACHEPREFIX in a copy of os.environ; subprocess.run"]
    - name: "scope.is_write_tool / is_readonly_tool"
      type: "function"
      purpose: "Fail-closed tool classification"
      interface:
        inputs: [{ name: "name", type: "str", description: "MCP tool name" }]
        outputs: { type: "bool", description: "class of the tool" }
        raises: []
      logic: ["read-only only when a read-only pattern matches and no write verb occurs; write otherwise"]
  dependencies:
    internal: ["scope", "gates"]
    external: ["tempfile", "os", "subprocess", "shlex", "sys"]

error_handling:
  strategy: "Refusals are tool errors to the worker as today; gate steps that cannot run are UNCHECKED, which ends the run BLOCKED as today (change-82dbf16a M-02)."
  logging:
    level: "WARNING for a skipped out-of-project syntax path and for the syntax SHIP override; INFO for the collection step"

testing:
  unit_tests:
    - { scenario: "S1 (FR-A) parametrised table of every tool of filesystem-mcp 2.5.0 (create, delete, diff, edit, find_files, list, list_roots, move, patch, read, replace_text, search_text, stat), mcp-ripgrep (search, count-matches, list-files, list-file-types) and mcp-grep (grep)", expected: "write: create, delete, edit, move, patch, replace_text; read-only: all others, including diff and count-matches; is_write_tool is the negation of is_readonly_tool for every name" }
    - { scenario: "S2 (FR-A) scope.check for copy_file, append_file, touch and frobnicate with {'path': <outside the project root>}, and with {} (no path)", expected: "is_write_tool True for each; Violation 'outside the project root'; Violation 'no recognised path argument'" }
    - { scenario: "S3 (FR-A) MCPClient({})._is_readonly_tool('frobnicate') and orchestrator._dispatch_refusal('frobnicate', {'frobnicate'}, is_worker_phase=False)", expected: "False; the review-phase refusal text \"tool 'frobnicate' writes; the review phase is read-only\"" }
    - { scenario: "S4 (FR-B) scope.check('write_file', {'path': 'src/a\\x00b.py'}, <project root>)", expected: "Violation with reason 'unresolvable path'" }
    - { scenario: "C1 (FR-C) syntax_check on <project>/src/ok.py named in work-summary.txt (real compile, no monkeypatch of subprocess.run except a spy that records the env and calls the real function)", expected: "[SYNTAX GATE: PASS]; no __pycache__ directory under <project>/src; the recorded PYTHONPYCACHEPREFIX directory no longer exists" }
    - { scenario: "C2 (FR-C) work-summary.txt naming an existing .py file outside the project root (tmp_path sibling) and one inside", expected: "count 1; the outside path is not in the block; warning 'is outside the project; not checked' logged" }
    - { scenario: "C3 (FR-C) run_phase post-write check: a fake write_file call that leaves <project>/src/bad.py with a syntax error (the fake MCP writes the file)", expected: "the existing 'Syntax error detected in' corrective text appears; no __pycache__ under <project>/src" }
    - { scenario: "C4 (FR-C) compile_file with subprocess.run raising TimeoutExpired, through syntax_check", expected: "block contains 'syntax check timed out after 30 s'; status FAIL (as test_t14)" }
    - { scenario: "D1 (FR-D) run_loop with run_phase and the gates replaced by fakes as in the existing run_loop tests: syntax block '[SYNTAX GATE: FAIL]...', no command gate failures, reviewer verdict SHIP, max_iterations 1", expected: "no .complete; review-feedback.txt starts with 'Syntax gate failed.' and contains the syntax block; return value as for a REVISE that reaches max iterations" }
    - { scenario: "D2 (FR-D) as D1 with '[SYNTAX GATE: PASS]...' and with an empty syntax block", expected: ".complete written; return 0" }
    - { scenario: "E1 (FR-E) project with tests/test_ok.py (passes) as target and tests/test_broken.py raising ImportError at import; _run_pytest_gate with the target test_ok.py", expected: "[TEST GATE: FAIL]; block contains 'collection-only pass' and the collection output naming test_broken.py" }
    - { scenario: "E2 (FR-E) collection step on a tests/ directory with no collectable test (only a helper module), target run passing", expected: "collection step exit 5 treated as PASS; [TEST GATE: PASS]" }
    - { scenario: "E3 (FR-E) collection step with subprocess.run raising TimeoutExpired for the --collect-only argv only", expected: "[TEST GATE: UNCHECKED]" }
    - { scenario: "E4 (FR-E) no tests/ directory (target under another directory) and a call with no target", expected: "no collection step run (spy on subprocess.run sees no --collect-only argv); block unchanged from c5d582d behaviour" }
  edge_cases:
    - "Use tmp_path and monkeypatch only; no network, no real engine run."
    - "Restore the 'engine' logger after tests that call setup_logging, as test_loop_robustness.py does."
    - "Existing tests that assert classification (test_write_scope.py, test_orchestrator_edge_cases.py) and py_compile argv and timeouts (test_loop_robustness.py T13, T14) must keep passing unchanged."
  validation:
    - "Baseline before any edit: python3 -m pytest tests/engine tests/webui -q; record counts (expected on Linux as root: 408 passed, 1 skipped)."
    - "After the change: same command; no new failures; all new tests pass."
    - "Mutation check (not committed), each on a temporary copy: (M1) is_write_tool back to the verb-only rule: S2 fails; (M2) restore the 'continue' in check: S4 fails; (M3) drop PYTHONPYCACHEPREFIX from compile_file: C1 fails; (M4) remove the project-root filter in syntax_check: C2 fails; (M5) remove the FR-D override: D1 fails; (M6) remove the collection step: E1 fails; (M7) treat exit 5 as FAIL: E2 fails. Record results."
    - "python3 ai/engine/src/linter.py dev and python3 ai/engine/src/protocol_checker.py dev; record results; fix new findings caused by this work only."

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
    - "Setup if needed: pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest (pip may need --break-system-packages)"
    - "Close this prompt with git mv dev/prompt/prompt-a5bd4fe1-scope-gate-hardening.md dev/prompt/closed/; leave the issue and change documents active"
    - "Commits: Conventional Commits; source as fix(engine), tests as test, report and prompt move as docs(dev)"
  files:
    - { path: "ai/engine/src/scope.py", content: "modified (FR-A, FR-B)" }
    - { path: "ai/engine/src/gates.py", content: "modified (FR-C, FR-E)" }
    - { path: "ai/engine/src/orchestrator.py", content: "modified (FR-C, FR-D, FR-E)" }
    - { path: "tests/engine/test_scope_gate_hardening.py", content: "new (S1 to S4, C1 to C4, D1 to D2, E1 to E4)" }
    - path: "dev/reports/report-a5bd4fe1-scope-gate-hardening.md"
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
  - "FR-A to FR-E implemented as specified; all new tests present and passing"
  - "Mutations M1 to M7 fail their named tests"
  - "Full suite: no failures beyond the recorded baseline"
  - "git diff <starting commit>..HEAD touches only the files in deliverable.files and the prompt move"
  - "No existing message changed except the new texts stated in FR-B, FR-C, FR-D and FR-E"
  - "Commits pushed to the session branch, not merged; report §7.0 lists the branch, starting commit and commit hashes"

notes: "The planner reviews the session branch before the operator merges it fast-forward into main. A follow-up audit by an independent session is required before closure (P02.8.2). The planner updates design-14e05e35 §6.0, §7.0 and §11.0, requirements-14e05e35 FR-03-04 and the operations guide after review."
```

Copyright (c) 2026 William Watson. MIT License.
