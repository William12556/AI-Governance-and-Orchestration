"""Tests for the engine run record, run.json (change-b8a6c445, prompt-b8a6c445 R1 to R6)."""

import argparse
import asyncio
import datetime
import json
import logging
import os

import pytest
import yaml

import manifest as M
import providers as P


# --- helpers (copied from test_loop_robustness.py, change-711a57d5 / change-5e8aea4f) ---------

def _legacy_config(project, state_rel, **loop):
    cfg = {"omlx": {"base_url": "http://127.0.0.1:8000/v1", "api_key": "local",
                    "default_model": "devstral"},
           "loop": dict({"state_dir": state_rel, "max_iterations": 1}, **loop)}
    path = project / "config.yaml"
    path.write_text(yaml.safe_dump(cfg))
    return path


def _main_args(config, task=None):
    return argparse.Namespace(config=str(config), mode="loop", task=task, model=None,
                              worker_model=None, reviewer_model=None, max_iterations=None,
                              duration=None)


@pytest.fixture
def isolated_engine_logger(monkeypatch):
    """Isolate the 'engine' logger as test_loop_robustness.py does."""
    logger = logging.getLogger("engine")
    monkeypatch.setattr(logger, "handlers", [])
    monkeypatch.setattr(logger, "level", logger.level)
    monkeypatch.setattr(logger, "propagate", logger.propagate)
    yield logger
    for handler in list(logger.handlers):
        handler.flush()
        handler.close()


class _FakeMCPClient:
    """Stand-in for MCPClient; connects and closes without a server."""

    def __init__(self, servers, **kw):
        pass

    async def connect(self):
        pass

    def get_openai_tools(self):
        return []

    async def close(self):
        pass


async def _ready(self, model, **kw):
    pass


async def _not_ready(self, model, **kw):
    """Fails at once, so a removed validation does not wait for readiness."""
    raise TimeoutError("stubbed readiness")


def _stub_providers(orch, monkeypatch):
    import openai

    monkeypatch.setattr(openai, "AsyncOpenAI", lambda **kw: object())
    monkeypatch.setattr(P.OpenAICompatProvider, "await_ready", _ready)
    monkeypatch.setattr(P.OpenAICompatProvider, "live_context_window", lambda self, model: None)
    monkeypatch.setattr(orch, "MCPClient", _FakeMCPClient)


def _run(orch, args, logger):
    rc = asyncio.run(orch.main_async(args))
    for handler in list(logger.handlers):
        handler.flush()
    return rc


def _record(state):
    return json.loads((state / "run.json").read_text())


def _is_iso(value):
    """True for a non-empty ISO 8601 string carrying a UTC offset."""
    if not isinstance(value, str) or not value:
        return False
    return datetime.datetime.fromisoformat(value).utcoffset() is not None


# --- R1 to R3: main_async writes the record ----------------------------------------------------

def test_r1_text_task_early_return_writes_start_and_end(orch, project, monkeypatch,
                                                         isolated_engine_logger):
    _stub_providers(orch, monkeypatch)
    config = _legacy_config(project, "ai/state/r1")
    assert _run(orch, _main_args(config), isolated_engine_logger) == 1
    record = _record(project / "ai" / "state" / "r1")
    assert record["mode"] == "loop"
    assert record["task_file"] is None
    assert record["pid"] == os.getpid()
    assert _is_iso(record["started"])
    assert _is_iso(record["ended"])
    assert record["rc"] == 1


def test_r2_task_file_recorded_as_absolute_path(orch, project, monkeypatch,
                                                 isolated_engine_logger):
    _stub_providers(orch, monkeypatch)

    def broken(self, run_type):
        raise M.ManifestError("recipe missing")

    monkeypatch.setattr(M.Manifest, "recipe_paths", broken)
    (project / "mytask.md").write_text("# task\n")
    config = _legacy_config(project, "ai/state/r2")
    assert _run(orch, _main_args(config, task="mytask.md"), isolated_engine_logger) == 1
    record = _record(project / "ai" / "state" / "r2")
    assert record["task_file"] == os.path.abspath("mytask.md")
    assert record["rc"] == 1


def test_r3_write_failure_is_a_warning_only(orch, project, monkeypatch, isolated_engine_logger):
    _stub_providers(orch, monkeypatch)

    def failing(state_dir, record):
        raise OSError("disk full")

    monkeypatch.setattr(orch, "_write_run_record", failing)
    config = _legacy_config(project, "ai/state/r3")
    assert _run(orch, _main_args(config), isolated_engine_logger) == 1
    state = project / "ai" / "state" / "r3"
    (log_file,) = state.glob("engine_*.LOG")
    lines = log_file.read_text().splitlines()
    assert any("WARNING" in ln and "run record not written" in ln for ln in lines)
    assert "engine end rc=1" in lines[-1]
    assert not (state / "run.json").exists()


# --- R4, R5: reset and refused runs -------------------------------------------------------------

def test_r4_reset_removes_run_record(orch, project):
    state = project / "ai" / "state"
    (state / "run.json").write_text("{}\n")
    assert orch.reset_state(str(state)) == 0
    assert not (state / "run.json").exists()


def test_r5_refused_run_writes_no_record(orch, project, monkeypatch):
    import openai

    monkeypatch.setattr(openai, "AsyncOpenAI", lambda **kw: object())
    monkeypatch.setattr(P.OpenAICompatProvider, "await_ready", _not_ready)
    config = _legacy_config(project, "ai/state/r5", mcp_timeout_seconds=0)
    assert asyncio.run(orch.main_async(_main_args(config, task="robustness check"))) == 1
    assert not (project / "ai" / "state" / "r5").exists()


# --- R6: atomic write ---------------------------------------------------------------------------

def test_r6_write_is_atomic_and_cleans_up(orch, tmp_path, monkeypatch):
    state = tmp_path / "state"
    state.mkdir()
    (state / "keep.txt").write_text("x")
    record = {"mode": "loop", "task_file": None, "pid": 1, "started": "s", "ended": None, "rc": None}

    real_replace = os.replace
    calls = []

    def spy(src, dst):
        calls.append((src, dst))
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", spy)
    orch._write_run_record(str(state), record)
    (src, dst), = calls
    assert os.path.dirname(src) == str(state)
    assert dst == os.path.join(str(state), "run.json")
    assert _record(state) == record
    before = set(os.listdir(state))

    def failing(src, dst):
        raise OSError("replace failed")

    monkeypatch.setattr(os, "replace", failing)
    with pytest.raises(OSError, match="replace failed"):
        orch._write_run_record(str(state), dict(record, rc=0))
    assert set(os.listdir(state)) == before
    assert _record(state) == record


# --- change-86c958dd (prompt-86c958dd A1, A2, A4): exit code and start record -------------------

def _stub_loop(orch, monkeypatch, outcome):
    """run_loop returns *outcome*, or raises it when it is an exception."""

    async def run_loop(*args, **kwargs):
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    monkeypatch.setattr(orch, "run_loop", run_loop)


def _log_lines(state, logger):
    for handler in list(logger.handlers):
        handler.flush()
    (log_file,) = state.glob("engine_*.LOG")
    return log_file.read_text().splitlines()


@pytest.mark.parametrize("loop_rc", [0, 2])
def test_a1a_record_holds_the_returned_code(orch, project, monkeypatch, isolated_engine_logger,
                                            loop_rc):
    _stub_providers(orch, monkeypatch)
    _stub_loop(orch, monkeypatch, loop_rc)
    config = _legacy_config(project, "ai/state/a1a")
    assert _run(orch, _main_args(config, task="do the work"), isolated_engine_logger) == loop_rc
    record = _record(project / "ai" / "state" / "a1a")
    assert record["rc"] == loop_rc
    assert "error" not in record
    assert _is_iso(record["ended"])


def _manifest_error(orch, monkeypatch, project):
    def broken(self, run_type):
        raise M.ManifestError("recipe missing")

    monkeypatch.setattr(M.Manifest, "recipe_paths", broken)
    return "do the work"


def _not_ready_provider(orch, monkeypatch, project):
    monkeypatch.setattr(P.OpenAICompatProvider, "await_ready", _not_ready)
    return "do the work"


def _strict_brief(orch, monkeypatch, project):
    (project / "strict.md").write_text("```yaml\nprompt_info:\n  target_profile: engine\n```\n")
    return "strict.md"


def _no_task(orch, monkeypatch, project):
    return None


@pytest.mark.parametrize("early_return", [_manifest_error, _not_ready_provider, _strict_brief,
                                          _no_task])
def test_a1b_early_returns_record_rc_1(orch, project, monkeypatch, isolated_engine_logger,
                                       early_return):
    _stub_providers(orch, monkeypatch)
    _stub_loop(orch, monkeypatch, AssertionError("run_loop reached"))
    task = early_return(orch, monkeypatch, project)
    config = _legacy_config(project, "ai/state/a1b")
    cfg = yaml.safe_load(config.read_text())
    cfg["execution"] = {"strict_tactical_brief": True}
    config.write_text(yaml.safe_dump(cfg))
    assert _run(orch, _main_args(config, task=task), isolated_engine_logger) == 1
    record = _record(project / "ai" / "state" / "a1b")
    assert record["rc"] == 1
    assert "error" not in record


def _raise_after_rc_0(orch, monkeypatch):
    _stub_loop(orch, monkeypatch, 0)

    def finish(*args, **kwargs):
        raise RuntimeError("finish failed")

    monkeypatch.setattr(orch, "_finish_run", finish)
    return RuntimeError


def _interrupt_loop(orch, monkeypatch):
    _stub_loop(orch, monkeypatch, KeyboardInterrupt())
    return KeyboardInterrupt


@pytest.mark.parametrize("setup", [_raise_after_rc_0, _interrupt_loop])
def test_a1c_exception_records_rc_null_and_type(orch, project, monkeypatch,
                                                isolated_engine_logger, setup):
    _stub_providers(orch, monkeypatch)
    exc_type = setup(orch, monkeypatch)
    config = _legacy_config(project, "ai/state/a1c")
    with pytest.raises(exc_type):
        asyncio.run(orch.main_async(_main_args(config, task="do the work")))
    state = project / "ai" / "state" / "a1c"
    record = _record(state)
    assert record["rc"] is None
    assert record["error"] == exc_type.__name__
    assert _is_iso(record["ended"])
    last = _log_lines(state, isolated_engine_logger)[-1]
    assert last.split(" INFO ", 1)[1].startswith("engine end rc=")  # "<timestamp> INFO <message>"


def test_a2a_start_record_build_failure_is_a_warning(orch, project, monkeypatch,
                                                     isolated_engine_logger):
    """datetime.datetime.now raises once, at the start record (the first call after setup_logging)."""
    _stub_providers(orch, monkeypatch)
    _stub_loop(orch, monkeypatch, 0)
    armed = {"on": False}
    real_datetime = orch.datetime.datetime

    class _FailingNow(real_datetime):
        @classmethod
        def now(cls, tz=None):
            if armed["on"]:
                armed["on"] = False
                raise OSError("clock unavailable")
            return real_datetime.now(tz)

    fake_module = type(orch.datetime)("datetime")
    fake_module.__dict__.update(vars(orch.datetime))
    fake_module.datetime = _FailingNow
    monkeypatch.setattr(orch, "datetime", fake_module)
    real_setup = orch.setup_logging

    def setup_then_arm(state_dir):
        logger = real_setup(state_dir)
        armed["on"] = True
        return logger

    monkeypatch.setattr(orch, "setup_logging", setup_then_arm)
    config = _legacy_config(project, "ai/state/a2a")
    assert _run(orch, _main_args(config, task="do the work"), isolated_engine_logger) == 0
    state = project / "ai" / "state" / "a2a"
    lines = _log_lines(state, isolated_engine_logger)
    assert any("WARNING" in ln and "run record not written: clock unavailable" in ln for ln in lines)
    assert "engine end rc=0" in lines[-1]
    assert not (state / "run.json").exists()


def test_a2b_end_write_failure_keeps_start_record(orch, project, monkeypatch,
                                                  isolated_engine_logger):
    """F-05: only the second _write_run_record call fails."""
    _stub_providers(orch, monkeypatch)
    _stub_loop(orch, monkeypatch, 2)
    real_write = orch._write_run_record
    calls = {"n": 0}

    def second_fails(state_dir, record):
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError("disk full")
        real_write(state_dir, record)

    monkeypatch.setattr(orch, "_write_run_record", second_fails)
    config = _legacy_config(project, "ai/state/a2b")
    assert _run(orch, _main_args(config, task="do the work"), isolated_engine_logger) == 2
    assert calls["n"] == 2
    state = project / "ai" / "state" / "a2b"
    lines = _log_lines(state, isolated_engine_logger)
    assert any("WARNING" in ln and "run record not written: disk full" in ln for ln in lines)
    assert "engine end rc=2" in lines[-1]
    record = _record(state)
    assert record["ended"] is None and record["rc"] is None


def test_a4_manifest_version_tracks_governance():
    """manifest.yaml states the version of the last governance.md version-history row (P-02)."""
    import re
    root = os.path.join(os.path.dirname(__file__), "..", "..", "ai", "governance",
                        "software-engineering")
    with open(os.path.join(root, "manifest.yaml")) as fh:
        manifest_version = yaml.safe_load(fh)["model"]["version"]
    with open(os.path.join(root, "governance.md")) as fh:
        text = fh.read()
    history = text[text.index("\n## Version History"):]
    history = history[:history.index("\n## ", 1)]
    rows = re.findall(r"^\| *([0-9]+\.[0-9]+) *\|", history, re.MULTILINE)
    assert manifest_version == rows[-1]


def test_c_run_json_is_a_signal_file():
    """audit-b8a6c445 F-05 (A8): run.json is protected from worker writes."""
    import scope as S
    assert "run.json" in S.SIGNAL_FILES
