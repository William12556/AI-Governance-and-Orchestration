"""Tests for bin/bootstrap.sh, bin/propagate.sh and bin/migrate-layout.sh and
for the audit review recipe text (change-541f5c58, T1 to T7; audit-14e05e35
L-10; audit-5bcd46ad L-12, H-01 option).

The scripts run with bash in tmp_path. bootstrap.sh gets a curl stand-in on
PATH that serves a local tarball. propagate.sh runs from a copy of bin/ and
ai/, so the framework repository is never a target. Where rsync is not
installed a no-op stand-in is used: in every propagate case the target is up
to date, so the copy has nothing to transfer.
"""

import os
import shutil
import stat
import io
import subprocess
import tarfile

import pytest
import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL = "software-engineering"
MANIFEST_REL = os.path.join("ai", "governance", MODEL, "manifest.yaml")

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="bash not available")

_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".DS_Store")


def _run(argv, env=None, cwd=None):
    return subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd,
                          stdin=subprocess.DEVNULL)


def _script(directory, name, body):
    path = directory / name
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def _declared_folders():
    with open(os.path.join(REPO, MANIFEST_REL), encoding="utf-8") as fh:
        return yaml.safe_load(fh)["workspace_folders"]


def _flow_style(manifest_path):
    """Rewrite the manifest's workspace_folders block list as a single-line flow list."""
    with open(manifest_path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith("workspace_folders:"))
    end = start + 1
    items = []
    while end < len(lines) and (lines[end].startswith((" ", "\t", "#")) or not lines[end].strip()):
        stripped = lines[end].strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].split("#")[0].strip().strip("\"'"))
        end += 1
    assert items == _declared_folders()
    quoted = [items[0], f'"{items[1]}"', f"'{items[2]}'"] + items[3:]
    # the trailing comment holds brackets: the list ends at its own closing bracket
    lines[start:end] = [f"workspace_folders: [{', '.join(quoted)}]  # flow style [see notes]", ""]
    with open(manifest_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    with open(manifest_path, encoding="utf-8") as fh:
        assert yaml.safe_load(fh)["workspace_folders"] == items


def _block_style(manifest_path, style):
    """
    Replace the manifest's workspace_folders list with the folders a and b
    (change-f68d51c2, FR-07): 'col0' writes the items at column 0 followed by
    another top-level key; 'crlf' writes an indented list and CRLF line ends.
    """
    with open(manifest_path, encoding="utf-8", newline="") as fh:
        lines = fh.read().split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith("workspace_folders:"))
    end = start + 1
    while end < len(lines) and (lines[end].startswith((" ", "\t", "#", "-")) or not lines[end].strip()):
        end += 1
    indent = "" if style == "col0" else "  "
    lines[start:end] = ["workspace_folders:", f"{indent}- a", f"{indent}- b", ""]
    newline = "\r\n" if style == "crlf" else "\n"
    with open(manifest_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(newline.join(lines))
    with open(manifest_path, encoding="utf-8") as fh:
        assert yaml.safe_load(fh)["workspace_folders"] == ["a", "b"]


def _workspace_names(project):
    return sorted(p.name for p in (project / "ai" / "workspace").iterdir())


# --- bootstrap.sh -------------------------------------------------------------------------------

def _tarball(tmp_path, layout):
    """
    A release tarball: 'new' holds the framework ai/, 'old' has no ai/engine/, 'flow' a flow list;
    'col0' and 'crlf' the folder lists of _block_style; 'escape' holds ai/engine/ and a member
    '../escaped.txt' (change-f68d51c2).
    """
    stage = tmp_path / f"stage-{layout}"
    archive = tmp_path / f"release-{layout}.tar.gz"
    if layout == "escape":
        with tarfile.open(archive, "w:gz") as tar:
            for name in ("ai/engine/src/orchestrator.py", "../escaped.txt"):
                info = tarfile.TarInfo(name)
                info.size = 2
                tar.addfile(info, io.BytesIO(b"x\n"))
        return archive
    if layout == "old":
        (stage / "ai" / "ael").mkdir(parents=True)
        (stage / "ai" / "ael" / "config.yaml").write_text("loop: {}\n")
        (stage / "ai" / "governance.md").write_text("# old layout\n")
    else:
        shutil.copytree(os.path.join(REPO, "ai"), stage / "ai", ignore=_IGNORE)
        for name in ("state", "logs", "workspace", "config.yaml", "dashboard-alerts.md"):
            target = stage / "ai" / name
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
        if layout == "flow":
            _flow_style(stage / MANIFEST_REL)
        elif layout in ("col0", "crlf"):
            _block_style(stage / MANIFEST_REL, layout)
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(stage / "ai", arcname="ai")
    return archive


def _bootstrap(tmp_path, archive, **extra_env):
    project = tmp_path / "project"
    project.mkdir()
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    _script(fake_bin, "curl", """#!/usr/bin/env bash
# curl stand-in: the release query prints a tag; a download copies the local tarball.
out=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --output) out="$2"; shift 2 ;;
        *) last="$1"; shift ;;
    esac
done
if [[ -n "${out}" && -n "${FAKE_CURL_FAIL:-}" ]]; then
    exit 22  # change-f68d51c2: a failed download
elif [[ -n "${out}" ]]; then
    cp "${FAKE_TARBALL}" "${out}"
else
    echo '{ "tag_name": "v9.9.9" }'
fi
""")
    env = dict(os.environ, PATH=f"{fake_bin}{os.pathsep}{os.environ['PATH']}", FAKE_TARBALL=str(archive),
               **extra_env)
    proc = _run(["bash", os.path.join(REPO, "bin", "bootstrap.sh"), str(project)], env=env)
    return project, proc


def test_t1_bootstrap_refuses_an_unreadable_archive(tmp_path):
    archive = tmp_path / "release-damaged.tar.gz"
    archive.write_text("this is not a gzip archive\n")
    project, proc = _bootstrap(tmp_path, archive)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "does not contain ai/engine/" in proc.stderr
    assert list(project.iterdir()) == []


def test_t1_bootstrap_refuses_a_tarball_without_engine(tmp_path):
    project, proc = _bootstrap(tmp_path, _tarball(tmp_path, "old"))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "does not contain ai/engine/" in proc.stderr
    assert "Nothing installed" in proc.stderr
    assert list(project.iterdir()) == []


@pytest.mark.parametrize("layout", ["new", "flow"])
def test_t2_bootstrap_installs_and_creates_workspace_folders(tmp_path, layout):
    project, proc = _bootstrap(tmp_path, _tarball(tmp_path, layout))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert (project / "ai" / "engine" / "src" / "orchestrator.py").is_file()
    assert (project / "ai" / "config.yaml").is_file()
    for folder in _declared_folders():
        assert (project / "ai" / "workspace" / folder).is_dir(), folder


def test_f68_t7_bootstrap_removes_tmpdir_after_failed_download(tmp_path):
    """T7 (change-f68d51c2, FR-04): the EXIT trap removes the temporary directory."""
    tmpdir = tmp_path / "tmpdir"
    tmpdir.mkdir()
    project, proc = _bootstrap(tmp_path, _tarball(tmp_path, "old"),
                               FAKE_CURL_FAIL="1", TMPDIR=str(tmpdir))
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert list(tmpdir.iterdir()) == []
    assert not (project / "ai").exists()


def test_f68_t8_bootstrap_removes_partial_ai_after_failed_extraction(tmp_path):
    """T8 (change-f68d51c2, FR-04): a failed extraction removes ai/ and the temporary directory."""
    tmpdir = tmp_path / "tmpdir"
    tmpdir.mkdir()
    project, proc = _bootstrap(tmp_path, _tarball(tmp_path, "escape"), TMPDIR=str(tmpdir))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "Error: extraction failed; ai/ removed" in proc.stderr
    assert not (project / "ai").exists()
    assert list(tmpdir.iterdir()) == []


@pytest.mark.parametrize("style", ["col0", "crlf"])
def test_f68_t12_bootstrap_reads_column_0_and_crlf_lists(tmp_path, style):
    """T12 (change-f68d51c2, FR-07): folders a and b exactly; no name ends in a carriage return."""
    project, proc = _bootstrap(tmp_path, _tarball(tmp_path, style))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert _workspace_names(project) == ["a", "b"]


# --- propagate.sh -------------------------------------------------------------------------------

@pytest.fixture
def framework(tmp_path):
    """A copy of bin/ and ai/ to run propagate.sh from, and the environment to run it in."""
    root = tmp_path / "framework"
    shutil.copytree(os.path.join(REPO, "bin"), root / "bin", ignore=_IGNORE)
    shutil.copytree(os.path.join(REPO, "ai"), root / "ai", ignore=_IGNORE)
    env = dict(os.environ)
    if shutil.which("rsync") is None:
        fake_bin = tmp_path / "fake-rsync"
        fake_bin.mkdir()
        _script(fake_bin, "rsync", "#!/usr/bin/env bash\n# no-op stand-in: the target is up to date\nexit 0\n")
        env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    return root, env


def _up_to_date_target(tmp_path, root):
    """A project whose ai/ equals the framework copy, with the seeds and every workspace folder."""
    project = tmp_path / "target"
    shutil.copytree(root / "ai", project / "ai", ignore=_IGNORE)
    shutil.copyfile(root / "ai" / "engine" / "config.template.yaml", project / "ai" / "config.yaml")
    seed = root / "ai" / "governance" / MODEL / "seed"
    shutil.copyfile(seed / "context.md", project / "ai" / "context.md")
    if not (project / "ai" / "task.md").exists():
        shutil.copyfile(seed / "task.md", project / "ai" / "task.md")
    with open(root / MANIFEST_REL, encoding="utf-8") as fh:
        folders = yaml.safe_load(fh)["workspace_folders"]
    for folder in folders:
        (project / "ai" / "workspace" / folder).mkdir(parents=True, exist_ok=True)
    return project, folders


def _leaf(folders):
    """A declared folder that has no declared folder below it."""
    return next(f for f in folders if not any(o.startswith(f + "/") for o in folders))


def _propagate(root, env, project, *flags):
    return _run(["bash", str(root / "bin" / "propagate.sh"), *flags, str(project)], env=env)


def test_t3_propagate_gates_workspace_folder_creation(tmp_path, framework):
    root, env = framework
    project, folders = _up_to_date_target(tmp_path, root)

    proc = _propagate(root, env, project)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "Target is up to date" in proc.stdout

    leaf = _leaf(folders)
    absent = project / "ai" / "workspace" / leaf
    absent.rmdir()
    proc = _propagate(root, env, project)  # stdin is not a terminal, no --yes
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert f"create       workspace/{leaf}/" in proc.stdout
    assert not absent.exists()

    proc = _propagate(root, env, project, "--yes")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert absent.is_dir()

    proc = _propagate(root, env, project)
    assert proc.returncode == 0 and "Target is up to date" in proc.stdout


def test_t4_propagate_plan_error_precedes_folder_creation(tmp_path, framework):
    root, env = framework
    project, folders = _up_to_date_target(tmp_path, root)
    absent = project / "ai" / "workspace" / _leaf(folders)
    absent.rmdir()
    (project / "ai-local" / "RELOCATED.md").mkdir(parents=True)  # a plan error
    proc = _propagate(root, env, project, "--yes")
    assert proc.returncode == 3, proc.stdout + proc.stderr
    assert "cannot proceed safely" in proc.stderr
    assert not absent.exists()


def test_t5_propagate_reads_a_flow_style_list(tmp_path, framework):
    root, env = framework
    _flow_style(root / MANIFEST_REL)
    project, folders = _up_to_date_target(tmp_path, root)
    shutil.rmtree(project / "ai" / "workspace")
    proc = _propagate(root, env, project, "--yes")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    for folder in folders:
        assert (project / "ai" / "workspace" / folder).is_dir(), folder


@pytest.mark.parametrize("style", ["col0", "crlf"])
def test_f68_t12_propagate_reads_column_0_and_crlf_lists(tmp_path, framework, style):
    """T12 (change-f68d51c2, FR-07): folders a and b exactly; no name ends in a carriage return."""
    root, env = framework
    _block_style(root / MANIFEST_REL, style)
    project, folders = _up_to_date_target(tmp_path, root)
    assert folders == ["a", "b"]
    shutil.rmtree(project / "ai" / "workspace")
    proc = _propagate(root, env, project, "--yes")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert _workspace_names(project) == ["a", "b"]


# --- migrate-layout.sh --------------------------------------------------------------------------

@pytest.mark.parametrize("value, warned", [("'ai/state'", None), ('"ai/state"', None),
                                           ("'custom/state'", "custom/state"),
                                           ('"custom/state"', "custom/state"),
                                           ("custom/state", "custom/state")])
def test_t6_migrate_layout_reads_single_quoted_state_dir(tmp_path, value, warned):
    project = tmp_path / "old-project"
    (project / "ai" / "ael").mkdir(parents=True)
    (project / "ai" / "ael" / "config.yaml").write_text(f"loop:\n  state_dir: {value}\n")
    proc = _run(["bash", os.path.join(REPO, "bin", "migrate-layout.sh"), str(project)])
    assert proc.returncode == 0, proc.stdout + proc.stderr
    warnings = [line for line in proc.stdout.splitlines() if line.startswith("warn ")]
    if warned is None:
        assert warnings == []
    else:
        assert len(warnings) == 1 and f'loop.state_dir is "{warned}"' in warnings[0]


# --- audit review recipe and guide --------------------------------------------------------------

def test_t7_audit_review_recipe_has_no_duration_limit_marker():
    recipe_path = os.path.join(REPO, "ai", "governance", MODEL, "recipes", "audit-review.yaml")
    with open(recipe_path, encoding="utf-8") as fh:
        text = fh.read()
    recipe = yaml.safe_load(text)
    assert recipe["version"] == "1.2.1"
    assert "DURATION_LIMIT" not in text
    assert "duration limit" in recipe["instructions"]  # the engine's role is stated
    with open(os.path.join(REPO, "ai", "engine", "doc", "guide-engine-operations.md"),
              encoding="utf-8") as fh:
        guide = fh.read()
    assert "DURATION_LIMIT" not in guide
    assert "TIMEOUT: iteration N" in guide
