Created: 2026 November 6

```yaml
prompt_info:
  id: "prompt-86c958dd"
  task_type: "debug"
  source_ref: "change-86c958dd"
  target_profile: "claude_code"  # Claude Code cloud session
  date: "2026-11-06"
  iteration: 2
  coupled_docs:
    change_ref: "change-86c958dd"
    change_iteration: 2

context:
  purpose: >
    Make the run record, Overwatch's engine status and the context-window
    resolution behave as specified: run.json records the run's exit code
    (or null with the exception type); the start record cannot end the
    run; HTTP 404 is not retried; the SE manifest states governance 12.8;
    Overwatch ignores a BLOCKED.md or .complete older than the run, raises
    FR-02-06 only while the engine runs and compares paths by file
    identity; a per-model context window is used before the live oMLX
    query. Remediates issue-86c958dd iteration 2 (audit-b8a6c445 F-01 to
    F-05, F-08; live-check P-01, P-02; CW) with the operator decisions of
    2026-11-05 and the approval of 2026-11-06.
  integration: >
    orchestrator.py main_async: configuration checks, then setup_logging,
    then 'rc = 1' and one try/finally (orchestrator.py:2742-2990 at
    d626369). Inside the try the start run record is built and written
    (_write_run_record in an inner try); early exits 'return 1'; the loop
    sets rc; the finally writes the end record (ended, rc), logs 'engine
    end rc=%d' and closes the MCP client. _completion_with_retry does not
    retry statuses in _NON_RETRYABLE_STATUS (orchestrator.py:108).
    resolve_context_window (orchestrator.py:756-814) is called per role
    with the provider's live_context_window (providers.py:232-236).
    overwatch.py: Scanner._read_engine_state (:486-570) derives the
    status from run.json, BLOCKED.md and .complete; ComplianceEngine's
    FR-02-06 check (:774-790) compares the record's task_file with open
    prompts. Line numbers are at main d626369; locate code by the quoted
    text if lines have moved.
  knowledge_references:
    - "dev/change/change-86c958dd-run-record-followup.md (approved scope, v1.1)"
    - "dev/issue/issue-86c958dd-run-record-followup.md (iteration 2)"
    - "dev/audit/audit-b8a6c445-followup-2026-11-05.md §6.0 (A1 to A8), §8.4 (F-01 to F-06), §8.5 (F-08), §11.0"
    - "dev/design/design-project-overwatch.md §4.0, §5.0"
    - "dev/design/design-14e05e35-engine-generalisation.md §4.2, §7.0, §11.0"
    - "CLAUDE.md; ai/governance/software-engineering/governance.md"
  constraints:
    - "Execution environment: Claude Code cloud (Linux container, repository clone). No oMLX, no model, no API key, no MCP server binaries. Do not start the engine against a real endpoint, do not start engine-mcp, and do not call any network endpoint other than package installation."
    - "Code changes are limited to ai/engine/src/orchestrator.py, ai/engine/src/providers.py (one docstring), the comments in ai/engine/config.template.yaml, ai/governance/software-engineering/manifest.yaml (the version line), ai/webui/src/overwatch.py, tests/engine/test_run_record.py, tests/engine/test_providers.py and tests/webui/test_overwatch.py. Other existing test files may change only where an assertion depends on behaviour or text changed by an FR below; record each such change in the report."
    - "Governance changes are limited to: creating the report named in deliverable.files, and moving this prompt to dev/prompt/closed/."
    - "Do not edit the issue, change, audit, requirements or design documents, ai/config.yaml, ai/engine/doc/, ai/engine/README.md, docs/, ai/engine/mcp/, ai/engine/src/mcp_client.py, ai/engine/src/gates.py, ai/engine/src/scope.py, ai/governance/ other than the manifest version line, ai/profiles/, README files, dev/smoke/ or dev/task.md; the planner updates documents after review."
    - "No new dependencies. Standard library only."
    - "Keep every existing message, log line, state file and BLOCKED.md text unchanged except where an FR states new text. In particular the log line 'engine end rc=%d' is unchanged."
    - "Git (CLAUDE.md §4.0): work on your session branch. Record the starting commit before any edit. Commit to the session branch and push it; do not merge into main, open a pull request, force-push or rewrite history."
    - "Stop condition: if any FR conflicts with existing code or tests, or needs a file outside the scope, implement the unaffected FRs, record the conflict in report §5.0 and §6.0, and stop."
    - "Stop condition: if the baseline suite has failures, do not fix them; record them and judge the final run against the baseline."

specification:
  description: "Eight changes, FR-A1 to FR-D, with the tests listed under testing.unit_tests."
  requirements:
    functional:
      - "FR-A1 (audit-b8a6c445 F-01; run.json rc) In main_async: (1) every 'return 1' inside the try that follows setup_logging (orchestrator.py:2773, :2811, :2852, :2860 at d626369) becomes 'rc = 1' then 'return rc'. (2) Add 'except BaseException as exc:' before the finally; it stores exc in a local (initialised to None before the try) and re-raises with a bare 'raise'. (3) In the finally's end record, when an exception was stored: _run_record['rc'] = None and _run_record['error'] = type(exc).__name__; otherwise _run_record['rc'] = rc and no 'error' key. The 'engine end rc=%d' log line is unchanged and still logs rc. Comment: change-86c958dd (audit-b8a6c445 F-01)."
      - "FR-A2 (audit-b8a6c445 F-08; start record) Build the start record dict inside the inner try that guards its _write_run_record call, so an exception from datetime.now(), astimezone() or os.path.abspath is logged with the existing 'run record not written: %s' warning and the run continues with _run_record_written False. Comment: change-86c958dd (audit-b8a6c445 F-08)."
      - "FR-A3 (P-01; HTTP 404) _NON_RETRYABLE_STATUS becomes frozenset({400, 401, 403, 404}). The non-retryable path and its BLOCKED.md text are otherwise unchanged. Comment: change-86c958dd (live check P-01)."
      - "FR-A4 (P-02; manifest version) In ai/governance/software-engineering/manifest.yaml, line 7 becomes 'version: \"12.8\"   # tracks governance.md'. Nothing else in the manifest changes."
      - "FR-B1 (audit-b8a6c445 F-02; marker age; operator decision 2026-11-05) In Scanner._read_engine_state: when a valid record exists and is not live, BLOCKED.md gives 'blocked' and .complete gives 'ship' (same order as today) only when the marker file's mtime is not earlier than the record's started time; otherwise the status is 'ended'. started is parsed with datetime.datetime.fromisoformat and compared as a POSIX timestamp truncated to whole seconds against int(mtime). When started is absent or cannot be parsed, or no valid record exists, precedence is unchanged. Update the method docstring. Comment: change-86c958dd (audit-b8a6c445 F-02)."
      - "FR-B2 (audit-b8a6c445 F-03; operator decision 2026-11-05) The FR-02-06 check (overwatch.py:777) runs only when eng.status == 'running' (in place of 'if eng.has_run_record:'). Update the comment. Comment: change-86c958dd (audit-b8a6c445 F-03)."
      - "FR-B3 (audit-b8a6c445 F-04) The FR-02-06 comparison uses a helper that returns os.path.samefile(a, b) and returns False on OSError or ValueError, in place of comparing os.path.realpath values. Comment: change-86c958dd (audit-b8a6c445 F-04)."
      - "FR-C (audit-b8a6c445 F-05) Tests only, as listed under testing."
      - "FR-D (CW; operator decision 2026-11-05) In resolve_context_window: tier 1 context.context_window (unchanged); tier 2 context.model_context_windows[model_name] when present; tier 3 the live query (the existing _LEGACY_LIVE_QUERY handling unchanged); tier 4 unresolved. Log texts become 'context window: %d (tier 2: config per-model override for '%s')' and 'context window: %d (tier 3: live oMLX admin query)'; the tiers_tried strings become 'tier 2 (per-model override): no entry for '<model>'', 'tier 3 (live oMLX query): null or failed' and 'tier 3 (live query): not available for this provider'. Update the docstring and the comment at the call site in main_async ('four-tier chain'). In providers.py:233 the docstring becomes 'Tier 3 of context resolution: live query for kind 'omlx' only.' In ai/engine/config.template.yaml (lines 115-123) the comments state: per-model entries are used first; null context_window with no entry tries the live oMLX query. Comment: change-86c958dd (operator decision 2026-11-05)."
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "PEP 8; type hints on new or changed signatures; docstrings in the existing module style"
        - "Comments referencing change-86c958dd and the finding ID at each change site"

design:
  architecture: "No new modules. One small helper in overwatch.py for the samefile comparison."
  components:
    - name: "overwatch samefile helper"
      type: "function"
      purpose: "Compare two paths by file identity without raising"
      interface:
        inputs:
          - { name: "a", type: "str", description: "path" }
          - { name: "b", type: "str", description: "path" }
        outputs: { type: "bool", description: "True when both name the same existing file" }
        raises: []
      logic: ["os.path.samefile in try; OSError or ValueError gives False"]
  dependencies:
    internal: ["orchestrator", "overwatch"]
    external: ["datetime", "os"]

error_handling:
  strategy: "Run-record problems never change rc or the control flow; an exception still propagates after the end record is written."
  logging:
    level: "WARNING for run record write or build failures (existing text)"

testing:
  unit_tests:
    - { scenario: "A1a (test_run_record.py): run_loop stubbed to return 0, and to return 2", expected: "run.json rc 0 and 2; no 'error' key; return values 0 and 2" }
    - { scenario: "A1b: each of the four early returns after setup_logging, reached by stubs (one case per return)", expected: "returned 1; run.json rc 1" }
    - { scenario: "A1c: _finish_run raising RuntimeError after run_loop returned 0; and run_loop raising KeyboardInterrupt", expected: "exception propagates; run.json rc null and error 'RuntimeError' / 'KeyboardInterrupt'; the last log line starts 'engine end rc='" }
    - { scenario: "A2a: datetime.datetime.now raising inside main_async's start record (monkeypatched module attribute)", expected: "warning 'run record not written'; run continues to its normal exit; no run.json" }
    - { scenario: "A2b (F-05): only the second _write_run_record call fails", expected: "rc unchanged; warning logged; start record left in place with ended null" }
    - { scenario: "A3: _completion_with_retry with a provider raising an error whose status is 404", expected: "one attempt; RuntimeError and BLOCKED.md name status 404" }
    - { scenario: "A4: manifest version equals the version in the last row of the governance.md version-history table", expected: "equal" }
    - { scenario: "B1 (test_overwatch.py): ended record with started T; BLOCKED.md with mtime T-10 and T+10; .complete with mtime T-10 and T+10; started 'not-a-date'", expected: "T-10: ended; T+10: blocked / ship; unparsable: blocked / ship" }
    - { scenario: "B2: ended record whose task_file is not an open prompt; live record (pid of the test process, ended null) whose task_file is not an open prompt", expected: "ended: no FR-02-06; live: FR-02-06" }
    - { scenario: "B3: live record whose task_file is a symlink to the open prompt; a task_file differing only in letter case (skip unless the tmp file system is case-insensitive); a missing task_file", expected: "symlink: no FR-02-06; case: no FR-02-06; missing: FR-02-06" }
    - { scenario: "C (F-05): O1 cases for pid as bool and as string, ended as a number, rc as bool, an invalid record with BLOCKED.md (blocked), a live record with .complete (running); _pid_alive for 0, -1 and PermissionError (monkeypatched os.kill); task_ref values; FR-02-06 silent with an invalid record; O3 with one document directly in test/; 'run.json' in SIGNAL_FILES", expected: "as specified in audit-b8a6c445 §8.4 F-05" }
    - { scenario: "D1 (test_providers.py): model_context_windows {'magistral': 40960}, live query returning 1000", expected: "40960; log text names tier 2" }
    - { scenario: "D2: no entry for the model, live query 1000", expected: "1000; log text names tier 3" }
    - { scenario: "D3: context.context_window 8192 with an entry and a live value", expected: "8192" }
    - { scenario: "D4: no entry, live query None", expected: "None; warning lists tier 2 and tier 3" }
  edge_cases:
    - "Use tmp_path and monkeypatch only; no network, no real engine run."
    - "Restore the 'engine' logger after tests that call setup_logging (isolated_engine_logger)."
    - "Set file mtimes with os.utime; derive T from the record's started string."
    - "tests/engine/test_providers.py:295 asserts the old order; replace that assertion with D1 and record it in the report."
  validation:
    - "Baseline before any edit: python3 -m pytest tests/engine tests/webui -q; record counts."
    - "After the change: same command; no new failures; all new tests pass."
    - "Mutation check (not committed), each on a temporary copy: (M1) one early return back to 'return 1' with rc left 0 by a stub: A1b fails; (M2) remove the except BaseException clause: A1c fails; (M3) start record dict moved back outside the inner try: A2a fails; (M4) remove 404 from _NON_RETRYABLE_STATUS: A3 fails; (M5) remove the marker age check: B1 fails; (M6) FR-02-06 back to has_run_record: B2 fails; (M7) samefile helper back to realpath equality: B3 symlink or case case fails, or record why it survives; (M8) tier order restored: D1 fails; (M9) _pid_alive returns True for pid 0: C fails. Record results."
    - "python3 ai/engine/src/linter.py dev and python3 ai/engine/src/protocol_checker.py dev; record results; fix new findings caused by this work only."

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
    - "Setup if needed: pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest (pip may need --break-system-packages)"
    - "Close this prompt with git mv dev/prompt/prompt-86c958dd-run-record-followup.md dev/prompt/closed/; leave the issue and change documents active"
    - "Commits: Conventional Commits; engine source as fix(engine), Overwatch source as fix(webui), manifest as fix(governance), tests as test, report and prompt move as docs(dev)"
  files:
    - { path: "ai/engine/src/orchestrator.py", content: "modified (FR-A1, FR-A2, FR-A3, FR-D)" }
    - { path: "ai/engine/src/providers.py", content: "modified, one docstring (FR-D)" }
    - { path: "ai/engine/config.template.yaml", content: "modified, comments only (FR-D)" }
    - { path: "ai/governance/software-engineering/manifest.yaml", content: "modified, version line (FR-A4)" }
    - { path: "ai/webui/src/overwatch.py", content: "modified (FR-B1, FR-B2, FR-B3)" }
    - { path: "tests/engine/test_run_record.py", content: "modified (A1, A2, A4)" }
    - { path: "tests/engine/test_providers.py", content: "modified (A3, D)" }
    - { path: "tests/webui/test_overwatch.py", content: "modified (B1 to B3, C)" }
    - path: "dev/reports/report-86c958dd-run-record-followup.md"
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
  - "FR-A1 to FR-D implemented as specified; all new tests present and passing"
  - "Mutations M1 to M9 fail their named tests, or the report states why one survives"
  - "Full suite: no failures beyond the recorded baseline"
  - "git diff <starting commit>..HEAD touches only the files in deliverable.files and the prompt move, plus recorded assertion updates"
  - "No existing message changed except the context-window log texts and tiers_tried strings of FR-D"
  - "Commits pushed to the session branch, not merged; report §7.0 lists the branch, starting commit and commit hashes"

notes: "The planner reviews the session branch before the operator merges it fast-forward into main. A follow-up audit by an independent session is required before closure (P02.8.2). The planner updates design-14e05e35, design-ael-orchestrator, design-project-overwatch, the operations guide, ai/engine/README.md, docs/guide-getting-started.md and requirements-1c1f4ef6 FR-AEL-008 after review."
```

Copyright (c) 2026 William Watson. MIT License.
