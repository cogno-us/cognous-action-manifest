"""Declaration binding: blocked actions and absent limits are reported as mismatches."""
from copy import deepcopy

import pytest

from agent_action_manifest.binding import manifest_digest, payload_digest, proposal_mismatches
from agent_action_manifest.loader import load_manifest
from agent_action_manifest.models import AgentActionManifest
from agent_action_manifest.validator import validate_manifest
from tests.test_runtime_binding import FIXTURE, _proposal


def _variant(mutate):
    data = deepcopy(load_manifest(FIXTURE).model_dump(mode="json"))
    mutate(data["actions"][0], data)
    manifest = AgentActionManifest.model_validate(data)
    proposal = _proposal(manifest)
    proposal.manifest_digest = manifest_digest(manifest)
    return manifest, proposal


def _block(action, data):
    action["default_action"] = "block"


def _block_without_limits(action, data):
    action["default_action"] = "block"
    action["effect_limits"] = None


def _read_without_limits(action, data):
    action["action_type"] = "read"
    action["effect_limits"] = None
    action["authority_context"] = None
    action["authority_required"] = []


def test_valid_control_unchanged_fixture_has_no_mismatches():
    manifest = load_manifest(FIXTURE)
    assert proposal_mismatches(manifest, _proposal(manifest)) == []


def test_valid_control_manifest_default_block_is_inherited_only_when_action_has_no_override():
    manifest, proposal = _variant(lambda action, data: (data.update(default_action="block"), action.update(default_action="allow", review_requirement={"mode": "human_review", "reviewer_role": "r"})))
    assert "action_blocked" not in proposal_mismatches(manifest, proposal)


def test_blocked_action_is_a_mismatch_even_within_declared_limits():
    manifest, proposal = _variant(_block)
    assert validate_manifest(manifest).valid
    assert "action_blocked" in proposal_mismatches(manifest, proposal)


def test_manifest_level_block_is_inherited():
    def inherit(action, data):
        data["default_action"] = "block"
        action["default_action"] = None
    manifest, proposal = _variant(inherit)
    assert "action_blocked" in proposal_mismatches(manifest, proposal)


def test_blocked_action_without_limits_rejects_very_large_amount_and_count():
    manifest, proposal = _variant(_block_without_limits)
    assert validate_manifest(manifest).valid
    proposal.amount = 1e12
    proposal.unit = "USD"
    proposal.effects = 1000
    mismatches = proposal_mismatches(manifest, proposal)
    assert "action_blocked" in mismatches
    assert "missing_effect_limits" in mismatches


def test_limitless_action_rejects_very_large_amount_and_count():
    manifest, proposal = _variant(_read_without_limits)
    assert validate_manifest(manifest).valid
    proposal.amount = 1e12
    proposal.unit = "USD"
    proposal.effects = 1000
    proposal.authority_context_ref = None
    proposal.requirement_id = None
    mismatches = proposal_mismatches(manifest, proposal)
    assert "missing_effect_limits" in mismatches


def test_limitless_action_with_no_amount_and_single_effect_still_matches():
    manifest, proposal = _variant(_read_without_limits)
    proposal.amount = 0
    proposal.unit = ""
    proposal.effects = 1
    proposal.authority_context_ref = None
    proposal.requirement_id = None
    assert proposal_mismatches(manifest, proposal) == []


def test_limits_without_amount_ceiling_reject_a_positive_amount():
    def no_ceiling(action, data):
        action["action_type"] = "read"
        action["authority_context"] = None
        action["authority_required"] = []
        action["effect_limits"] = {"max_amount": None, "unit": None, "max_effects": 1}
    manifest, proposal = _variant(no_ceiling)
    assert validate_manifest(manifest).valid
    proposal.authority_context_ref = None
    proposal.requirement_id = None
    proposal.amount = 1e12
    proposal.unit = "USD"
    assert "missing_amount_limit" in proposal_mismatches(manifest, proposal)
    proposal.amount = 0
    proposal.unit = ""
    assert proposal_mismatches(manifest, proposal) == []
