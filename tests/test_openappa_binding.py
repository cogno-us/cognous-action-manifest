import pytest

from agent_action_manifest.models import (
    AgentActionManifest, PayloadPolicy, TargetPolicy, ToolAction, ToolDefinition,
)
from agent_action_manifest.openappa_binding import (
    AppaToolBindingError, build_appa_tool_binding,
)


def fixture_manifest():
    return AgentActionManifest(
        manifest_version="1.1", manifest_id="refund", agent_name="synthetic",
        tools=[ToolDefinition(tool_name="refund_tool", adapter_id="refund_adapter")],
        actions=[ToolAction(
            action_name="refund", action_id="refund.v1", tool_name="refund_tool",
            action_type="write",
            payload_policy=PayloadPolicy(required_fields=["amount", "recipient"]),
            target_policy=TargetPolicy(allowed_targets=["refund.sqlite"]),
        )],
    )


def make_binding(manifest=None, **kw):
    return build_appa_tool_binding(
        manifest or fixture_manifest(), "refund.v1", appa_tool_name="refund_tool",
        parameter_roles=kw.get("parameter_roles", {"amount": "content", "recipient": "recipient"}),
        sinks=kw.get("sinks", ["refund.sqlite"]),
    )


def test_exact_declaration_and_no_authority():
    r = make_binding().as_record()
    assert r["authority_effect"] == "none"
    assert r["action_id"] == "refund.v1"
    assert r["adapter_id"] == "refund_adapter"
    assert r["manifest_digest"].startswith("sha256:")


@pytest.mark.parametrize("roles,sinks", [
    ({"amount": "content"}, ["refund.sqlite"]),
    ({"amount": "content", "recipient": "invalid"}, ["refund.sqlite"]),
    ({"amount": "content", "recipient": "recipient"}, []),
    ({"amount": "content", "recipient": "recipient"}, ["refund.sqlite", "refund.sqlite"]),
])
def test_rejects_incomplete_mapping(roles, sinks):
    with pytest.raises(AppaToolBindingError):
        make_binding(parameter_roles=roles, sinks=sinks)


def test_rejects_unbounded_target():
    m = fixture_manifest()
    m.actions[0].target_policy.allow_any_target = True
    with pytest.raises(AppaToolBindingError, match="unbounded_targets"):
        make_binding(m)


def test_rejects_unknown_action():
    with pytest.raises(AppaToolBindingError, match="unknown_or_ambiguous_action"):
        build_appa_tool_binding(
            fixture_manifest(), "nonexistent", appa_tool_name="any",
            parameter_roles={}, sinks=["refund.sqlite"],
        )


def test_rejects_legacy_manifest():
    m = fixture_manifest()
    m.manifest_version = "1.0"
    with pytest.raises(AppaToolBindingError, match="unsupported_manifest_version"):
        make_binding(m)
