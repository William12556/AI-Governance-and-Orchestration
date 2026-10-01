"""Tests for manifest.py, gates.py and their orchestrator wiring (change-e58fd295, design-14e05e35 §5.0, §6.0).

No model or network is used. Command gates run short `python -c` commands.
"""

import asyncio
import copy
import io
import logging
import os
import subprocess
import sys
import time

import pytest
import yaml

import gates as G
import manifest as M

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SE_MANIFEST = os.path.join(REPO, "ai", "governance", "software-engineering", "manifest.yaml")
PY = sys.executable


def _se_data():
    with open(SE_MANIFEST) as fh:
        return yaml.safe_load(fh)


def _write_manifest(tmp_path, data, name="model"):
    d = tmp_path / "governance" / name
    d.mkdir(parents=True, exist_ok=True)
    p = d / "manifest.yaml"
    p.write_text(yaml.safe_dump(data))
    return str(p)


def _loop_only(data):
    data = copy.deepcopy(data)
    data["run_types"] = {"loop": data["run_types"]["loop"]}
    return data


# --- manifest -----------------------------------------------------------------

def test_se_manifest_loads_and_reproduces_current_flow():
    m = M.load_manifest(M.locate_manifest())
    assert m.name == "software-engineering"
    assert m.loop_stage().id == "implement"
    assert m.loop_stage().gates == ["syntax", "pytest", "reviewer"]
    assert m.loop_stage().on_blocked == "prompt"
    assert m.next_approval_stage("implement").id == "accept"
    assert m.writable_paths == ["tests/"]
    for run_type in ("loop", "audit"):
        work, review = m.recipe_paths(run_type)
        assert os.path.isfile(work) and os.path.isfile(review)
    assert "recipes" in m.recipe_paths("audit")[0].replace(os.sep, "/").split("/software-engineering/")[1]


def _mutate(path_expr, value):
    def apply(d):
        target = d
        keys = path_expr.split(".")
        for k in keys[:-1]:
            target = target[int(k)] if isinstance(target, list) else target[k]
        last = keys[-1]
        if value is _DELETE:
            del target[last]
        elif isinstance(target, list):
            target[int(last)] = value
        else:
            target[last] = value
        return d
    return apply


_DELETE = object()


@pytest.mark.parametrize("mutation,fragment", [
    (_mutate("model", _DELETE), "model"),
    (_mutate("stages.0.owner", "robot"), "stages[0].owner"),
    (_mutate("stages.3.gates", ["syntax", "lint", "reviewer"]), "gate 'lint'"),
    (_mutate("stages.3.gates", ["syntax", "pytest"]), "requires the reviewer gate"),
    (_mutate("stages.3.on_blocked", "accept"), "on_blocked"),
    (_mutate("stages.1.id", "issue"), "duplicate stage id"),
    (_mutate("stages.0.evidence.folder", "nowhere"), "evidence.folder"),
    (_mutate("gates.pytest.command", ""), "gates.pytest.command"),
    (_mutate("gates.syntax", {"command": "x"}), "reserved"),
    (_mutate("workspace_folders", ["../outside"]), "workspace_folders"),
    (_mutate("paths.full.stages", ["change", "issue", "prompt", "implement", "accept"]), "stage order"),
    (_mutate("paths.full.detect", "nothing"), "paths.full.detect"),
    (_mutate("run_types.loop.worker", "missing-recipe.yaml"), "run_types.loop.worker"),
])
def test_invalid_manifest_names_the_field(tmp_path, mutation, fragment):
    path = _write_manifest(tmp_path, mutation(_loop_only(_se_data())))
    with pytest.raises(M.ManifestError):
        M.load_manifest(path)
    try:
        M.load_manifest(path)
    except M.ManifestError as e:
        assert path in str(e) and fragment in str(e)


def test_valid_fixture_loads(tmp_path):
    m = M.load_manifest(_write_manifest(tmp_path, _loop_only(_se_data())))
    assert m.loop_stage().id == "implement"


def test_locate_manifest_requires_exactly_one(tmp_path):
    root = tmp_path / "governance"
    root.mkdir()
    with pytest.raises(M.ManifestError):
        M.locate_manifest(str(root))
    one = _write_manifest(tmp_path, _loop_only(_se_data()), "a")
    assert M.locate_manifest(str(root)) == one
    _write_manifest(tmp_path, _loop_only(_se_data()), "b")
    with pytest.raises(M.ManifestError):
        M.locate_manifest(str(root))


def test_unreadable_yaml_is_reported(tmp_path):
    d = tmp_path / "governance" / "x"
    d.mkdir(parents=True)
    (d / "manifest.yaml").write_text("model: [unclosed\n")
    with pytest.raises(M.ManifestError):
        M.load_manifest(str(d / "manifest.yaml"))


# --- gates ----------------------------------------------------------------------

def test_build_command_expands_placeholders():
    argv = G.build_command("{python} -m pytest -q {targets}", "/py", "/root", ["a", "b c"])
    assert argv == ["/py", "-m", "pytest", "-q", "a", "b c"]
    assert G.build_command("{python} x {project_root}/y", "p", "/r", []) == ["p", "x", "/r/y"]


@pytest.mark.parametrize("command,status", [
    ('{python} -c "import sys; sys.exit(0)"', "PASS"),
    ('{python} -c "import sys; sys.exit(2)"', "FAIL"),
    ("/nonexistent/tool --check", "UNCHECKED"),
])
def test_command_gate_outcomes(tmp_path, log, command, status):
    block = G.run_command_gate("lint", {"command": command, "python": PY}, [], str(tmp_path), log)
    assert block.startswith(f"[LINT GATE: {status}]")
    assert block.rstrip().endswith("[END LINT GATE]")
    assert G.gate_status(block) == status


def test_command_gate_timeout_is_unchecked(tmp_path, log):
    block = G.run_command_gate("slow", {"command": '{python} -c "import time; time.sleep(5)"',
                                        "python": PY, "timeout_seconds": 0.5}, [], str(tmp_path), log)
    assert G.gate_status(block) == "UNCHECKED"


def test_gate_status_of_empty_block_is_skipped():
    assert G.gate_status("") == "SKIPPED"


def _split_project(project):
    (project / "src" / "split.py").write_text("def split_into_chunks(items, n):\n    return []\n")
    (project / "tests" / "test_split.py").write_text("def test_x():\n    assert True\n")
    (project / "ai" / "state" / "work-summary.txt").write_text("Wrote src/split.py\n")


def test_pytest_gate_uses_configured_command_and_interpreter(orch, log, project):
    _split_project(project)
    spec = {"command": '{python} -c "import sys; sys.exit(3)" {targets}', "python": PY}
    block = orch._run_pytest_gate(str(project / "ai" / "state"), log, str(project), spec=spec)
    assert block.startswith("[TEST GATE: FAIL]")
    assert "test_split.py" in block


def test_pytest_gate_default_command_unchanged(orch, log, project, monkeypatch):
    _split_project(project)
    seen = {}

    def fake_run(argv, **kw):
        seen["argv"] = argv
        return subprocess.CompletedProcess(argv, 0, "1 passed", "")

    monkeypatch.setattr(G.subprocess, "run", fake_run)
    block = orch._run_pytest_gate(str(project / "ai" / "state"), log, str(project))
    assert seen["argv"][:4] == [PY, "-m", "pytest", "-q"]
    assert block.startswith("[TEST GATE: PASS]")


def test_gate_specs_merge_manifest_and_config(orch, project):
    m = M.load_manifest(M.locate_manifest())
    specs = orch._resolve_gate_specs(m, {"gates": {"python": "venv/bin/python",
                                                    "pytest": {"timeout_seconds": 60}}})
    assert specs["pytest"]["command"] == "{python} -m pytest -q {targets}"
    assert specs["pytest"]["timeout_seconds"] == 60
    assert specs["pytest"]["python"] == os.path.join(str(project), "venv", "bin", "python")
    assert orch._resolve_gate_specs(m, {})["pytest"]["python"] == PY
    with pytest.raises(orch.ConfigError):
        orch._resolve_gate_specs(m, {"gates": {"lint": {"command": "x"}}})


# --- loop wiring ------------------------------------------------------------------

class _Records(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(record.getMessage())


def test_failing_command_gate_overrides_ship_and_gates_are_logged(orch, project, monkeypatch):
    state = project / "ai" / "state"
    deliverable = project / "src" / "mod.py"
    deliverable.write_text("x = 1\n")
    log = logging.getLogger("engine-test-gates")
    log.setLevel(logging.INFO)
    rec = _Records()
    log.addHandler(rec)

    async def fake_run_phase(client, mcp, model, recipe, task, max_iter, state_dir, log, **kw):
        if kw["phase_label"] == "WORKER":
            (state / "work-summary.txt").write_text(f"Wrote {deliverable}\n")
            return 0, "done", set()
        (state / "review-result.txt").write_text("SHIP")
        return 0, "SHIP", {str(deliverable)}

    def no_pytest(*a, **k):
        raise AssertionError("pytest gate must not run when not declared")

    monkeypatch.setattr(orch, "run_phase", fake_run_phase)
    monkeypatch.setattr(orch, "_run_pytest_gate", no_pytest)
    monkeypatch.setattr(orch.sys, "stdin", io.StringIO())
    try:
        rc = asyncio.run(orch.run_loop(
            None, None, "w", "r", {}, {}, "task", 1, 2, str(state), log,
            project_root=str(project), gates=["syntax", "lint", "reviewer"],
            gate_specs={"lint": {"command": '{python} -c "import sys; sys.exit(1)"', "python": PY}}))
    finally:
        log.removeHandler(rec)
    assert rc == 1
    assert not (state / ".complete").exists()
    assert "lint gate failed" in (state / "review-feedback.txt").read_text()
    assert any(l.startswith("gate=syntax type=built_in result=") for l in rec.lines)
    assert "gate=lint type=command result=FAIL" in rec.lines
    assert "gate=reviewer type=reviewer_verdict result=SHIP" in rec.lines


def test_awaiting_approval_after_ship(orch, log, project):
    m = M.load_manifest(M.locate_manifest())
    state = project / "ai" / "state"
    orch._write_awaiting_approval(str(state), m, "implement", "53c6f252", log)
    text = (state / "awaiting-approval.md").read_text()
    assert "Work item: 53c6f252" in text and "Stage: accept" in text
    orch._write_awaiting_approval(str(state), m, "implement", None, log)
    assert "untracked task" in (state / "awaiting-approval.md").read_text()


def test_blocked_names_return_stage_once_for_tracked_work_item(orch, log, project):
    m = M.load_manifest(M.locate_manifest())
    state = project / "ai" / "state"
    blocked = state / "BLOCKED.md"
    since = time.time() - 1
    blocked.write_text("# BLOCKED\n\nstall\n")
    orch._annotate_blocked_return(str(state), m.loop_stage(), None, since, log)
    assert "Return to stage" not in blocked.read_text()
    orch._annotate_blocked_return(str(state), m.loop_stage(), "e58fd295", since, log)
    orch._annotate_blocked_return(str(state), m.loop_stage(), "e58fd295", since, log)
    assert blocked.read_text().count("Return to stage: prompt (work item e58fd295)") == 1


def test_stale_blocked_file_is_not_annotated(orch, log, project):
    m = M.load_manifest(M.locate_manifest())
    state = project / "ai" / "state"
    (state / "BLOCKED.md").write_text("# BLOCKED\n\nold\n")
    orch._annotate_blocked_return(str(state), m.loop_stage(), "e58fd295", time.time() + 60, log)
    assert "Return to stage" not in (state / "BLOCKED.md").read_text()


@pytest.mark.parametrize("task,expected", [
    ("ai/workspace/prompt/prompt-e58fd295-manifest-gates.md", "e58fd295"),
    ("prompt-53c6f252-providers.md", "53c6f252"),
    ("implement the login module", None),
    (None, None),
    ("ai/workspace/change/change-e58fd295-x.md", None),
])
def test_work_item_uuid(orch, task, expected):
    assert orch._work_item_uuid(task) == expected


# --- workspace folders (bootstrap.sh, propagate.sh) ------------------------------------

def _shell_function(script):
    with open(os.path.join(REPO, "bin", script)) as fh:
        lines = fh.read().splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("create_workspace_folders()"))
    end = next(i for i in range(start, len(lines)) if lines[i] == "}")
    return "\n".join(lines[start:end + 1])


@pytest.mark.parametrize("script", ["bootstrap.sh", "propagate.sh"])
def test_workspace_folders_created_and_existing_paths_untouched(tmp_path, script):
    ws = tmp_path / "workspace"
    (ws / "issues").mkdir(parents=True)
    (ws / "issues" / "keep.md").write_text("keep")
    (ws / "trace").write_text("a file in the way")
    code = _shell_function(script) + f'\ncreate_workspace_folders "{SE_MANIFEST}" "{ws}"\n'
    out = subprocess.run(["bash", "-c", code], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    for folder in _se_data()["workspace_folders"]:
        if folder != "trace":
            assert (ws / folder).is_dir(), folder
    assert (ws / "issues" / "keep.md").read_text() == "keep"
    assert (ws / "trace").is_file()
    assert "trace exists and is not a directory" in out.stdout
