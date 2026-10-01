"""Tests for stages.py, approve.py and the pre-run check (change-ee5357ec, design-14e05e35 §8.0)."""

import argparse
import asyncio
import os
import subprocess

import pytest

import approve as A
import manifest as M
import stages as ST

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
U = "1a2b3c4d"


@pytest.fixture
def se():
    return M.load_manifest(M.locate_manifest())


@pytest.fixture
def repo(project, monkeypatch):
    """The throwaway project as a git repository with one initial commit."""
    for k, v in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@example.com"),
                 ("GIT_COMMITTER_NAME", "t"), ("GIT_COMMITTER_EMAIL", "t@example.com")):
        monkeypatch.setenv(k, v)
    _git(project, "init", "-q")
    (project / "README.md").write_text("x\n")
    _git(project, "add", "README.md")
    _git(project, "commit", "-q", "-m", "init")
    return project


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True)


def _doc(root, folder, prefix, status_key=None, status=None, closed=False, uuid=U):
    d = root / "ai" / "workspace" / folder / ("closed" if closed else "")
    d.mkdir(parents=True, exist_ok=True)
    body = "Created: 2026 October 01\n\n```yaml\n"
    if status_key:
        body += f"{status_key}:\n  id: \"{prefix}-{uuid}\"\n  status: \"{status}\"\n"
    else:
        body += f"prompt_info:\n  id: \"prompt-{uuid}\"\n"
    body += "```\n"
    p = d / f"{prefix}-{uuid}-work.md"
    p.write_text(body)
    return p


def _commit_approval(root, stage, uuid=U):
    path = root / "ai" / "approvals.yaml"
    text = path.read_text() if path.exists() else "approvals:\n"
    path.write_text(text + f'  - {{ uuid: "{uuid}", stage: "{stage}" }}\n')
    _git(root, "add", "ai/approvals.yaml")
    _git(root, "commit", "-q", "-m", f"approve {stage}")


# --- derivation -------------------------------------------------------------------

def test_design_sourced_path_progresses_with_committed_approvals(repo, se):
    _doc(repo, "prompt", "prompt")
    item = ST.scan(str(repo), se).work_items[U]
    assert item.path == "design_sourced" and item.current_stage == "prompt"
    assert any("approve.py 1a2b3c4d prompt" in m for m in item.missing)
    _commit_approval(repo, "prompt")
    item = ST.scan(str(repo), se).work_items[U]
    assert item.current_stage == "implement" and item.missing == ["implement: engine loop run"]
    _commit_approval(repo, "accept")
    item = ST.scan(str(repo), se).work_items[U]
    assert item.current_stage is None and item.approvals == ["accept", "prompt"]


def test_full_path_reports_status_and_approval(repo, se):
    _doc(repo, "issues", "issue", "issue_info", "open")
    _doc(repo, "change", "change", "change_info", "proposed")
    _doc(repo, "prompt", "prompt")
    item = ST.scan(str(repo), se).work_items[U]
    assert item.path == "full" and item.current_stage == "change"
    assert any("change_info.status" in m and "found: proposed" in m for m in item.missing)
    assert any("operator approval" in m for m in item.missing)


def test_change_sourced_path_and_closed_documents(repo, se):
    _doc(repo, "change", "change", "change_info", "verified", closed=True)
    _doc(repo, "prompt", "prompt", closed=True)
    _commit_approval(repo, "change")
    _commit_approval(repo, "prompt")
    item = ST.scan(str(repo), se).work_items[U]
    assert item.path == "change_sourced" and item.current_stage == "implement"
    assert all(d.closed for d in item.documents)
    assert item.anomalies == []


def test_anomalies(repo, se):
    _doc(repo, "change", "change", "change_info", "proposed", closed=True)
    _doc(repo, "prompt", "prompt")
    _doc(repo, "prompt", "prompt", closed=True)
    item = ST.scan(str(repo), se).work_items[U]
    assert any("closed with status 'proposed'" in a for a in item.anomalies)
    assert any("prompt: documents in both" in a for a in item.anomalies)


def test_uncommitted_approval_is_ignored_and_reported(repo, se):
    _doc(repo, "prompt", "prompt")
    (repo / "ai" / "approvals.yaml").write_text(f'approvals:\n  - {{ uuid: "{U}", stage: "prompt" }}\n')
    report = ST.scan(str(repo), se)
    assert report.work_items[U].current_stage == "prompt"
    assert any("uncommitted changes to ai/approvals.yaml are ignored" in w for w in report.warnings)


def test_not_a_git_repository(project, se):
    _doc(project, "prompt", "prompt")
    report = ST.scan(str(project), se)
    assert any("not a git repository" in w for w in report.warnings)
    assert "not a git repository" in ST.prerun_missing(str(project), se, U)[0]


def test_report_json_is_serialisable(repo, se):
    _doc(repo, "prompt", "prompt")
    assert f'"{U}"' in ST.scan(str(repo), se).to_json()


# --- pre-run check (FR-08-05) ------------------------------------------------------

def test_prerun_missing_until_prompt_approved(repo, se):
    _doc(repo, "prompt", "prompt")
    assert ST.prerun_missing(str(repo), se, U)
    _commit_approval(repo, "prompt")
    assert ST.prerun_missing(str(repo), se, U) == []
    assert "no documents found" in ST.prerun_missing(str(repo), se, "deadbeef")[0]


def test_is_tracked_task(project):
    inside = _doc(project, "prompt", "prompt")
    outside = project / "prompt-1a2b3c4d-x.md"
    outside.write_text("x")
    assert ST.is_tracked_task(str(project), str(inside))
    assert not ST.is_tracked_task(str(project), str(outside))
    assert not ST.is_tracked_task(str(project), "implement x")


def _config(project):
    cfg = project / "config.yaml"
    cfg.write_text("omlx:\n  base_url: http://127.0.0.1:9/v1\n  api_key: local\n  default_model: m\n"
                   "loop:\n  state_dir: ai/state/fresh\n  max_iterations: 1\n")
    return str(cfg)


def test_engine_refuses_untracked_prerequisites_with_exit_3(orch, repo):
    prompt = _doc(repo, "prompt", "prompt")
    args = argparse.Namespace(config=_config(repo), mode="loop", task=str(prompt), model=None,
                              worker_model=None, reviewer_model=None, max_iterations=None, duration=None)
    assert asyncio.run(orch.main_async(args)) == 3
    assert not (repo / "ai" / "state" / "fresh").exists()


# --- approve.py ------------------------------------------------------------------------

def test_approve_records_and_commits(repo, se):
    _doc(repo, "prompt", "prompt")
    code, msg = A.approve(str(repo), U, "prompt", manifest=se)
    assert code == 0 and "approved and committed" in msg and "current stage: implement" in msg
    log = _git(repo, "log", "-1", "--format=%s").stdout.strip()
    assert log == f"approve: {U} prompt"
    assert (U, "prompt") in ST.committed_approvals(str(repo))
    assert _git(repo, "status", "--porcelain").stdout.strip() == "" or \
        "approvals.yaml" not in _git(repo, "status", "--porcelain").stdout
    code, msg = A.approve(str(repo), U, "prompt", manifest=se)
    assert code == 0 and "already approved" in msg


def test_approve_commits_only_the_approvals_file(repo, se):
    _doc(repo, "prompt", "prompt")
    (repo / "README.md").write_text("changed\n")
    _git(repo, "add", "README.md")
    assert A.approve(str(repo), U, "prompt", manifest=se)[0] == 0
    changed = _git(repo, "show", "--name-only", "--format=", "HEAD").stdout.split()
    assert changed == ["ai/approvals.yaml"]
    assert "README.md" in _git(repo, "diff", "--cached", "--name-only").stdout


@pytest.mark.parametrize("uuid,stage,fragment", [
    ("XYZ", "prompt", "not an 8-character"),
    (U, "nonsense", "unknown stage"),
    (U, "implement", "takes no approval"),
    ("deadbeef", "prompt", "no documents found"),
])
def test_approve_refusals(repo, se, uuid, stage, fragment):
    _doc(repo, "prompt", "prompt")
    code, msg = A.approve(str(repo), uuid, stage, manifest=se)
    assert code == 1 and fragment in msg


def test_approve_requires_git(project, se):
    _doc(project, "prompt", "prompt")
    code, msg = A.approve(str(project), U, "prompt", manifest=se)
    assert code == 1 and "not a git repository" in msg


# --- propagation -------------------------------------------------------------------------

def test_propagate_declares_approvals_file():
    with open(os.path.join(REPO, "bin", "propagate.sh")) as fh:
        text = fh.read()
    assert "--exclude='/approvals.yaml'" in text
    start = text.index("is_declared() {")
    func = text[start:text.index("\n}\n", start) + 3]
    out = subprocess.run(["bash", "-c", func + "\nis_declared approvals.yaml && echo yes"],
                         capture_output=True, text=True)
    assert out.stdout.strip() == "yes"
