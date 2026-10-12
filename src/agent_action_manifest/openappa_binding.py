"""Optional declaration-only bridge from Manifest 1.1 to APPA tool bindings.

This module never asks OpenAPPA for permission and never grants institutional
authority. Runtime implementations must bind the canonical call to both
independent checks, using a pinned OpenAPPA wire contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .binding import manifest_digest
from .models import AgentActionManifest


class AppaToolBindingError(ValueError):
    """Declaration cannot be mapped to an unambiguous OpenAPPA tool."""


def _identifier(value: object) -> bool:
    """Reject ambiguous spellings without silently normalizing identities."""
    return (isinstance(value, str) and bool(value) and value == value.strip()
            and not any(ord(char) < 32 or ord(char) == 127 for char in value))


def _unique_identifiers(values: list[str]) -> bool:
    return all(_identifier(value) for value in values) and len(values) == len(set(values))


@dataclass(frozen=True)
class AppaToolBinding:
    profile: Literal["cognous-openappa-tool-binding/0.1"]
    manifest_id: str
    manifest_version: str
    manifest_digest: str
    action_id: str
    tool_name: str
    adapter_id: str
    appa_tool_name: str
    action_type: str
    allowed_targets: tuple[str, ...]
    parameter_roles: tuple[tuple[str, str], ...]
    sinks: tuple[str, ...]
    data_classification: str | None

    def as_record(self) -> dict:
        return {
            "profile": self.profile,
            "manifest_id": self.manifest_id,
            "manifest_version": self.manifest_version,
            "manifest_digest": self.manifest_digest,
            "action_id": self.action_id,
            "tool_name": self.tool_name,
            "adapter_id": self.adapter_id,
            "appa_tool_name": self.appa_tool_name,
            "action_type": self.action_type,
            "allowed_targets": list(self.allowed_targets),
            "parameter_roles": dict(self.parameter_roles),
            "sinks": list(self.sinks),
            "data_classification": self.data_classification,
            "authority_effect": "none",
        }


def build_appa_tool_binding(
    manifest: AgentActionManifest,
    action_id: str,
    *,
    appa_tool_name: str,
    parameter_roles: dict[str, str],
    sinks: list[str],
) -> AppaToolBinding:
    """Build a strict local declaration projection; do not synthesize permissions.

    `parameter_roles` must enumerate all payload fields allowed by the
    action's finite payload policy. Valid roles: content, recipient, resource,
    command, control. A read operation may still disclose its remote query.
    """
    if manifest.manifest_version != "1.1":
        raise AppaToolBindingError("unsupported_manifest_version")
    if not _identifier(appa_tool_name):
        raise AppaToolBindingError("missing_appa_tool_name")
    if not _identifier(manifest.manifest_id) or not _identifier(action_id):
        raise AppaToolBindingError("invalid_declaration_identity")
    if not _unique_identifiers([a.action_id for a in manifest.actions]):
        raise AppaToolBindingError("ambiguous_manifest_action_ids")
    if not _unique_identifiers([t.tool_name for t in manifest.tools]):
        raise AppaToolBindingError("ambiguous_manifest_tool_names")
    actions = [a for a in manifest.actions if a.action_id == action_id]
    if len(actions) != 1:
        raise AppaToolBindingError("unknown_or_ambiguous_action_id")
    action = actions[0]
    tools = [t for t in manifest.tools if t.tool_name == action.tool_name]
    if len(tools) != 1 or not tools[0].allowed or not _identifier(tools[0].adapter_id):
        raise AppaToolBindingError("missing_or_disallowed_adapter")
    if action.target_policy is None or action.target_policy.allow_any_target:
        raise AppaToolBindingError("unbounded_targets")
    if not action.target_policy.allowed_targets:
        raise AppaToolBindingError("missing_targets")
    if not _unique_identifiers(action.target_policy.allowed_targets):
        raise AppaToolBindingError("invalid_or_duplicate_targets")
    if action.payload_policy is None:
        raise AppaToolBindingError("missing_payload_contract")
    policy = action.payload_policy
    if not all(_unique_identifiers(fields) for fields in
               (policy.required_fields, policy.optional_fields, policy.forbidden_fields)):
        raise AppaToolBindingError("invalid_or_duplicate_payload_fields")
    if set(policy.required_fields) & set(policy.optional_fields):
        raise AppaToolBindingError("contradictory_payload_contract")
    if not isinstance(parameter_roles, dict):
        raise AppaToolBindingError("invalid_parameter_roles")
    declared = set(action.payload_policy.required_fields) | set(action.payload_policy.optional_fields)
    forbidden = set(action.payload_policy.forbidden_fields)
    if declared & forbidden:
        raise AppaToolBindingError("contradictory_payload_contract")
    if set(parameter_roles) != declared:
        raise AppaToolBindingError("incomplete_parameter_roles")
    roles = {"content", "recipient", "resource", "command", "control"}
    if any(not isinstance(role, str) or role not in roles for role in parameter_roles.values()):
        raise AppaToolBindingError("unknown_parameter_role")
    if not isinstance(sinks, list) or not sinks or any(not _identifier(sink) for sink in sinks):
        raise AppaToolBindingError("missing_or_invalid_sinks")
    if len(sinks) != len(set(sinks)):
        raise AppaToolBindingError("duplicate_sink")
    if len(manifest.actions) != len({a.action_id for a in manifest.actions}):
        raise AppaToolBindingError("ambiguous_manifest_action_ids")
    return AppaToolBinding(
        profile="cognous-openappa-tool-binding/0.1",
        manifest_id=manifest.manifest_id,
        manifest_version=manifest.manifest_version,
        manifest_digest=manifest_digest(manifest),
        action_id=action_id,
        tool_name=action.tool_name,
        adapter_id=tools[0].adapter_id,
        appa_tool_name=appa_tool_name,
        action_type=action.action_type.value,
        allowed_targets=tuple(action.target_policy.allowed_targets),
        parameter_roles=tuple(sorted(parameter_roles.items())),
        sinks=tuple(sinks),
        data_classification=tools[0].data_classification,
    )
