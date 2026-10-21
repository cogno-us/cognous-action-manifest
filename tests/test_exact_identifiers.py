"""v1.1 identity and target are exact and finite (E024, E025) and export is effectful (E008, E014)."""
import copy
import json
from pathlib import Path

import pytest

from agent_action_manifest.binding import proposal_mismatches
from agent_action_manifest.models import AgentActionManifest
from agent_action_manifest.validator import validate_manifest

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / "examples/refund_integration_v1_1.manifest.json").read_text())


def _codes(doc):
    report = validate_manifest(AgentActionManifest.model_validate(doc))
    return report.valid, {i.code for i in report.issues if i.severity.value == "error"}


def _mutated(fn):
    doc = copy.deepcopy(BASE)
    fn(doc)
    return doc


def test_base_is_valid():
    assert _codes(BASE) == (True, set())


BAD = {"blank": " ", "padded": " x", "trailing": "x ", "newline": "a\nb", "nul": "a\x00b", "del": "a\x7fb", "tab": "a\tb"}


@pytest.mark.parametrize("bad", sorted(BAD))
def test_ambiguous_action_id_refused(bad):
    valid, codes = _codes(_mutated(lambda d: d["actions"][0].__setitem__("action_id", BAD[bad])))
    assert not valid and "E024" in codes


@pytest.mark.parametrize("bad", sorted(BAD))
def test_ambiguous_adapter_id_refused(bad):
    valid, codes = _codes(_mutated(lambda d: d["tools"][0].__setitem__("adapter_id", BAD[bad])))
    assert not valid and "E024" in codes


@pytest.mark.parametrize("bad", sorted(BAD) + ["empty"])
def test_ambiguous_target_refused(bad):
    value = "" if bad == "empty" else BAD[bad]
    valid, codes = _codes(_mutated(lambda d: d["actions"][0]["target_policy"].__setitem__("allowed_targets", [value])))
    assert not valid and "E024" in codes


def test_duplicate_target_refused():
    target = BASE["actions"][0]["target_policy"]["allowed_targets"][0]
    valid, codes = _codes(_mutated(lambda d: d["actions"][0]["target_policy"].__setitem__("allowed_targets", [target, target])))
    assert not valid and "E025" in codes


def test_star_target_is_a_literal_string():
    doc = _mutated(lambda d: d["actions"][0]["target_policy"].__setitem__("allowed_targets", ["*"]))
    assert _codes(doc) == (True, set())


@pytest.mark.parametrize("field", ["adapter", "action", "target"])
def test_matcher_reports_invalid_manifest_for_ambiguous_identity(field):
    from agent_action_manifest.models import RuntimeActionProposal
    from tests.test_runtime_binding import _proposal

    def mutate(d):
        if field == "adapter":
            d["tools"][0]["adapter_id"] = " "
        elif field == "action":
            d["actions"][0]["action_id"] = " "
        else:
            d["actions"][0]["target_policy"]["allowed_targets"] = [" "]

    manifest = AgentActionManifest.model_validate(_mutated(mutate))
    proposal = _proposal(manifest).model_copy(update={
        "adapter_id": " " if field == "adapter" else _proposal(manifest).adapter_id,
        "action_id": " " if field == "action" else _proposal(manifest).action_id,
        "target": " " if field == "target" else _proposal(manifest).target,
    })
    assert "invalid_manifest" in proposal_mismatches(manifest, proposal)


def _export_doc(**action):
    def mutate(d):
        a = d["actions"][0]
        a.update(action_type="export", default_action="allow", authority_required=[], review_requirement={"mode": "none"})
    return _mutated(mutate)


def test_export_allow_without_authority_or_review_refused():
    valid, codes = _codes(_export_doc())
    assert not valid and {"E008", "E014"} <= codes


def test_export_allow_with_authority_and_review_valid():
    def mutate(d):
        a = d["actions"][0]
        a.update(action_type="export", default_action="allow", review_requirement={"mode": "human_review"})
    assert _codes(_mutated(mutate)) == (True, set())


def test_export_blocked_without_authority_valid():
    doc = _export_doc()
    doc["actions"][0]["default_action"] = "block"
    valid, codes = _codes(doc)
    assert "E008" not in codes and "E014" not in codes
