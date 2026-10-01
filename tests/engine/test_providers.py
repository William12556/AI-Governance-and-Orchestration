"""Tests for providers.py and its orchestrator wiring (change-53c6f252, design-14e05e35 §3.0, §4.0).

No network, API key or model is used: providers get fake clients, and role
bindings use a stub factory unless the test targets make_provider itself.
"""

import argparse
import asyncio
import json
import re
from types import SimpleNamespace

import pytest

import providers as P

ID_RE = re.compile(r"^[A-Za-z0-9]{9}$")


def _openai_response(content="", tool_calls=None, choices=True, usage=None):
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    if not choices:
        return SimpleNamespace(choices=[], usage=usage)
    return SimpleNamespace(choices=[SimpleNamespace(message=message, finish_reason=None)], usage=usage)


def _native_call(name, arguments, call_id="abcDEF123"):
    return SimpleNamespace(id=call_id, function=SimpleNamespace(name=name, arguments=arguments))


# --- tool call IDs (FR-04-09) ------------------------------------------------

def test_tool_call_id_is_nine_alphanumeric_characters():
    ids = {P.new_tool_call_id() for _ in range(50)}
    assert all(ID_RE.match(i) for i in ids)
    assert len(ids) > 1


# --- OpenAI-compatible normalisation ------------------------------------------

def test_native_tool_calls_keep_id_and_parse_arguments():
    c = P.OpenAICompatProvider.normalise(_openai_response(
        "", [_native_call("read_file", json.dumps({"path": "a.py"}))]))
    assert [(t.id, t.name, t.arguments) for t in c.tool_calls] == [("abcDEF123", "read_file", {"path": "a.py"})]
    assert c.finish_reason == "tool_calls"


def test_native_tool_call_without_id_gets_generated_id_and_bad_json_is_empty():
    c = P.OpenAICompatProvider.normalise(_openai_response(
        "", [_native_call("write_file", "{not json", call_id=None)]))
    assert ID_RE.match(c.tool_calls[0].id)
    assert c.tool_calls[0].arguments == {}


def test_plain_text_tool_call_is_parsed_with_generated_id():
    c = P.OpenAICompatProvider.normalise(_openai_response(
        '[TOOL_CALLS]read_file[ARGS]{"path": "src/x.py"}'))
    assert len(c.tool_calls) == 1
    assert c.tool_calls[0].name == "read_file"
    assert c.tool_calls[0].arguments == {"path": "src/x.py"}
    assert ID_RE.match(c.tool_calls[0].id)


def test_tool_call_inside_reasoning_block_is_not_dispatched():
    c = P.OpenAICompatProvider.normalise(_openai_response(
        '<think>[TOOL_CALLS]read_file[ARGS]{"path": "x"}</think>All done.'))
    assert c.tool_calls == []
    assert "All done." in c.text


def test_response_without_choices_raises_provider_error():
    with pytest.raises(P.ProviderError):
        P.OpenAICompatProvider.normalise(_openai_response(choices=False))


def test_usage_is_normalised():
    c = P.OpenAICompatProvider.normalise(_openai_response(
        "hi", usage=SimpleNamespace(prompt_tokens=10, completion_tokens=3)))
    assert c.usage == {"input_tokens": 10, "output_tokens": 3}


def test_complete_passes_max_tokens_only_when_set():
    seen = []

    async def create(**kw):
        seen.append(kw)
        return _openai_response("ok")

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    prov = P.OpenAICompatProvider(kind="openai_compatible", base_url="u", client=client)
    asyncio.run(prov.complete("m", [{"role": "user", "content": "x"}], None))
    asyncio.run(prov.complete("m", [{"role": "user", "content": "x"}], None, 100))
    assert "max_tokens" not in seen[0] and seen[1]["max_tokens"] == 100


def _models_client(ids):
    async def list_models():
        return SimpleNamespace(data=[SimpleNamespace(id=i) for i in ids])
    return SimpleNamespace(models=SimpleNamespace(list=list_models))


def test_readiness_omlx_accepts_unlisted_model():
    prov = P.OpenAICompatProvider(kind="omlx", base_url="u", client=_models_client(["other"]))
    asyncio.run(prov.await_ready("m", timeout=1, interval=0))


def test_readiness_openai_compatible_requires_listed_model():
    prov = P.OpenAICompatProvider(kind="openai_compatible", base_url="u", client=_models_client(["other"]))
    with pytest.raises(P.ProviderError):
        asyncio.run(prov.await_ready("devstral-latest", timeout=1, interval=0))
    ok = P.OpenAICompatProvider(kind="openai_compatible", base_url="u", client=_models_client(["m"]))
    asyncio.run(ok.await_ready("m", timeout=1, interval=0))


def test_live_context_window_only_for_omlx(monkeypatch):
    monkeypatch.setattr(P, "query_omlx_context_window", lambda m, u: 4096)
    assert P.OpenAICompatProvider(kind="omlx", base_url="u", client=object()).live_context_window("m") == 4096
    assert P.OpenAICompatProvider(kind="openai_compatible", base_url="u", client=object()).live_context_window("m") is None


# --- Anthropic conversion -------------------------------------------------------

def test_anthropic_messages_conversion():
    msgs = [
        {"role": "system", "content": "sys A"},
        {"role": "system", "content": "sys B"},
        {"role": "user", "content": "task"},
        {"role": "assistant", "content": "reading",
         "tool_calls": [{"id": "t1", "type": "function",
                         "function": {"name": "read", "arguments": json.dumps({"path": "a"})}},
                        {"id": "t2", "type": "function",
                         "function": {"name": "read", "arguments": json.dumps({"path": "b"})}}]},
        {"role": "tool", "content": "A", "tool_call_id": "t1"},
        {"role": "tool", "content": "", "tool_call_id": "t2"},
        {"role": "user", "content": "go on"},
    ]
    system, out = P.to_anthropic_messages(msgs)
    assert [b["text"] for b in system] == ["sys A", "sys B"]
    assert "cache_control" in system[-1] and "cache_control" not in system[0]
    assert [m["role"] for m in out] == ["user", "assistant", "user"]
    uses = [b for b in out[1]["content"] if b["type"] == "tool_use"]
    assert [(u["id"], u["input"]) for u in uses] == [("t1", {"path": "a"}), ("t2", {"path": "b"})]
    results = [b for b in out[2]["content"] if b["type"] == "tool_result"]
    assert [r["tool_use_id"] for r in results] == ["t1", "t2"]
    assert results[1]["content"] == "(empty)"
    assert out[2]["content"][-1] == {"type": "text", "text": "go on"}


def test_anthropic_tools_conversion():
    tools = [{"type": "function", "function": {"name": "a", "description": "A", "parameters": {"type": "object"}}},
             {"type": "function", "function": {"name": "b", "description": "B", "parameters": None}}]
    out = P.to_anthropic_tools(tools, strict=True)
    assert out[0]["input_schema"] == {"type": "object"} and out[0]["strict"] is True
    assert out[1]["input_schema"]["type"] == "object"
    assert "cache_control" in out[1] and "cache_control" not in out[0]
    assert "strict" not in P.to_anthropic_tools(tools, strict=False)[0]


def test_anthropic_response_conversion():
    resp = SimpleNamespace(
        content=[SimpleNamespace(type="thinking", thinking="plan"),
                 SimpleNamespace(type="text", text="ok"),
                 SimpleNamespace(type="tool_use", id="toolu_1", name="read", input={"path": "a"})],
        stop_reason="tool_use", usage=SimpleNamespace(input_tokens=5, output_tokens=2))
    c = P.from_anthropic_response(resp)
    assert c.text == "ok" and c.reasoning_content == "plan"
    assert [(t.id, t.name, t.arguments) for t in c.tool_calls] == [("toolu_1", "read", {"path": "a"})]
    assert c.finish_reason == "tool_calls"
    assert c.usage == {"input_tokens": 5, "output_tokens": 2}


def test_anthropic_complete_request_shape():
    seen = {}

    async def create(**kw):
        seen.update(kw)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text="done")],
                               stop_reason="end_turn", usage=None)

    prov = P.AnthropicProvider(max_tokens=1234, strict_tools=True,
                               client=SimpleNamespace(messages=SimpleNamespace(create=create)))
    tools = [{"type": "function", "function": {"name": "a", "description": "", "parameters": {"type": "object"}}}]
    c = asyncio.run(prov.complete("claude-x", [{"role": "system", "content": "s"},
                                               {"role": "user", "content": "u"}], tools))
    assert c.text == "done" and c.finish_reason == "stop"
    assert seen["max_tokens"] == 1234 and seen["model"] == "claude-x"
    assert seen["system"][0]["text"] == "s" and seen["tools"][0]["name"] == "a"
    assert seen["messages"] == [{"role": "user", "content": [{"type": "text", "text": "u"}]}]


# --- role bindings (FR-04-01, FR-04-08) -----------------------------------------

def _stub_factory(created):
    def factory(name, cfg):
        created.append(name)
        return SimpleNamespace(name=name, cfg=cfg)
    return factory


def _args(**kw):
    base = dict(model=None, worker_model=None, reviewer_model=None)
    base.update(kw)
    return argparse.Namespace(**base)


LEGACY = {"omlx": {"base_url": "http://x/v1", "api_key": "local",
                   "default_model": "devstral", "reviewer_model": "magistral"}}


def test_legacy_binding_uses_omlx_block_for_both_roles():
    created = []
    b = P.build_role_bindings(LEGACY, _args(), factory=_stub_factory(created))
    assert (b["worker"].provider_name, b["worker"].model) == ("omlx", "devstral")
    assert (b["reviewer"].provider_name, b["reviewer"].model) == ("omlx", "magistral")
    assert b["worker"].provider is b["reviewer"].provider and created == ["omlx"]


def test_legacy_cli_precedence_matches_previous_behaviour():
    b = P.build_role_bindings(LEGACY, _args(model="m2"), factory=_stub_factory([]))
    assert b["worker"].model == "m2" and b["reviewer"].model == "magistral"
    b = P.build_role_bindings(LEGACY, _args(reviewer_model="r3"), factory=_stub_factory([]))
    assert b["reviewer"].model == "r3"


ROLES = {
    "providers": {"omlx": {"kind": "omlx", "base_url": "http://x/v1"},
                  "mistral": {"kind": "openai_compatible", "base_url": "https://api.mistral.ai/v1",
                              "api_key_env": "MISTRAL_API_KEY"}},
    "roles": {"worker": {"provider": "omlx", "model": "devstral"},
              "reviewer": {"provider": "mistral", "model": "mistral-medium-2604"}},
}


def test_roles_bind_each_role_to_its_provider():
    b = P.build_role_bindings(ROLES, _args(), factory=_stub_factory([]))
    assert (b["worker"].provider_name, b["worker"].model) == ("omlx", "devstral")
    assert (b["reviewer"].provider_name, b["reviewer"].model) == ("mistral", "mistral-medium-2604")


def test_roles_cli_precedence():
    b = P.build_role_bindings(ROLES, _args(model="m", reviewer_model="r"), factory=_stub_factory([]))
    assert b["worker"].model == "m" and b["reviewer"].model == "r"


@pytest.mark.parametrize("config,fragment", [
    ({"loop": {}}, "roles: block or the legacy omlx: block"),
    ({"roles": {"worker": {"provider": "x", "model": "m"}, "reviewer": {"provider": "x", "model": "m"}}},
     "provider 'x' is not defined"),
    ({"providers": {"p": {"kind": "omlx", "base_url": "u"}},
      "roles": {"worker": {"provider": "p"}, "reviewer": {"provider": "p", "model": "m"}}},
     "roles.worker.model"),
])
def test_binding_errors_name_the_key(config, fragment):
    with pytest.raises(P.ConfigError):
        P.build_role_bindings(config, _args(), factory=_stub_factory([]))
    try:
        P.build_role_bindings(config, _args(), factory=_stub_factory([]))
    except P.ConfigError as e:
        assert fragment in str(e)


def test_missing_api_key_variable_is_named(monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    try:
        P.make_provider("mistral", ROLES["providers"]["mistral"])
        assert False, "expected ConfigError"
    except P.ConfigError as e:
        assert "MISTRAL_API_KEY" in str(e)


def test_literal_api_key_rejected_for_remote_providers():
    with pytest.raises(P.ConfigError):
        P.make_provider("m", {"kind": "openai_compatible", "base_url": "u", "api_key": "secret"})
    with pytest.raises(P.ConfigError):
        P.make_provider("m", {"kind": "unknown"})


def test_make_provider_reads_key_from_environment(monkeypatch):
    monkeypatch.setenv("MISTRAL_API_KEY", "k")
    prov = P.make_provider("mistral", ROLES["providers"]["mistral"])
    assert prov.kind == "openai_compatible" and prov.base_url == "https://api.mistral.ai/v1"


# --- orchestrator wiring ---------------------------------------------------------

def test_context_window_per_role(orch):
    config = {"context": {"model_context_windows": {"devstral": 262144, "magistral": 40960}}}
    assert orch.resolve_context_window("devstral", config, live_query=None) == 262144
    assert orch.resolve_context_window("magistral", config, live_query=None) == 40960
    assert orch.resolve_context_window("magistral", config, live_query=lambda m: 1000) == 1000
    assert orch.resolve_context_window("x", {}, live_query=None) is None


def test_completion_retry_recovers_from_provider_error(orch, log, project):
    calls = {"n": 0}

    class Flaky:
        async def complete(self, model, messages, tools, max_tokens=None):
            calls["n"] += 1
            if calls["n"] < 2:
                raise P.ProviderError("completion response contains no choices")
            return P.Completion(text="ok")

    c = asyncio.run(orch._completion_with_retry(Flaky(), "m", [], None, log,
                                                str(project / "ai" / "state"), initial_backoff=0))
    assert c.text == "ok" and calls["n"] == 2


def test_completion_retry_blocks_after_persistent_error(orch, log, project):
    class Broken:
        async def complete(self, model, messages, tools, max_tokens=None):
            raise P.ProviderError("completion response contains no choices")

    state = project / "ai" / "state"
    with pytest.raises(RuntimeError):
        asyncio.run(orch._completion_with_retry(Broken(), "m", [], None, log, str(state),
                                                max_retries=2, initial_backoff=0))
    assert "no choices" in (state / "BLOCKED.md").read_text()


class _ScriptedProvider:
    def __init__(self, script):
        self.script = list(script)
        self.seen = []

    async def complete(self, model, messages, tools, max_tokens=None):
        self.seen.append([dict(m) for m in messages])
        return self.script.pop(0)


class _MCP:
    def get_openai_tools(self, readonly=False):
        return [{"type": "function", "function": {"name": "read_file", "description": "", "parameters": {"type": "object"}}}]

    async def call_tool(self, name, arguments):
        return "contents"


def test_run_phase_uses_provider_tool_call_ids(orch, log, project):
    prov = _ScriptedProvider([
        P.Completion(text="", tool_calls=[P.ToolCall("aB3dE5gH7", "read_file", {"path": "x"})]),
        P.Completion(text="final summary"),
    ])
    rc, final, _ = asyncio.run(orch.run_phase(
        prov, _MCP(), "m", {"instructions": "w {{TOOLS}}"}, "task", 3,
        str(project / "ai" / "state"), log, phase_label="WORKER", project_root=str(project)))
    assert rc == 0 and final == "final summary"
    second = prov.seen[1]
    assert second[2]["tool_calls"][0]["id"] == "aB3dE5gH7"
    assert second[3]["role"] == "tool" and second[3]["tool_call_id"] == "aB3dE5gH7"


def test_run_loop_gives_reviewer_its_own_provider_and_window(orch, log, project, monkeypatch):
    seen = {}

    async def fake_run_phase(client, mcp, model, recipe, task, max_iter, state_dir, log, **kw):
        seen[kw["phase_label"]] = (client, model, kw["context_window"])
        if kw["phase_label"] == "WORKER":
            (project / "ai" / "state" / "work-summary.txt").write_text("done")
            return 0, "done", set()
        (project / "ai" / "state" / "review-result.txt").write_text("SHIP")
        return 0, "SHIP", set()

    monkeypatch.setattr(orch, "run_phase", fake_run_phase)
    monkeypatch.setattr(orch, "_run_syntax_gate", lambda state_dir, log: "")
    monkeypatch.setattr(orch, "_run_pytest_gate", lambda state_dir, log, root: "")
    asyncio.run(orch.run_loop("W", None, "wm", "rm", {}, {}, "task", 1, 2,
                              str(project / "ai" / "state"), log, context_window=100,
                              project_root=str(project), reviewer_client="R",
                              reviewer_context_window=50))
    assert seen["WORKER"] == ("W", "wm", 100)
    assert seen["REVIEWER"] == ("R", "rm", 50)


def test_main_async_stops_on_configuration_error(orch, project):
    config = project / "config.yaml"
    config.write_text("loop:\n  state_dir: ai/state/fresh\n")
    args = argparse.Namespace(config=str(config), mode="loop", task="implement x", model=None,
                              worker_model=None, reviewer_model=None, max_iterations=None,
                              duration=None)
    assert asyncio.run(orch.main_async(args)) == 1
    assert not (project / "ai" / "state" / "fresh").exists()
