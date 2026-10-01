"""Tests for scope.py and the write-scope wiring (change-bdc6820f, design-14e05e35 §7.0)."""

import asyncio
import logging
import os

import pytest

import scope as S

PROMPT = """Created: 2026 October 01

```yaml
prompt_info:
  id: "prompt-abcd1234"
deliverable:
  files:
    - path: "src/pkg/mod.py"
    - path: "docs/notes.md"
```
"""

NOT_A_PROMPT = """# Task

```yaml
deliverable:
  files:
    - path: "src/x.py"
```
"""


def _scope(project):
    return S.build_write_scope(str(project), ["src/pkg/mod.py", "docs/notes.md"], ["tests/"],
                               str(project / "ai" / "state"))


# --- classification (L-09) --------------------------------------------------------

@pytest.mark.parametrize("name,write", [
    ("write_file", True), ("create", True), ("makedirs", True), ("search_and_replace", True),
    ("bulk_rewrite", True),          # unknown tool with a write verb: fail-closed
    ("read_file", False), ("list_directory", False), ("search", False), ("count-matches", False),
])
def test_is_write_tool_is_fail_closed(name, write):
    assert S.is_write_tool(name) is write


def test_readonly_classification_shared_with_mcp_client():
    from mcp_client import MCPClient
    for name in ("read", "list", "search_text", "search_and_replace", "create", "bulk_rewrite"):
        assert MCPClient({})._is_readonly_tool(name) is S.is_readonly_tool(name)


# --- deliverable extraction ----------------------------------------------------------

def test_deliverables_from_t03_prompt():
    assert S.extract_deliverable_paths(PROMPT) == ["src/pkg/mod.py", "docs/notes.md"]


def test_non_prompt_task_has_no_scope():
    assert S.extract_deliverable_paths(NOT_A_PROMPT) is None
    assert S.extract_deliverable_paths("implement the login module") is None


def test_prompt_without_deliverables_gives_empty_list():
    assert S.extract_deliverable_paths('```yaml\nprompt_info:\n  id: "p"\n```\n') == []


# --- scope check (FR-05-01) ------------------------------------------------------------

@pytest.mark.parametrize("tool,arguments", [
    ("write_file", {"path": "src/pkg/mod.py", "content": ""}),
    ("create", {"files": [{"path": "docs/notes.md", "content": ""}]}),
    ("write_file", {"path": "tests/test_mod.py", "content": ""}),
    ("write_file", {"path": "tests/unit/deep/test_x.py", "content": ""}),
    ("write_file", {"path": "ai/state/work-summary.txt", "content": ""}),
    ("create_directory", {"path": "src/pkg"}),
    ("mkdir", {"path": "src"}),
    ("read_file", {"path": "src/other.py"}),
])
def test_allowed_writes(project, tool, arguments):
    assert S.check(tool, arguments, str(project), _scope(project)) is None


@pytest.mark.parametrize("tool,arguments,bad", [
    ("write_file", {"path": "src/other.py", "content": ""}, "src/other.py"),
    ("edit", {"files": [{"path": "README.md", "edits": []}]}, "README.md"),
    ("move", {"moves": [{"source": "src/pkg/mod.py", "destination": "src/elsewhere.py"}]}, "src/elsewhere.py"),
    ("delete", {"paths": ["setup.py"]}, "setup.py"),
    ("create_directory", {"path": "build"}, "build"),
    ("bulk_rewrite", {"path": "src/other.py"}, "src/other.py"),
])
def test_rejected_writes_name_the_path(project, tool, arguments, bad):
    v = S.check(tool, arguments, str(project), _scope(project))
    assert v is not None and v.path == bad and v.reason == "outside the declared scope"
    assert v.message.startswith(f"write outside the declared scope: {bad}; allowed: ")
    assert "src/pkg/mod.py" in v.message and "tests/" in v.message


def test_project_root_containment_still_applies(project):
    v = S.check("write_file", {"path": "/outside/x.py"}, str(project), _scope(project))
    assert v is not None and v.reason == "outside the project root"


def test_free_text_task_keeps_root_containment(orch, project):
    assert orch._validate_write_scope("write_file", {"path": "src/any.py"}, str(project)) is None
    assert orch._validate_write_scope("write_file", {"path": "/outside/x.py"}, str(project))


# --- wiring -------------------------------------------------------------------------------

class _Records(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(record.getMessage())


def test_run_phase_rejects_and_logs_out_of_scope_write(orch, project):
    import providers as P

    class Script:
        def __init__(self):
            self.steps = [
                P.Completion(text="", tool_calls=[P.ToolCall("aaaaaaaa1", "write_file",
                                                             {"path": "src/other.py", "content": "x"})]),
                P.Completion(text="", tool_calls=[P.ToolCall("aaaaaaaa2", "write_file",
                                                             {"path": "src/pkg/mod.py", "content": "y"})]),
                P.Completion(text="Wrote src/pkg/mod.py"),
            ]
            self.seen = []

        async def complete(self, model, messages, tools, max_tokens=None):
            self.seen.append([dict(m) for m in messages])
            return self.steps.pop(0)

    class MCP:
        def get_openai_tools(self, readonly=False):
            return [{"type": "function", "function": {"name": "write_file", "description": "", "parameters": {"type": "object"}}}]

        async def call_tool(self, name, arguments):
            os.makedirs(os.path.dirname(arguments["path"]), exist_ok=True)
            with open(arguments["path"], "w") as fh:
                fh.write(arguments["content"])
            return "ok"

    log = logging.getLogger("engine-test-scope")
    log.setLevel(logging.INFO)
    rec = _Records()
    log.addHandler(rec)
    script = Script()
    try:
        rc, _, _ = asyncio.run(orch.run_phase(
            script, MCP(), "m", {"instructions": "w {{TOOLS}}"}, "task", 5,
            str(project / "ai" / "state"), log, phase_label="WORKER", project_root=str(project),
            write_scope=_scope(project)))
    finally:
        log.removeHandler(rec)
    assert rc == 0
    assert not (project / "src" / "other.py").exists()
    assert (project / "src" / "pkg" / "mod.py").read_text() == "y"
    tool_result = next(m for m in script.seen[1] if m["role"] == "tool")
    assert "write outside the declared scope: src/other.py" in tool_result["content"]
    assert "write rejected tool=write_file path=src/other.py reason=outside the declared scope" in rec.lines


def test_reviewer_gets_absolute_deliverables_block(orch, log, project):
    state = project / "ai" / "state"
    (project / "src" / "a.py").write_text("x = 1\n")
    (state / "work-summary.txt").write_text("Wrote src/a.py\n")
    block = orch._deliverables_block_for(str(state), log)
    assert block.startswith("[DELIVERABLES]")
    assert f"  - {project / 'src' / 'a.py'}" in block
    (state / "work-summary.txt").write_text("nothing\n")
    assert orch._deliverables_block_for(str(state), log) == ""
