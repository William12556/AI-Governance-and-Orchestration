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
