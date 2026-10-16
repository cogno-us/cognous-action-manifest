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
    assert '\\u001b' in output
