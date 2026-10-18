"""Input validation: text that cannot be encoded as UTF-8 is refused at the model boundary."""
import json
from copy import deepcopy

import pytest
from pydantic import ValidationError

from agent_action_manifest.loader import ManifestLoadError, load_manifest, load_manifest_json
from agent_action_manifest.models import AgentActionManifest, RuntimeActionProposal
from tests.test_runtime_binding import FIXTURE, _proposal


def _raw():
    return deepcopy(json.loads(FIXTURE.read_text()))


def test_valid_control_non_ascii_text_and_paired_code_points_are_accepted():
    raw = _raw()
    raw["agent_name"] = "agent é中 \U0001f600"
    raw["metadata"] = {"kéy": ["v\U0001f600"]}
    assert load_manifest_json(raw).agent_name.startswith("agent")


def test_lone_surrogate_in_a_value_is_refused():
    raw = _raw()
    raw["agent_name"] = "lone\ud800value"
    with pytest.raises(ValidationError):
        AgentActionManifest.model_validate(raw)


@pytest.mark.parametrize("where", ["top", "nested", "action"])
def test_lone_surrogate_in_a_dict_key_is_refused(where):
    raw = _raw()
    if where == "top":
        raw["metadata"] = {"bad\udc00key": 1}
    elif where == "nested":
        raw["metadata"] = {"outer": [{"deep": {"bad\ud800": "x"}}]}
    else:
        raw["actions"][0]["metadata"] = {"\udfff": "x"}
    with pytest.raises(ValidationError):
        AgentActionManifest.model_validate(raw)


def test_lone_surrogate_in_a_list_item_is_refused():
    raw = _raw()
    raw["actions"][0]["tags"] = ["ok", "bad\ud83d"]
    with pytest.raises(ValidationError):
        AgentActionManifest.model_validate(raw)


def test_lone_surrogate_in_proposal_payload_key_is_refused():
    proposal = _proposal(load_manifest(FIXTURE)).model_dump()
    proposal["payload"] = {"a\ud800": 1}
    with pytest.raises(ValidationError):
        RuntimeActionProposal.model_validate(proposal)


def test_escaped_lone_surrogate_in_a_file_is_refused_by_the_loader(tmp_path):
    raw = _raw()
    text = json.dumps(raw).replace(raw["agent_name"], "a\\ud800b")
    path = tmp_path / "m.json"
    path.write_text(text)
    with pytest.raises(ManifestLoadError):
        load_manifest(path)
