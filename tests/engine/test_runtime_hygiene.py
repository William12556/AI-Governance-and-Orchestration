"""Tests for engine runtime hygiene: console prefix, configuration checks and
the MCP tool catalogue (change-bae631c7, T1 to T9; audit-caab2052 L-13, L-16;
audit-b8c75bac F-05; audit-86c958dd F-02)."""

import argparse
import asyncio
import io
import logging
import os
import re
import sys
import types

import pytest
import yaml

import mcp_client as MC
import stages as ST

SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ai", "engine", "src"))


def _squash(text):
    """Text without whitespace: Rich wraps long console lines."""
    return "".join(text.split())


def _tree(root):
    """Every path below root with its file content, for the no-state-change check."""
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
    """Isolate the 'engine' logger, as test_config_validation.py does."""
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


@pytest.fixture
def engine(orch, project, monkeypatch, isolated_engine_logger):
    """main_async with a fake SDK; a run that passes validation stops at archive_prior_logs."""
    import openai

    monkeypatch.setattr(openai, "AsyncOpenAI", lambda **kw: object())
    monkeypatch.setattr(orch, "archive_prior_logs", _stop_at_archive)
    return orch


def _config(context=None):
    cfg = {"omlx": {"base_url": "http://127.0.0.1:8000/v1", "api_key": "local",
                    "default_model": "devstral"},
           "loop": {"state_dir": "ai/state/cfg", "max_iterations": 1}}
    if context is not None:
        cfg["context"] = context
    return cfg


def _write(project, cfg):
    path = project / "config.yaml"
    path.write_text(cfg if isinstance(cfg, str) else yaml.safe_dump(cfg))
    return path


def _args(config):
    return argparse.Namespace(config=str(config), mode="loop", task="config check", model=None,
                              worker_model=None, reviewer_model=None,
                              max_iterations=None, duration=None)


def _refused(orch, project, capsys, config, expected):
    """The run returns 1, prints the message and changes nothing in the project."""
    before = _tree(project)
    assert asyncio.run(orch.main_async(_args(config))) == 1
    out = capsys.readouterr().out
    assert _squash(f"configuration error ({config}): {expected}") in _squash(out)
    assert "Traceback" not in out
    assert _tree(project) == before
    assert not (project / "ai" / "state" / "cfg").exists()
    return out


def _passes(orch, project, config):
    """Validation passed: the run reached archive_prior_logs; nothing written."""
    before = _tree(project)
    with pytest.raises(_Stop):
        asyncio.run(orch.main_async(_args(config)))
    assert _tree(project) == before


# --- A (work item 5 (f)): the console prefix ----------------------------------------------------

def test_t1_console_lines_keep_the_engine_prefix(engine, project, capsys):
    config = _write(project, "loop: [")
    assert asyncio.run(engine.main_async(_args(config))) == 1
    out = capsys.readouterr().out
    assert "[engine] configuration error" in out


def test_t2_no_unescaped_engine_prefix_in_console_markup():
    with open(os.path.join(SRC, "orchestrator.py"), encoding="utf-8") as fh:
        source = fh.read()
    # A style tag directly followed by '[engine]' is read by Rich as markup.
    assert re.findall(r"\]\[engine\]", source) == []
    assert len(re.findall(r"\]\\\\\[engine\]", source)) >= 75


# --- B (work item 5 (g), audit-b8c75bac F-05): deeply nested configuration ----------------------

def test_t3_deeply_nested_config_is_a_configuration_error(engine, project, capsys):
    config = _write(project, "loop: " + "[" * 5000 + "]" * 5000 + "\n")
    _refused(engine, project, capsys, config, "invalid YAML: nesting too deep")


# --- C (work item 5 (h), audit-86c958dd F-02): context.model_context_windows --------------------

@pytest.mark.parametrize("context", [{"model_context_windows": None}, {}, None])
def test_t4_null_model_context_windows_is_empty(engine, project, context):
    config = _write(project, _config(context))
    _passes(engine, project, config)
    cfg = {"context": context} if context is not None else {}
    assert engine.resolve_context_window("devstral", cfg, live_query=lambda m: 1000) == 1000
    assert engine.resolve_context_window("devstral", cfg, live_query=None) is None


@pytest.mark.parametrize("value", [None, 0, -1, True, False, "262144", 1.5, [1]])
def test_t5_invalid_model_context_windows_are_refused(engine, project, capsys, value):
    config = _write(project, _config({"model_context_windows": {"devstral": value}}))
    _refused(engine, project, capsys, config,
             "context.model_context_windows.devstral: must be a positive integer")


@pytest.mark.parametrize("value", [["devstral"], "devstral: 1000", 7])
def test_t5_invalid_model_context_windows_mapping_is_refused(engine, project, capsys, value):
    config = _write(project, _config({"model_context_windows": value}))
    _refused(engine, project, capsys, config, "context.model_context_windows: must be a mapping")


def test_t6_valid_model_context_windows_entry_passes(engine, project):
    context = {"model_context_windows": {"devstral": 262144, "other": 1}}
    config = _write(project, _config(context))
    _passes(engine, project, config)
    assert engine.resolve_context_window("devstral", {"context": context},
                                         live_query=lambda m: 1000) == 262144


# --- D (audit-caab2052 L-13): MCP tool catalogue ------------------------------------------------

class _CM:
    def __init__(self, value):
        self.value = value

    async def __aenter__(self):
        return self.value

    async def __aexit__(self, *exc):
        return False


def _fake_transport(monkeypatch, tools_by_command, failing=()):
    """stdio_client and ClientSession stand-ins; the server is identified by its command."""

    class FakeSession:
        def __init__(self, command):
            self.command = command

        async def initialize(self):
            pass

        async def list_tools(self):
            tools = [types.SimpleNamespace(name=n, description="", inputSchema={})
                     for n in tools_by_command[self.command]]
            return types.SimpleNamespace(tools=tools)

    def fake_stdio(params):
        if params.command in failing:
            raise RuntimeError(f"cannot start {params.command}")
        return _CM((params.command, "w"))

    monkeypatch.setattr(MC, "stdio_client", fake_stdio)
    monkeypatch.setattr(MC, "ClientSession", lambda read, write, **kw: _CM(FakeSession(read)))


def _connect(servers):
    client = MC.MCPClient(servers)

    async def run():
        await client.connect()
        await client.close()

    asyncio.run(run())
    return client


def test_t7_duplicate_tool_name_is_reported(monkeypatch, isolated_engine_logger, caplog, capsys):
    isolated_engine_logger.propagate = True
    _fake_transport(monkeypatch, {"a": ["read_file", "list"], "b": ["read_file"]})
    with caplog.at_level(logging.INFO, logger="engine"):
        client = _connect({"first": {"command": "a"}, "second": {"command": "b"}})
    expected = "tool 'read_file' is offered by 'first' and 'second'; using 'second'"
    assert expected in capsys.readouterr().out
    warnings = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert any(expected in m for m in warnings)
    assert client._tools["read_file"]["server"] == "second"
    assert sorted(client._tools) == ["list", "read_file"]
    # 'list' is offered once: no warning names it
    assert not any("'list'" in m for m in warnings)


def test_t7_one_server_listing_a_tool_twice_is_not_reported(monkeypatch, isolated_engine_logger,
                                                            caplog, capsys):
    isolated_engine_logger.propagate = True
    _fake_transport(monkeypatch, {"a": ["read_file", "read_file"]})
    with caplog.at_level(logging.INFO, logger="engine"):
        client = _connect({"fs": {"command": "a"}})
    assert "is offered by" not in capsys.readouterr().out
    assert not [r for r in caplog.records if r.levelno == logging.WARNING]
    assert client._tools["read_file"]["server"] == "fs"


def test_t8_failed_connection_is_logged(monkeypatch, isolated_engine_logger, caplog, capsys):
    isolated_engine_logger.propagate = True
    _fake_transport(monkeypatch, {"a": ["read_file"]}, failing=("missing",))
    with caplog.at_level(logging.INFO, logger="engine"):
        client = _connect({"broken": {"command": "missing"}, "fs": {"command": "a"}})
    out = capsys.readouterr().out
    assert "Warning: failed to connect to 'broken': cannot start missing" in out
    warnings = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert any("failed to connect to 'broken'" in m and "cannot start missing" in m
               for m in warnings)
    infos = [r.getMessage() for r in caplog.records if r.levelno == logging.INFO]
    assert any("Connected: fs (1 tools)" in m for m in infos)
    assert client._tools["read_file"]["server"] == "fs"


# --- E (audit-caab2052 L-16): approvals fallback type -------------------------------------------

def test_t9_scan_outside_a_repository_uses_an_empty_approvals_mapping(tmp_path, monkeypatch):
    import manifest as M

    (tmp_path / "ai" / "workspace").mkdir(parents=True)
    monkeypatch.setattr(ST, "is_git_repository", lambda root: False)
    monkeypatch.setattr(ST, "_documents", lambda root, manifest, skipped=None: {"1a2b3c4d": []})
    captured = []
    monkeypatch.setattr(ST, "_evaluate", lambda item, manifest, approvals: captured.append(approvals))
    monkeypatch.setattr(ST, "_flag_stale_approvals", lambda *a: None)
    report = ST.scan(str(tmp_path), M.load_manifest(M.locate_manifest()))
    assert any("not a git repository" in w for w in report.warnings)
    assert len(captured) == 1 and isinstance(captured[0], dict) and captured[0] == {}


# --- change-f68d51c2 (audit-bae631c7 F-01 to F-03; audit-9377f9b9-followup F-01, F-02) ---------

class _FlakyProvider:
    """Provider stand-in: the first call raises an error with markup-like text, the second succeeds."""

    def __init__(self):
        self.calls = 0

    async def complete(self, model, messages, tools, max_completion_tokens):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("404 Not Found for url [/v1/chat/completions]")
        return "completion"


def test_f68_t4_retry_line_escapes_provider_text(orch, tmp_path, capsys):
    """T4 (change-f68d51c2, FR-02): the provider error text is printed literally, no MarkupError."""
    provider = _FlakyProvider()
    result = asyncio.run(orch._completion_with_retry(
        provider, "m", [], None, logging.getLogger("engine-test-f68-retry"), str(tmp_path),
        max_retries=2, initial_backoff=0.0))
    assert result == "completion"
    assert provider.calls == 2
    assert "[/v1/chat/completions]" in _squash(capsys.readouterr().out)


@pytest.mark.parametrize("key", ["context", "execution"])
def test_f68_t5_null_config_block_is_empty(engine, project, key):
    """T5 (change-f68d51c2, FR-03): a null context: or execution: block passes the check."""
    cfg = _config()
    cfg[key] = None
    config = _write(project, cfg)
    assert f"{key}: null" in config.read_text()
    _passes(engine, project, config)


@pytest.mark.parametrize("value", [["a"], "a"])
@pytest.mark.parametrize("key", ["context", "execution"])
def test_f68_t6_non_mapping_config_block_is_refused(engine, project, capsys, key, value):
    """T6 (change-f68d51c2, FR-03): a list or string block is a configuration error; no state."""
    cfg = _config()
    cfg[key] = value
    config = _write(project, cfg)
    _refused(engine, project, capsys, config, f"{key}: must be a mapping")


@pytest.mark.parametrize("text, expected", [
    ("created: 2026-11-31\n", "invalid YAML"),
    ("x: " + "[" * 5000 + "]" * 5000 + "\n", "invalid YAML: nesting too deep"),
], ids=["date", "deep"])
def test_f68_t9_t10_load_yaml_raises_config_error(orch, tmp_path, text, expected):
    """T9, T10 (change-f68d51c2, FR-05): load_yaml raises ConfigError naming the path."""
    path = tmp_path / "recipe.yaml"
    path.write_text(text)
    with pytest.raises(orch.ConfigError) as exc:
        orch.load_yaml(str(path))
    assert str(exc.value).startswith(f"{path}: {expected}")


def test_f68_t9_load_config_invalid_date(orch, tmp_path):
    """T9 (change-f68d51c2, FR-05): _load_config raises ConfigError 'invalid YAML: ...'."""
    path = tmp_path / "config.yaml"
    path.write_text("created: 2026-11-31\nloop: {state_dir: ai/state}\n")
    with pytest.raises(orch.ConfigError) as exc:
        orch._load_config(str(path))
    assert str(exc.value).startswith("invalid YAML: ")


class _TtyInput(io.StringIO):
    """stdin stand-in that reports a terminal."""

    def isatty(self):
        return True


@pytest.mark.parametrize("stdin", [io.StringIO(), _TtyInput("n\n")], ids=["non-interactive", "interactive"])
def test_f68_t11_continuation_prompt_shows_y_n(orch, project, monkeypatch, capsys, stdin):
    """T11 (change-f68d51c2, FR-06): the continuation prompt shows '[y/N]'."""
    monkeypatch.setattr(orch.sys, "stdin", stdin)
    rc = asyncio.run(orch.run_loop(None, None, "w", "r", {}, {}, "task", 0, 1,
                                   str(project / "ai" / "state"),
                                   logging.getLogger("engine-test-f68-prompt"),
                                   project_root=str(project), gates=[], gate_specs={}))
    assert rc == 1
    assert "[y/N]" in capsys.readouterr().out
