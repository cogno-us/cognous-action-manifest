import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from agent_action_manifest.models import AgentActionManifest, RuntimeActionProposal, EffectLimits
from agent_action_manifest.validator import validate_manifest
from agent_action_manifest.binding import proposal_mismatches
from agent_action_manifest.cli import _cmd_summarize
from tests.test_runtime_binding import _proposal, FIXTURE
from agent_action_manifest.loader import load_manifest


def test_unknown_policy_and_tenant_fields_are_not_discarded():
    raw=json.loads(FIXTURE.read_text())
    raw['actions'][0]['target_policy']['allow_any_targte']=True
    with pytest.raises(ValidationError):AgentActionManifest.model_validate(raw)
    proposal=_proposal(load_manifest(FIXTURE)).model_dump()
    proposal['tenant_id']='cannot-disappear'
    with pytest.raises(ValidationError):RuntimeActionProposal.model_validate(proposal)


def test_optional_authority_does_not_satisfy_mandatory_requirement():
    manifest=load_manifest(FIXTURE)
    for a in manifest.actions:
        for requirement in a.authority_required:requirement.required=False
    assert not validate_manifest(manifest).valid
    assert 'invalid_manifest' in proposal_mismatches(manifest,_proposal(manifest))


@pytest.mark.parametrize('value',[float('nan'),float('inf'),float('-inf')])
def test_nonfinite_effect_limits_fail(value):
    with pytest.raises(ValidationError):EffectLimits(max_amount=value)


def test_nonfinite_arbitrary_metadata_fails():
    raw=json.loads(FIXTURE.read_text());raw['metadata']={'value':float('nan')}
    with pytest.raises(ValidationError):AgentActionManifest.model_validate(raw)


def test_terminal_controls_render_as_visible_text(tmp_path,capsys):
    raw=json.loads(FIXTURE.read_text());raw['agent_name']='name\x1b[31m'
    p=tmp_path/'manifest.json';p.write_text(json.dumps(raw))
    assert _cmd_summarize([str(p)])==0
    output=capsys.readouterr().out
    assert '\x1b' not in output
    assert '\\x1b' in output


# ---- stream C: effect limits, loader, writer, CLI ---------------------------------------------------------------
import os
import subprocess
from copy import deepcopy

from agent_action_manifest.loader import MAX_MANIFEST_BYTES, ManifestLoadError, dump_manifest


def _with_limits(limits):
    raw = json.loads(FIXTURE.read_text())
    raw["actions"][0]["effect_limits"] = limits
    return AgentActionManifest.model_validate(raw)


@pytest.mark.parametrize("limits", [
    {}, {"max_effects": 1}, {"max_amount": None, "unit": "USD"}, {"max_amount": 5}, {"max_amount": 5, "unit": ""},
    {"max_amount": 5, "unit": "  "}, {"max_amount": None, "unit": None},
])
def test_v11_incomplete_effect_limits_are_invalid(limits):
    manifest = _with_limits(limits)
    report = validate_manifest(manifest)
    assert not report.valid
    assert ("E023", "incomplete_effect_limits") in {(i.code, i.alias) for i in report.issues}
    assert "invalid_manifest" in proposal_mismatches(manifest, _proposal(manifest))


@pytest.mark.parametrize("limits", [
    {"max_amount": 100.0, "unit": "USD", "max_effects": 1},
    {"max_amount": 0, "max_effects": 1},  # explicit non-monetary mode
])
def test_v11_complete_effect_limits_are_valid(limits):
    assert validate_manifest(_with_limits(limits)).valid


def test_loader_refuses_non_utf8_deep_nesting_and_oversize(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_bytes(b'{"manifest_version": "1.1", "x": "\xff\xfe"}')
    with pytest.raises(ManifestLoadError, match="UTF-8"):
        load_manifest(bad)
    deep = tmp_path / "deep.json"
    deep.write_text("[" * 200000 + "]" * 200000)
    with pytest.raises(ManifestLoadError):
        load_manifest(deep)
    big = tmp_path / "big.json"
    big.write_bytes(b" " * (MAX_MANIFEST_BYTES + 1))
    with pytest.raises(ManifestLoadError, match="larger than"):
        load_manifest(big)


def test_dump_manifest_refused_write_leaves_existing_file_and_success_is_atomic(tmp_path):
    manifest = load_manifest(FIXTURE)
    target = tmp_path / "out" / "m.json"
    dump_manifest(manifest, target)
    before = target.read_bytes()
    assert load_manifest(target).manifest_id == manifest.manifest_id
    bad = manifest.model_copy(update={"agent_name": "lone\ud800surrogate"})
    with pytest.raises(ValueError):
        dump_manifest(bad, target)
    assert target.read_bytes() == before
    assert sorted(os.listdir(target.parent)) == ["m.json"]  # no temp file left behind


def test_cli_escapes_non_printable_values_but_keeps_its_own_line_breaks(tmp_path, capsys):
    raw = json.loads(FIXTURE.read_text())
    raw["agent_name"] = "a‮b c\x00d\x1b[31m"
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps(raw))
    assert _cmd_summarize([str(p)]) == 0
    output = capsys.readouterr().out
    for ch in ("‮", " ", "\x00", "\x1b"):
        assert ch not in output
    assert "\\u202e" in output and "\\x00" in output
    assert "\nActions by type:" in output


def test_no_build_artefacts_are_tracked():
    root = Path(__file__).resolve().parents[1]
    if not (root / ".git").exists():
        pytest.skip("not a git checkout")
    tracked = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True).stdout.splitlines()
    assert [x for x in tracked if "__pycache__" in x or ".egg-info" in x or x.endswith(".pyc")] == []
    assert (root / ".gitignore").exists()
