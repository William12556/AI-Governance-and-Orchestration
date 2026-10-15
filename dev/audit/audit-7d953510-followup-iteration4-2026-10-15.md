Created: 2026 October 15

# Strategic Follow-up Audit — Provider API Key from the macOS Keychain (7d953510, Iteration 4)

---

## Table of Contents

[1.0 Summary](<#1.0 summary>)
[2.0 Method](<#2.0 method>)
[3.0 Refused Runs Write No State (FR-08-05)](<#3.0 refused runs write no state (fr-08-05)>)
[4.0 Logger State and setup_logging](<#4.0 logger state and setup_logging>)
[5.0 Key Source Record in the Run Log](<#5.0 key source record in the run log>)
[6.0 Key Leakage Analysis (NFR-05)](<#6.0 key leakage analysis (nfr-05)>)
[7.0 Side Effects](<#7.0 side effects>)
[8.0 Regression Check and Test Sensitivity](<#8.0 regression check and test sensitivity>)
[9.0 Scope and Governance Compliance](<#9.0 scope and governance compliance>)
[10.0 Findings](<#10.0 findings>)
[11.0 Positive Findings](<#11.0 positive findings>)
[12.0 T08 Record](<#12.0 t08 record>)
[13.0 Closure Recommendation](<#13.0 closure recommendation>)
[Version History](<#version history>)

---

## 1.0 Summary

- **Subject:** change-7d953510 iteration 4 (FR-I). Source commit `050e5ec` (`ai/engine/src/orchestrator.py`: `_RecordBuffer`, `_resolve_bindings_capturing`, the replay in `main_async`; tests T19 to T21 in `tests/engine/test_providers.py`). Document commits `dffbf0b` (report §10.0, prompt closed) and `664244b` (change and issue records). Audited at `664244b`.
- **Criteria:** change-7d953510 v1.9 (iteration 4), `dev/prompt/closed/prompt-7d953510-keychain-api-key.md` (iteration 4, FR-I, T19 to T21), design-14e05e35 v1.16 §3.0 Keys, requirements-14e05e35 FR-08-05.
- **Previous audits:** `dev/audit/audit-7d953510-strategic-2026-10-14.md`, `dev/audit/audit-7d953510-followup-2026-10-14.md`.
- **Protocol:** P02 Audit, strategic mode (P02.9.1), follow-up audit required by P02.8.2 because iteration 4 changed source code.
- **Independence:** limited. The session that wrote this audit also implemented iteration 4 (`050e5ec`, `dffbf0b`). change-7d953510 assigns this audit to an "independent session". See §2.0 and F-03.
- **Verdict:** FR-I is implemented as specified. Refused runs (configuration error, manifest error, pre-run exit 3) still write no state directory and no log file. The `engine` logger is unchanged after binding resolution on success, on ConfigError and on any other exception. Through `main_async` itself, the `key source` record reaches `engine_*.LOG` before `engine start`, for both an `env:` and a `keychain:` source, and the key value does not reach the file. No new path lets the key reach a log record, an exception message, `__cause__` or `__context__`.
- **New findings:** 0 critical, 0 high, 0 medium, 3 low (F-01 the `main_async` replay is untested; F-02 the T19 and T20 level assertions depend on test order; F-03 the auditor is not independent).
- **Tests:** 330 passed, 1 skipped (root), matching report §10.0. Linter 0 errors and 95 warnings (pre-existing); protocol checker 0 findings.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Method

- **Auditor:** Claude Code cloud session. This session implemented iteration 4 earlier in the same conversation, so it is not independent of the work audited. To offset this, every claim in report §10.0 was checked again against the source and new probes, and §5.0 and §8.0 test the behaviour directly rather than relying on the existing tests. The planner should decide whether this meets the "independent session" owner named in change-7d953510 (F-03).
- **Documents read:** governance P02 (P02.8.2, P02.9.1), the two previous 7d953510 audits, the closed prompt (iteration 4), report §10.0, change-7d953510 v1.9, issue-7d953510, design-14e05e35 v1.16 §3.0 Keys, requirements-14e05e35 FR-08-05.
- **Source reviewed:** `git show 050e5ec`; `orchestrator.py` at `664244b` lines 889-925 (helper and buffer), 927-939 (`setup_logging`), 2405-2512 (`main_async` up to `engine start`), 2735-2758 (`main`); `providers.py` logging calls; `ai/engine/mcp/server.py` run launch.
- **Environment:** Linux, Python 3.13.16, dependencies from `ai/engine/requirements.txt`, run as root. No macOS, Keychain or API key; no live run, no network call. The Keychain was simulated by replacing `providers.subprocess.run` and setting `providers.sys.platform = "darwin"`; `openai.AsyncOpenAI` was replaced by a stub.
- **Probes:** one script in the session scratchpad (not committed), each case in a fresh Python process and a fresh temporary project directory. `main_async` runs were stopped right after the `engine start` line by making `_select_recipe_set` raise. Cases: `env` source run; `keychain` source run; configuration error; manifest error (`locate_manifest` raising `ManifestError`); pre-run exit 3 (`ST.is_tracked_task` → True, `ST.prerun_missing` → one item, tracked prompt path); logger state on success, ConfigError and RuntimeError, then `setup_logging`; a WARNING emitted during resolution (direct call versus helper, success and ConfigError, with `logging.lastResort` redirected to a buffer); a root handler configured with `logging.basicConfig(level=WARNING)`; two `main_async` runs in one process.
- **Mutation tests:** four single-line mutations of `050e5ec` in a temporary git worktree (created and removed): M1 remove the replay loop in `main_async`; M2 remove `logger.setLevel(logging.DEBUG)`; M3 remove `logger.removeHandler(buffer)`; M4 do not restore the saved level. Each was run against the full suite and against T19, T20 and T21 alone.
- **Side effects:** a temporary worktree was created and removed. No tracked file was changed. This report is the only file added.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Refused Runs Write No State (FR-08-05)

The order in `main_async` is unchanged: binding resolution (line 2431), manifest load, gate specs, pre-run check (`return 3` at line 2471), then `archive_prior_logs` (2502) and `setup_logging` (2504). The only change before `setup_logging` is that line 2431 calls `_resolve_bindings_capturing`, which writes nothing to disk.

| Refusal | Probe result | State directory | Log file | `engine` logger afterwards |
|---|---|---|---|---|
| Configuration error (`api_key_env` unset) | rc 1, existing message | not created | none | unchanged |
| Manifest error | rc 1, existing message | not created | none | unchanged |
| Pre-run check (tracked prompt, one missing item) | rc 3, missing item listed | not created | none | unchanged |

`test_main_async_stops_on_configuration_error` is unchanged and passes. Records buffered before a refusal are discarded with the local variable; nothing is written. Criterion 1 is met.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Logger State and setup_logging

- **Code:** `_resolve_bindings_capturing` saves `logger.level`, adds the buffer, sets DEBUG, and in `finally` removes the buffer and restores the level. It does not touch `propagate` or `disabled`. `setup_logging` (lines 927-939) is unchanged and adds its FileHandler only when `logger.handlers` is empty (line 934).
- **Probe:** in a fresh process the `engine` logger is `([], NOTSET, propagate=True)` before the call. It is identical after a successful resolution, after a ConfigError and after a RuntimeError from `build_role_bindings`. A following `setup_logging` attaches its `FileHandler`.
- **ConfigError chaining:** the ConfigError passes through `finally` only; its `__context__` and `__cause__` are `None` in the probe.

Criterion 2 is met.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Key Source Record in the Run Log

Probe of `main_async` itself, stopped after `engine start`:

| Source | Run log, line 1 | Run log, line 2 | Key in file |
|---|---|---|---|
| `api_key_env: AUDIT_KEY` (set to the probe key) | `INFO providers.mistral: key source env:AUDIT_KEY` | `INFO engine start mode=loop worker=mistral:m reviewer=mistral:m ...` | No |
| `api_key_keychain: ai-go-mistral` (simulated `security`) | `INFO providers.mistral: key source keychain:ai-go-mistral` | `INFO engine start ...` | No |

- The record appears once and is written before `engine start`. It is written through the run log formatter with its original time, a few milliseconds before `engine start` (report §10.0 open point 3).
- The two providers share one binding, so one record is emitted (`build_role_bindings` builds each provider once).
- The existing tests do not cover this wiring: T19 to T21 call the helper and `setup_logging` directly, and mutation M1 (no replay in `main_async`) passes the full suite (F-01).

Criterion 3 is met in the source and by probe. The live GTach run that change-7d953510 still requires is the remaining confirmation on macOS.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Key Leakage Analysis (NFR-05)

| Path | Result | Evidence |
|---|---|---|
| Buffered and replayed records | No leak | The buffer holds records of the `engine` logger only. During resolution, `providers.py` emits only `"providers.%s: key source %s"` with the provider name and the label (`env:<VAR>` or `keychain:<service>`) as arguments. T19 checks `msg`, `args` and the formatted message of the captured records; the probe checks the whole log file for both sources |
| Records of other loggers (`openai`, `anthropic`, `httpx`) | Not captured | The buffer is attached to `engine` only, and its level change does not affect these loggers |
| Exception messages and `args` | No change | The helper adds no message; ConfigError text is unchanged from iteration 3 |
| `__cause__` and `__context__` | No change | The helper uses `try/finally` without `except`; a ConfigError passing through has `__context__ is None` and `__cause__ is None` (probe, §4.0). The iteration 3 guarantees in `_keychain_secret` are untouched (`providers.py` unchanged) |
| Root logger propagation | No leak | Records propagated during resolution carry the same label-only message (§7.0 item 2) |
| Environment and subprocesses | No change | The key is not placed in `os.environ`; orchestrator scrubbing is unchanged |

The buffer adds only one place where records are held: `main_async`'s local `_binding_records` list, which keeps label-only records for the life of the run. Criterion 4 is met.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Side Effects

1. **WARNING records and `logging.lastResort`.** Before iteration 4, a WARNING on the `engine` logger during resolution had no handler in the hierarchy and went to stderr through `logging.lastResort`. With the buffer attached, it is buffered instead (probe: direct call prints `probe warning during resolution` to stderr; through the helper stderr is empty and the record is buffered). On success it reaches the run log. **On a ConfigError it is discarded and appears nowhere**, a point report §10.0 open point 4 does not mention. No code path emits such a record today: the only `log.warning` in `providers.py` (line 107) is in `query_omlx_context_window`, reached from `live_context_window`, which is called after bindings are resolved. This is an observation, not a finding. A later change that adds a warning to `make_provider` should print buffered WARNING records on the refusal path, or keep them on stderr.
2. **Temporary DEBUG level and root handlers.** While the level is DEBUG, `engine` records are created at every level and propagate to the root logger (`propagate` is True before `setup_logging`). With a root handler configured by `logging.basicConfig(level=WARNING)`, the probe shows the `key source` INFO line printed through the root handler by the helper but not by a direct call. The orchestrator configures no root handler (none after import, probe), and the line holds no key, so there is no effect in the engine. This is an observation only.
3. **Repeated runs in one process.** `setup_logging` never removes handlers, so a second `main_async` in the same process writes into the first run's log file. This is pre-existing: the second run's state directory is created but holds no log. Iteration 4 adds one effect: in the second run the `engine` logger already has the FileHandler and level DEBUG, so the `key source` record is written live and again by the replay. The probe found 3 `key source` lines and 2 `engine start` lines in the first log. Production runs one `main_async` per process (`main` ends with `os._exit`; engine-mcp starts the orchestrator with `subprocess.Popen`), so only tests can reach this. This is an observation only.
4. **Child loggers.** No `engine.*` child logger exists in `ai/engine/` (`getLogger` calls use `"engine"` only), so the temporary level affects no other logger.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Regression Check and Test Sensitivity

- **Full suite:** `python3 -m pytest tests/engine tests/overwatch -q`: 330 passed, 1 skipped (`tests/overwatch/test_overwatch.py:296`, root ignores directory permissions). This matches the baseline given for this audit and report §10.0. T1 to T18 are unchanged (`050e5ec` only adds lines to the test file).
- **Governance checks:** `linter.py dev` gives 0 errors and 95 warnings, unchanged; the only 7d953510 warning is the closed prompt's missing `metadata.schema_type`, which was there before. `protocol_checker.py dev` gives 0 errors and 0 warnings.
- **Mutation results:**

| Mutation | Full suite | T19 alone | T20 alone | T21 alone |
|---|---|---|---|---|
| M1 no replay in `main_async` | **330 passed** (survives) | passes | passes | passes |
| M2 no `setLevel(DEBUG)` | 2 failed | fails | passes | fails |
| M3 buffer not removed | T19, T20 fail; T21 does not finish (the replay appends to the buffer it is iterating) | fails | fails | does not finish |
| M4 level not restored | **`test_providers.py` 63 passed** (survives) | fails | fails | passes |

- M1 survives because no test runs `main_async` past `setup_logging` (F-01).
- M4 survives in file order because earlier tests in `test_providers.py` call `setup_logging`, which leaves the `engine` logger at DEBUG. The saved level then equals the level M4 leaves behind, so the level assertions in T19 and T20 check nothing in a normal run (F-02). They catch M4 only when run alone.

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Scope and Governance Compliance

- **Source scope:** `050e5ec` touches only `ai/engine/src/orchestrator.py` and `tests/engine/test_providers.py`. `providers.py`, `setup_logging`, `archive_prior_logs` and `propagate` are unchanged, as FR-I requires. `git diff 050e5ec 664244b` touches only the report, the prompt move, the change and the issue.
- **FR-I text:** class name, `records` attribute, function name and signature, buffer level DEBUG, logger level DEBUG, `finally` restoration, the replacement line inside the existing `try/except ConfigError`, and the replay loop placed right after `setup_logging` and before `engine start` all match the prompt literally.
- **Design and requirements:** design-14e05e35 v1.16 §3.0 Keys says that records emitted during resolution are held in memory and written to the run log once it is created, and that a run that stops before then writes no log. The probes in §3.0 and §5.0 confirm both. FR-08-05 holds (§3.0).
- **Workflow:** P03 → P04 → P13 followed. Issue and change are both at iteration 4 (P04.2); issue `resolved` with change `implemented` (P03.7); the prompt is closed by `git mv`; report §10.0 records the starting commit `fc6845f`, the source commit and the test counts. Commits follow Conventional Commits with a descriptive body.
- **Report accuracy:** the counts, governance results, open points 1 to 4 and commit hashes in report §10.0 were checked and are correct. Open point 2 (no `main_async` test) is confirmed and made concrete by M1 (F-01). Open point 4 does not mention that the buffer discards WARNING records on a refused run (§7.0 item 1).

[Return to Table of Contents](<#table of contents>)

---

## 10.0 Findings

### 10.1 Critical

None.

### 10.2 High

None.

### 10.3 Medium

None.

### 10.4 Low

**F-01. No test covers the replay in `main_async`.**
- Location: `ai/engine/src/orchestrator.py:2506-2507`; `tests/engine/test_providers.py:715-753`.
- Description: T19 to T21 test `_resolve_bindings_capturing` and a hand-written replay after `setup_logging`. Deleting the two-line replay in `main_async` (M1) leaves all 330 tests passing, so the defect iteration 4 fixes could come back without any test failing. The behaviour was confirmed only by this audit's probe (§5.0).
- Recommendation: add one test that runs `main_async` with a configuration like T19's, stops it after `engine start` (for example by making `_select_recipe_set` raise), and asserts that `engine_*.LOG` contains the `key source` line before `engine start` and does not contain the key. Isolate the `engine` logger as T21 does. This is a test-only change; under P15.11 it needs a new issue and change, or it can join the next change to these files.

**F-02. The T19 and T20 level assertions depend on test order.**
- Location: `tests/engine/test_providers.py:715-733` (`_engine_logger_state` comparisons).
- Description: earlier tests in the module call `setup_logging`, which sets the `engine` logger to DEBUG. In a normal run, T19 and T20 therefore compare DEBUG with DEBUG, and a helper that never restores the level (M4) passes. The assertion is effective only when the tests run alone.
- Recommendation: before the call, set a known level different from DEBUG with `monkeypatch.setattr(logger, "level", logging.NOTSET)` (restored by monkeypatch), so that restoration is actually checked. Fix it with F-01.

**F-03. The follow-up audit was not done by an independent session.**
- Location: change-7d953510 implementation plan, step "Follow-up audit of iteration 4 (P02.8.2)", owner "independent session".
- Description: this audit was written by the session that implemented `050e5ec` and `dffbf0b`. The method in §2.0 limits the effect: claims were re-checked against source, and behaviour was tested with new probes and mutations. Even so, the auditor's own assumptions could be repeated in the audit.
- Recommendation: the planner either accepts this audit and records the deviation in change-7d953510, or has a separate session repeat checks 3 and 5 (the probes in §5.0 and §7.0 are quick to reproduce). The live GTach run is independent evidence for criterion 3 in any case.

[Return to Table of Contents](<#table of contents>)

---

## 11.0 Positive Findings

- The design choice keeps FR-08-05 intact. Binding resolution still precedes any disk write, and the alternative (moving `setup_logging` earlier) was correctly rejected in change-7d953510.
- The helper is small and exception-safe: `try/finally` restores the logger on every exit path, including exceptions other than ConfigError, and adds no exception context.
- The implementation follows FR-I literally; no unrequested change was made to `setup_logging`, `propagate` or `providers.py`.
- T21 is a real end-to-end check of the log file content, including the absence of the key, and it isolates the `engine` logger correctly with monkeypatch.
- Report §10.0 is accurate, and its open points 2 to 4 anticipate the issues this audit confirms.

[Return to Table of Contents](<#table of contents>)

---

## 12.0 T08 Record

```yaml
audit_info:
  id: "audit-7d953510"
  title: "Strategic follow-up audit — change-7d953510 iteration 4 (050e5ec)"
  date: "2026-10-15"
  mode: "strategic"
  status: "complete"
  auditor: "planner (Claude Code cloud session; not independent — the same session implemented iteration 4, see F-03)"

scope:
  target: "ai/engine/src/orchestrator.py (_RecordBuffer, _resolve_bindings_capturing, main_async replay) and tests/engine/test_providers.py T19 to T21 at 664244b (commit 050e5ec); prompt-7d953510 (closed, iteration 4); report-7d953510 §10.0; change-7d953510 v1.9; design-14e05e35 v1.16 §3.0; requirements-14e05e35 FR-08-05"
  criteria:
    - "refused runs (configuration error, manifest error, pre-run exit 3) write no state directory and no log file (FR-08-05)"
    - "'engine' logger handlers, level and propagate unchanged after binding resolution; setup_logging still attaches its FileHandler"
    - "'key source' record reaches engine_*.LOG before 'engine start', probed through main_async"
    - "key leakage: log records, exception messages, __cause__, __context__"
    - "side effects of the temporary DEBUG level and the buffer; repeated in-process runs"
    - "regression: full suite, linter, protocol checker"
  exclusions:
    - "Live macOS run, Keychain and engine-mcp (no macOS in the audit environment; pending per change-7d953510)"
    - "Iterations 1 to 3 beyond regression (audited in audit-7d953510-strategic-2026-10-14 and audit-7d953510-followup-2026-10-14)"

findings:
  critical: []
  high: []
  medium: []
  low:
    - location: "ai/engine/src/orchestrator.py:2506-2507; tests/engine/test_providers.py:715-753"
      description: "F-01. No test runs main_async past setup_logging; removing the replay loop leaves the full suite passing."
    - location: "tests/engine/test_providers.py:715-733"
      description: "F-02. T19 and T20 compare the logger level DEBUG with DEBUG in a normal run, so a helper that does not restore the level passes."
    - location: "dev/change/change-7d953510-keychain-api-key.md implementation plan (follow-up audit owner)"
      description: "F-03. The follow-up audit was written by the implementing session, not an independent one."

metrics:
  items_audited: 9  # refusal paths, logger state, main_async run log (2 sources), leakage, side effects (4 counted as one), test suite, mutation sensitivity, scope, report §10.0
  findings_total: 3
  findings_by_severity:
    critical: 0
    high: 0
    medium: 0
    low: 3

recommendations:
  - "Accept FR-I as implemented; criteria 1 to 4 are met in source and by probe."
  - "Add a main_async-level run log test and make T19/T20 start from a level other than DEBUG (F-01, F-02); test-only, under a new issue and change or with the next change to these files."
  - "Decide on F-03: accept with a recorded deviation, or have a separate session repeat the §5.0 and §7.0 probes."
  - "Complete the GTach engine-mcp run showing 'providers.mistral: key source keychain:ai-go-mistral' before 'engine start' before change-7d953510 moves to verified."

traceability:
  design_refs:
    - "dev/design/design-14e05e35-engine-generalisation.md v1.16 §3.0 Keys"
    - "dev/requirements/requirements-14e05e35-engine-generalisation.md FR-08-05, NFR-05"
  issue_refs: []
  related_audits:
    - audit_ref: "audit-7d953510"
      relationship: "follow_up"  # dev/audit/audit-7d953510-strategic-2026-10-14.md; dev/audit/audit-7d953510-followup-2026-10-14.md

notes: "330 passed, 1 skipped (root) on Linux, Python 3.13.16. main_async probed in fresh processes and stopped after 'engine start'; Keychain simulated; no live run or network call. Mutations M1 to M4 run in a temporary worktree, created and removed; no tracked file changed. WARNING redirection from lastResort, root-handler propagation and duplicate lines on in-process reruns are observations, not findings (§7.0)."

version_history:
  - version: "1.0"
    date: "2026-10-15"
    changes:
      - "Initial strategic follow-up audit of change-7d953510 iteration 4"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t08_audit"
```

[Return to Table of Contents](<#table of contents>)

---

## 13.0 Closure Recommendation

- P02.8.2 follow-up audit of iteration 4: done, subject to the planner's decision on F-03.
- FR-I: implemented and confirmed by probe through `main_async`; FR-08-05 holds; no new key-leakage path.
- F-01 and F-02 are test-quality gaps. They do not block the change, but F-01 should be fixed before the issue is closed, because without it the fixed defect can come back without any test failing.
- change-7d953510 should stay `implemented` until the GTach engine-mcp run shows `providers.mistral: key source keychain:ai-go-mistral` before `engine start`.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-10-15 | Initial strategic follow-up audit of change-7d953510 iteration 4 |

---

Copyright (c) 2026 William Watson. MIT License.
