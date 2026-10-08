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
    if not appa_tool_name or not appa_tool_name.strip():
        raise AppaToolBindingError("missing_appa_tool_name")
    actions = [a for a in manifest.actions if a.action_id == action_id]
    if len(actions) != 1:
        raise AppaToolBindingError("unknown_or_ambiguous_action_id")
    action = actions[0]
    tools = [t for t in manifest.tools if t.tool_name == action.tool_name]
    if len(tools) != 1 or not tools[0].allowed or not tools[0].adapter_id:
        raise AppaToolBindingError("missing_or_disallowed_adapter")
    if action.target_policy is None or action.target_policy.allow_any_target:
        raise AppaToolBindingError("unbounded_targets")
    if not action.target_policy.allowed_targets:
        raise AppaToolBindingError("missing_targets")
    if action.payload_policy is None:
        raise AppaToolBindingError("missing_payload_contract")
    declared = set(action.payload_policy.required_fields) | set(action.payload_policy.optional_fields)
    forbidden = set(action.payload_policy.forbidden_fields)
    if declared & forbidden:
        raise AppaToolBindingError("contradictory_payload_contract")
    if set(parameter_roles) != declared:
        raise AppaToolBindingError("incomplete_parameter_roles")
    roles = {"content", "recipient", "resource", "command", "control"}
    if any(role not in roles for role in parameter_roles.values()):
        raise AppaToolBindingError("unknown_parameter_role")
    if not sinks or any(not isinstance(sink, str) or not sink.strip() for sink in sinks):
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
