"""Strict input (scan 3): duplicate JSON members are refused at every level, and the runtime proposal does not coerce."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_action_manifest import binding as b
from agent_action_manifest.loader import ManifestLoadError, load_manifest, load_manifest_json
from agent_action_manifest.models import RuntimeActionProposal, RuntimeActionProposalV12

FIXTURE = Path(__file__).parent.parent / "examples/refund_integration_v1_1.manifest.json"


def _write(tmp_path, text):
    path = tmp_path / "m.json"
    path.write_text(text, encoding="utf-8")
    return path


def test_valid_example_still_loads_from_file(tmp_path):
    assert load_manifest(FIXTURE).manifest_id


def test_duplicate_top_level_member_is_refused(tmp_path):
    text = FIXTURE.read_text(encoding="utf-8")
    dup = text.replace('"manifest_id":', '"manifest_id": "other", "manifest_id":', 1)
    assert dup != text
    with pytest.raises(ManifestLoadError, match="duplicate object member 'manifest_id'"):
        load_manifest(_write(tmp_path, dup))


def test_duplicate_nested_member_is_refused_not_last_wins(tmp_path):
    text = json.dumps(json.loads(FIXTURE.read_text(encoding="utf-8")))
    dup = text.replace('"allowed": true', '"allowed": false, "allowed": true', 1)  # inside tools[0]
    assert dup.count('"allowed": false, "allowed": true') == 1
    with pytest.raises(ManifestLoadError, match="duplicate object member 'allowed'"):
        load_manifest(_write(tmp_path, dup))


def test_duplicate_member_in_a_deeply_nested_object_is_refused(tmp_path):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    text = json.dumps(data).replace('"allow_any_target": false', '"allow_any_target": true, "allow_any_target": false', 1)
    with pytest.raises(ManifestLoadError, match="allow_any_target"):
        load_manifest(_write(tmp_path, text))


def _proposal_kwargs():
    man = load_manifest_json(json.loads(FIXTURE.read_text(encoding="utf-8")))
    act = man.actions[0]
    payload = {"customer_id": "c", "refund_reason": "r"}
    return dict(manifest_id=man.manifest_id, manifest_version="1.1", manifest_digest=b.manifest_digest(man), actor="a", principal="p",
                action_id=act.action_id, adapter_id=man.tools[0].adapter_id, target=act.target_policy.allowed_targets[0],
                payload=payload, payload_commitment=b.payload_digest(payload), amount=10, unit="USD", effects=1)


def test_valid_proposal_numbers_still_accepted():
    for amount in (0, 10, 10.5):
        assert RuntimeActionProposal(**{**_proposal_kwargs(), "amount": amount}).amount == amount
    assert RuntimeActionProposalV12(**{**_proposal_kwargs(), "tenant_id": "t"}).effects == 1


@pytest.mark.parametrize("update", [
    {"amount": "10"}, {"amount": True}, {"effects": True}, {"effects": 1.0}, {"effects": "1"},
    {"amount": float("nan")}, {"amount": float("inf")}, {"amount": -1},
])
def test_runtime_proposal_does_not_coerce(update):
    with pytest.raises(ValueError):
        RuntimeActionProposal(**{**_proposal_kwargs(), **update})
    with pytest.raises(ValueError):
        RuntimeActionProposalV12(**{**_proposal_kwargs(), "tenant_id": "t", **update})


@pytest.mark.parametrize("mutate", [
    lambda d: d["actions"][0]["target_policy"].update(allow_any_target="yes"),
    lambda d: d["tools"][0].update(allowed="false"),
    lambda d: d["tools"][0].update(allowed=0),
    lambda d: d["actions"][0]["authority_required"][0].update(required="false"),
    lambda d: d["actions"][0]["reliance_requirement"].update(required="true"),
])
def test_boolean_manifest_fields_do_not_coerce(mutate):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    mutate(data)
    with pytest.raises(ManifestLoadError):
        load_manifest_json(data)
