"""Tests for the Layer 2 protocol checker (change-e4428fd5, issue-e4428fd5).

Covers class resolution through linter.resolve_class (audit-caab2052 M-03),
the closed-prompt self-containment downgrade (operator decision 2026-11-07),
type checks on YAML values (audit-caab2052 L-11), the superseded test status,
and one defective and one valid fixture per protocol check. Workspaces are
built under tmp_path; no network is used.
"""

import pytest
import yaml

import linter as L
import protocol_checker as P

U = "1a2b3c4d"


# --- helpers ------------------------------------------------------------------

def _write(ws, rel: str, data) -> str:
    path = ws / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    text = data if isinstance(data, str) else yaml.safe_dump(data, sort_keys=False)
    path.write_text("Created: 2026 November 7\n\n```yaml\n" + text + "```\n\n"
                    "## Version History\n\n| 1.0 | 2026-11-07 | x |\n\n"
                    "Copyright (c) 2026 William Watson. MIT License.\n")
    return str(path)


def _meta(schema_type):
    return {"template_version": "1.0", "schema_type": schema_type}


def _change(uuid=U, status="proposed", issue_ref=None, prompt_ref=None, schema_type="change"):
    docs = {"issue_ref": issue_ref or f"issue-{uuid}", "issue_iteration": 1}
    if prompt_ref is not None:
        docs["prompt_ref"] = prompt_ref
    return {"change_info": {"id": f"change-{uuid}", "status": status, "iteration": 1,
                            "coupled_docs": docs},
            "metadata": _meta(schema_type)}


def _issue(uuid=U, status="open", change_ref=None, schema_type="issue"):
    return {"issue_info": {"id": f"issue-{uuid}", "status": status, "iteration": 1,
                           "coupled_docs": {"change_ref": change_ref if change_ref is not None
                                            else f"change-{uuid}",
                                            "change_iteration": 1}},
            "metadata": _meta(schema_type)}


def _prompt(uuid=U, description="d", components=None, files=None):
    return {"prompt_info": {"id": f"prompt-{uuid}", "task_type": "debug", "iteration": 1,
                            "coupled_docs": {"change_ref": f"change-{uuid}",
                                             "change_iteration": 1}},
            "specification": {"description": description},
            "design": {"components": [{"name": "c"}] if components is None else components},
            "deliverable": {"files": [{"path": "x.py"}] if files is None else files}}


def _test(uuid=U, status="planned"):
    return {"test_info": {"id": f"test-{uuid}", "status": status, "iteration": 1,
                          "coupled_docs": {"prompt_ref": f"prompt-{uuid}",
                                           "prompt_iteration": 1}},
            "metadata": _meta("test")}


def _of(findings, check):
    return sorted((f.severity, f.message) for f in findings if f.check == check)


# --- A2: class resolution -------------------------------------------------------

@pytest.mark.parametrize("change_spelling,issue_spelling", [
    ("change", "issue"), ("t02_change", "t03_issue"), ("t07_change", "t06_issue"),
])
def test_documents_loaded_by_class_word(tmp_path, change_spelling, issue_spelling):
    ws = tmp_path / "ws"
    _write(ws, "change/change-1a2b3c4d-x.md", _change(schema_type=change_spelling))
    _write(ws, "issue/issue-1a2b3c4d-x.md", _issue(schema_type=issue_spelling))
    _write(ws, "prompt/prompt-1a2b3c4d-x.md", _prompt())
    docs, _ = P.load_workspace(str(ws))
    assert sorted(d.schema_type for d in docs) == ["change", "issue", "prompt"]


def test_unresolved_class_is_skipped_without_finding(tmp_path):
    ws = tmp_path / "ws"
    _write(ws, "change/change-1a2b3c4d-x.md", _change(schema_type="foo"))
    _write(ws, "issue/issue-1a2b3c4d-x.md", {"title": "no root key"})
    docs, warnings = P.load_workspace(str(ws))
    assert docs == [] and warnings == []


def test_prompt_without_metadata_gets_prompt_checks(tmp_path):
    ws = tmp_path / "ws"
    path = _write(ws, "prompt/prompt-1a2b3c4d-x.md", _prompt(description=""))
    assert _of(P.run(str(ws)), "prompt_self_contained") == [
        ("ERROR", "specification.description is empty — prompt is not self-contained")]
    assert P.load_workspace(str(ws))[0][0].path == path


# --- Amendment 1 (FR-A4): root-key inference limited by path -------------------

def test_am3_closed_change_without_schema_type_is_not_validated(tmp_path):
    ws = tmp_path / "ws"
    change = _change(status="closed")
    del change["metadata"]
    change_path = _write(ws, "change/closed/change-1a2b3c4d-x.md", change)
    _write(ws, "issue/closed/issue-1a2b3c4d-x.md", _issue(status="closed"))
    lint = [(f.severity, f.check, f.message) for f in L.run(str(ws)) if f.path == change_path]
    assert lint == [("WARN", "yaml", "YAML block present but metadata.schema_type is missing")]
    proto = P.run(str(ws))
    assert [f for f in proto if f.check in ("lifecycle", "status_consistency")] == []
    assert [d.path for d in P.load_workspace(str(ws))[0]] == [
        str(ws / "issue/closed/issue-1a2b3c4d-x.md")]


def test_am4_active_prompt_without_metadata_gets_self_containment_error(tmp_path):
    ws = tmp_path / "ws"
    path = _write(ws, "prompt/prompt-1a2b3c4d-x.md", _prompt(description=""))
    assert [(f.path, f.severity, f.message) for f in P.run(str(ws))
            if f.check == "prompt_self_contained"] == [
        (path, "ERROR", "specification.description is empty — prompt is not self-contained")]


# --- B: closed prompts ----------------------------------------------------------

def test_prompt_self_contained_active_error_closed_warn(tmp_path):
    ws = tmp_path / "ws"
    defective = _prompt(description="", components=[])
    _write(ws, "prompt/prompt-1a2b3c4d-x.md", defective)
    # change-e4428fd5 amendment 1: no root-key inference in closed/, so the
    # closed prompt carries schema_type
    closed_prompt = _prompt(uuid="2b3c4d5e", description="", components=[])
    closed_prompt["metadata"] = _meta("prompt")
    _write(ws, "prompt/closed/prompt-2b3c4d5e-x.md", closed_prompt)
    findings = [f for f in P.run(str(ws)) if f.check == "prompt_self_contained"]
    active = sorted((f.severity, f.message) for f in findings if "/closed/" not in f.path)
    closed = sorted((f.severity, f.message) for f in findings if "/closed/" in f.path)
    assert active == [
        ("ERROR", "design.components is empty — prompt is not self-contained"),
        ("ERROR", "specification.description is empty — prompt is not self-contained"),
    ]
    assert closed == [
        ("WARN", "design.components is empty — prompt is not self-contained (closed record)"),
        ("WARN", "specification.description is empty — prompt is not self-contained "
                 "(closed record)"),
    ]


def test_closed_documents_keep_severity_of_other_checks(tmp_path):
    ws = tmp_path / "ws"
    change = _write(ws, "change/closed/change-1a2b3c4d-x.md", _change(status="closed"))
    issue = _write(ws, "issue/closed/issue-1a2b3c4d-x.md", _issue(status="open"))
    lint = [f for f in L.run(str(ws)) if f.path == change and f.check == "yaml"]
    assert [(f.severity, f.message) for f in lint] == [
        ("ERROR", "'change_info.status' value 'closed' not in "
                  "['approved', 'implemented', 'proposed', 'rejected', 'verified']")]
    proto = P.run(str(ws))
    assert sorted((f.path, f.severity, f.message) for f in proto if f.check == "lifecycle") == [
        (change, "ERROR", "document in closed/ has non-terminal status 'closed' "
                          "(expected one of ['verified'])"),
        (issue, "ERROR", "document in closed/ has non-terminal status 'open' "
                         "(expected one of ['closed'])"),
    ]


# --- C: type checks (audit-caab2052 L-11) ---------------------------------------

BAD_VALUES = [["a"], {"a": 1}, 7]


def test_uuid_from_id_non_string():
    for value in BAD_VALUES + [None]:
        assert P._uuid_from_id(value) is None
    assert P._uuid_from_id("change-1a2b3c4d") == U


@pytest.mark.parametrize("value", BAD_VALUES)
def test_non_string_id_is_skipped(tmp_path, value):
    ws = tmp_path / "ws"
    data = _change()
    data["change_info"]["id"] = value
    _write(ws, "change/change-1a2b3c4d-x.md", data)
    assert P.load_workspace(str(ws))[0] == []


@pytest.mark.parametrize("value", BAD_VALUES)
def test_non_string_references_and_status_raise_nothing(tmp_path, value):
    ws = tmp_path / "ws"
    change = _change()
    change["change_info"]["coupled_docs"]["issue_ref"] = value
    _write(ws, "change/change-1a2b3c4d-x.md", change)
    prompt = _prompt()
    prompt["prompt_info"]["coupled_docs"]["change_ref"] = value
    _write(ws, "prompt/prompt-1a2b3c4d-x.md", prompt)
    _write(ws, "change/change-2b3c4d5e-x.md", _change(uuid="2b3c4d5e", status=value))
    _write(ws, "issue/closed/issue-2b3c4d5e-x.md", _issue(uuid="2b3c4d5e", status=value))
    findings = P.run(str(ws))
    for check in ("uuid_chain", "one_to_one", "status_consistency", "lifecycle"):
        assert _of(findings, check) == [], check


def test_yaml_top_level_not_mapping_is_skipped(tmp_path):
    ws = tmp_path / "ws"
    _write(ws, "change/change-1a2b3c4d-x.md", "- a\n- b\n")
    _write(ws, "issue/issue-1a2b3c4d-x.md", "just a string\n")
    assert P.run(str(ws)) == []


# --- D: superseded --------------------------------------------------------------

def test_superseded_test_status(tmp_path):
    ws = tmp_path / "ws"
    closed_sup = _write(ws, "test/closed/test-1a2b3c4d-x.md", _test(status="superseded"))
    closed_exe = _write(ws, "test/closed/test-2b3c4d5e-x.md", _test(uuid="2b3c4d5e",
                                                                   status="executed"))
    active_sup = _write(ws, "test/test-3c4d5e6f-x.md", _test(uuid="3c4d5e6f",
                                                            status="superseded"))
    lifecycle = {f.path: (f.severity, f.message) for f in P.run(str(ws)) if f.check == "lifecycle"}
    assert closed_sup not in lifecycle
    assert lifecycle[closed_exe] == (
        "ERROR", "document in closed/ has non-terminal status 'executed' "
                 "(expected one of ['passed', 'superseded'])")
    assert lifecycle[active_sup] == (
        "WARN", "document outside closed/ has terminal status 'superseded' "
                "— should be moved to closed/")


# --- E: one defective and one valid fixture per check ----------------------------

def _docs(tmp_path, files: dict):
    """Fresh workspace per call holding files; returns (docs, paths)."""
    n = len(list(tmp_path.iterdir()))
    ws = tmp_path / f"ws{n}"
    paths = {rel: _write(ws, rel, data) for rel, data in files.items()}
    return P.load_workspace(str(ws))[0], paths


def test_uuid_chain(tmp_path):
    docs, _ = _docs(tmp_path, {"change/change-1a2b3c4d-x.md": _change(issue_ref="issue-99999999")})
    assert [(f.severity, f.message) for f in P.check_uuid_chain(docs)] == [
        ("ERROR", "UUID mismatch: 'change-1a2b3c4d' → 'issue-99999999' "
                  "(expected shared UUID '1a2b3c4d')")]
    docs, _ = _docs(tmp_path, {"change/change-1a2b3c4d-x.md": _change()})
    assert P.check_uuid_chain(docs) == []


def test_bidirectional_mandatory_back_reference(tmp_path):
    docs, paths = _docs(tmp_path, {"change/change-1a2b3c4d-x.md": _change(),
                                   "issue/issue-1a2b3c4d-x.md": _issue(change_ref="")})
    assert [(f.severity, f.path, f.message) for f in P.check_bidirectional(docs)] == [
        ("ERROR", paths["issue/issue-1a2b3c4d-x.md"],
         "missing back-reference 'issue_info.coupled_docs.change_ref' → 'change-1a2b3c4d'")]


def test_bidirectional_optional_back_reference(tmp_path):
    docs, paths = _docs(tmp_path, {"change/change-1a2b3c4d-x.md": _change(),
                                   "issue/issue-1a2b3c4d-x.md": _issue(),
                                   "prompt/prompt-1a2b3c4d-x.md": _prompt()})
    assert [(f.severity, f.path, f.message) for f in P.check_bidirectional(docs)] == [
        ("WARN", paths["change/change-1a2b3c4d-x.md"],
         "missing back-reference 'change_info.coupled_docs.prompt_ref' → 'prompt-1a2b3c4d'")]


def test_bidirectional_valid(tmp_path):
    docs, _ = _docs(tmp_path, {"change/change-1a2b3c4d-x.md": _change(prompt_ref=f"prompt-{U}"),
                               "issue/issue-1a2b3c4d-x.md": _issue(),
                               "prompt/prompt-1a2b3c4d-x.md": _prompt()})
    assert P.check_bidirectional(docs) == []


def test_one_to_one(tmp_path):
    docs, _ = _docs(tmp_path, {"change/change-1a2b3c4d-x.md": _change(),
                               "change/change-2b3c4d5e-x.md": _change(uuid="2b3c4d5e",
                                                                      issue_ref=f"issue-{U}")})
    findings = P.check_one_to_one(docs)
    assert len(findings) == 1 and findings[0].severity == "ERROR"
    assert "'issue-1a2b3c4d' referenced by 2 change documents" in findings[0].message
    docs, _ = _docs(tmp_path, {"change/change-1a2b3c4d-x.md": _change()})
    assert P.check_one_to_one(docs) == []


def test_status_consistency(tmp_path):
    docs, paths = _docs(tmp_path, {"change/change-1a2b3c4d-x.md": _change(status="implemented"),
                                   "issue/issue-1a2b3c4d-x.md": _issue(status="closed")})
    assert sorted((f.path, f.message) for f in P.check_status_consistency(docs)) == [
        (paths["issue/issue-1a2b3c4d-x.md"],
         "issue is 'closed' but coupled change 'change-1a2b3c4d' has status 'implemented' "
         "(expected 'verified')")]
    docs, _ = _docs(tmp_path, {"change/change-1a2b3c4d-x.md": _change(status="implemented"),
                               "issue/issue-1a2b3c4d-x.md": _issue(status="resolved")})
    assert P.check_status_consistency(docs) == []


def test_lifecycle_placement(tmp_path):
    docs, paths = _docs(tmp_path, {"change/closed/change-1a2b3c4d-x.md":
                                   _change(status="implemented")})
    assert [(f.severity, f.message) for f in P.check_lifecycle_placement(docs)] == [
        ("ERROR", "document in closed/ has non-terminal status 'implemented' "
                  "(expected one of ['verified'])")]
    docs, _ = _docs(tmp_path, {"change/closed/change-1a2b3c4d-x.md": _change(status="verified")})
    assert P.check_lifecycle_placement(docs) == []


def test_prompt_self_contained(tmp_path):
    docs, _ = _docs(tmp_path, {"prompt/prompt-1a2b3c4d-x.md": _prompt(files=[])})
    assert [(f.severity, f.message) for f in P.check_prompt_self_contained(docs)] == [
        ("ERROR", "deliverable.files is empty — no output target specified")]
    docs, _ = _docs(tmp_path, {"prompt/prompt-1a2b3c4d-x.md": _prompt()})
    assert P.check_prompt_self_contained(docs) == []


# --- F: checker hygiene (change-9377f9b9) ----------------------------------------

def test_t4_workspace_below_closed_prompt_self_containment(tmp_path):
    ws = tmp_path / "closed" / "ws"
    path = _write(ws, "prompt/prompt-1a2b3c4d-x.md", _prompt(description=""))
    assert [(f.path, f.severity, f.message) for f in P.run(str(ws))
            if f.check == "prompt_self_contained"] == [
        (path, "ERROR", "specification.description is empty — prompt is not self-contained")]


@pytest.mark.parametrize("text", ["change_info: [\n",
                                  "change_info: " + "[" * 5000 + "]" * 5000 + "\n"])
def test_t1_t2_unparsable_yaml_is_skipped(tmp_path, text):
    ws = tmp_path / "ws"
    _write(ws, "change/change-1a2b3c4d-x.md", text)
    _write(ws, "change/closed/change-2b3c4d5e-x.md", text)
    assert P.load_workspace(str(ws)) == ([], [])
    assert P.run(str(ws)) == []


@pytest.mark.parametrize("change_status,issue_status", [
    ("implemented", ["resolved"]),
    (["implemented"], "open"),
])
def test_t9_status_consistency_mixed_types(tmp_path, change_status, issue_status):
    docs, _ = _docs(tmp_path, {"change/change-1a2b3c4d-x.md": _change(status=change_status),
                               "issue/issue-1a2b3c4d-x.md": _issue(status=issue_status)})
    assert len(docs) == 2
    assert P.check_status_consistency(docs) == []


def test_t10_closed_prompt_empty_deliverable_files_is_warn(tmp_path):
    ws = tmp_path / "ws"
    closed_prompt = _prompt(description="", components=[], files=[])
    closed_prompt["metadata"] = _meta("prompt")
    path = _write(ws, "prompt/closed/prompt-1a2b3c4d-x.md", closed_prompt)
    findings = [(f.path, f.severity, f.message) for f in P.run(str(ws))
                if f.check == "prompt_self_contained"]
    assert (path, "WARN", "deliverable.files is empty — no output target specified "
                          "(closed record)") in findings
    assert all(sev == "WARN" and msg.endswith(" (closed record)")
               for _p, sev, msg in findings)
