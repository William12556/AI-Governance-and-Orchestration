"""
Work-item stage tracking (design-14e05e35 §8.0; change-ee5357ec).

The stage of each work item (UUID) is derived from its documents in
ai/workspace/, using the manifest's stage evidence and paths; nothing else
records it (FR-08-01). Operator approvals count only when committed: they are
read from git HEAD, so uncommitted edits to ai/approvals.yaml are ignored
(design §8.3). This module only reads files and git.
"""

from __future__ import annotations

import glob
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass, field

import yaml

APPROVALS_FILE = "ai/approvals.yaml"
WORKSPACE = os.path.join("ai", "workspace")
UUID_RE = re.compile(r"^[0-9a-f]{8}$")


class NotAGitRepository(Exception):
    """Approvals need git; the project is not a git working tree."""


@dataclass
class Document:
    stage: str
    path: str            # project-relative
    status: str | None
    closed: bool


@dataclass
class WorkItem:
    uuid: str
    path: str | None = None                       # manifest path name
    documents: list[Document] = field(default_factory=list)
    approvals: list[str] = field(default_factory=list)
    current_stage: str | None = None              # None: every stage complete
    missing: list[str] = field(default_factory=list)
    anomalies: list[str] = field(default_factory=list)


@dataclass
class Report:
    work_items: dict[str, WorkItem]
    warnings: list[str]

    def to_json(self) -> str:
        return json.dumps({"work_items": {k: asdict(v) for k, v in sorted(self.work_items.items())},
                           "warnings": self.warnings}, indent=2)


# --- approvals -----------------------------------------------------------------

def _git(project_root: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", project_root, *args], capture_output=True, text=True)


def is_git_repository(project_root: str) -> bool:
    try:
        return _git(project_root, "rev-parse", "--is-inside-work-tree").stdout.strip() == "true"
    except OSError:
        return False


def parse_approvals(text: str) -> set[tuple[str, str]]:
    """(uuid, stage) pairs from approvals.yaml content; malformed entries are skipped."""
    try:
        data = yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return set()
    entries = data.get("approvals") if isinstance(data, dict) else None
    out: set[tuple[str, str]] = set()
    for e in entries or []:
        if isinstance(e, dict) and e.get("uuid") and e.get("stage"):
            out.add((str(e["uuid"]), str(e["stage"])))
    return out


def committed_approvals(project_root: str) -> set[tuple[str, str]]:
    """Approvals in git HEAD. Raises NotAGitRepository outside a git working tree."""
    if not is_git_repository(project_root):
        raise NotAGitRepository(f"{project_root} is not a git repository; approvals cannot be read")
    proc = _git(project_root, "show", f"HEAD:{APPROVALS_FILE}")
    return parse_approvals(proc.stdout) if proc.returncode == 0 else set()


def _uncommitted_approvals(project_root: str) -> bool:
    if not os.path.exists(os.path.join(project_root, APPROVALS_FILE)):
        return False
    proc = _git(project_root, "status", "--porcelain", "--", APPROVALS_FILE)
    return bool(proc.stdout.strip())


# --- documents ----------------------------------------------------------------------

def _status(path: str, field_path: str) -> str | None:
    """Value at a dotted path in the document's fenced YAML blocks (or a plain YAML file)."""
    try:
        with open(path) as fh:
            raw = fh.read()
    except OSError:
        return None
    blocks = re.findall(r"```yaml\n(.*?)```", raw, re.DOTALL) or [raw]
    for block in blocks:
        try:
            doc = yaml.safe_load(block)
        except yaml.YAMLError:
            continue
        value = doc
        for key in field_path.split("."):
            value = value.get(key) if isinstance(value, dict) else None
        if value not in (None, ""):
            return str(value)
    return None


def _documents(project_root: str, manifest) -> dict[str, list[Document]]:
    """Every evidence document, grouped by UUID."""
    found: dict[str, list[Document]] = {}
    pattern_re = {}
    for st in manifest.stages:
        ev = st.evidence
        if not ev:
            continue
        pattern_re[st.id] = re.compile(rf"^{re.escape(ev['prefix'])}-([0-9a-f]{{8}})-.*\.md$")
        for closed in (False, True):
            folder = os.path.join(project_root, WORKSPACE, ev["folder"], *(["closed"] if closed else []))
            for path in sorted(glob.glob(os.path.join(folder, f"{ev['prefix']}-*.md"))):
                m = pattern_re[st.id].match(os.path.basename(path))
                if not m:
                    continue
                status = _status(path, ev["status_field"]) if ev.get("status_field") else None
                found.setdefault(m.group(1), []).append(
                    Document(stage=st.id, path=os.path.relpath(path, project_root),
                             status=status, closed=closed))
    return found


def _complete_evidence(stage, docs: list[Document]) -> bool:
    ev = stage.evidence
    mine = [d for d in docs if d.stage == stage.id]
    if not mine:
        return False
    if not ev.get("status_field"):
        return True
    return any(d.status in ev["complete_statuses"] for d in mine)


def _evaluate(item: WorkItem, manifest, approvals: set[tuple[str, str]]) -> None:
    """Fill path, current_stage, missing and anomalies for one work item."""
    stage_ids = [s.id for s in manifest.stages]
    present = {d.stage for d in item.documents}
    candidates = [(stage_ids.index(p["detect"]), name) for name, p in manifest.paths.items()
                  if p["detect"] in present]
    if not candidates:
        item.anomalies.append("no document selects a stage path")
        return
    item.path = min(candidates)[1]
    path_stages = [manifest.stage(s) for s in manifest.paths[item.path]["stages"]]
    item.approvals = sorted(st for (u, st) in approvals if u == item.uuid)

    def complete(st) -> bool:
        if st.evidence and not _complete_evidence(st, item.documents):
            return False
        if st.approval and (item.uuid, st.id) not in approvals:
            return False
        return bool(st.evidence or st.approval)

    done = [complete(st) for st in path_stages]
    # A stage with neither evidence nor approval (the loop stage) is complete
    # once a later stage on the path is complete.
    for i, st in enumerate(path_stages):
        if not (st.evidence or st.approval):
            done[i] = any(done[i + 1:])
    for i, st in enumerate(path_stages):
        if not done[i]:
            item.current_stage = st.id
            item.missing = _missing_for(st, item, approvals)
            break

    for d in item.documents:
        st = manifest.stage(d.stage)
        if d.closed and st.evidence.get("status_field") and d.status not in st.evidence["complete_statuses"]:
            item.anomalies.append(f"{d.path}: closed with status '{d.status}'")
    for st in path_stages:
        mine = [d for d in item.documents if d.stage == st.id]
        if any(d.closed for d in mine) and any(not d.closed for d in mine):
            item.anomalies.append(f"{st.id}: documents in both the active and the closed folder")


def _missing_for(st, item: WorkItem, approvals: set[tuple[str, str]]) -> list[str]:
    missing: list[str] = []
    ev = st.evidence
    if ev and not _complete_evidence(st, item.documents):
        what = f"{ev['folder']}/{ev['prefix']}-{item.uuid}-*.md"
        if ev.get("status_field"):
            found = [d.status for d in item.documents if d.stage == st.id]
            what += f" with {ev['status_field']} in [{', '.join(ev['complete_statuses'])}]"
            if found:
                what += f" (found: {', '.join(str(f) for f in found)})"
        missing.append(f"{st.id}: document {what}")
    if st.approval and (item.uuid, st.id) not in approvals:
        missing.append(f"{st.id}: operator approval (python ai/engine/src/approve.py {item.uuid} {st.id})")
    if not missing and st.owner == "loop":
        missing.append(f"{st.id}: engine loop run")
    return missing


# --- public API ------------------------------------------------------------------------

def scan(project_root: str, manifest) -> Report:
    """Derive every work item's stage. Read-only."""
    warnings: list[str] = []
    try:
        approvals = committed_approvals(project_root)
        if _uncommitted_approvals(project_root):
            warnings.append(f"uncommitted changes to {APPROVALS_FILE} are ignored; "
                            f"record approvals with ai/engine/src/approve.py")
    except NotAGitRepository as e:
        approvals = set()
        warnings.append(str(e))
    items: dict[str, WorkItem] = {}
    for uuid, docs in _documents(project_root, manifest).items():
        item = WorkItem(uuid=uuid, documents=docs)
        _evaluate(item, manifest, approvals)
        items[uuid] = item
    return Report(work_items=items, warnings=warnings)


def is_tracked_task(project_root: str, task_path: str | None) -> bool:
    """A T03 prompt file inside ai/workspace/ is a tracked work item."""
    if not task_path or not os.path.isfile(task_path):
        return False
    workspace = os.path.abspath(os.path.join(project_root, WORKSPACE))
    return os.path.abspath(task_path).startswith(workspace + os.sep)


def prerun_missing(project_root: str, manifest, uuid: str) -> list[str]:
    """
    What is missing before the work item may enter the loop stage (FR-08-05).
    Empty when the run may start.
    """
    if not is_git_repository(project_root):
        return [f"{project_root} is not a git repository; approvals cannot be verified"]
    report = scan(project_root, manifest)
    item = report.work_items.get(uuid)
    if item is None:
        return [f"work item {uuid}: no documents found in {WORKSPACE}/"]
    if item.path is None:
        return [f"work item {uuid}: {'; '.join(item.anomalies)}"]
    loop_id = manifest.loop_stage().id
    path_stages = manifest.paths[item.path]["stages"]
    if loop_id not in path_stages:
        return [f"work item {uuid}: path '{item.path}' has no {loop_id} stage"]
    before = path_stages[:path_stages.index(loop_id)]
    approvals = committed_approvals(project_root)
    missing: list[str] = []
    for sid in before:
        st = manifest.stage(sid)
        missing += _missing_for(st, item, approvals)
    return missing


def main() -> None:
    """Command line: print the stage report for the project in the current directory."""
    import argparse
    import sys

    from manifest import ManifestError, load_manifest, locate_manifest

    p = argparse.ArgumentParser(description="Report the stage of every work item.")
    p.add_argument("--json", action="store_true", help="print the report as JSON")
    args = p.parse_args()
    try:
        manifest = load_manifest(locate_manifest())
    except ManifestError as e:
        print(json.dumps({"error": f"manifest error: {e}"}) if args.json else f"manifest error: {e}",
              file=sys.stdout if args.json else sys.stderr)
        sys.exit(1)
    report = scan(os.getcwd(), manifest)
    if args.json:
        print(report.to_json())
        return
    for w in report.warnings:
        print(f"warning: {w}")
    for uuid, item in sorted(report.work_items.items()):
        state = item.current_stage or "complete"
        print(f"{uuid}  {item.path or '-'}  {state}")
        for m in item.missing:
            print(f"    missing: {m}")
        for a in item.anomalies:
            print(f"    anomaly: {a}")


if __name__ == "__main__":
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
