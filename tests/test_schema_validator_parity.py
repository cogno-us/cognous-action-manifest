"""Parity between the published JSON schema and the Python validator over a fixture corpus.

Every case is run through both. Cases in KNOWN_SCHEMA_GAPS are rules the schema language cannot express
(cross-field or cross-item rules) and are pinned as differing, so closing one is a deliberate change.
"""
import json
from copy import deepcopy
from pathlib import Path

import jsonschema
import pytest
from pydantic import ValidationError
from referencing import Registry, Resource

from agent_action_manifest.models import AgentActionManifest
from agent_action_manifest.validator import validate_manifest

ROOT = Path(__file__).resolve().parents[1]

KNOWN_SCHEMA_GAPS = {
    "E004 dup action name": "uniqueness across array items",
    "E005 dup tool": "uniqueness across array items",
    "E017 dup action id": "uniqueness across array items",
    "E006 unknown tool": "reference to a sibling collection",
    "E015 disallowed tool": "reference to a sibling collection",
    "E019 missing adapter": "reference to a sibling collection",
    "E007 ext send no auth": "existential rule over authority_required",
    "E008 write no auth": "existential rule over authority_required",
    "E008 optional only": "existential rule over authority_required",
    "E009 forb/req": "overlap between two arrays",
    "E011 sens unknown": "subset rule between two arrays",
    "E014 allow high risk": "combined authority and review rule",
    "empty tools": "reference to a sibling collection",
}


def _registry():
    registry = Registry()
    for path in (ROOT / "schemas").glob("*.json"):
        doc = json.loads(path.read_text())
        registry = registry.with_resource(doc["$id"], Resource.from_contents(doc))
        registry = registry.with_resource(path.name, Resource.from_contents(doc))
    return registry


SCHEMA = json.loads((ROOT / "schemas/agent_action_manifest.schema.json").read_text())
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA, registry=_registry())
base = json.loads((ROOT / "examples/refund_integration_v1_1.manifest.json").read_text())
v10 = json.loads((ROOT / "examples/customer_service_agent.manifest.json").read_text())


def _python_valid(doc):
    try:
        manifest = AgentActionManifest.model_validate(doc)
    except ValidationError:
        return False
    return validate_manifest(manifest).valid


def mut(b, f):
    d = deepcopy(b)
    f(d)
    return d


def _cases():
    cases = {}
    add = cases.__setitem__
    for path in sorted((ROOT / "examples").glob("*.manifest.json")):
        add("example " + path.name, json.loads(path.read_text()))
    add('E001 empty version',mut(base,lambda d:d.update(manifest_version="")))
    add('E001 blank version',mut(base,lambda d:d.update(manifest_version=" ")))
    add('E016 unsupported version',mut(base,lambda d:d.update(manifest_version="9.9")))
    add('E002 empty id',mut(base,lambda d:d.update(manifest_id="")))
    add('E002 blank id',mut(base,lambda d:d.update(manifest_id="  ")))
    add('E003 blank agent',mut(base,lambda d:d.update(agent_name="  ")))
    add('E004 dup action name',mut(base,lambda d:d['actions'][1].update(action_name=d['actions'][0]['action_name'])))
    add('E005 dup tool',mut(base,lambda d:d['tools'].append(deepcopy(d['tools'][0]))))
    add('E017 dup action id',mut(base,lambda d:d['actions'][1].update(action_id=d['actions'][0]['action_id'])))
    add('E018 missing action id',mut(base,lambda d:d['actions'][0].pop('action_id')))
    add('E019 missing adapter',mut(base,lambda d:d['tools'][0].pop('adapter_id')))
    add('E020 any target',mut(base,lambda d:d['actions'][0]['target_policy'].update(allow_any_target=True)))
    add('E020 no targets',mut(base,lambda d:d['actions'][0]['target_policy'].update(allowed_targets=[])))
    add('E020 no policy',mut(base,lambda d:d['actions'][0].pop('target_policy')))
    add('E021 no authctx',mut(base,lambda d:d['actions'][0].pop('authority_context')))
    add('E022 no limits',mut(base,lambda d:d['actions'][0].pop('effect_limits')))
    add('E023 null amount',mut(base,lambda d:d['actions'][0]['effect_limits'].update(max_amount=None)))
    add('E023 no unit',mut(base,lambda d:d['actions'][0]['effect_limits'].update(unit=None)))
    add('E023 blank unit',mut(base,lambda d:d['actions'][0]['effect_limits'].update(unit=" ")))
    add('ok nonmonetary',mut(base,lambda d:d['actions'][0]['effect_limits'].update(unit=None,max_amount=0)))
    add('E006 unknown tool',mut(base,lambda d:d['actions'][0].update(tool_name='nope')))
    add('E015 disallowed tool',mut(base,lambda d:d['tools'][0].update(allowed=False)))
    add('E007 ext send no auth',mut(v10,lambda d:[a.update(authority_required=[]) for a in d['actions'] if a['action_type']=='external_send']))
    add('E008 write no auth',mut(base,lambda d:d['actions'][0].update(authority_required=[])))
    add('E008 optional only',mut(base,lambda d:[r.update(required=False) for r in d['actions'][0]['authority_required']]))
    add('E009 forb/req',mut(base,lambda d:d['actions'][0]['payload_policy'].update(forbidden_fields=d['actions'][0]['payload_policy']['required_fields'][:1])))
    add('E011 sens unknown',mut(base,lambda d:d['actions'][0]['payload_policy'].update(sensitive_fields=['zzz'])))
    add('E012 empty redaction path',mut(base,lambda d:d['actions'][0].update(redaction_hints=[{'field_path':' '}])))
    add('E013 approval no role',mut(base,lambda d:d['actions'][0].update(review_requirement={'mode':'approval_required'})))
    add('E014 allow high risk',mut(base,lambda d:d['actions'][0].update(default_action='allow',action_type='delete',review_requirement={'mode':'none'})))
    add('extra top member',mut(base,lambda d:d.update(zzz=1)))
    add('extra action member',mut(base,lambda d:d['actions'][0].update(zzz=1)))
    add('extra tool member',mut(base,lambda d:d['tools'][0].update(zzz=1)))
    add('bad enum type',mut(base,lambda d:d['actions'][0].update(action_type='zzz')))
    add('bad default',mut(base,lambda d:d.update(default_action='zzz')))
    add('negative max',mut(base,lambda d:d['actions'][0]['effect_limits'].update(max_amount=-1)))
    add('negative effects',mut(base,lambda d:d['actions'][0]['effect_limits'].update(max_effects=-1)))
    add('float effects',mut(base,lambda d:d['actions'][0]['effect_limits'].update(max_effects=1.5)))
    add('bool effects',mut(base,lambda d:d['actions'][0]['effect_limits'].update(max_effects=True)))
    add('string amount',mut(base,lambda d:d['actions'][0]['effect_limits'].update(max_amount="5")))
    add('v1.0 write no limits',mut(base,lambda d:(d.update(manifest_version="1.0"),d['actions'][0].pop('effect_limits'))))
    add('block write no limits',mut(base,lambda d:(d['actions'][0].update(default_action='block'),d['actions'][0].pop('effect_limits'))))
    add('manifest block no limits',mut(base,lambda d:(d.update(default_action='block'),d['actions'][0].update(default_action=None),d['actions'][0].pop('effect_limits'))))
    add('manifest block action allow no limits',mut(base,lambda d:(d.update(default_action='block'),d['actions'][0].update(default_action='allow',review_requirement={'mode':'human_review'}),d['actions'][0].pop('effect_limits'))))
    add('manifest block action null',mut(base,lambda d:(d.update(default_action='block'),d['actions'][0].update(default_action=None))))
    add('ctx tier bad',mut(base,lambda d:d['actions'][0]['authority_context'].update(consequence_tier='T9')))
    add('ctx missing field',mut(base,lambda d:d['actions'][0]['authority_context'].pop('institution_id')))
    add('review bad mode',mut(base,lambda d:d['actions'][0].update(review_requirement={'mode':'zzz'})))
    add('reliance bad type',mut(base,lambda d:d['actions'][0].update(reliance_requirement={'allowed_source_types':['zzz']})))
    add('nonfinite via schema n/a',mut(base,lambda d:d['actions'][0].update(metadata={'a':1})))
    add('empty tools',mut(base,lambda d:d.update(tools=[])))
    add('null tool_name',mut(base,lambda d:d['tools'][0].update(tool_name=None)))
    add('missing tool_name',mut(base,lambda d:d['tools'][0].pop('tool_name')))
    add('null env',mut(base,lambda d:d.update(environment=None)))
    add('null default_action manifest',mut(base,lambda d:d.update(default_action=None)))
    add('unit non-string',mut(base,lambda d:d['actions'][0]['effect_limits'].update(unit=5)))
    add('deep nest',mut(base,lambda d:d.update(metadata={'a':{'a':{'a':1}}})))
    return cases


CASES = _cases()


@pytest.mark.parametrize("name", sorted(CASES))
def test_schema_and_python_validator_agree(name):
    doc = CASES[name]
    python_valid, schema_valid = _python_valid(doc), VALIDATOR.is_valid(doc)
    if name in KNOWN_SCHEMA_GAPS:
        assert python_valid != schema_valid, f"{name} now agrees; remove it from KNOWN_SCHEMA_GAPS"
    else:
        assert python_valid == schema_valid


def test_valid_controls_pass_both():
    for name in ("example refund_integration_v1_1.manifest.json", "ok nonmonetary", "v1.0 write no limits", "block write no limits"):
        assert _python_valid(CASES[name]) and VALIDATOR.is_valid(CASES[name]), name
