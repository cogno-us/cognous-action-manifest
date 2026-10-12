"""Tenant-aware runtime-action-proposal/1.2 contract tests."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from agent_action_manifest.binding import commitment, proposal_digest
from agent_action_manifest.models import RuntimeActionProposal, RuntimeActionProposalV12


FIXTURE = Path(__file__).parent.parent / "examples/runtime_action_proposal_v1_2.json"


def _raw():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_v12_requires_exact_tenant_id():
    raw = _raw()
    proposal = RuntimeActionProposalV12.model_validate(raw)
    assert proposal.tenant_id == "tenant-alpha"

    raw.pop("tenant_id")
    with pytest.raises(ValidationError):
        RuntimeActionProposalV12.model_validate(raw)


def test_v12_rejects_empty_or_oversized_tenant_id():
    for tenant_id in ("", "x" * 129):
        raw = _raw()
        raw["tenant_id"] = tenant_id
        with pytest.raises(ValidationError):
            RuntimeActionProposalV12.model_validate(raw)


def test_tenant_only_substitution_changes_canonical_proposal_commitment():
    proposal = RuntimeActionProposalV12.model_validate(_raw())
    before = proposal_digest(proposal)
    changed = proposal.model_copy(update={"tenant_id": "tenant-beta"})
    assert proposal_digest(changed) != before


def test_v12_commitment_is_compact_sorted_utf8_json_over_complete_proposal():
    proposal = RuntimeActionProposalV12.model_validate(_raw())
    assert proposal_digest(proposal) == commitment(
        proposal.model_dump(mode="json", exclude_none=False)
    )


def test_v11_remains_decodable_without_tenant_and_has_no_backfill():
    raw = _raw()
    raw.pop("tenant_id")
    historical = RuntimeActionProposal.model_validate(raw)
    dumped = historical.model_dump(mode="json", exclude_none=False)
    assert "tenant_id" not in dumped


def test_tenant_is_not_inferred_from_payload_or_target():
    raw = _raw()
    raw.pop("tenant_id")
    raw["payload"]["tenant_id"] = "tenant-alpha"
    raw["target"] = "urn:cognous:tenant:tenant-alpha:synthetic-account:customer-001"
    with pytest.raises(ValidationError):
        RuntimeActionProposalV12.model_validate(raw)
