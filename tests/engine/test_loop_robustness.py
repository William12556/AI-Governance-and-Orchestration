"""Tests for engine loop robustness (change-711a57d5, prompt-711a57d5 T1 to T16;
change-5e8aea4f, prompt-5e8aea4f T17 to T28; change-b8c75bac, prompt-b8c75bac
B1 to B4)."""

import argparse
import asyncio
import logging
import subprocess
import sys
import types
from datetime import timedelta

import pytest
import yaml

import gates as G
import manifest as M
import mcp_client as MC
import providers as P


class _Records(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(record.getMessage())


@pytest.fixture
def rec_log():
    log = logging.getLogger("engine-test-711a57d5")
    log.setLevel(logging.DEBUG)
    rec = _Records()
    log.addHandler(rec)
    yield log, rec
    log.removeHandler(rec)


def _tool(name):
    return {"type": "function", "function": {"name": name, "description": "", "parameters": {"type": "object"}}}


class _Script:
    """Fake provider returning scripted completions; records the messages it sees."""

    def __init__(self, steps):
        self.steps = list(steps)
        self.seen = []

    async def complete(self, model, messages, tools, max_tokens=None):
        self.seen.append([dict(m) for m in messages])
        return self.steps.pop(0)


class _MCP:
    """Fake MCP client offering the named tools and recording dispatched calls."""

    def __init__(self, offered):
        self.offered = offered
        self.calls = []

    def get_openai_tools(self, readonly=False):
        return [_tool(n) for n in self.offered]

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return "ok"


def _call(call_id, name, arguments):
    return P.Completion(text="", tool_calls=[P.ToolCall(call_id, name, arguments)])


# --- FR-A (audit-caab2052 M-01): malformed tool arguments --------------------------------

def test_t1_malformed_arguments_become_tool_errors(orch, project, rec_log):
    log, rec = rec_log
    script = _Script([_call("aaaaaaaa1", "write_file", [1, 2]),
                      _call("aaaaaaaa2", "read_file", '"{\\"path\\": \\"a\\"}"'),
                      P.Completion(text="done")])
    mcp = _MCP(["read_file", "write_file"])
    rc, _, _ = asyncio.run(orch.run_phase(
        script, mcp, "m", {"instructions": "{{TOOLS}}"}, "task", 5,
        str(project / "ai" / "state"), log, phase_label="WORKER", project_root=str(project)))
    assert rc == 0
    assert mcp.calls == []
    tool_msgs = [m for m in script.seen[-1] if m["role"] == "tool"]
    assert [m["tool_call_id"] for m in tool_msgs] == ["aaaaaaaa1", "aaaaaaaa2"]
    assert all(m["content"].startswith("Error: arguments for tool") for m in tool_msgs)
    assert "got list" in tool_msgs[0]["content"] and "got str" in tool_msgs[1]["content"]
    assert "malformed tool arguments tool=write_file type=list" in rec.lines


def test_t2_repeated_malformed_call_blocks_through_f27(orch, project, rec_log):
    log, _ = rec_log
    state = project / "ai" / "state"
    script = _Script([_call(f"aaaaaaaa{i}", "write_file", [1, 2]) for i in range(1, 5)])
    mcp = _MCP(["write_file"])
    # The MCP error threshold is raised above 4 so the F27 path is the one observed;
    # with the default threshold of 3 the MCP error path blocks at the third call.
    rc, _, _ = asyncio.run(orch.run_phase(
        script, mcp, "m", {"instructions": "{{TOOLS}}"}, "task", 10,
        str(state), log, phase_label="WORKER", project_root=str(project),
        mcp_error_threshold=10))
    assert rc == 1
    assert mcp.calls == []
    assert "Repeated identical failed call: 4 attempts." in (state / "BLOCKED.md").read_text()


# --- FR-B (audit-caab2052 M-02): token estimate --------------------------------------------

def test_t3_estimate_counts_tool_call_arguments(orch):
    msg = {"role": "assistant", "content": "",
           "tool_calls": [{"id": "x", "type": "function",
                           "function": {"name": "write_file", "arguments": "a" * 40_000}}]}
    assert orch.estimate_tokens([msg]) >= 10_000


def test_t3_estimate_ignores_malformed_tool_call_entries(orch):
    msg = {"role": "assistant", "content": "abcd",
           "tool_calls": [None, {"function": None}, {"function": {"arguments": {"a": 1}}}]}
    assert orch.estimate_tokens([msg]) == 1


def test_t4_budget_check_estimates_with_phase_tools(orch, project, rec_log, monkeypatch):
    log, _ = rec_log
    seen = []
    real = orch.estimate_tokens

    def spy(messages, tools=None):
        seen.append(tools)
        return real(messages, tools)

    monkeypatch.setattr(orch, "estimate_tokens", spy)
    mcp = _MCP(["read_file", "write_file"])
    asyncio.run(orch.run_phase(
        _Script([P.Completion(text="done")]), mcp, "m", {"instructions": ""}, "task", 2,
        str(project / "ai" / "state"), log, phase_label="WORKER", project_root=str(project),
        context_window=100_000))
    assert seen and seen[0] == mcp.get_openai_tools()


# --- FR-C (audit-caab2052 M-06): model call timeout ------------------------------------------

@pytest.fixture
def fake_sdks(monkeypatch):
    """Replace openai.AsyncOpenAI and anthropic.AsyncAnthropic with capturing fakes."""
    import openai

    captured = {}

    class FakeAsyncOpenAI:
        def __init__(self, **kw):
            captured["openai"] = kw

    class FakeAnthropic:
        def __init__(self, **kw):
            captured["anthropic"] = kw

    monkeypatch.setattr(openai, "AsyncOpenAI", FakeAsyncOpenAI)
    monkeypatch.setitem(sys.modules, "anthropic", types.SimpleNamespace(AsyncAnthropic=FakeAnthropic))
    monkeypatch.setenv("T711_KEY", "fake-key")
    return captured


_OPENAI_CFG = {"kind": "openai_compatible", "base_url": "https://api.example.invalid/v1",
               "api_key_env": "T711_KEY"}
_ANTHROPIC_CFG = {"kind": "anthropic", "api_key_env": "T711_KEY"}


@pytest.mark.parametrize("sdk,pcfg", [("openai", _OPENAI_CFG), ("anthropic", _ANTHROPIC_CFG)])
def test_t5_sdk_clients_get_timeout_and_no_retries(fake_sdks, sdk, pcfg):
    P.make_provider("p", dict(pcfg))
    assert fake_sdks[sdk]["timeout"] == 300.0 and fake_sdks[sdk]["max_retries"] == 0
    P.make_provider("p", dict(pcfg, request_timeout_seconds=45))
    assert fake_sdks[sdk]["timeout"] == 45 and fake_sdks[sdk]["max_retries"] == 0


@pytest.mark.parametrize("value", [0, -1, "x", True])
@pytest.mark.parametrize("pcfg", [
    # no key source: the timeout is validated before the key lookup
    {"kind": "openai_compatible", "base_url": "https://api.example.invalid/v1"},
    {"kind": "anthropic"},
])
def test_t6_invalid_request_timeout_is_a_config_error(fake_sdks, pcfg, value):
    with pytest.raises(P.ConfigError) as ei:
        P.make_provider("remote", dict(pcfg, request_timeout_seconds=value))
    assert "providers.remote.request_timeout_seconds: must be a positive number" in str(ei.value)


def test_t7_legacy_omlx_block_carries_request_timeout(fake_sdks):
    config = {"omlx": {"base_url": "http://127.0.0.1:8000/v1", "api_key": "local",
                       "default_model": "devstral", "request_timeout_seconds": 90}}
    P.build_role_bindings(config, argparse.Namespace(model=None, worker_model=None, reviewer_model=None))
    assert fake_sdks["openai"]["timeout"] == 90 and fake_sdks["openai"]["max_retries"] == 0


# --- FR-D (audit-caab2052 M-06): MCP request timeout -----------------------------------------

def _fake_mcp_transport(monkeypatch):
    seen = {}

    class _CM:
        def __init__(self, value):
            self.value = value

        async def __aenter__(self):
            return self.value

        async def __aexit__(self, *exc):
            return False

    class FakeSession:
        async def initialize(self):
            pass

        async def list_tools(self):
            return types.SimpleNamespace(tools=[])

    def fake_session(read, write, **kw):
        seen.update(kw)
        return _CM(FakeSession())

    monkeypatch.setattr(MC, "stdio_client", lambda params: _CM(("r", "w")))
    monkeypatch.setattr(MC, "ClientSession", fake_session)
    return seen


@pytest.mark.parametrize("kwargs,expected", [({}, 120), ({"timeout_seconds": 7}, 7)])
def test_t8_session_built_with_read_timeout(monkeypatch, kwargs, expected):
    seen = _fake_mcp_transport(monkeypatch)
    client = MC.MCPClient({"fs": {"command": "true"}}, **kwargs)

    async def run():
        await client.connect()
        await client.close()

    asyncio.run(run())
    assert seen["read_timeout_seconds"] == timedelta(seconds=expected)


def test_t9_call_tool_timeout_is_a_tool_error():
    class TimingOut:
        async def call_tool(self, name, arguments):
            raise Exception("Timed out")

    client = MC.MCPClient({})
    client._tools["read_file"] = {"server": "fs", "description": "", "input_schema": {}}
    client._sessions["fs"] = TimingOut()
    result = asyncio.run(client.call_tool("read_file", {"path": "a"}))
    assert result.startswith("Error calling '")


# --- FR-E (audit-14e05e35 L-09): non-retryable completion errors -------------------------------

class _StatusError(Exception):
    def __init__(self, msg, status_code=None):
        super().__init__(msg)
        if status_code is not None:
            self.status_code = status_code


class _Failing:
    def __init__(self, exc):
        self.exc = exc
        self.calls = 0

    async def complete(self, model, messages, tools, max_tokens=None):
        self.calls += 1
        raise self.exc


def test_t10_client_error_is_not_retried(orch, tmp_path, rec_log):
    log, rec = rec_log
    provider = _Failing(_StatusError("unauthorised", 401))
    with pytest.raises(RuntimeError):
        asyncio.run(orch._completion_with_retry(provider, "m", [], None, log, str(tmp_path),
                                                initial_backoff=0))
    assert provider.calls == 1
    blocked = (tmp_path / "BLOCKED.md").read_text()
    assert "HTTP 401" in blocked and "not retried" in blocked
    assert "completion call failed with HTTP 401 (not retried)" in rec.lines


@pytest.mark.parametrize("exc", [_StatusError("server", 500), _StatusError("plain")])
def test_t11_other_errors_keep_retrying(orch, tmp_path, rec_log, exc):
    log, _ = rec_log
    provider = _Failing(exc)
    with pytest.raises(RuntimeError):
        asyncio.run(orch._completion_with_retry(provider, "m", [], None, log, str(tmp_path),
                                                initial_backoff=0))
    assert provider.calls == orch._COMPLETION_MAX_RETRIES
    assert "after 3 attempts" in (tmp_path / "BLOCKED.md").read_text()


# --- FR-F (audit-caab2052 L-03): preflight grep and subprocess timeouts --------------------------

def _criteria_task(*criteria):
    return "```yaml\n" + yaml.safe_dump({"success_criteria": list(criteria)}) + "```\n"


def test_t12_option_like_pattern_is_not_satisfied(orch, tmp_path, rec_log):
    log, _ = rec_log
    target = tmp_path / "notes.txt"
    target.write_text("nothing relevant here\n")
    summary = orch.run_preflight_check(_criteria_task(f"{target} contains '--version'"), log)
    assert "SATISFIED" not in summary
    assert "REMAINING" in summary


class _RecordingRun:
    def __init__(self):
        self.calls = []

    def __call__(self, argv, **kw):
        self.calls.append((list(argv), kw))
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")


def test_t13_grep_terminator_and_timeouts(orch, project, rec_log, monkeypatch):
    log, _ = rec_log
    (project / "src" / "a.txt").write_text("x\n")
    (project / "src" / "b.py").write_text("x = 1\n")
    fake = _RecordingRun()
    monkeypatch.setattr(subprocess, "run", fake)
    orch.run_preflight_check(_criteria_task("src/a.txt contains '-e'", "src/b.py has no syntax errors"), log)
    state = project / "ai" / "state"
    (state / "work-summary.txt").write_text("src/b.py\n")
    G.syntax_check(str(state), log)

    grep = [(a, k) for a, k in fake.calls if a[0] == "grep"]
    compiles = [(a, k) for a, k in fake.calls if a[1:3] == ["-m", "py_compile"]]
    assert len(grep) == 1 and len(compiles) == 2
    argv, kw = grep[0]
    assert argv[argv.index("-e") - 1] == "--"
    assert kw["timeout"] == 30
    assert all(k["timeout"] == 30 for _, k in compiles)


def test_t14_syntax_gate_reports_timeout(project, rec_log, monkeypatch):
    log, _ = rec_log
    (project / "src" / "slow.py").write_text("x = 1\n")
    state = project / "ai" / "state"
    (state / "work-summary.txt").write_text("src/slow.py\n")

    def timing_out(argv, **kw):
        raise subprocess.TimeoutExpired(argv, kw.get("timeout"))

    monkeypatch.setattr(subprocess, "run", timing_out)
    block, count = G.syntax_check(str(state), log)
    assert count == 1
    assert "src/slow.py: syntax check timed out after 30 s" in block
    assert G.gate_status(block) == "FAIL"


# --- FR-G (audit-caab2052 L-09) and FR-D configuration: main_async ------------------------------

def _legacy_config(project, state_rel, **loop):
    cfg = {"omlx": {"base_url": "http://127.0.0.1:8000/v1", "api_key": "local",
                    "default_model": "devstral"},
           "loop": dict({"state_dir": state_rel, "max_iterations": 1}, **loop)}
    path = project / "config.yaml"
    path.write_text(yaml.safe_dump(cfg))
    return path


def _main_args(config):
    return argparse.Namespace(config=str(config), mode="loop", task="robustness check", model=None,
                              worker_model=None, reviewer_model=None, max_iterations=None,
                              duration=None)


@pytest.fixture
def isolated_engine_logger(monkeypatch):
    """Isolate the 'engine' logger as test_providers.py T21/T22 do."""
    logger = logging.getLogger("engine")
    monkeypatch.setattr(logger, "handlers", [])
    monkeypatch.setattr(logger, "level", logger.level)
    monkeypatch.setattr(logger, "propagate", logger.propagate)
    yield logger
    for handler in list(logger.handlers):
        handler.flush()
        handler.close()


def test_t15_manifest_error_after_setup_logging_logs_engine_end(orch, project, monkeypatch,
                                                                 isolated_engine_logger):
    import openai

    monkeypatch.setattr(openai, "AsyncOpenAI", lambda **kw: object())
    constructed = []
    monkeypatch.setattr(orch, "MCPClient", lambda *a, **kw: constructed.append(a) or None)

    def broken(self, run_type):
        raise M.ManifestError("recipe missing")

    monkeypatch.setattr(M.Manifest, "recipe_paths", broken)
    config = _legacy_config(project, "ai/state/t15")
    assert asyncio.run(orch.main_async(_main_args(config))) == 1
    for handler in list(isolated_engine_logger.handlers):
        handler.flush()
    (log_file,) = (project / "ai" / "state" / "t15").glob("engine_*.LOG")
    lines = log_file.read_text().splitlines()
    assert "engine end rc=1" in lines[-1]
    assert constructed == []


async def _not_ready(self, model, **kw):
    """Readiness stub that fails at once (prompt-5e8aea4f T24)."""
    raise TimeoutError("stubbed readiness")


def _squash(text):
    """Text without whitespace: Rich wraps long console lines (change-b8c75bac)."""
    return "".join(text.split())


@pytest.mark.parametrize("value", [0, -1, "x", True])
def test_t16_invalid_mcp_timeout_stops_before_state(orch, project, monkeypatch, capsys, value,
                                                    isolated_engine_logger):
    import openai

    monkeypatch.setattr(openai, "AsyncOpenAI", lambda **kw: object())
    # T24: a removed validation fails at once instead of after the readiness wait
    monkeypatch.setattr(P.OpenAICompatProvider, "await_ready", _not_ready)
    config = _legacy_config(project, "ai/state/t16", mcp_timeout_seconds=value)
    assert asyncio.run(orch.main_async(_main_args(config))) == 1
    assert not (project / "ai" / "state" / "t16").exists()
    # change-b8c75bac (audit-5e8aea4f F-02): 'configuration error (<config path>)' form
    assert _squash(f"configuration error ({config}): loop.mcp_timeout_seconds: "
                   "must be a positive number") in _squash(capsys.readouterr().out)


# =================================================================================================
# change-5e8aea4f (prompt-5e8aea4f T17 to T28): audit-711a57d5 follow-up findings
# =================================================================================================

class _ResultMCP(_MCP):
    """Fake MCP client returning a fixed result per tool name (default 'ok')."""

    def __init__(self, offered, results=None):
        super().__init__(offered)
        self.results = results or {}

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return self.results.get(name, "ok")


# --- FR-A (audit-711a57d5 F-01): non-string read paths -----------------------------------------

def test_t17_non_string_read_paths_are_ignored(orch, project, rec_log):
    log, _ = rec_log
    state = str(project / "ai" / "state")
    worker = _Script([_call("bbbbbbbb1", "read_file", {"path": ["a"]}),
                      _call("bbbbbbbb2", "read", {"paths": 5}),
                      P.Completion(text="done")])
    mcp = _MCP(["read", "read_file"])
    rc, _, _ = asyncio.run(orch.run_phase(
        worker, mcp, "m", {"instructions": ""}, "task", 5, state, log,
        phase_label="WORKER", project_root=str(project)))
    assert rc == 0
    assert mcp.calls == [("read_file", {"path": ["a"]}), ("read", {"paths": 5})]

    review = _Script([_call("bbbbbbbb3", "read_file", {"path": ["a"]}),
                      _call("bbbbbbbb4", "read_file", {"path": 5}),
                      P.Completion(text="done")])
    mcp = _MCP(["read_file"])
    rc, _, read_paths = asyncio.run(orch.run_phase(
        review, mcp, "m", {"instructions": ""}, "task", 5, state, log,
        phase_label="REVIEW", project_root=str(project)))
    assert rc == 0
    assert mcp.calls == [("read_file", {"path": ["a"]}), ("read_file", {"path": 5})]
    assert all(isinstance(p, str) for p in read_paths)


def test_t17b_edit_pattern_with_non_string_path(orch, project, rec_log):
    log, _ = rec_log
    # A str file_path is added so the pre-dispatch scope check (scope.check, M-01)
    # finds a recognised path and the call reaches the edit-pattern branch with a
    # non-str 'path'; with 'path' alone the call is refused before dispatch.
    args = {"path": ["a.py"], "file_path": "src/a.py"}
    script = _Script([_call("bbbbbbbb5", "edit_file", args), P.Completion(text="done")])
    mcp = _ResultMCP(["edit_file"], {"edit_file": "Error: edits failed to match"})
    rc, _, _ = asyncio.run(orch.run_phase(
        script, mcp, "m", {"instructions": ""}, "task", 5, str(project / "ai" / "state"), log,
        phase_label="WORKER", project_root=str(project)))
    assert rc == 0
    assert mcp.calls == [("edit_file", args)]
    (tool_msg,) = [m for m in script.seen[-1] if m["role"] == "tool"]
    assert "the target file" in tool_msg["content"]


# --- FR-B (audit-711a57d5 F-02): MCP close after a timeout -------------------------------------

def test_t18_close_error_becomes_warning(capsys):
    client = MC.MCPClient({})

    async def failing_aclose():
        raise ExceptionGroup("x", [RuntimeError("late answer")])

    client._stack.aclose = failing_aclose
    client._sessions["fs"] = object()
    asyncio.run(client.close())
    assert "Warning: error while closing MCP connections" in capsys.readouterr().out
    assert client._sessions == {}


def test_t18b_close_propagates_cancellation(capsys):
    """change-b8c75bac (audit-5e8aea4f F-03, N2b): BaseException is not swallowed."""
    client = MC.MCPClient({})

    async def cancelled_aclose():
        raise asyncio.CancelledError()

    client._stack.aclose = cancelled_aclose
    client._sessions["fs"] = object()

    async def run():
        with pytest.raises(asyncio.CancelledError):
            await client.close()

    asyncio.run(run())
    assert "Warning: error while closing MCP connections" not in capsys.readouterr().out
    assert client._sessions == {}


# --- FR-C (audit-711a57d5 F-03): non-finite timeouts -------------------------------------------

@pytest.mark.parametrize("value", [float("nan"), float("inf")])
@pytest.mark.parametrize("pcfg", [
    {"kind": "openai_compatible", "base_url": "https://api.example.invalid/v1"},
    {"kind": "anthropic"},
])
def test_t19_non_finite_request_timeout_is_a_config_error(fake_sdks, pcfg, value):
    with pytest.raises(P.ConfigError) as ei:
        P.make_provider("remote", dict(pcfg, request_timeout_seconds=value))
    assert "providers.remote.request_timeout_seconds: must be a positive number" in str(ei.value)


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_t20_non_finite_mcp_timeout_stops_before_state(orch, project, monkeypatch, capsys, value,
                                                       isolated_engine_logger):
    import openai

    monkeypatch.setattr(openai, "AsyncOpenAI", lambda **kw: object())
    monkeypatch.setattr(P.OpenAICompatProvider, "await_ready", _not_ready)
    config = _legacy_config(project, "ai/state/t20", mcp_timeout_seconds=value)
    assert asyncio.run(orch.main_async(_main_args(config))) == 1
    assert not (project / "ai" / "state" / "t20").exists()
    # change-b8c75bac (audit-5e8aea4f F-02): 'configuration error (<config path>)' form
    assert _squash(f"configuration error ({config}): loop.mcp_timeout_seconds: "
                   "must be a positive number") in _squash(capsys.readouterr().out)


# --- FR-E (audit-711a57d5 F-04): untested behaviours M4, M5, M6, M15 ---------------------------

def _compile_calls(fake):
    return [(a, k) for a, k in fake.calls if a[1:3] == ["-m", "py_compile"]]


def _run_t21(orch, project, log):
    (project / "src" / "w.py").write_text("x = 1\n")
    script = _Script([_call("cccccccc1", "edit_file", {"path": "src/e.py"}),
                      _call("cccccccc2", "write_file", {"path": "src/w.py", "content": "x = 1\n"}),
                      P.Completion(text="done")])
    mcp = _ResultMCP(["edit_file", "write_file"], {"edit_file": "Error: edits failed to match"})
    return asyncio.run(orch.run_phase(
        script, mcp, "m", {"instructions": ""}, "task", 5, str(project / "ai" / "state"), log,
        phase_label="WORKER", project_root=str(project)))


def test_t21_py_compile_calls_are_bounded(orch, project, rec_log, monkeypatch):
    log, _ = rec_log
    fake = _RecordingRun()
    monkeypatch.setattr(subprocess, "run", fake)
    rc, _, _ = _run_t21(orch, project, log)
    assert rc == 0
    compiles = _compile_calls(fake)
    assert [a[3] for a, _ in compiles] == ["src/e.py", "src/w.py"]
    assert all(k["timeout"] == 30 for _, k in compiles)


def test_t21_py_compile_timeout_does_not_stop_phase(orch, project, rec_log, monkeypatch):
    log, _ = rec_log
    calls = []

    def timing_out(argv, **kw):
        calls.append(list(argv))
        raise subprocess.TimeoutExpired(argv, kw.get("timeout"))

    monkeypatch.setattr(subprocess, "run", timing_out)
    rc, _, _ = _run_t21(orch, project, log)
    assert rc == 0
    assert [a[3] for a in calls if a[1:3] == ["-m", "py_compile"]] == ["src/e.py", "src/w.py"]


class _FakeMCPClient:
    """Stand-in for MCPClient recording construction kwargs and awaited closes."""

    instances: list = []

    def __init__(self, servers, **kw):
        self.kwargs = kw
        self.closed = 0
        _FakeMCPClient.instances.append(self)

    async def connect(self):
        pass

    async def close(self):
        self.closed += 1


async def _ready(self, model, **kw):
    pass


def _run_without_task(orch, project, monkeypatch, isolated_engine_logger, state_rel, **loop):
    import openai

    monkeypatch.setattr(openai, "AsyncOpenAI", lambda **kw: object())
    monkeypatch.setattr(P.OpenAICompatProvider, "await_ready", _ready)
    monkeypatch.setattr(P.OpenAICompatProvider, "live_context_window", lambda self, model: None)
    monkeypatch.setattr(_FakeMCPClient, "instances", [])
    monkeypatch.setattr(orch, "MCPClient", _FakeMCPClient)
    config = _legacy_config(project, state_rel, **loop)
    args = _main_args(config)
    args.task = None
    rc = asyncio.run(orch.main_async(args))
    for handler in list(isolated_engine_logger.handlers):
        handler.flush()
    return rc


def test_t22_mcp_client_closed_once_on_early_return(orch, project, monkeypatch,
                                                    isolated_engine_logger):
    rc = _run_without_task(orch, project, monkeypatch, isolated_engine_logger, "ai/state/t22")
    assert rc == 1
    (client,) = _FakeMCPClient.instances
    assert client.closed == 1
    (log_file,) = (project / "ai" / "state" / "t22").glob("engine_*.LOG")
    assert "engine end rc=1" in log_file.read_text().splitlines()[-1]


def test_t23_mcp_client_gets_configured_timeout(orch, project, monkeypatch,
                                                isolated_engine_logger):
    rc = _run_without_task(orch, project, monkeypatch, isolated_engine_logger, "ai/state/t23",
                           mcp_timeout_seconds=7)
    assert rc == 1
    (client,) = _FakeMCPClient.instances
    assert client.kwargs["timeout_seconds"] == 7


# --- FR-D (audit-711a57d5 F-05): key redaction ---------------------------------------------------

FAKE_SECRET = "sk-test-SECRET"


def test_t25_provider_redacts_only_a_secret_key(fake_sdks, monkeypatch):
    monkeypatch.setenv("T5E8_KEY", FAKE_SECRET)
    remote = P.make_provider("remote", {"kind": "openai_compatible",
                                        "base_url": "https://api.example.invalid/v1",
                                        "api_key_env": "T5E8_KEY"})
    assert remote.redact(f"bad key {FAKE_SECRET}!") == f"bad key {P.REDACTED}!"
    assert FAKE_SECRET not in repr(remote)
    local = P.make_provider("omlx", {"kind": "omlx", "base_url": "http://127.0.0.1:8000/v1",
                                     "api_key": "local-test-key"})
    assert local.redact("bad key local-test-key") == "bad key local-test-key"
    # change-b8c75bac (audit-5e8aea4f F-03, N12): kind anthropic with api_key_env
    anth = P.make_provider("anth", {"kind": "anthropic", "api_key_env": "T5E8_KEY"})
    assert isinstance(anth, P.AnthropicProvider)
    assert fake_sdks["anthropic"]["api_key"] == FAKE_SECRET
    assert anth.redact(f"bad key {FAKE_SECRET}!") == f"bad key {P.REDACTED}!"
    assert FAKE_SECRET not in repr(anth)


class _SecretFailing(_Failing):
    """Failing provider whose redact replaces FAKE_SECRET, as a real provider does."""

    def redact(self, text):
        return text.replace(FAKE_SECRET, P.REDACTED)


@pytest.mark.parametrize("exc,blocked_marker", [
    (_StatusError(f"401 invalid key {FAKE_SECRET}", 401), "not retried"),
    (_StatusError(f"connection reset for key {FAKE_SECRET}"), "after 3 attempts"),
])
def test_t26_completion_errors_are_redacted(orch, tmp_path, rec_log, capsys, exc, blocked_marker):
    log, rec = rec_log
    with pytest.raises(RuntimeError) as ei:
        asyncio.run(orch._completion_with_retry(_SecretFailing(exc), "m", [], None, log,
                                                str(tmp_path), initial_backoff=0))
    blocked = (tmp_path / "BLOCKED.md").read_text()
    out = capsys.readouterr().out
    assert blocked_marker in blocked
    assert P.REDACTED in blocked and P.REDACTED in str(ei.value)
    assert any(P.REDACTED in line for line in rec.lines)
    for text in [blocked, str(ei.value), out, *rec.lines]:
        assert FAKE_SECRET not in text


def test_t26_provider_without_redact_still_works(orch, tmp_path, rec_log):
    log, _ = rec_log
    with pytest.raises(RuntimeError) as ei:
        asyncio.run(orch._completion_with_retry(_Failing(_StatusError("plain")), "m", [], None,
                                                log, str(tmp_path), initial_backoff=0))
    assert str(ei.value) == "Completion call failed: plain"


class _ListFails:
    """Fake SDK client whose models.list raises an error containing FAKE_SECRET."""

    def __init__(self):
        self.models = self

    async def list(self):
        raise RuntimeError(f"401 unauthorised: key {FAKE_SECRET}")


class _RetrieveFails:
    """Fake Anthropic client whose models.retrieve raises an error containing FAKE_SECRET
    (change-b8c75bac, audit-5e8aea4f F-03, N5)."""

    def __init__(self):
        self.models = self

    async def retrieve(self, model):
        raise RuntimeError(f"401 unauthorised: key {FAKE_SECRET}")


@pytest.mark.parametrize("make", [
    lambda: P.OpenAICompatProvider(kind="openai_compatible", base_url="https://x.invalid/v1",
                                   client=_ListFails(), secret=FAKE_SECRET),
    lambda: P.AnthropicProvider(base_url="https://x.invalid", client=_ListFails(),
                                secret=FAKE_SECRET),
    # change-b8c75bac: the Anthropic API branch (no base_url)
    lambda: P.AnthropicProvider(client=_RetrieveFails(), secret=FAKE_SECRET),
])
@pytest.mark.parametrize("timeout", [0, 0.05])
def test_t27_await_ready_text_is_redacted(make, timeout):
    echoed = []
    with pytest.raises(TimeoutError) as ei:
        asyncio.run(make().await_ready("m", timeout=timeout, interval=0.01, echo=echoed.append))
    assert P.REDACTED in str(ei.value) and FAKE_SECRET not in str(ei.value)
    if timeout:
        assert echoed
    for line in echoed:
        assert P.REDACTED in line and FAKE_SECRET not in line


def test_t28_resolve_api_key_reports_secret_sources(monkeypatch):
    remote = {"kind": "openai_compatible", "base_url": "https://api.example.invalid/v1"}
    monkeypatch.setenv("T5E8_KEY", FAKE_SECRET)
    env_cfg = dict(remote, api_key_env="T5E8_KEY")
    assert P._resolve_api_key("r", env_cfg, "openai_compatible") == (FAKE_SECRET, True)
    assert P._api_key("r", env_cfg, "openai_compatible") == FAKE_SECRET

    def security(argv, **kw):
        return subprocess.CompletedProcess(argv, 0, FAKE_SECRET + "\n", "")

    monkeypatch.setattr(P.sys, "platform", "darwin")
    monkeypatch.setattr(P.subprocess, "run", security)
    kc_cfg = dict(remote, api_key_keychain="ai-go-test")
    assert P._resolve_api_key("r", kc_cfg, "openai_compatible") == (FAKE_SECRET, True)
    assert P._api_key("r", kc_cfg, "openai_compatible") == FAKE_SECRET

    lit_cfg = {"kind": "omlx", "base_url": "http://127.0.0.1:8000/v1", "api_key": "local-test-key"}
    assert P._resolve_api_key("o", lit_cfg, "omlx") == ("local-test-key", False)
    assert P._api_key("o", lit_cfg, "omlx") == "local-test-key"

    default_cfg = {"kind": "omlx", "base_url": "http://127.0.0.1:8000/v1"}
    assert P._resolve_api_key("o", default_cfg, "omlx") == ("local", False)
    assert P._api_key("o", default_cfg, "omlx") == "local"


# =================================================================================================
# change-b8c75bac (prompt-b8c75bac B1, B2): audit-5e8aea4f F-01, F-02
# =================================================================================================

# --- B1 (audit-5e8aea4f F-01): F21 audit-report check with any argument shape ------------------

_REPORT = "## Item 1\nfinding\n"


@pytest.fixture
def report_state(project):
    state = project / "ai" / "state"
    (state / "audit-report.md").write_text(_REPORT)
    return state


@pytest.mark.parametrize("tool,arguments,refused", [
    ("write_file", {"path": ["src/x.py"]}, False),
    ("write_file", {"path": 5, "file_path": "src/x.py"}, False),
    ("create", {"files": [{"path": 3}, "x", {"path": "audit-report.md", "content": 7}]}, True),
    ("create", {"files": "x"}, False),
    ("write_file", {"path": "ai/state/audit-report.md", "content": None}, True),
])
def test_b1_audit_report_check_accepts_any_argument_shape(orch, report_state, tool, arguments,
                                                          refused):
    result = orch._validate_audit_report_write(tool, arguments, str(report_state))
    if refused:
        assert result == (
            f"Error: This write would discard {len(_REPORT.strip())} characters of existing "
            "audit-report.md findings. audit-report.md is append-only — use the edit "
            "tool to append, or include the full existing content before your new entry.")
    else:
        assert result is None


def test_b1_report_write_keeping_the_content_is_allowed(orch, report_state):
    arguments = {"path": "ai/state/audit-report.md", "content": _REPORT + "## Item 2\n"}
    assert orch._validate_audit_report_write("write_file", arguments, str(report_state)) is None


def test_b1_list_path_through_run_phase(orch, project, report_state, rec_log):
    """As audit-5e8aea4f probe A2: no traceback; the phase continues."""
    log, _ = rec_log
    script = _Script([_call("ffffffff1", "write_file", {"path": ["src/x.py"]}),
                      _call("ffffffff2", "write_file", {"path": "src/y.txt", "content": "y"}),
                      P.Completion(text="done")])
    mcp = _ResultMCP(["write_file"])
    rc, _, _ = asyncio.run(orch.run_phase(
        script, mcp, "m", {"instructions": ""}, "task", 5, str(report_state), log,
        phase_label="WORKER", project_root=str(project)))
    assert rc == 0
    assert mcp.calls == [("write_file", {"path": "src/y.txt", "content": "y"})]
    (first,) = [m for m in script.seen[1] if m["role"] == "tool"]
    assert first["content"].startswith("Error: write refused: tool 'write_file' was called "
                                       "without a recognised path argument")


# --- B2 (audit-5e8aea4f F-02): timeout maximum 86400 s ------------------------------------------

_POSITIVE = "must be a positive number"
_MAXIMUM = "must not exceed 86400 seconds"
_TIMEOUT_CASES = [
    (86400, None),
    (86400.5, _MAXIMUM),
    (1e14, _MAXIMUM),
    (10 ** 400, _POSITIVE),
    (True, _POSITIVE),
    ("60", _POSITIVE),
    (0, _POSITIVE),
    (-1, _POSITIVE),
    (float("nan"), _POSITIVE),
    (float("inf"), _POSITIVE),
]
_CASE_IDS = ["86400", "86400.5", "1e14", "10**400", "True", "str60", "0", "-1", "nan", "inf"]


@pytest.mark.parametrize("value,error", _TIMEOUT_CASES, ids=_CASE_IDS)
def test_b2_validate_timeout(value, error):
    if error is None:
        assert P.validate_timeout(value, "x.y") == 86400.0
    else:
        with pytest.raises(P.ConfigError) as ei:
            P.validate_timeout(value, "x.y")
        assert str(ei.value) == f"x.y: {error}"


@pytest.mark.parametrize("value,error", _TIMEOUT_CASES, ids=_CASE_IDS)
@pytest.mark.parametrize("sdk,pcfg", [("openai", _OPENAI_CFG), ("anthropic", _ANTHROPIC_CFG)])
def test_t19b_request_timeout_bounds(fake_sdks, sdk, pcfg, value, error):
    if error is None:
        P.make_provider("remote", dict(pcfg, request_timeout_seconds=value))
        assert fake_sdks[sdk]["timeout"] == 86400
    else:
        with pytest.raises(P.ConfigError) as ei:
            P.make_provider("remote", dict(pcfg, request_timeout_seconds=value))
        assert str(ei.value) == f"providers.remote.request_timeout_seconds: {error}"


class _Stop(Exception):
    """Raised by a stubbed archive_prior_logs: validation passed, no state written."""


def _stop_at_archive(state_dir, archive_dir):
    raise _Stop(state_dir)


def _timeout_config(project, state_rel, field, value):
    cfg = {"omlx": {"base_url": "http://127.0.0.1:8000/v1", "api_key": "local",
                    "default_model": "devstral"},
           "loop": {"state_dir": state_rel, "max_iterations": 1}}
    if field == "request_timeout_seconds":
        cfg["omlx"]["request_timeout_seconds"] = value
        name = "providers.omlx.request_timeout_seconds"
    else:
        cfg["loop"]["mcp_timeout_seconds"] = value
        name = "loop.mcp_timeout_seconds"
    path = project / "config.yaml"
    path.write_text(yaml.safe_dump(cfg))
    return path, name


@pytest.mark.parametrize("value,error", _TIMEOUT_CASES, ids=_CASE_IDS)
@pytest.mark.parametrize("field", ["request_timeout_seconds", "mcp_timeout_seconds"])
def test_t20b_timeout_bounds_through_main_async(orch, project, monkeypatch, capsys,
                                                isolated_engine_logger, field, value, error):
    import openai

    monkeypatch.setattr(openai, "AsyncOpenAI", lambda **kw: object())
    monkeypatch.setattr(P.OpenAICompatProvider, "await_ready", _not_ready)
    monkeypatch.setattr(orch, "archive_prior_logs", _stop_at_archive)
    config, name = _timeout_config(project, "ai/state/t20b", field, value)
    if error is None:
        with pytest.raises(_Stop):
            asyncio.run(orch.main_async(_main_args(config)))
    else:
        assert asyncio.run(orch.main_async(_main_args(config))) == 1
        assert (_squash(f"configuration error ({config}): {name}: {error}")
                in _squash(capsys.readouterr().out))
    assert not (project / "ai" / "state" / "t20b").exists()
