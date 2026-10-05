"""Runtime-consumption contract tests for manifest v1.1."""
from copy import deepcopy
from pathlib import Path

from agent_action_manifest.binding import manifest_digest, proposal_mismatches
from agent_action_manifest.loader import load_manifest
from agent_action_manifest.models import AgentActionManifest, RuntimeActionProposal
from agent_action_manifest.validator import validate_manifest


FIXTURE = Path(__file__).parent.parent / "examples/refund_integration_v1_1.manifest.json"


def _proposal(manifest):
    return RuntimeActionProposal(
        manifest_id=manifest.manifest_id,
        manifest_version=manifest.manifest_version,
        manifest_digest=manifest_digest(manifest),
        action_id="urn:cognous:action:refund-issue-routine-v1",
        adapter_id="urn:cognous:adapter:synthetic-refund-v1",
        target="urn:cognous:synthetic-account:customer-001",
        payload={"customer_id": "customer-001", "refund_reason": "duplicate charge"},
        amount=50,
        unit="USD",
        effects=1,
        authority_context_ref="urn:cognous:alvorada:public-stack-profile:0.1.0",
        requirement_id="urn:cognous:authority-requirement:refund-routine-v1",
        correlation_id="corr-001",
        run_id="run-001",
    )


def test_v11_refund_fixture_validates():
    manifest = load_manifest(FIXTURE)
    report = validate_manifest(manifest)
    assert report.valid is True
    assert report.issues == []


def test_positive_exact_binding():
    manifest = load_manifest(FIXTURE)
    assert proposal_mismatches(manifest, _proposal(manifest)) == []


def test_unknown_action_rejected():
    manifest = load_manifest(FIXTURE)
    proposal = _proposal(manifest)
    proposal.action_id = "urn:cognous:action:not-declared"
    assert "unknown_action" in proposal_mismatches(manifest, proposal)


def test_substituted_adapter_rejected():
    manifest = load_manifest(FIXTURE)
    proposal = _proposal(manifest)
    proposal.adapter_id = "urn:cognous:adapter:other"
    assert "adapter_mismatch" in proposal_mismatches(manifest, proposal)


def test_changed_payload_scope_rejected():
    manifest = load_manifest(FIXTURE)
    proposal = _proposal(manifest)
    proposal.payload["currency_override"] = "EUR"
    assert "undeclared_payload_field" in proposal_mismatches(manifest, proposal)


def test_target_substitution_rejected():
    manifest = load_manifest(FIXTURE)
    proposal = _proposal(manifest)
    proposal.target = "urn:cognous:synthetic-account:customer-999"
    assert "target_out_of_scope" in proposal_mismatches(manifest, proposal)


def test_manifest_version_mismatch_rejected():
    manifest = load_manifest(FIXTURE)
    proposal = _proposal(manifest)
    proposal.manifest_version = "1.0"
    assert "manifest_version_mismatch" in proposal_mismatches(manifest, proposal)


def test_manifest_digest_mismatch_rejected():
    manifest = load_manifest(FIXTURE)
    proposal = _proposal(manifest)
    proposal.manifest_digest = "sha256:" + "0" * 64
    assert "manifest_digest_mismatch" in proposal_mismatches(manifest, proposal)


def test_amount_over_declaration_rejected():
    manifest = load_manifest(FIXTURE)
    proposal = _proposal(manifest)
    proposal.amount = 101
    assert "amount_exceeded" in proposal_mismatches(manifest, proposal)


def test_authority_requirement_substitution_rejected():
    manifest = load_manifest(FIXTURE)
    proposal = _proposal(manifest)
    proposal.requirement_id = "urn:cognous:authority-requirement:other"
    assert "authority_requirement_mismatch" in proposal_mismatches(manifest, proposal)


def test_v11_validator_rejects_missing_finite_target():
    manifest = load_manifest(FIXTURE)
    data = deepcopy(manifest.model_dump(mode="json"))
    data["actions"][0]["target_policy"]["allowed_targets"] = []
    changed = AgentActionManifest.model_validate(data)
    aliases = {i.alias for i in validate_manifest(changed).issues}
    assert "unbounded_target_policy" in aliases


def test_unsupported_manifest_version_rejected():
    manifest = load_manifest(FIXTURE)
    data = deepcopy(manifest.model_dump(mode="json"))
    data["manifest_version"] = "9.9"
    changed = AgentActionManifest.model_validate(data)
    aliases = {i.alias for i in validate_manifest(changed).issues}
    assert "unsupported_manifest_version" in aliases
