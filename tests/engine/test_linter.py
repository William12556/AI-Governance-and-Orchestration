"""Tests for the Layer 1 governance linter (change-e4428fd5, issue-e4428fd5).

Covers the class resolver and class-keyed rule tables (audit-caab2052 M-03),
type checks on YAML values (audit-caab2052 L-11), the superseded test status,
the templates, and one defective and one valid fixture per linter check.
Workspaces are built under tmp_path; no network is used.
"""

import os
import re
import subprocess
import sys

import pytest
import yaml

import linter as L
import protocol_checker as P

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEMPLATES = os.path.join(REPO, "ai", "governance", "software-engineering", "templates")


# --- helpers ------------------------------------------------------------------

def _md(data, extra: str = "") -> str:
    """Markdown governance document with one YAML block holding data."""
    text = data if isinstance(data, str) else yaml.safe_dump(data, sort_keys=False)
    return ("Created: 2026 November 7\n\n```yaml\n" + text + "```\n\n" + extra
            + "## Version History\n\n| 1.0 | 2026-11-07 | x |\n\n"
            "Copyright (c) 2026 William Watson. MIT License.\n")


def _write(ws, rel: str, data, extra: str = "") -> str:
    path = ws / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_md(data, extra))
    return str(path)


def _meta(schema_type):
    meta = {"copyright": "Copyright (c) 2026 William Watson. MIT License.",
            "template_version": "1.0"}
    if schema_type is not None:
        meta["schema_type"] = schema_type
    return meta


def _change(uuid="1a2b3c4d", schema_type="change", **info):
    base = {"id": f"change-{uuid}", "title": "t", "status": "proposed",
            "priority": "medium", "iteration": 1,
            "coupled_docs": {"issue_ref": f"issue-{uuid}", "issue_iteration": 1}}
    base.update(info)
    return {"change_info": base, "metadata": _meta(schema_type)}


def _issue(uuid="1a2b3c4d", schema_type="issue", **info):
    base = {"id": f"issue-{uuid}", "title": "t", "status": "open", "severity": "medium",
            "type": "defect", "iteration": 1,
            "coupled_docs": {"change_ref": f"change-{uuid}", "change_iteration": 1}}
    base.update(info)
    return {"issue_info": base, "metadata": _meta(schema_type)}


def _prompt(uuid="1a2b3c4d", schema_type=None, **info):
    base = {"id": f"prompt-{uuid}", "task_type": "debug", "iteration": 1,
            "coupled_docs": {"change_ref": f"change-{uuid}", "change_iteration": 1}}
    base.update(info)
    data = {"prompt_info": base,
            "specification": {"description": "d"},
            "design": {"components": [{"name": "c"}]},
            "deliverable": {"files": [{"path": "x.py"}]}}
    if schema_type is not None:
        data["metadata"] = _meta(schema_type)
    return data


def _test(uuid="1a2b3c4d", schema_type="test", **info):
    base = {"id": f"test-{uuid}", "status": "planned", "type": "unit",
            "priority": "medium", "iteration": 1,
            "coupled_docs": {"prompt_ref": f"prompt-{uuid}", "prompt_iteration": 1}}
    base.update(info)
    return {"test_info": base, "metadata": _meta(schema_type)}


def _result(uuid="1a2b3c4d", schema_type="result", **info):
    base = {"id": f"result-{uuid}", "status": "passed", "iteration": 1,
            "coupled_docs": {"test_ref": f"test-{uuid}", "test_iteration": 1}}
    base.update(info)
    return {"result_info": base, "metadata": _meta(schema_type)}


def _yaml_findings(data) -> list:
    findings, _data, _cls = L.check_yaml("doc.md", _md(data))
    return findings


def _key(findings) -> list:
    return sorted((f.severity, f.check, f.message) for f in findings)


# --- A1: resolve_class --------------------------------------------------------

NUMBERED = [
    ("t01_design", "design"), ("t02_change", "change"), ("t03_issue", "issue"),
    ("t04_prompt", "prompt"), ("t05_test", "test"), ("t06_result", "result"),
    ("t07_requirements", "requirements"), ("t08_audit", "audit"),
    ("t01_requirements", "requirements"), ("t02_design", "design"),
    ("t03_prompt", "prompt"), ("t04_test", "test"), ("t05_result", "result"),
    ("t06_issue", "issue"), ("t07_change", "change"),
]


def test_numbered_values_are_the_fifteen_distinct_values():
    assert len({v for v, _ in NUMBERED}) == 15


@pytest.mark.parametrize("word", L.CLASS_WORDS)
def test_resolve_class_word(word):
    assert L.resolve_class({"metadata": {"schema_type": word}}) == (word, None)


@pytest.mark.parametrize("value,word", NUMBERED)
def test_resolve_class_numbered_alias(value, word):
    assert L.resolve_class({"metadata": {"schema_type": value}}) == (word, None)


@pytest.mark.parametrize("value", ["t09_change", "Change", "change ", "foo"])
def test_resolve_class_unknown_value(value):
    assert L.resolve_class({"metadata": {"schema_type": value}}) == (
        None, f"unknown schema_type '{value}'")


@pytest.mark.parametrize("value", [["change"], {"a": 1}, 3])
def test_resolve_class_non_string(value):
    assert L.resolve_class({"metadata": {"schema_type": value}}) == (
        None, "metadata.schema_type must be a string")


@pytest.mark.parametrize("key,word", sorted(L.ROOT_KEYS.items()))
def test_resolve_class_from_root_key(key, word):
    assert L.resolve_class({key: {"id": "x"}}) == (word, None)


@pytest.mark.parametrize("data", [{"project_info": {}}, {"title": "x", "notes": "y"}])
def test_resolve_class_absent_without_root_key(data):
    assert L.resolve_class(data) == (
        None, "YAML block present but metadata.schema_type is missing")


def test_resolve_class_uses_first_root_key():
    assert L.resolve_class({"project_info": {}, "change_info": {}, "issue_info": {}}) == (
        "change", None)


# --- Amendment 1 (FR-A4): root-key inference limited by path -------------------

@pytest.mark.parametrize("path,expected", [
    ("prompt/prompt-x.md", ("prompt", None)),
    ("prompt/closed/prompt-x.md", (None, L.MISSING_SCHEMA_TYPE)),
    (None, ("prompt", None)),
])
def test_am1_resolve_class_root_key_by_path(path, expected):
    assert L.resolve_class({"prompt_info": {"id": "prompt-1a2b3c4d"}}, path) == expected


@pytest.mark.parametrize("path,cls,findings", [
    ("prompt/prompt-1a2b3c4d-x.md", "prompt", []),
    ("prompt/closed/prompt-1a2b3c4d-x.md", None,
     [("WARN", "yaml", "YAML block present but metadata.schema_type is missing")]),
])
def test_am1_check_yaml_passes_path(path, cls, findings):
    found, _data, got = L.check_yaml(path, _md(_prompt()))
    assert (got, _key(found)) == (cls, findings)


def test_am2_proposal_with_change_info_is_not_a_change(tmp_path):
    ws = tmp_path / "ws"
    data = _change()
    del data["metadata"]
    path = _write(ws, "proposals/proposal-1a2b3c4d-x.md", data)
    findings, _data, cls = L.check_yaml(path, _md(data))
    assert cls is None
    assert _key(findings) == [
        ("WARN", "yaml", "YAML block present but metadata.schema_type is missing")]
    assert P.load_workspace(str(ws)) == ([], [])


# --- A2: rules applied by class -------------------------------------------------

FOUR_DEFECTS = [
    ("ERROR", "yaml", "'change_info.id' value 'change-XYZ' does not match pattern "
                      "'^change-[0-9a-f]{8}$'"),
    ("ERROR", "yaml", "'change_info.status' value 'done' not in "
                      "['approved', 'implemented', 'proposed', 'rejected', 'verified']"),
    ("ERROR", "yaml", "'change_info.priority' value 'urgent' not in "
                      "['critical', 'high', 'low', 'medium']"),
    ("ERROR", "yaml", "iteration must be integer ≥ 1, got '0'"),
]


@pytest.mark.parametrize("spelling", ["t02_change", "t07_change", "change"])
def test_change_with_four_defects_same_findings_per_spelling(spelling):
    data = _change(schema_type=spelling, id="change-XYZ", status="done",
                   priority="urgent", iteration=0)
    assert _key(_yaml_findings(data)) == sorted(FOUR_DEFECTS)


SPELLINGS = {
    "issue":  (_issue,  ["issue", "t03_issue", "t06_issue"],
               {"status": "gone", "severity": "huge"}),
    "test":   (_test,   ["test", "t05_test", "t04_test"],
               {"status": "maybe", "type": "fuzz"}),
    "result": (_result, ["result", "t06_result", "t05_result"],
               {"status": "unknown"}),
    "prompt": (_prompt, ["prompt", "t04_prompt", "t03_prompt"],
               {"task_type": "enhancement"}),
}


@pytest.mark.parametrize("cls", sorted(SPELLINGS))
def test_documents_same_findings_per_spelling(cls):
    build, spellings, defects = SPELLINGS[cls]
    valid = [_key(_yaml_findings(build(schema_type=s))) for s in spellings]
    defective = [_key(_yaml_findings(build(schema_type=s, **defects))) for s in spellings]
    assert valid == [[]] * len(spellings)
    assert defective[0] and len(defective[0]) == len(defects)
    assert all(d == defective[0] for d in defective)


@pytest.mark.parametrize("spelling,root", [
    ("design", "project_info"), ("t01_design", "project_info"), ("t02_design", "project_info"),
    ("requirements", "project_info"), ("t07_requirements", "project_info"),
    ("t01_requirements", "project_info"), ("audit", "audit_info"), ("t08_audit", "audit_info"),
])
def test_classes_without_rules_give_no_finding(spelling, root):
    data = {root: {"name": "x"}, "metadata": _meta(spelling)}
    findings, _data, cls = L.check_yaml("doc.md", _md(data))
    assert findings == []
    assert cls in ("design", "requirements", "audit")


def test_prompt_without_metadata_is_checked_as_prompt(tmp_path):
    ws = tmp_path / "ws"
    _write(ws, "prompt/prompt-1a2b3c4d-x.md", _prompt(task_type="enhancement"))
    findings = L.run(str(ws))
    msgs = [f.message for f in findings]
    assert not any("schema_type is missing" in m for m in msgs)
    assert not any("template_version" in m for m in msgs)
    # prompt rules applied: enum check and coupling
    assert any("'prompt_info.task_type' value 'enhancement'" in m for m in msgs)
    assert any(f.check == "coupling" and "'change-1a2b3c4d' not found" in f.message
               for f in findings)


def test_check_yaml_returns_class_word_for_alias():
    _f, _d, cls = L.check_yaml("doc.md", _md(_change(schema_type="t07_change")))
    assert cls == "change"


def test_unknown_schema_type_is_warned_without_field_checks():
    data = _change(schema_type="foo", id="bad", status="bad", iteration=0)
    findings, _data, cls = L.check_yaml("doc.md", _md(data))
    assert cls is None
    assert _key(findings) == [("WARN", "yaml", "unknown schema_type 'foo'")]


def test_missing_template_version_warned_only_with_schema_type():
    data = _change()
    del data["metadata"]["template_version"]
    assert ("WARN", "yaml", "missing metadata.template_version") in _key(_yaml_findings(data))
    data = _change()
    del data["metadata"]
    # change-e4428fd5 amendment 1: inference needs a matching file name
    findings, _data, _cls = L.check_yaml("change-1a2b3c4d-x.md", _md(data))
    assert _key(findings) == []


# --- A3: templates --------------------------------------------------------------

TEMPLATE_CLASS = {
    "T01-requirements.md": "requirements", "T02-design.md": "design",
    "T04-test.md": "test", "T05-result.md": "result", "T06-issue.md": "issue",
    "T07-change.md": "change", "T08-audit.md": "audit",
}


def _template_blocks(name: str) -> list:
    with open(os.path.join(TEMPLATES, name), encoding="utf-8") as fh:
        content = fh.read()
    return [yaml.safe_load(b) for b in L.YAML_BLOCK_RE.findall(content)]


@pytest.mark.parametrize("name,word", sorted(TEMPLATE_CLASS.items()))
def test_template_emits_class_word(name, word):
    template, schema = _template_blocks(name)[:2]
    assert template["metadata"]["schema_type"] == word
    assert L.resolve_class(template) == (word, None)
    enum = schema["properties"]["metadata"]["properties"]["schema_type"]["enum"]
    assert enum == [word]


def test_prompt_template_has_no_schema_type_and_resolves_to_prompt():
    template = _template_blocks("T03-prompt.md")[0]
    assert L._get(template, "metadata.schema_type") is None
    assert L.resolve_class(template) == ("prompt", None)


def test_test_template_lists_superseded():
    template, schema = _template_blocks("T04-test.md")[:2]
    enum = schema["properties"]["test_info"]["properties"]["status"]["enum"]
    assert "superseded" in enum
    with open(os.path.join(TEMPLATES, "T04-test.md"), encoding="utf-8") as fh:
        assert re.search(r'^  status: "".*superseded', fh.read(), re.MULTILINE)


# --- C: type checks (audit-caab2052 L-11) ---------------------------------------

BAD_VALUES = [["a"], {"a": 1}, 7]


@pytest.mark.parametrize("value", BAD_VALUES)
def test_schema_type_wrong_type_is_warned(value):
    assert _key(_yaml_findings(_change(schema_type=value))) == [
        ("WARN", "yaml", "metadata.schema_type must be a string")]


@pytest.mark.parametrize("value", BAD_VALUES)
def test_id_wrong_type_is_error(value):
    assert ("ERROR", "yaml", "'change_info.id' must be a string") in _key(
        _yaml_findings(_change(id=value)))


@pytest.mark.parametrize("value", BAD_VALUES)
def test_enum_wrong_type_is_error(value):
    assert _key(_yaml_findings(_change(status=value))) == [
        ("ERROR", "yaml", "'change_info.status' value must be a string")]


@pytest.mark.parametrize("value", BAD_VALUES)
def test_coupling_ref_wrong_type_is_error(tmp_path, value):
    ws = tmp_path / "ws"
    data = _change()
    data["change_info"]["coupled_docs"]["issue_ref"] = value
    path = _write(ws, "change/change-1a2b3c4d-x.md", data)
    _write(ws, "issue/issue-1a2b3c4d-x.md", _issue())
    findings = [f for f in L.run(str(ws)) if f.path == path]
    assert _key(findings) == [
        ("ERROR", "coupling", "'change_info.coupled_docs.issue_ref' must be a string")]
    P.run(str(ws))  # no exception


@pytest.mark.parametrize("field", ["schema_type", "id", "status", "issue_ref"])
@pytest.mark.parametrize("value", BAD_VALUES)
def test_no_exception_for_any_value_shape(tmp_path, field, value):
    ws = tmp_path / "ws"
    change = _change()
    issue = _issue()
    if field == "schema_type":
        change["metadata"]["schema_type"] = value
        issue["metadata"]["schema_type"] = value
    elif field == "issue_ref":
        change["change_info"]["coupled_docs"]["issue_ref"] = value
        issue["issue_info"]["coupled_docs"]["change_ref"] = value
    else:
        change["change_info"][field] = value
        issue["issue_info"][field] = value
    _write(ws, "change/change-1a2b3c4d-x.md", change)
    _write(ws, "issue/closed/issue-1a2b3c4d-x.md", issue)
    lint = L.run(str(ws))
    assert any(f.severity in ("ERROR", "WARN") for f in lint)
    P.run(str(ws))


def test_yaml_top_level_list_is_error(tmp_path):
    ws = tmp_path / "ws"
    path = _write(ws, "change/change-1a2b3c4d-x.md", "- a\n- b\n")
    findings = [f for f in L.run(str(ws)) if f.check == "yaml"]
    assert _key(findings) == [("ERROR", "yaml", "YAML block top level must be a mapping")]
    assert findings[0].path == path
    docs, _ = P.load_workspace(str(ws))
    assert docs == []


# --- D: superseded --------------------------------------------------------------

def test_superseded_is_a_valid_test_status():
    assert _yaml_findings(_test(status="superseded")) == []


# --- E: one defective and one valid fixture per check ----------------------------

def test_naming():
    assert _key(L.check_naming("widget-1a2b3c4d-x.md", "p")) == [
        ("ERROR", "naming", "unknown document class 'widget'")]
    assert L.check_naming("change-1a2b3c4d-x.md", "p") == []
    assert L.check_naming("README.md", "p") == []


def test_structure():
    bare = "```yaml\nchange_info: {}\n```\n"
    assert _key(L.check_structure("p", bare, "change-1a2b3c4d-x.md")) == [
        ("ERROR", "structure", "missing 'Version History' section"),
        ("WARN", "structure", "missing 'Created:' timestamp"),
        ("WARN", "structure", "missing copyright line"),
    ]
    assert L.check_structure("p", _md(_change()), "change-1a2b3c4d-x.md") == []
    # prompts are exempt from the version history requirement (change-51f1aef0)
    assert L.check_structure("p", "Created: x\ncopyright\n", "prompt-1a2b3c4d-x.md") == []


def test_yaml_check():
    assert _yaml_findings(_change()) == []
    assert _key(_yaml_findings(_change(id=""))) == [
        ("ERROR", "yaml", "required field 'change_info.id' is missing or empty")]


@pytest.mark.parametrize("mutate,expected", [
    (lambda c: c["change_info"]["coupled_docs"].update(issue_ref=""),
     [("WARN", "coupling", "'change_info.coupled_docs.issue_ref' is empty — coupling incomplete")]),
    (lambda c: c["change_info"]["coupled_docs"].update(issue_ref="issue-99999999"),
     [("ERROR", "coupling", "referenced document 'issue-99999999' not found in workspace")]),
    (lambda c: c["change_info"]["coupled_docs"].update(issue_iteration=2),
     [("ERROR", "coupling", "iteration mismatch: own=1, coupled_docs=2")]),
    (lambda c: None, []),
])
def test_coupling(tmp_path, mutate, expected):
    ws = tmp_path / "ws"
    change = _change()
    mutate(change)
    path = _write(ws, "change/change-1a2b3c4d-x.md", change)
    _write(ws, "issue/issue-1a2b3c4d-x.md", _issue())
    assert _key(f for f in L.run(str(ws)) if f.path == path and f.check == "coupling") == expected


def test_links(tmp_path):
    (tmp_path / "other.md").write_text("x")
    content = "# Title\n\n## Section One\n\n[a](#section-one) [b](other.md)\n"
    assert L.check_links(str(tmp_path / "doc.md"), content, str(tmp_path)) == []
    bad = content + "[c](#nowhere) [d](missing.md)\n"
    assert _key(L.check_links(str(tmp_path / "doc.md"), bad, str(tmp_path))) == [
        ("WARN", "links", "anchor '#nowhere' not found in document headings"),
        ("WARN", "links", "linked file 'missing.md' not found"),
    ]


# --- F: checker hygiene (change-9377f9b9) ----------------------------------------

DEEP = "[" * 5000 + "]" * 5000

PARSE_CASES = [
    ("change_info: [\n", "YAML block does not parse: "),
    ("change_info: " + DEEP + "\n", "YAML block does not parse: nesting too deep"),
]


def _parse_case(tmp_path, rel, text):
    ws = tmp_path / "ws"
    path = _write(ws, rel, text)
    lint = [f for f in L.run(str(ws)) if f.path == path and f.check == "yaml"]
    proto = [f for f in P.run(str(ws)) if f.path == path]
    return lint, proto


@pytest.mark.parametrize("text,prefix", PARSE_CASES)
def test_t1_t2_unparsable_yaml_active_is_error(tmp_path, text, prefix):
    lint, proto = _parse_case(tmp_path, "change/change-1a2b3c4d-x.md", text)
    assert len(lint) == 1
    assert lint[0].severity == "ERROR"
    assert lint[0].message.startswith(prefix)
    assert not lint[0].message.endswith(" (closed record)")
    if prefix.endswith("deep"):
        assert lint[0].message == prefix
    assert proto == []


@pytest.mark.parametrize("text,prefix", PARSE_CASES)
def test_t1_t2_unparsable_yaml_closed_is_warn(tmp_path, text, prefix):
    lint, proto = _parse_case(tmp_path, "change/closed/change-1a2b3c4d-x.md", text)
    assert len(lint) == 1
    assert lint[0].severity == "WARN"
    assert lint[0].message.startswith(prefix)
    assert lint[0].message.endswith(" (closed record)")
    if prefix.endswith("deep"):
        assert lint[0].message == prefix + " (closed record)"
    assert proto == []


def test_t3_parse_yaml_block():
    assert L._parse_yaml_block("# no block\n") == (None, None)
    assert L._parse_yaml_block("```yaml\na: 1\n```\n") == ({"a": 1}, None)
    data, problem = L._parse_yaml_block("```yaml\nchange_info: [\n```\n")
    assert data is None
    assert isinstance(problem, str) and problem
    assert L._extract_yaml("```yaml\na: " + DEEP + "\n```\n") is None


def test_t3_no_yaml_block_gives_no_parse_finding():
    assert L.check_yaml("doc.md", "Created: x\n\nno block\n") == ([], None, None)


def test_t4_workspace_below_closed_infers_class(tmp_path):
    ws = tmp_path / "closed" / "ws"
    change = _change(status="done")
    del change["metadata"]
    path = _write(ws, "change/change-1a2b3c4d-x.md", change)
    _write(ws, "issue/issue-1a2b3c4d-x.md", _issue())
    lint = [f for f in L.run(str(ws)) if f.path == path and f.check == "yaml"]
    assert _key(lint) == [
        ("ERROR", "yaml", "'change_info.status' value 'done' not in "
                          "['approved', 'implemented', 'proposed', 'rejected', 'verified']")]
    _found, _data, cls = L.check_yaml(path, _md(change), str(ws))
    assert cls == "change"


@pytest.mark.parametrize("value", [True, False])
def test_t5_bool_iteration_is_error(value):
    assert (("ERROR", "yaml", f"iteration must be integer ≥ 1, got '{value}'")
            in _key(_yaml_findings(_change(iteration=value))))


def test_t7_resolve_class_t02_changes():
    assert L.resolve_class(_change(schema_type="t02_changes")) == (
        None, "unknown schema_type 't02_changes'")


@pytest.mark.parametrize("path", ["prompt/enclosed/prompt-x.md",
                                  "prompt/prompt-1a2b3c4d-closed-loop.md"])
def test_t8_closed_substring_does_not_block_inference(path):
    assert L.resolve_class({"prompt_info": {"id": "prompt-1a2b3c4d"}}, path) == (
        "prompt", None)


@pytest.mark.parametrize("value", [[], 0])
def test_t11_id_empty_list_or_zero_is_error(value):
    assert ("ERROR", "yaml", "'change_info.id' must be a string") in _key(
        _yaml_findings(_change(id=value)))


def test_dev_corpus_unparsable_closed_prompts_are_warned():
    out = subprocess.run([sys.executable, os.path.join(REPO, "ai", "engine", "src", "linter.py"),
                          os.path.join(REPO, "dev")], capture_output=True, text=True)
    lines = [ln for ln in out.stdout.splitlines() if "YAML block does not parse" in ln]
    names = sorted(os.path.basename(ln.split(": ", 1)[0].split("] ", 1)[1]) for ln in lines)
    assert names == ["prompt-5e8aea4f-loop-robustness-followup.md",
                     "prompt-711a57d5-loop-robustness.md"], out.stdout
    for ln in lines:
        assert ln.startswith("WARN") and "/prompt/closed/" in ln.replace("\\", "/")
        assert ln.endswith(" (closed record)")


# --- corpus ---------------------------------------------------------------------

@pytest.mark.parametrize("checker", ["linter.py", "protocol_checker.py"])
def test_checkers_complete_on_dev_corpus(checker):
    out = subprocess.run([sys.executable, os.path.join(REPO, "ai", "engine", "src", checker),
                          os.path.join(REPO, "dev")], capture_output=True, text=True)
    assert out.returncode in (0, 1), out.stderr
    assert "Traceback" not in out.stderr
    m = re.search(r"(\d+) error\(s\)  \d+ warning\(s\)", out.stdout)
    assert m
    # change-e4428fd5 amendment 1: each checker reports 0 errors on dev/
    assert m.group(1) == "0", out.stdout
    assert out.returncode == 0
