"""Deterministic declaration binding helpers.

These helpers compare an exact runtime proposal with a manifest declaration.
They do not resolve grants, policy status, approvals, institutional mandates,
or permission to execute.
"""
from __future__ import annotations

import hashlib
import json

from .models import AgentActionManifest, RuntimeActionProposal, ToolAction

SUPPORTED_RUNTIME_MANIFEST_VERSIONS = {"1.1"}


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def commitment(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def manifest_digest(manifest: AgentActionManifest) -> str:
    return commitment(manifest.model_dump(mode="json", exclude_none=False))


def payload_digest(payload: dict) -> str:
    return commitment(payload)


def proposal_digest(proposal: RuntimeActionProposal) -> str:
    return commitment(proposal.model_dump(mode="json", exclude_none=False))


def resolve_action(manifest: AgentActionManifest, action_id: str) -> ToolAction | None:
    matches = [action for action in manifest.actions if action.action_id == action_id]
    return matches[0] if len(matches) == 1 else None


def proposal_mismatches(manifest: AgentActionManifest, proposal: RuntimeActionProposal) -> list[str]:
    """Return deterministic declaration mismatches only, never authorization."""
    mismatches: list[str] = []

    if manifest.manifest_version not in SUPPORTED_RUNTIME_MANIFEST_VERSIONS:
        mismatches.append("unsupported_manifest_version")
    if proposal.manifest_id != manifest.manifest_id:
        mismatches.append("manifest_id_mismatch")
    if proposal.manifest_version != manifest.manifest_version:
        mismatches.append("manifest_version_mismatch")
    if proposal.manifest_digest != manifest_digest(manifest):
        mismatches.append("manifest_digest_mismatch")
    if proposal.payload_commitment != payload_digest(proposal.payload):
        mismatches.append("payload_commitment_mismatch")

    action = resolve_action(manifest, proposal.action_id)
    if action is None:
        return sorted(set(mismatches + ["unknown_action"]))

    tool = next((tool for tool in manifest.tools if tool.tool_name == action.tool_name), None)
    if tool is None:
        mismatches.append("unknown_tool")
    elif tool.adapter_id != proposal.adapter_id:
        mismatches.append("adapter_mismatch")

    if action.target_policy is None:
        mismatches.append("missing_target_policy")
    else:
        if action.target_policy.allow_any_target:
            mismatches.append("unbounded_target_policy")
        if proposal.target not in action.target_policy.allowed_targets:
            mismatches.append("target_out_of_scope")

    if action.payload_policy is None:
        mismatches.append("missing_payload_policy")
    else:
        keys = set(proposal.payload)
        required = set(action.payload_policy.required_fields)
        optional = set(action.payload_policy.optional_fields)
        forbidden = set(action.payload_policy.forbidden_fields)
        if required - keys:
            mismatches.append("missing_required_payload_field")
        if keys & forbidden:
            mismatches.append("forbidden_payload_field")
        if keys - required - optional:
            mismatches.append("undeclared_payload_field")

    if action.effect_limits is not None:
        limits = action.effect_limits
        if proposal.effects > limits.max_effects:
            mismatches.append("effect_count_exceeded")
        if limits.max_amount is not None and proposal.amount > limits.max_amount:
            mismatches.append("amount_exceeded")
        if limits.unit is not None and proposal.unit != limits.unit:
            mismatches.append("amount_unit_mismatch")

    required_permissions = {item.scope for item in action.authority_required if item.required}
    if not required_permissions.issubset(set(proposal.requested_permissions)):
        mismatches.append("missing_requested_permission")

    if action.authority_context is not None:
        auth = action.authority_context
        if proposal.authority_context_ref != auth.profile_ref:
            mismatches.append("authority_profile_mismatch")
        if proposal.requirement_id != auth.requirement_id:
            mismatches.append("authority_requirement_mismatch")

    return sorted(set(mismatches))
