"""Tests for configuration validation and the F28 read paths (change-b8c75bac,
prompt-b8c75bac C1 to C7 and D1; audit-14e05e35 L-08, NFR-04, FR-08-05;
d7f4a1c8 P08 review)."""

import argparse
import asyncio
import logging
import os
import sys
import time
import types

import pytest
import yaml

import providers as P


def _squash(text):
    """Text without whitespace: Rich wraps long console lines."""
    return "".join(text.split())


def _tree(root):
    """Every path below root with its file content, for the no-state-change check (C7)."""
    entries = {}
    for d, dirs, files in os.walk(root):
        for name in dirs:
            entries[os.path.relpath(os.path.join(d, name), root)] = None
        for name in files:
            path = os.path.join(d, name)
            with open(path, "rb") as fh:
                entries[os.path.relpath(path, root)] = fh.read()
    return entries


@pytest.fixture
def isolated_engine_logger(monkeypatch):
    """Isolate the 'engine' logger, as test_loop_robustness.py does."""
    logger = logging.getLogger("engine")
    monkeypatch.setattr(logger, "handlers", [])
    monkeypatch.setattr(logger, "level", logger.level)
    monkeypatch.setattr(logger, "propagate", logger.propagate)
    yield logger
    for handler in list(logger.handlers):
        handler.flush()
        handler.close()


class _Stop(Exception):
    """Raised by the stubbed archive_prior_logs: validation passed, no state written."""


def _stop_at_archive(state_dir, archive_dir):
    raise _Stop(state_dir)


class _FakeAnthropic:
    def __init__(self, **kw):
        self.kw = kw


@pytest.fixture
def engine(orch, project, monkeypatch, isolated_engine_logger):
    """main_async with fake SDKs; a run that passes validation stops at archive_prior_logs."""
    import openai

    monkeypatch.setattr(openai, "AsyncOpenAI", lambda **kw: object())
    monkeypatch.setitem(sys.modules, "anthropic", types.SimpleNamespace(AsyncAnthropic=_FakeAnthropic))
    monkeypatch.setenv("TB8C7_KEY", "fake-key")
    monkeypatch.setattr(orch, "archive_prior_logs", _stop_at_archive)
    return orch


def _base_config(state_rel="ai/state/cfg"):
    return {"omlx": {"base_url": "http://127.0.0.1:8000/v1", "api_key": "local",
                     "default_model": "devstral"},
            "loop": {"state_dir": state_rel, "max_iterations": 1}}


def _write(project, cfg, name="config.yaml"):
    path = project / name
    path.write_text(cfg if isinstance(cfg, str) else yaml.safe_dump(cfg))
    return path


def _args(config, mode="loop", max_iterations=None):
    return argparse.Namespace(config=str(config), mode=mode, task="config check", model=None,
                              worker_model=None, reviewer_model=None,
                              max_iterations=max_iterations, duration=None)


def _refused(orch, project, capsys, config, expected, **kw):
    """C7: the run returns 1, prints the message and changes nothing in the project."""
    before = _tree(project)
    assert asyncio.run(orch.main_async(_args(config, **kw))) == 1
    out = capsys.readouterr().out
    assert _squash(f"configuration error ({config}): {expected}") in _squash(out)
    assert "Traceback" not in out
    assert _tree(project) == before
    assert not (project / "ai" / "state" / "cfg").exists()
    return out


def _passes(orch, project, config, **kw):
    """Validation passed: the run reached archive_prior_logs; nothing written."""
    before = _tree(project)
    with pytest.raises(_Stop):
        asyncio.run(orch.main_async(_args(config, **kw)))
    assert _tree(project) == before


# --- C1: file, YAML and top level ---------------------------------------------------------------

def test_c1_missing_file(engine, project, capsys):
    config = project / "absent.yaml"
    _refused(engine, project, capsys, config, "cannot read file: No such file or directory")


def test_c1_invalid_yaml(engine, project, capsys):
    config = _write(project, "loop: [\n")
    out = _refused(engine, project, capsys, config, "invalid YAML: ")
    assert " at line " in " ".join(out.split())


def test_c1_top_level_not_a_mapping(engine, project, capsys):
    config = _write(project, "- a\n")
    _refused(engine, project, capsys, config, "top level must be a mapping")


def test_c1_load_config_messages(orch, project):
    with pytest.raises(P.ConfigError) as ei:
        orch._load_config(str(project / "absent.yaml"))
    assert str(ei.value) == "cannot read file: No such file or directory"
    with pytest.raises(P.ConfigError) as ei:
        orch._load_config(str(_write(project, "a: 1\nloop: [\n")))
    assert str(ei.value).startswith("invalid YAML: ")
    assert str(ei.value).endswith(" at line 3")
    with pytest.raises(P.ConfigError) as ei:
        orch._load_config(str(_write(project, "")))
    assert str(ei.value) == "top level must be a mapping"
    assert orch._load_config(str(_write(project, _base_config()))) == _base_config()


# --- C2: loop and loop.state_dir ----------------------------------------------------------------

_LOOP = "loop: required and must be a mapping"
_STATE_DIR = "loop.state_dir: required and must be a non-empty string"


@pytest.mark.parametrize("loop,expected", [
    ("absent", _LOOP),
    (["state_dir"], _LOOP),
    ({"max_iterations": 1}, _STATE_DIR),
    ({"state_dir": "", "max_iterations": 1}, _STATE_DIR),
], ids=["no-loop", "loop-list", "no-state-dir", "empty-state-dir"])
def test_c2_loop_and_state_dir_required(engine, project, capsys, loop, expected):
    cfg = _base_config()
    if loop == "absent":
        del cfg["loop"]
    else:
        cfg["loop"] = loop
    _refused(engine, project, capsys, _write(project, cfg), expected)


# --- C3: checked before the reset branch --------------------------------------------------------

def test_c3_reset_without_loop_is_refused(engine, project, capsys, monkeypatch):
    calls = []
    monkeypatch.setattr(engine, "reset_state", lambda state_dir: calls.append(state_dir) or 0)
    cfg = _base_config()
    del cfg["loop"]
    _refused(engine, project, capsys, _write(project, cfg), _LOOP, mode="reset")
    assert calls == []


# --- C4: loop.max_iterations --------------------------------------------------------------------

_MAX_ITER = "loop.max_iterations: required as a positive integer unless --max-iterations is given"


@pytest.mark.parametrize("value", ["absent", 0, True, "x"])
def test_c4_max_iterations_required(engine, project, capsys, value):
    cfg = _base_config()
    if value == "absent":
        del cfg["loop"]["max_iterations"]
    else:
        cfg["loop"]["max_iterations"] = value
    _refused(engine, project, capsys, _write(project, cfg), _MAX_ITER)


def test_c4_max_iterations_from_the_command_line(engine, project):
    cfg = _base_config()
    del cfg["loop"]["max_iterations"]
    _passes(engine, project, _write(project, cfg), max_iterations=2)


def test_c4_valid_config_passes(engine, project):
    _passes(engine, project, _write(project, _base_config()))


# --- C5: providers.<name>.max_tokens ------------------------------------------------------------

def _anthropic_config(max_tokens):
    cfg = _base_config()
    cfg["providers"] = {"anth": {"kind": "anthropic", "api_key_env": "TB8C7_KEY",
                                 "max_tokens": max_tokens}}
    cfg["roles"] = {"worker": {"provider": "anth", "model": "m"},
                    "reviewer": {"provider": "anth", "model": "m"}}
    return cfg


@pytest.mark.parametrize("value", ["many", 0, True])
def test_c5_invalid_max_tokens(engine, project, capsys, value):
    _refused(engine, project, capsys, _write(project, _anthropic_config(value)),
             "providers.anth.max_tokens: must be a positive integer")


@pytest.mark.parametrize("value", ["4096", 4096])
def test_c5_valid_max_tokens(engine, project, value):
    provider = P.make_provider("anth", _anthropic_config(value)["providers"]["anth"])
    assert provider.max_tokens == 4096
    _passes(engine, project, _write(project, _anthropic_config(value)))


def test_c5_absent_max_tokens_uses_the_default(engine):
    provider = P.make_provider("anth", {"kind": "anthropic", "api_key_env": "TB8C7_KEY"})
    assert provider.max_tokens == P._ANTHROPIC_DEFAULT_MAX_TOKENS


# --- C6: gates.<name>.timeout_seconds in ai/config.yaml -----------------------------------------

def _gate_config(timeout):
    cfg = _base_config()
    cfg["gates"] = {"pytest": {"timeout_seconds": timeout}}
    return cfg


@pytest.mark.parametrize("value", [-1, "x", True, float("nan")], ids=["-1", "x", "True", "nan"])
def test_c6_invalid_gate_timeout(engine, project, capsys, value):
    _refused(engine, project, capsys, _write(project, _gate_config(value)),
             "gates.pytest.timeout_seconds: must be a positive number")


def test_c6_valid_gate_timeout(engine, project):
    from manifest import load_manifest, locate_manifest

    specs = engine._resolve_gate_specs(load_manifest(locate_manifest()), _gate_config(600))
    assert specs["pytest"]["timeout_seconds"] == 600
    _passes(engine, project, _write(project, _gate_config(600)))


# --- D1: F28 wall-clock-cap return normalises read paths ----------------------------------------

def _tool(name):
    return {"type": "function", "function": {"name": name, "description": "", "parameters": {"type": "object"}}}


class _ReadMCP:
    def get_openai_tools(self, readonly=False):
        return [_tool("read_file")]

    async def call_tool(self, name, arguments):
        return "x = 1"


class _ClockScript:
    """Fake provider: one read of src/a.py, after which the clock passes the phase cap."""

    def __init__(self, clock):
        self.clock = clock

    async def complete(self, model, messages, tools, max_tokens=None):
        self.clock[0] = 10_000.0
        return P.Completion(text="", tool_calls=[P.ToolCall("dddddddd1", "read_file",
                                                            {"path": "src/a.py"})])


def test_d1_wall_clock_cap_returns_absolute_read_paths(orch, project, monkeypatch):
    log = logging.getLogger("engine-test-b8c75bac")
    (project / "src" / "a.py").write_text("x = 1\n")
    clock = [0.0]
    fake_time = types.SimpleNamespace(**{k: getattr(time, k) for k in dir(time)
                                         if not k.startswith("_")})
    fake_time.monotonic = lambda: clock[0]
    monkeypatch.setattr(orch, "time", fake_time)
    rc, final, read_paths = asyncio.run(orch.run_phase(
        _ClockScript(clock), _ReadMCP(), "m", {"instructions": ""}, "task", 5,
        str(project / "ai" / "state"), log, phase_label="REVIEW", project_root=str(project),
        phase_duration_seconds=60))
    assert (rc, final) == (0, "")
    assert read_paths == {os.path.abspath("src/a.py")}
