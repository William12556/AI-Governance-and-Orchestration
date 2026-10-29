"""Tests for engine loop robustness (change-711a57d5, prompt-711a57d5 T1 to T16)."""

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


@pytest.mark.parametrize("value", [0, -1, "x", True])
def test_t16_invalid_mcp_timeout_stops_before_state(orch, project, monkeypatch, capsys, value):
    import openai

    monkeypatch.setattr(openai, "AsyncOpenAI", lambda **kw: object())
    config = _legacy_config(project, "ai/state/t16", mcp_timeout_seconds=value)
    assert asyncio.run(orch.main_async(_main_args(config))) == 1
    assert not (project / "ai" / "state" / "t16").exists()
    assert "loop.mcp_timeout_seconds: must be a positive number" in capsys.readouterr().out
