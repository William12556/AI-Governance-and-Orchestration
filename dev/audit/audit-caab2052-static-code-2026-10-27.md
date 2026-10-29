Created: 2026 October 27

# Static Code Audit — ai/engine/src and ai/webui/src (caab2052)

---

## Table of Contents

[1.0 Summary](<#1.0 summary>)
[2.0 Method](<#2.0 method>)
[3.0 Scope and File Inventory](<#3.0 scope and file inventory>)
[4.0 Requirements and Design Compliance](<#4.0 requirements and design compliance>)
[5.0 Findings by Dimension](<#5.0 findings by dimension>)
[6.0 Findings Register](<#6.0 findings register>)
[7.0 Prior-Finding Re-verification](<#7.0 prior-finding re-verification>)
[8.0 Test Coverage Gaps](<#8.0 test coverage gaps>)
[9.0 Positive Findings](<#9.0 positive findings>)
[10.0 Recommended Remediation Order](<#10.0 recommended remediation order>)
[11.0 Open Questions for the Operator](<#11.0 open questions for the operator>)
[12.0 T08 Record](<#12.0 t08 record>)
[13.0 Closure Recommendation](<#13.0 closure recommendation>)
[14.0 Operator Decisions](<#14.0 operator decisions>)
[Version History](<#version history>)

---

## 1.0 Summary

- **Subject:** the AI-G&O framework source in `ai/engine/src/` (11 modules) and `ai/webui/src/overwatch.py`, at `24b2dfc` (branch `claude/gracious-bardeen-jnq01l`, equal to `main` at audit start).
- **Protocol:** P02 Audit, strategic mode (P02.9.1). Read-only static audit. No source, test, configuration or governance file was changed.
- **Verdict:** sound, with remediation recommended. The security controls added by change-82dbf16a and change-7d953510 hold. No path was found by which a worker forges a verdict, writes an engine signal file, or reads a provider key from a log, an exception or an MCP server environment. The defects found are in robustness, monitoring accuracy and the governance checkers.
- **Findings:** 0 critical, 0 high, 6 medium, 19 low (25 in total).
- **Central results:**
  - M-01: a tool call whose arguments are not a JSON object (a list, a number, or a double-encoded string) raises `AttributeError` in `run_phase`. The run ends with a traceback, no `BLOCKED.md` and no return stage. Probe-confirmed for write and read tools.
  - M-02: the per-iteration context budget counts message `content` only. Tool-call arguments in assistant messages and the tool schema are not counted, so a phase that writes large files reaches the provider's context limit without a budget abort. Probe: a 40,000-character `write_file` call is estimated at 0 tokens.
  - M-03: `linter.py` and `protocol_checker.py` skip every document whose `schema_type` is not one of the five retired-scheme values, and report nothing. A `t07_change` document with four defects gives 0 findings. 21 closed documents in `dev/` carry such values. This is the hazard recorded in audit-eb782f83 F-04, now realised.
  - M-04 and M-05: Overwatch reports `RUNNING` after any run that ends without `BLOCKED.md` or `.complete`. It also raises FR-02-06 whenever a prompt is open, because the engine's `task.md` now begins with the runtime header.
- **Tests:** 331 passed, 1 skipped (`tests/webui/test_overwatch.py:296`, skipped when run as root). `linter.py dev`: 0 errors, 96 warnings. `protocol_checker.py dev`: 0 errors, 0 warnings.
- **Prior findings:** of 41 re-verification rows for findings that concern these files, 31 are resolved, 7 are still present (6 deferred in `dev/task.md`, one of which is realised as M-03; 1 accepted), 1 is partly resolved and 2 are not applicable to this scope (§7.0).

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Method

- **Environment:** Claude Code cloud container, Linux 6.18.44, Python 3.13.17, git 2.43.0, running as root. The system interpreter has `mcp` 2.3.0, which the engine excludes (`mcp>=1.0.0,<2`), so all tools ran in a virtual environment in the session scratchpad.
- **Installed versions** (from `ai/engine/requirements.txt` and `ai/webui/requirements.txt`, plus the audit tools): openai 3.39.0, anthropic 2.3.0, mcp 1.30.0, PyYAML 6.0.3, rich 15.0.0, pytest 9.1.1, ruff 0.17.3, mypy 2.4.0, bandit 1.9.4. No requirements file was changed.
- **Reading:** every in-scope file was read completely. Context files were read to the extent needed: `ai/engine/mcp/server.py`, both recipe folders, `ai/governance/software-engineering/manifest.yaml`, `ai/engine/config.template.yaml`, `ai/engine/doc/guide-engine-operations.md` §3.0, the test modules and the six baseline documents.
- **Commands** (from the repository root unless stated):
  - `python -m pytest tests/engine tests/webui -q -p no:cacheprovider` (and `-rs`, `--collect-only -q`)
  - `ruff check --isolated --no-cache --statistics ai/engine/src ai/webui/src`; the same with `--select F,B007,S105,S110,S112,S310,S324,S607`
  - `mypy --ignore-missing-imports <module>`, run from each source folder with the cache in the scratchpad
  - `bandit -q -r ai/engine/src ai/webui/src`
  - `python ai/engine/src/linter.py dev`; `python ai/engine/src/protocol_checker.py dev`
  - `npm pack @j0hanz/filesystem-mcp@2.5.0` into the scratchpad, then a text search of `dist/` for the registered tool names. The package was not installed or executed.
- **Probes:** five throwaway scripts in the scratchpad (`p1_args.py` to `p5_git.py`), run with `python -I`, each against temporary directories or temporary git repositories. They are not committed. Results are cited as P1 to P5:
  - P1/P2: non-object tool-call arguments through `providers`, `parser`, `scope` and `run_phase` (M-01).
  - P3: Overwatch on fixture projects (M-04, M-05, L-07, L-08).
  - P4: token estimate, write classification, a path containing NUL, a preflight grep, tracking by name (M-02, L-01, L-02, L-03, L-04).
  - P5: `approve.py` with a failing pre-commit hook; a project in a subdirectory of a git repository (L-05, L-06).
  - Linter fixture: two change documents with the same four defects, one `t02_change` and one `t07_change` (M-03).
- **Claim classification:** each finding is marked *observed* (tool output, probe or file:line) or *inferred* (with confidence and a verification method).
- **Side effects:** the virtual environment, the mypy cache, the npm tarball and the probe scripts were written to the scratchpad. pytest and the probes created gitignored `__pycache__/` folders under `ai/` and `tests/`; these were removed before the commit. `git status` showed only this report before the commit.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Scope and File Inventory

| File | LOC | Purpose |
|---|---|---|
| `ai/engine/src/approve.py` | 104 | Operator command: records and commits one stage approval with evidence blob hashes |
| `ai/engine/src/gates.py` | 177 | Built-in syntax gate, deliverable-to-pytest mapping, command gate runner |
| `ai/engine/src/linter.py` | 416 | Layer 1 governance linter: naming, structure, YAML fields, coupling, links |
| `ai/engine/src/manifest.py` | 227 | Governance model manifest loader and validator |
| `ai/engine/src/mcp_client.py` | 120 | Async stdio MCP client: tool catalogue and dispatch |
| `ai/engine/src/orchestrator.py` | 2,759 | Engine CLI: worker/reviewer phases, loop, gates, state files, startup |
| `ai/engine/src/parser.py` | 136 | Plain-text tool-call parser (Mistral, Devstral, Cohere formats) |
| `ai/engine/src/protocol_checker.py` | 402 | Layer 2 multi-document workflow invariant checker |
| `ai/engine/src/providers.py` | 556 | Provider interface: OpenAI-compatible and native Anthropic; key resolution; role bindings |
| `ai/engine/src/scope.py` | 228 | Write-tool classification, write scope, signal-file protection |
| `ai/engine/src/stages.py` | 464 | Work-item stage derivation, committed approvals, pre-run check |
| `ai/webui/src/overwatch.py` | 1,345 | Read-only governance monitor rendered to `overwatch.html` |
| **Total** | **6,934** | |

Context only: `ai/engine/mcp/server.py` (344), `ai/engine/recipes/` (2 files), `tests/engine/` (9 files, 2,864 LOC), `tests/webui/` (1 file, 339 LOC).

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Requirements and Design Compliance

### 4.1 requirements-14e05e35 and design-14e05e35

| Item | Status | Evidence |
|---|---|---|
| CON-01 single user, local first | Pass | No server or socket in scope; oMLX on loopback by default |
| CON-02 one model per project | Pass | `manifest.py:96-101` refuses zero or several manifests |
| CON-03 planner outside the engine | Pass | Engine runs worker and reviewer only |
| CON-04 governance.md not split | N/A | Document constraint |
| CON-05 providers | Pass | `providers.py:39` kinds `omlx`, `openai_compatible`, `anthropic` |
| CON-06 ownership boundary | N/A | Propagation is in `bin/` (out of scope) |
| CON-07 pip only; only new dependency `anthropic` | Pass | `ai/engine/requirements.txt`: openai, anthropic (lazy import, `providers.py:317`), mcp, pyyaml, rich |
| FR-01-01, FR-01-02, FR-01-03 manifest content | Pass | `manifest.py:131-208`; SE manifest declares `loop` and `audit` |
| FR-01-04 workspace folders | N/A | Created by `bin/` scripts |
| FR-01-05 validation before any model call | Partial | `orchestrator.py:2438-2442` precedes readiness. Unhashable values crash with `TypeError` instead of `ManifestError` (L-11) |
| FR-01-06 audit recipes in the model folder | Pass | `ai/governance/software-engineering/recipes/audit-*.yaml` |
| FR-01-07 writable paths | Pass | `manifest.py:139-143`; `scope.py:178-180` |
| FR-02-01, FR-02-02 stage order, loop-owned only | Pass | `manifest.py:57-59`; `orchestrator.py:2448` |
| FR-02-03 return stage in `BLOCKED.md` | Partial | `orchestrator.py:2392-2405`. Failure exits that write no `BLOCKED.md` get no return stage (M-01, M-04) |
| FR-03-01 three gate types | Pass | Human approval, reviewer verdict, command exit code |
| FR-03-02 every applicable gate passes | Conflict | A command gate FAIL overrides SHIP (`orchestrator.py:2243-2266`); a syntax gate FAIL does not. Design §6.0 says the syntax gate results are "unchanged". OQ-01 |
| FR-03-03 command, cwd and interpreter configurable | Pass | `orchestrator.py:2309-2338`; `gates.py:230-238` (`{project_root}` placeholder) |
| FR-03-04 syntax and pytest as declared command gates | Deviates | Syntax stays built in (`manifest.py:20`), as design §6.0 states. OQ-01 |
| FR-03-05 human approval never passed | Pass | `orchestrator.py:2352-2375` writes `awaiting-approval.md` only |
| FR-03-06 one log line per gate per iteration | Pass | `orchestrator.py:1739-1741, 2066, 2076, 2169` |
| FR-04-01, FR-04-02, FR-04-08 role binding, legacy block | Pass | `providers.py:495-549` |
| FR-04-03 one interface, two implementations | Pass | `providers.py:115-377`. Signatures drift from design §4.1 (L-19) |
| FR-04-04 strict tools, prompt caching | Pass (static) | `providers.py:212-227, 269-270`. Live check against the Anthropic API is deferred (`dev/task.md`) |
| FR-04-05, FR-04-06 per-role context window and readiness | Pass | `orchestrator.py:2540-2570`; tier order is a known deferred item (`dev/task.md`) |
| FR-04-07 keys from environment or Keychain | Pass | `providers.py:403-473` |
| FR-04-09 9-character tool call IDs | Pass | `providers.py:75-77` |
| FR-05-01 write scope | Partial | `scope.py:190-228`. Classification is by tool name, so a write tool whose name lacks a listed verb is not checked (L-01); an unresolvable path is skipped (L-02) |
| FR-05-02 one classification source | Pass | `scope.py:51-60`, imported by `mcp_client.py:23` and `orchestrator.py:66` |
| FR-05-03 absolute deliverable paths for the reviewer | Pass | `orchestrator.py:1860-1875, 2129-2132` |
| FR-05-04 rejected writes logged | Pass | `orchestrator.py:1305-1307` |
| FR-06-01 to FR-06-03 engine-mcp | N/A | `server.py` is context only |
| FR-07-01 to FR-07-05 terminology | Pass | No Strategic or Tactical Domain term in scope; `govwatch` survives in one output heading (L-15) |
| FR-08-01 to FR-08-03 stage derivation | Pass | `stages.py:192-264` |
| FR-08-04 approvals only by operator command | Pass | `approve.py`; no engine path writes `ai/approvals.yaml` |
| FR-08-05 pre-run check | Partial | `orchestrator.py:2457-2473`; `stages.py:365-404`. CLI tracks by name as well as location, unlike design §8.4 (L-04). A project nested in a larger repository never sees its approvals (L-06) |
| FR-08-06 read-only status | Pass | `stages.py:424-458`, `_git` with `--no-optional-locks` |
| FR-08-07 contradictions reported | Partial | `stages.py:257-264`; the active-folder case is a known deferred item (L-11 of audit-14e05e35) |
| NFR-01 unchanged SE gate results | Pass (static) | Gate code moved without change of result; live V-02 recorded earlier |
| NFR-02 legacy values | Pass | `orchestrator.py:2586`; `overwatch.py:723, 787`; `providers.py:528-537` |
| NFR-03 no provider branching in the loop | Pass | No provider kind test in `orchestrator.py` |
| NFR-04 invalid configuration stops with file and field | Partial | Known deferred gaps (`dev/task.md`, audit-14e05e35 L-08); also L-11 |
| NFR-05 no key in logs, state or committed files | Pass | Label-only logging (`providers.py:457, 461`); MCP children receive only `HOME, LOGNAME, PATH, SHELL, TERM, USER` plus configured `env` (mcp 1.30.0 `get_default_environment`); gate scrubbing (`gates.py:255-256`). Keychain readable by gate code is accepted (DI-06) |
| NFR-06 offline tests | Pass | 331 tests, no network |

### 4.2 requirements-1c1f4ef6 (AEL baseline) and design-ael-orchestrator

| Item | Status | Evidence |
|---|---|---|
| FR-AEL-001 to FR-AEL-004 loop, modes, dispatch, parsing | Pass | `orchestrator.py:1078-1554, 1878-2306, 2735-2755`; `parser.py` |
| FR-AEL-005 budget enforcement | Partial | Thresholds enforced, but the estimate omits tool-call arguments and the tool schema (M-02); design-ael §5.1 requires the schema |
| FR-AEL-006 state files | Pass | `orchestrator.py:603-611` |
| FR-AEL-007 tactical brief extraction | Pass | `orchestrator.py:965-1012` |
| FR-AEL-008 context window | Superseded | FR-04-05/FR-04-06; four-tier chain `orchestrator.py:650-708` |
| FR-AEL-009 readiness | Pass | `providers.py:170-199, 338-374` |
| FR-AEL-010 SHIP and BLOCKED signalling | Partial | Several failure exits write no `BLOCKED.md` (M-01, M-04) |
| FR-AEL-011 `engine end rc=N` on all exits | Partial | Absent on returns between `setup_logging` and the `try` (L-09); log name is now `engine_*.LOG` |
| FR-AEL-012 context report | Pass | `orchestrator.py:755-821` |
| FR-AEL-013 MCP error handling | Deviates (documented) | Corrective text is embedded in the tool result, not a user message (`orchestrator.py:1402-1405`). OQ-03 |
| FR-AEL-014, FR-AEL-015 tool call cap, duplicate reads | Pass | `orchestrator.py:1237-1244, 1336-1346` |
| NFR-AEL-001 single process | Superseded | Gates, `git`, `grep`, `security` and `py_compile` run as subprocesses. OQ-03 |
| NFR-AEL-002, NFR-AEL-003 async, config-driven | Pass | Blocking `subprocess.run` calls inside coroutines (ruff ASYNC221) are accepted for a single-process tool |
| NFR-AEL-004 `--task` file or string | Pass | `orchestrator.py:2416-2421` |
| NFR-AEL-005 minimal dependencies | Superseded | `anthropic` is optional; design-ael §10.0 still lists four packages. OQ-03 |
| design-ael §9.0 "`finally` always logs `engine end`" | Partial | L-09 |

### 4.3 requirements-0c6aedee and design-project-overwatch

| Item | Status | Evidence |
|---|---|---|
| CON-01 / NFR-01 read-only | Pass | Writes only `overwatch.html` (`overwatch.py:1068-1071`) and `ai/dashboard-alerts.md` (`:890`), as design §3.1 and §11.0 permit. Citation and wording conflict, OQ-02 |
| CON-02, CON-03 / NFR-02, NFR-03 scope | Pass | `resolve_paths` under the project root; the state directory comes from `loop.state_dir` |
| CON-04 Python 3.11+ | Pass | PEP 604 annotations under `from __future__ import annotations` |
| CON-05 / NFR-06 localhost only | Pass | No socket; static file with meta refresh |
| CON-07 no document authorship | Pass | No workspace write |
| FR-01-01 to FR-01-03 three panels | Partial | Rendered (`overwatch.py:1080-1214`), but engine status and FR-02-06 are wrong in common states (M-04, M-05); duplicated result documents (L-07) |
| FR-01-04 govwatch retirement | Pass | No govwatch module remains; heading text remains (L-15) |
| FR-02 to FR-10 | Parked | `dev/task.md` (`0c6aedee`) |
| NFR-04 malformed documents give WARNING | Pass | `overwatch.py:351-352, 409-425, 604-611` |
| NFR-05 absent state directory is idle | Pass | `overwatch.py:452-453` |
| NFR-07 dependency footprint `pyyaml` only | Pass | `ai/webui/requirements.txt`; `test_render_no_textual_or_rich_import` |

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Findings by Dimension

### 5.1 Correctness

- **M-01 Non-object tool-call arguments crash the phase.** Observed (P1, P2). `OpenAICompatProvider.normalise` keeps any JSON value (`providers.py:150-152`). `parser.parse_tool_calls` passes `arguments` through unchecked in format 1 (`parser.py:93, 96`) and format 2 (`parser.py:110-117`). `run_phase` then calls `.get` on the value in `scope.check` (`scope.py:64, 70`, reached from `orchestrator.py:1302`), in `_validate_audit_report_write` (`orchestrator.py:275`), in read tracking (`orchestrator.py:1338`) and in edit handling (`orchestrator.py:1415`). P2 drove `run_phase` with `write_file` and `read_file` calls whose arguments are `[1, 2]`. Both raised `AttributeError`, and no `BLOCKED.md` was written. A double-encoded string, which local models emit, gives the same result (P1). The run ends with a traceback. `_finish_run` is skipped, so the FR-02-03 return stage is not recorded, and engine-mcp reports the run as neither shipped nor blocked. No write is dispatched, so the failure is safe but unhandled.
- **M-02 The budget estimate omits tool-call arguments and the tool schema.** Observed (P4). `estimate_tokens` counts only `content` (`orchestrator.py:720-728`). In assistant messages the call payload is in `tool_calls[].function.arguments` (`orchestrator.py:1248-1256`), so it is never counted. P4: a 40,000-character `write_file` call is estimated at 0 tokens. `run_phase` calls `estimate_tokens(messages)` without `tools` (`orchestrator.py:1179`), although the docstring (F8) and design-ael §5.1 require the schema. P4: 8,000 characters of schema add 2,000 tokens when passed and 0 at `:1179`. A worker that writes large files therefore reaches the provider's context limit with no budget abort. The provider error is then retried three times and ends BLOCKED with a generic message.
- **M-03 Governance checkers silently skip unknown schema types.** Observed (fixture, `rg`). `check_yaml` returns before any field check when `schema_type` is not in `_ID_FIELDS` (`linter.py:237-262`); the coupling pass skips the same documents (`linter.py:378`); `protocol_checker.load_workspace` drops them (`protocol_checker.py:132-133`). None of these emits a warning. A `t07_change` document with an invalid id, an invalid status, iteration 0 and a dangling issue reference gives 0 findings, while the same document as `t02_change` gives 4 errors. 21 closed documents in `dev/` use `t07_change`, `t06_issue` or `t03_prompt`. The templates still emit the retired values, so new documents are checked today. The defect is that the divergence audit-eb782f83 F-04 predicted now exists and the tools report a clean result. Retiring the numeric prefix is deferred (`dev/task.md`); this finding concerns only the missing warning.
- **M-04 Runs that end without a terminal marker are shown as running.** Observed (P3, code). Overwatch sets `running` whenever `task.md` exists and neither `BLOCKED.md` nor `.complete` does (`overwatch.py:466-473`). The engine writes `task.md` at every start (`orchestrator.py:2637`) and only `--mode reset` removes it (`orchestrator.py:395-407`). These exits write neither marker: context-budget abort (`:1184-1189`, then `:2037-2039`), declined continuation after max iterations (`:1996-1997`), review-phase failure (`:2154-2156`), the `--duration` limit (`:1968-1972`, writes `.timeout`, which Overwatch does not read) and M-01. After any of these, the dashboard shows `RUNNING` until the next reset.
- **M-05 FR-02-06 fires whenever a prompt is open.** Observed (P3). `task_ref` is the first non-empty line of `task.md` (`overwatch.py:483-489`). Since the runtime header was added, that line is always `[ENGINE RUNTIME CONTEXT]` (`orchestrator.py:2627-2634`). The FR-02-06 match on the prompt's UUID or file name (`overwatch.py:706-710`) therefore never succeeds. The task text is also the tactical brief, which need not name the prompt.
- **L-04 CLI tracking depends on the file name.** Observed (P4). The CLI tracks a task only when its name matches `prompt-<uuid>-` (`orchestrator.py:2341-2349, 2461`). Design §8.4 tracks by resolved location in `ai/workspace/`. A T03 prompt at `ai/workspace/prompt/my-task.md` runs from the CLI with no pre-run check and no approval. engine-mcp refuses such names (`server.py` `_PROMPT_NAME`), so only direct CLI runs are affected.
- **L-06 Approvals are unreadable when the project is a subdirectory of a repository.** Observed (P5). `git show HEAD:ai/approvals.yaml` resolves the path from the repository root, not from `-C` (`stages.py:128`). `approve.py` commits the entry (`approve.py:81-82`), but `committed_approvals` returns `{}`, so every tracked run is refused as unapproved. Using `HEAD:./ai/approvals.yaml` would resolve the path relative to `-C`. The failure is closed (runs are refused), not open.
- **L-07 Overwatch lists test results twice.** Observed (P3). `CLASS_DIRS` maps `test` to `test/` and `result` to `test/result/` (`overwatch.py:52-53`), and the scan uses `rglob` (`:403`), so every result document appears twice. This doubles registry rows and the FR-02-05 count.
- **L-08 An ancestor named `closed` hides every document.** Observed (P3). The exclusion tests `"closed" in filepath.parts` on the absolute path (`overwatch.py:405`). A project under `/…/closed/…` shows no documents.
- **L-14 Audit archive overwrites silently and uses the current directory.** Observed (code). `_archive_audit_artifacts` copies to `ai/workspace/audit/audit-<uid>-report.md` with `shutil.copy2` and no existence check (`orchestrator.py:533-540`), so a second audit of the same work item replaces the first archive. It resolves the folder from `os.getcwd()` rather than the run's project root.

### 5.2 Security

- **L-01 Write classification is by name pattern.** Observed (P4); impact inferred. `is_write_tool` matches ten verbs (`scope.py:38-53`). `copy_file`, `append_file`, `save_file`, `touch`, `upload_file`, `apply_diff`, `insert_text`, `update_file`, `chmod`, `truncate`, `set_content` and `execute_command` are not write tools, so `scope.check` returns before any path test (`scope.py:200-201`). The worker is offered every tool (`orchestrator.py:1111`). The pinned `@j0hanz/filesystem-mcp@2.5.0` registers `create, delete, diff, edit, find_files, list, list_roots, move, patch, read, replace_text, search_text, stat`, all classified correctly. The gap therefore opens only with another server or version. The module docstring's "fail-closed" claim (`scope.py:6-7`) holds for names that contain a listed verb, not in general. Confidence that no current configuration is exposed: high for the template's servers.
- **L-02 An unresolvable path is skipped, not refused.** Observed (P4). `scope.check` does `continue` when `realpath` raises (`scope.py:209-212`). A `write_file` path containing NUL passes with no violation. The MCP server will most likely reject it, but the check fails open. Severity is low because no exploit path was found.
- **L-03 Preflight `grep` has no option terminator and no timeout.** Observed (P4). `["grep", "-qF", pattern, path]` (`orchestrator.py:1644-1647`) treats a pattern that starts with `-` as an option. P4: the criterion "a.txt contains '--version'" was reported SATISFIED for a file that does not contain the text. The pattern comes from a planner-authored prompt. The same call and the `py_compile` calls (`orchestrator.py:1428, 1497, 1623`; `gates.py:171`) have no timeout, so a FIFO or a very slow file blocks the phase.
- **L-12 `py_compile` writes outside the write scope.** Inferred, high confidence (PEP 3147 behaviour of `python -m py_compile`). The syntax gate compiles every existing `.py` path named in `work-summary.txt`, including paths outside the project (`gates.py:157-172`). The post-write and edit-failure checks do the same for worker-written files (`orchestrator.py:1428, 1497`). Each run writes `__pycache__/*.pyc` beside the source, which the write scope does not authorise. To verify, run the gate on a deliverable in a read-only-scoped folder and list `__pycache__/`.
- **Triaged, not counted:**
  - bandit B324 (SHA-1, `stages.py:86`) is required for the git blob format. Approval binding therefore rests on SHA-1. A chosen-prefix collision is outside this project's single-user threat model.
  - bandit B310 (`providers.py:98`): the URL comes from operator configuration.
  - B603/B607 (subprocess without shell, partial path `git`/`grep`): argv lists with `shell=False` throughout. No `shell=True`, `eval`, `exec`, `pickle` or unsafe YAML load exists in scope.
  - HTML output: every interpolated string is escaped (`overwatch.py:1010-1214`), and the embedded JSON escapes `<` and `>` (`:1226-1227`). No injection path was found.
  - Gate code runs with the operator's permissions (design DI-06, accepted). Worker-written tests can still read a Keychain item or write anywhere the operator can. This is recorded, not counted.

### 5.3 Design and Requirements Compliance

See §4.0. Departures not covered by a finding: FR-03-02/FR-03-04 against design §6.0 for the syntax gate (OQ-01); the CON-07 citation for Overwatch (OQ-02); the AEL baseline items superseded in practice (OQ-03); and design §7.0 "the run type's own paths", which has no implementation (OQ-04).

### 5.4 Architecture

- **L-17 Logic duplicated between engine and webui.** Observed. These are candidates for the reserved `ai/core/`:
  - The fenced-YAML extraction regex appears eight times: `linter.py:39`, `scope.py:111`, `stages.py:178`, `orchestrator.py:949, 975, 1577` and `overwatch.py:222`, with a variant that accepts trailing whitespace.
  - The document file-name patterns appear in `linter.py:37-38`, `stages.py:201, 354` and `overwatch.py:61-68`.
  - Overwatch hard-codes the workspace folder map (`overwatch.py:48-58`) instead of reading the manifest's `workspace_folders`.
  - `loop.state_dir` resolution is duplicated (`overwatch.py:1240-1247`, `server.py:86-93`).
  - `protocol_checker.py:28` imports private linter helpers and mirrors `_ID_FIELDS` (`:50-56`).
- **L-13 MCP tool catalogue.** Observed (code). A tool name offered by two servers is overwritten without warning (`mcp_client.py:56-61`). A server that fails to connect is only printed (`:63-64`), and the run continues with fewer tools, or none (`orchestrator.py:2574-2575`). Status messages use `print` instead of the engine logger.
- **L-15 Stale terminology.** Observed. `dashboard-alerts.md` is headed `# govwatch alerts — <project>` (`overwatch.py:856`). The docstring references to govwatch (`:6, 9, 932`) are historical and acceptable. No AEL, Ralph Loop, Strategic/Tactical Domain or `ai/src` term remains in scope. The remaining `ael` values are legacy `target_profile` values, kept by NFR-02.
- **L-19 Provider interface drift.** Observed. Design §4.1 specifies `context_window(model)` and `await_ready(...) -> bool` with `poll`. The code has `live_context_window`, `await_ready(...) -> None` with `interval` and `echo` (`providers.py:170, 201, 338, 376`). The behaviour matches; the design text does not.

### 5.5 Robustness

- **M-06 No bounded timeout on model or MCP calls.** Observed constants; behaviour inferred, high confidence. Both SDK clients are built with their defaults (`providers.py:124, 321`): a 600 s read timeout and 2 retries in openai 3.39.0 and anthropic 2.3.0 (printed from `DEFAULT_TIMEOUT`/`DEFAULT_MAX_RETRIES`). The engine adds 3 attempts (`orchestrator.py:475-505`). A stalled endpoint can therefore hold one completion for up to 9 × 600 s before BLOCKED. MCP `initialize` and `call_tool` have no timeout (`mcp_client.py:53, 101`). The F28 phase cap (`orchestrator.py:1169`) and the `--duration` deadline (`:1968`) are checked only between iterations, so neither can interrupt a hung call. To verify, point a provider at a server that accepts and never responds, and time the run to BLOCKED.
- **L-05 `approve.py` leaves state behind when the commit fails.** Observed (P5). The file is written and staged before `git commit` (`approve.py:77-85`). With a failing pre-commit hook the command exits 1 with the message `git failed (commit -q): ` (empty detail) and leaves `ai/approvals.yaml` staged. Re-running appends a second entry for the same pair. `parse_approvals` takes the last, so the result is still correct.
- **L-09 `engine end rc=N` is missing on some exits.** Observed (code). After `setup_logging` (`orchestrator.py:2504`) these return before the `try`/`finally` at `:2658`: the recipe manifest error (`:2519-2520`), provider not ready (`:2553-2558`), strict brief (`:2599-2600`) and no task (`:2606-2609`). An exception there, for example `UnicodeDecodeError` on a task file that is not UTF-8 (`:2580`), also skips `mcp.close()`.
- **L-10 State and output files are not written atomically.** Inferred, medium confidence that partial reads occur in practice. `write_state` (`orchestrator.py:608-611`), `AlertWriter.write` (`overwatch.py:890`), `HtmlRenderer.write` (`:1071`) and `approve.py:77-78` truncate and rewrite in place. Overwatch, engine-mcp and the browser read these files concurrently. Writing to a temporary file and calling `os.replace` would remove partial reads.
- **L-11 Unhashable or non-string YAML values crash the checkers.** Observed (code; Python semantics). `manifest.py:188` (`g not in gates`, where `g` is a mapping), `linter.py:250` (a list compared against a frozenset), `linter.py:289` (a list reference against a dict) and `protocol_checker.py:86, 164` (`re.search` on a non-string) raise `TypeError` instead of reporting the file and field (NFR-04).

### 5.6 Maintainability

- **L-18 orchestrator.py size and implicit working directory.** Observed.
  - The module has 2,759 lines. `run_phase` spans `orchestrator.py:1078-1554` (477 lines), `run_loop` `:1878-2306` (429 lines) and `main_async` `:2408-2732` (325 lines), with deep nesting in the SHIP gate block (`:2185-2275`).
  - The project root is taken from the working directory three ways: at import (`PROJECT_ROOT`, `:55`), in `main_async` (`:2612`) and in `_archive_audit_artifacts` (`:533`).
  - `stages` and `gates` rely on paths relative to the working directory.
  - These make unit testing depend on `chdir`.
- **L-16 Dead code and type errors.** Observed (ruff, mypy, code).
  - Unused imports: `mcp_client.py:11` (`uuid`) and `orchestrator.py:71` (`Rule`).
  - Unused variables: `orchestrator.py:1183` (`pct_str`) and `protocol_checker.py:153` (`by_id`).
  - f-strings without placeholders: `orchestrator.py:1321` and `providers.py:535`.
  - The pytest default command at `gates.py:251` is unreachable through the engine, because `manifest.py:165-166` requires a command.
  - Stale docstring test paths: `linter.py:13` and `protocol_checker.py:14` name test files that do not exist.
  - mypy reports 11 errors. The substantive one is `stages.py:296`: `approvals = set()` where a dict is declared, which works only because the empty set is never indexed. The others are `orchestrator.py:686` (sentinel typed as `object`), `orchestrator.py:1644` (bytes against str) and `orchestrator.py:2465-2472` (`str | None`).
  - ruff 0.17.3 with its default rule set reports 97 issues (47 fixable), mostly annotation style (UP045 ×27) and blind `except` (BLE001 ×14). No pyflakes error indicates a runtime defect.
- **Type hints and docstrings** are present on most functions. Exceptions: `linter._get`, `scope.path_values` and the `stages` functions that take `manifest` and `st` untyped.

### 5.7 Test Coverage

See §8.0.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Findings Register

Critical: none. High: none. Medium: M-01 to M-06. Low: L-01 to L-19.

| ID | Severity | File:line | Finding | Evidence | Recommendation |
|---|---|---|---|---|---|
| M-01 | Medium | `orchestrator.py:1302, 1338`; `scope.py:64, 70`; `providers.py:150`; `parser.py:93, 96, 110` | Non-object tool-call arguments raise `AttributeError` in `run_phase`; no `BLOCKED.md`, no return stage | Observed: P1, P2 | Normalise arguments to a dict at the provider boundary, or reply with a tool error for a non-object; add a test |
| M-02 | Medium | `orchestrator.py:720-728, 1179` | Budget estimate omits `tool_calls` arguments and the tool schema | Observed: P4 (0 tokens for 40,000 characters) | Count arguments and pass `tools`, as design-ael §5.1 states |
| M-03 | Medium | `linter.py:237-262, 378`; `protocol_checker.py:132` | Documents with an unrecognised `schema_type` are skipped without a warning | Observed: fixture (4 errors vs 0); 21 closed `dev/` documents | Warn on an unknown `schema_type`; decide the namespace (eb782f83 F-04) |
| M-04 | Medium | `overwatch.py:466-473`; `orchestrator.py:1189, 1997, 2156, 2637` | Failure exits leave no terminal marker; Overwatch shows `RUNNING` | Observed: P3, code | Write a terminal marker on every non-SHIP exit, or derive status from the run record or the log's `engine end` |
| M-05 | Medium | `overwatch.py:483-489, 703-717`; `orchestrator.py:2627-2634` | FR-02-06 always fires while a prompt is open | Observed: P3 | Match against the task path recorded by the run, not the first line of `task.md` |
| M-06 | Medium | `providers.py:124, 321`; `orchestrator.py:475-505`; `mcp_client.py:53, 101` | No configurable timeout; retries multiply to up to 9 × 600 s; caps cannot interrupt | Observed constants; inferred behaviour | Set explicit SDK timeout and `max_retries`; wrap MCP calls in `asyncio.wait_for` |
| L-01 | Low | `scope.py:38-53, 200-201` | Write tools are recognised by name verbs; several write verbs are missing | Observed: P4; pinned server unaffected | Classify the configured server's tools explicitly, and refuse unclassified tools in the worker phase |
| L-02 | Low | `scope.py:209-212` | A path whose resolution raises is skipped | Observed: P4 (NUL path allowed) | Refuse instead of `continue` |
| L-03 | Low | `orchestrator.py:1644-1647, 1428, 1497, 1623`; `gates.py:171` | Preflight `grep` lacks `--`; subprocesses lack timeouts | Observed: P4 | Add `--` and a timeout to each call |
| L-04 | Low | `orchestrator.py:2341-2349, 2461` | CLI tracks tasks by name, not by location as design §8.4 states | Observed: P4 | Track every file under `ai/workspace/` and apply the task-file rule |
| L-05 | Low | `approve.py:77-85` | Failed commit leaves the file staged; a retry duplicates the entry; the error text can be empty | Observed: P5 | Restore the file on failure; include the hook output |
| L-06 | Low | `stages.py:128` | `HEAD:ai/approvals.yaml` resolves from the repository root | Observed: P5 | Use `HEAD:./ai/approvals.yaml` |
| L-07 | Low | `overwatch.py:52-53, 403` | Result documents scanned twice | Observed: P3 | Exclude `test/result/` from the `test` scan, or deduplicate by path |
| L-08 | Low | `overwatch.py:405` | `closed` matched against absolute path parts | Observed: P3 | Test the parts relative to the workspace |
| L-09 | Low | `orchestrator.py:2504-2609` | `engine end rc=N` not logged on early returns after logging starts | Observed: code | Start the `try` immediately after `setup_logging` |
| L-10 | Low | `orchestrator.py:608-611`; `overwatch.py:890, 1071`; `approve.py:77` | Non-atomic writes of files read concurrently | Inferred, medium | Temporary file and `os.replace` |
| L-11 | Low | `manifest.py:188`; `linter.py:250, 289`; `protocol_checker.py:86, 164` | Unhashable or non-string values raise `TypeError` | Observed: code | Type-check before membership tests |
| L-12 | Low | `gates.py:157-172`; `orchestrator.py:1428, 1497` | `py_compile` writes `__pycache__` outside the write scope; the syntax gate compiles paths outside the project | Inferred, high | Compile in memory (`compile()`), or set `PYTHONPYCACHEPREFIX` to the state directory; limit to project paths |
| L-13 | Low | `mcp_client.py:56-64` | Tool-name collisions overwrite silently; connection failures only print | Observed: code | Warn on collision; log failures; refuse a run with no tools |
| L-14 | Low | `orchestrator.py:533-540` | Audit archive overwrites an earlier archive; uses `os.getcwd()` | Observed: code | Refuse or version an existing target; pass the project root |
| L-15 | Low | `overwatch.py:856` | `# govwatch alerts` heading in generated output | Observed | Rename to Overwatch |
| L-16 | Low | `mcp_client.py:11`; `orchestrator.py:71, 1183, 1321`; `protocol_checker.py:153`; `providers.py:535`; `gates.py:251`; `stages.py:296` | Dead code, stale docstrings, 11 mypy errors | Observed: ruff, mypy | Remove; correct the `stages.py:296` type |
| L-17 | Low | `linter.py:37-39`; `scope.py:111`; `stages.py:178, 201`; `orchestrator.py:949, 975, 1577`; `overwatch.py:48-68, 222, 1240` | Duplicated parsing and layout logic across engine and webui | Observed | Consolidate in `ai/core/` when that package is opened |
| L-18 | Low | `orchestrator.py:55, 533, 1078-1554, 1878-2306, 2612` | Very large functions; project root implied by the working directory | Observed | Split `run_phase`/`run_loop`; pass the project root explicitly |
| L-19 | Low | `providers.py:170, 201, 338, 376` | Provider method names and returns differ from design §4.1 | Observed | Amend the design |

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Prior-Finding Re-verification

Status is against the code at `24b2dfc`. "Deferred" means the item is open in `dev/task.md` and is not reported again as new.

| Prior finding | Subject | Status | Evidence |
|---|---|---|---|
| audit-14e05e35 H-01 | Worker forges the verdict | Resolved | Verdict from the final message only (`orchestrator.py:2158-2168`); signal files protected (`scope.py:130-140, 217-223`) |
| audit-14e05e35 H-02 | Approvals not bound to content | Resolved | Blob hashes recorded (`approve.py:55, 64-66`) and compared (`stages.py:142-159, 398-403`) |
| audit-14e05e35 H-03 | Reviewer executes write tools | Resolved | `orchestrator.py:1066-1075, 1297` |
| audit-14e05e35 M-01 | Scope fail-open for unknown path keys | Resolved | `scope.py:202-206`. New residuals L-01, L-02 |
| audit-14e05e35 M-02 | Non-FAIL gates do not block | Resolved | UNCHECKED blocks (`orchestrator.py:2104-2117`); SKIPPED listed (`:2387`) |
| audit-14e05e35 M-03 | Terminology migration | Resolved in scope | No retired role term; L-15 is govwatch only |
| audit-14e05e35 M-04 | Scan writes the git index | Resolved | `stages.py:73-75` |
| audit-14e05e35 M-05 | Keys inherited by gates | Resolved | `orchestrator.py:2325-2326`; `gates.py:255-256` |
| audit-14e05e35 L-01 | Symlinked task untracked | Resolved | `stages.py:327-329` |
| audit-14e05e35 L-02 | Scope uses `abspath` | Resolved | `scope.py:143-145` |
| audit-14e05e35 L-03 | `writable_paths` unvalidated | Resolved | `manifest.py:140-143` |
| audit-14e05e35 L-06 | Legacy `--model` precedence | Resolved (documented) | `guide-engine-operations.md:129` states the implemented order (`providers.py:531-533`) |
| audit-14e05e35 L-08 | Configuration validation gaps | Still present — deferred | `orchestrator.py:2410, 2477`; `providers.py:486` |
| audit-14e05e35 L-09 | 400/401/403 retried | Still present — deferred | `orchestrator.py:475-505`; `providers.py:367-374` |
| audit-14e05e35 L-11 | Completed status in active folder | Still present — deferred | `stages.py:257-264` |
| audit-14e05e35 L-12 | No return stage in worker mode | Resolved | `orchestrator.py:2388-2389` |
| audit-14e05e35 L-13 | Declared deliverables not in block | Resolved | `orchestrator.py:1860-1868` |
| audit-14e05e35 L-14 | `accept` before a run; unquoted UUIDs | Partly resolved | Unquoted UUIDs skipped (`stages.py:112-113`); `accept` before a run deferred |
| audit-14e05e35 L-04, L-05, L-07, L-10, L-15, L-16 | Documents, `bin/`, reports | Not applicable | Outside this scope |
| 14e05e35 follow-up F-01 | Gate supplies the verdict | Resolved | `review-result.txt` not read (`orchestrator.py:2158-2161`) |
| F-02 | Task file not bound to approval | Resolved | `stages.py:340-362` |
| F-03 | Blob map keyed by basename | Resolved | `stages.py:137` |
| F-04 | Directory tools reach signal files | Resolved | `scope.py:217-223` |
| F-05 | Case-sensitive protection | Resolved | `scope.py:140, 219` |
| F-06 | Document corrections | Not applicable | Documents |
| F2-01 | Name ending in a newline | Resolved | `fullmatch` at `stages.py:205, 354` |
| F2-02 | Work item from unresolved name | Resolved | `stages.py:357-361` |
| F2-03 | Gate writes `.complete` | Resolved | Clear after gates includes `.complete` (`orchestrator.py:2091-2092`) |
| F2-04 | Gate-written feedback survives | Resolved | `orchestrator.py:2091, 2175-2183` |
| F3-01 | Gate state survives an UNCHECKED gate | Resolved | Clear precedes the UNCHECKED return (`orchestrator.py:2091-2117`) |
| F3-02 | Task checked and read separately | Resolved | Read once (`orchestrator.py:2457-2465`); hash compared (`stages.py:407-421`) |
| F4-01 | Non-regular state entries survive | Resolved | `orchestrator.py:633, 824-838` |
| F4-02 | Tracked task without bytes | Resolved | `stages.py:378-379` |
| F5-01 | Non-regular prompt path classified untracked | Still present — deferred | `stages.py:325`; `orchestrator.py:2458` |
| Follow-up 5 §6.0 notes 1, 3 | `log.error` follows the `BLOCKED.md` write; test gaps | Still present — deferred | `orchestrator.py:1942-1945, 2094-2097` |
| audit-7d953510 M-01 | Keychain readable by gate code | Still present — accepted | Design DI-06; no source change by decision |
| audit-7d953510 L-01 | `__context__` holds raw output | Resolved | `providers.py:416-431` raises after the `try` |
| audit-7d953510 L-02 | "Login Keychain" wording | Resolved | `providers.py:405-406` |
| audit-7d953510 L-03 | Keychain test gaps | Resolved | `test_keychain_t16_*`, T17, T18 in `tests/engine/test_providers.py` |
| audit-5bcd46ad L-09 | Two write classifications | Resolved | `mcp_client.py:23` imports `scope.is_readonly_tool` |
| audit-eb782f83 F-04 | Two `schema_type` namespaces | Still present — deferred (realised as M-03) | 21 closed `dev/` documents use the new scheme and are skipped by both checkers (M-03); retirement deferred |

Totals: 41 rows, where one row groups six findings outside this scope. 31 resolved, 7 still present (6 deferred, 1 accepted), 1 partly resolved, 2 rows not applicable.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Test Coverage Gaps

Observed from `pytest --collect-only` (332 items) and a search of `tests/` for each public name. No tests were written.

| Area | Untested public behaviour |
|---|---|
| `linter.py` | The whole module: naming, structure, YAML, coupling, link checks and the exit code |
| `protocol_checker.py` | The whole module: the six checks and the exit code |
| `parser.py` | Direct tests of format 1 with several blocks, format 2 sanitising, format 3 (Cohere) and non-object arguments (M-01). Covered only indirectly through one provider test |
| `gates.py` | `syntax_check`; `pytest_targets`, including the flat-layout fallback; `gate_status` on malformed blocks |
| `orchestrator.py` budget | `estimate_tokens` with tool calls and tools (M-02); `check_context_budget`; the abort path in `run_phase`; `write_context_report` |
| `orchestrator.py` loop | Syntax FAIL with reviewer SHIP (OQ-01); `--duration` exit code 2 and `.timeout`; max-iterations continuation; `_truncate_tool_result`; `run_preflight_check`; `extract_reasoning`; `format_tool_signatures`; `_strip_verdict` |
| `orchestrator.py` audit run | `_parse_audit_items`, the scope lock, the SHIP coverage override, `_archive_audit_artifacts`. Only the `create` overwrite guard is tested |
| `orchestrator.py` startup | `_substitute_project_root`; strict tactical brief; the readiness BLOCKED; `engine end` on early exits (L-09) |
| `mcp_client.py` | `connect` failure handling, name collisions, `call_tool` error text. Tests use fakes |
| `providers.py` | `strict_tools` given as a string; SDK timeout and retry configuration (M-06) |
| `stages.py` | A project nested in a larger repository (L-06); `main` output |
| `approve.py` | Commit failure path (L-05) |
| `overwatch.py` | `Scanner`, `PhaseInference`, every `ComplianceEngine` rule (FR-02-01 to FR-02-12), `_read_engine_state`, `_read_budget`, `AlertWriter.payload`. The 19 tests cover rendering, escaping and writing only |

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Positive Findings

- No `shell=True`, `eval`, `exec`, `pickle` or unsafe YAML load in scope. Every subprocess takes a list argv, and every YAML read uses `safe_load` (12 call sites).
- Provider keys are well contained:
  - The log records only the source label.
  - Keychain errors carry no output and no exception context.
  - MCP servers receive a fixed environment subset.
  - Gate processes have the configured key variables removed.
- The verdict path fails safe: anything not positively identified as SHIP is REVISE (`orchestrator.py:319-364`). The verdict comes only from the reviewer's final message.
- Approvals are bound to content by git blob hash and read from `HEAD`. The scan uses `--no-optional-locks` and writes nothing.
- The write scope resolves symlinks, folds case for signal files, refuses directory targets that hold a signal file, and refuses write calls without a recognised path.
- Manifest validation names the file and field for each structural error and runs before any model call.
- Overwatch escapes every interpolated value and the embedded JSON, writes only its two permitted files, and swallows per-document errors as warnings.
- The test suite is hermetic and fast: 331 tests in about 12 s with no network. The edge-case tests encode prior audit scenarios (E-1b to E-3e) as regressions.
- Prior remediation was thorough: every critical, high and medium finding of audit-14e05e35 and its follow-ups is resolved in the code.

[Return to Table of Contents](<#table of contents>)

---

## 10.0 Recommended Remediation Order

1. **Loop robustness:** M-01, M-02, M-06, L-03, L-09. These affect unattended runs and the reliability of BLOCKED signalling.
2. **Status accuracy:** M-04 and M-05, with L-07, L-08 and L-15. The operator relies on these when deciding whether a run needs attention.
3. **Governance checkers:** M-03 and L-11, together with the deferred `schema_type` decision (eb782f83 F-04), and the missing `linter.py`/`protocol_checker.py` tests.
4. **Approval and tracking edge cases:** L-04, L-05, L-06.
5. **Scope hardening:** L-01, L-02, L-12.
6. **Hygiene and structure:** L-10, L-13, L-14, L-16, L-17, L-18, L-19. L-17 and L-18 fit naturally with opening `ai/core/`.
7. **Tests:** the §8.0 gaps, starting with the Overwatch compliance rules and the audit-run gates.

[Return to Table of Contents](<#table of contents>)

---

## 11.0 Open Questions for the Operator

| ID | Question | Bearing |
|---|---|---|
| OQ-01 | FR-03-02 requires every applicable gate to pass and FR-03-04 makes syntax a declared command gate. Design §6.0 keeps syntax built in with "results unchanged", and in the code a syntax FAIL is advisory: it does not override SHIP (`orchestrator.py:2243-2266`). Which document is authoritative? | Syntax gate semantics; FR-03-02, FR-03-04 |
| OQ-02 | The audit request and `overwatch.py:828` cite CON-07 as Overwatch's read-only constraint. In requirements-0c6aedee, CON-07 is document authorship, read-only is CON-01, and NFR-01 says no write capability exists, while design §3.1 and §11.0 permit two write targets. Is the design clarification authoritative, and should the citation and NFR-01 be corrected? | Overwatch compliance basis |
| OQ-03 | requirements-1c1f4ef6 still states FR-AEL-013 (corrective user message), NFR-AEL-001 (no subprocess beyond MCP) and NFR-AEL-005 (no optional dependency), and design-ael §10.0 lists four packages. The code departs from each, with documented reasons. Should the baseline be amended or marked superseded by requirements-14e05e35? | Baseline currency |
| OQ-04 | Design §7.0 lists "the run type's own paths" as allowed write targets. No such category exists in `scope.py`; the audit report lives in the state directory, which is already writable. Remove the phrase, or implement it? | FR-05-01 wording |

[Return to Table of Contents](<#table of contents>)

---

## 12.0 T08 Record

```yaml
audit_info:
  id: "audit-caab2052"
  title: "Static code audit — ai/engine/src and ai/webui/src"
  date: "2026-10-27"
  mode: "strategic"
  status: "complete"
  auditor: "planner (Claude Code cloud session; read-only static audit)"

scope:
  target: "ai/engine/src/ (11 modules), ai/webui/src/overwatch.py at 24b2dfc"
  criteria:
    - "correctness, security, design and requirements compliance, architecture, robustness, maintainability, test coverage"
    - "re-verification of prior findings in dev/audit/closed/"
  exclusions:
    - "bin/, docs/, dev/ content, governance documents, downstream projects"
    - "runtime and live-model behaviour"
    - "ai/engine/mcp/, recipes and tests read as context only"

findings:
  critical: []
  high: []
  medium:
    - location: "orchestrator.py:1302, 1338; scope.py:64, 70; providers.py:150; parser.py:93, 96, 110"
      description: "M-01. Non-object tool-call arguments raise AttributeError in run_phase."
    - location: "orchestrator.py:720-728, 1179"
      description: "M-02. Budget estimate omits tool-call arguments and the tool schema."
    - location: "linter.py:237-262, 378; protocol_checker.py:132"
      description: "M-03. Unknown schema_type documents skipped without warning."
    - location: "overwatch.py:466-473; orchestrator.py:1189, 1997, 2156, 2637"
      description: "M-04. Failure exits leave no terminal marker; Overwatch shows RUNNING."
    - location: "overwatch.py:483-489, 703-717; orchestrator.py:2627-2634"
      description: "M-05. FR-02-06 always fires while a prompt is open."
    - location: "providers.py:124, 321; orchestrator.py:475-505; mcp_client.py:53, 101"
      description: "M-06. No configurable timeouts; retries multiply; caps cannot interrupt."
  low:
    - location: "scope.py:38-53, 200-201"
      description: "L-01. Write tools recognised by name verbs only."
    - location: "scope.py:209-212"
      description: "L-02. Unresolvable path skipped."
    - location: "orchestrator.py:1644-1647, 1428, 1497, 1623; gates.py:171"
      description: "L-03. Preflight grep lacks '--'; subprocesses lack timeouts."
    - location: "orchestrator.py:2341-2349, 2461"
      description: "L-04. CLI tracks tasks by name, not location."
    - location: "approve.py:77-85"
      description: "L-05. Failed commit leaves staged file; retry duplicates entry."
    - location: "stages.py:128"
      description: "L-06. Approvals unreadable in a nested project."
    - location: "overwatch.py:52-53, 403"
      description: "L-07. Result documents listed twice."
    - location: "overwatch.py:405"
      description: "L-08. Ancestor named closed hides all documents."
    - location: "orchestrator.py:2504-2609"
      description: "L-09. engine end not logged on some exits."
    - location: "orchestrator.py:608-611; overwatch.py:890, 1071; approve.py:77"
      description: "L-10. Non-atomic writes."
    - location: "manifest.py:188; linter.py:250, 289; protocol_checker.py:86, 164"
      description: "L-11. TypeError on unhashable or non-string values."
    - location: "gates.py:157-172; orchestrator.py:1428, 1497"
      description: "L-12. py_compile writes outside write scope."
    - location: "mcp_client.py:56-64"
      description: "L-13. Tool collisions and connection failures unreported."
    - location: "orchestrator.py:533-540"
      description: "L-14. Audit archive overwrites silently."
    - location: "overwatch.py:856"
      description: "L-15. govwatch heading in output."
    - location: "mcp_client.py:11; orchestrator.py:71, 1183, 1321; protocol_checker.py:153; providers.py:535; gates.py:251; stages.py:296"
      description: "L-16. Dead code, stale docstrings, mypy errors."
    - location: "linter.py:37-39; scope.py:111; stages.py:178, 201; orchestrator.py:949, 975, 1577; overwatch.py:48-68, 222, 1240"
      description: "L-17. Duplicated parsing and layout logic (ai/core candidates)."
    - location: "orchestrator.py:55, 533, 1078-1554, 1878-2306, 2612"
      description: "L-18. Large functions; implicit working directory."
    - location: "providers.py:170, 201, 338, 376"
      description: "L-19. Provider interface drift from design §4.1."

metrics:
  items_audited: 12  # files; plus 70 requirement, constraint and design items in §4.0
  findings_total: 25
  findings_by_severity:
    critical: 0
    high: 0
    medium: 6
    low: 19

recommendations:
  - "Remediate in the order of §10.0; raise T06/T07/T03 triples at the operator's discretion."
  - "Decide OQ-01 to OQ-04."

traceability:
  design_refs:
    - "dev/design/design-14e05e35-engine-generalisation.md"
    - "dev/design/design-ael-orchestrator.md"
    - "dev/design/design-project-overwatch.md"
  issue_refs: []
  related_audits:
    - audit_ref: "audit-14e05e35"
      relationship: "related"  # prior findings re-verified (§7.0)
    - audit_ref: "audit-7d953510"
      relationship: "related"  # prior findings re-verified (§7.0)
    - audit_ref: "audit-5bcd46ad"
      relationship: "related"  # L-09 re-verified (§7.0)
    - audit_ref: "audit-eb782f83"
      relationship: "related"  # F-04 schema_type namespace

notes: "331 passed, 1 skipped (root) on Linux, Python 3.13.17. Probes and tools ran from the scratchpad; no tracked file other than this report changed."

version_history:
  - version: "1.0"
    date: "2026-10-27"
    changes:
      - "Initial static code audit"
  - version: "1.1"
    date: "2026-10-29"
    changes:
      - "Planner review corrections; closure recommendation and operator decisions added"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t08_audit"
```

[Return to Table of Contents](<#table of contents>)

---

## 13.0 Closure Recommendation

- No critical or high findings. P02.8.1 therefore does not block closure on findings alone.
- Closure requires a recorded decision for each medium finding (§14.0) and human approval.
- Findings remediated by a source change require a follow-up audit before closure (P02.8.2).
- OQ-01 to OQ-04 should be decided before closure. Their answers decide whether the Conflict and Deviates rows in §4.0 are resolved in code or in documents.

[Return to Table of Contents](<#table of contents>)

---

## 14.0 Operator Decisions

Recorded by the planner on 2026-10-29 on the operator's decision.

| Finding | Decision | Disposition |
|---|---|---|
| M-01, M-02, M-06, L-03, L-09 | Remediate | First triple, together with audit-14e05e35 L-09 (HTTP 400/401/403 not retried). M-01: a non-object argument value gets a tool error reply, from one check in `run_phase`. M-06: configurable timeouts, default 300 s per model call and 120 s per MCP call; SDK retries 0, engine retry loop retained. Follow-up audit required (P02.8.2) |
| M-03, M-04, M-05; L-01, L-02, L-04 to L-08, L-10 to L-19 | Not yet decided | Registered in `dev/task.md` by §10.0 group |
| OQ-01 to OQ-04 | Open | Registered in `dev/task.md` |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-10-27 | Initial static code audit of ai/engine/src and ai/webui/src |
| 1.1 | 2026-10-29 | Planner review corrections: M-03 document count 23 → 21 (two matches were narrative text); eb782f83 F-04 row relabelled deferred; register and T08 locations aligned (M-01, M-05, L-03, L-17); related_audits set to related and audit-5bcd46ad added; severity line in §6.0; §13.0 Closure Recommendation and §14.0 Operator Decisions added |

---

Copyright (c) 2026 William Watson. MIT License.
