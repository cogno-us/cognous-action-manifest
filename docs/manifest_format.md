# Manifest Format

This document describes the fields of the Agent Action Manifest format.

---

## Top-level fields

| Field | Type | Required | Description |
|---|---|---|---|
| `manifest_version` | string | yes | Schema version (e.g. `"1.0"`) |
| `manifest_id` | string | yes | Unique identifier for this manifest |
| `agent_name` | string | yes | Name of the agent |
| `agent_description` | string or null | no | Human-readable agent description |
| `owner` | string or null | no | Team or individual responsible |
| `environment` | string | no | Deployment environment (default: `"development"`) |
| `default_action` | enum | no | `"allow"`, `"block"`, or `"escalate"` (default: `"escalate"`) |
| `tools` | array | no | List of ToolDefinition objects |
| `actions` | array | no | List of ToolAction objects |
| `metadata` | object | no | Arbitrary metadata |

---

## ToolDefinition fields

| Field | Type | Required | Description |
|---|---|---|---|
| `tool_name` | string | yes | Unique tool identifier |
| `description` | string or null | no | Human-readable description |
| `allowed` | boolean | no | Whether the agent may call this tool (default: `true`) |
| `external_system` | string or null | no | External system the tool communicates with |
| `data_classification` | string or null | no | Data classification level |

---

## ToolAction fields

| Field | Type | Required | Description |
|---|---|---|---|
| `action_name` | string | yes | Unique action identifier |
| `tool_name` | string | yes | Tool that executes this action |
| `action_type` | enum | yes | See action types below |
| `description` | string or null | no | Human-readable description |
| `default_action` | enum or null | no | Action-level posture override |
| `authority_required` | array | no | List of AuthorityRequirement objects |
| `review_requirement` | object or null | no | ReviewRequirement |
| `reliance_requirement` | object or null | no | RelianceRequirement |
| `payload_policy` | object or null | no | PayloadPolicy |
| `redaction_hints` | array | no | List of RedactionHint objects |
| `tags` | array | no | String tags |
| `metadata` | object | no | Arbitrary metadata |

---

## Action types

| Value | Description |
|---|---|
| `read` | Reads data from a source |
| `write` | Writes or updates data |
| `external_send` | Sends data to an external system |
| `delete` | Deletes data |
| `export` | Exports data to an output location |
| `purchase` | Initiates a purchase or financial transaction |
| `approve` | Records an approval decision |
| `escalate` | Escalates a decision or request |
| `other` | Any other action type |

---

## Default action values

| Value | Description |
|---|---|
| `allow` | Action is permitted without additional gates |
| `block` | Action is blocked by default |
| `escalate` | Action is escalated for human review by default |

---

## Review modes

| Value | Description |
|---|---|
| `none` | No review required |
| `human_review` | A human must review before execution |
| `approval_required` | Explicit approval required; `reviewer_role` must be set |
| `draft_first` | Action produces a draft that must be reviewed before sending |

---

## Example: minimal manifest

```json
{
  "manifest_version": "1.0",
  "manifest_id": "my-agent-v1",
  "agent_name": "My Agent",
  "owner": "my-team",
  "environment": "production",
  "default_action": "escalate",
  "tools": [],
  "actions": []
}
```

---

## Example: action with authority and review

```json
{
  "action_name": "send_email",
  "tool_name": "email_tool",
  "action_type": "external_send",
  "description": "Send an approved email to a customer.",
  "authority_required": [
    {
      "scope": "email.send.customer",
      "description": "Permission to send outbound emails.",
      "required": true
    }
  ],
  "review_requirement": {
    "mode": "approval_required",
    "reviewer_role": "customer-service-supervisor",
    "reason": "All outbound emails require approval."
  },
  "reliance_requirement": {
    "required": true,
    "allowed_source_types": ["tool", "user_input"]
  },
  "payload_policy": {
    "required_fields": ["to", "subject", "body"],
    "optional_fields": ["cc"],
    "sensitive_fields": ["to", "body"],
    "forbidden_fields": []
  },
  "redaction_hints": [
    {
      "field_path": "to",
      "reason": "Recipient email address must be redacted in exports.",
      "replacement": "[REDACTED]"
    }
  ]
}
```


---

## Runtime-consumption profile v1.1

v1.1 is backward-compatible at the package level: v1.0 manifests still load and
validate. Consumers that require deterministic runtime binding should require
v1.1 explicitly.

Additional v1.1 action fields:

| Field | Type | Required in v1.1 runtime profile | Meaning |
|---|---|---|---|
| `action_id` | string | yes | Stable action identifier |
| tool `adapter_id` | string | yes | Stable runtime adapter identity |
| `target_policy` | object | effectful actions | Finite allowed target set |
| `effect_limits` | object | effectful actions | Explicit maximum amount/unit/effect count |
| `authority_context` | object | effectful actions | Reference-only Authority Context mapping |

"Effectful actions" means `write`, `external_send`, `delete`, `export`,
`purchase` and `approve` actions whose effective `default_action` is not
`block`. For those actions `validate_manifest` reports E020
(`unbounded_target_policy`), E021 (`missing_authority_context`) or E022
(`missing_effect_limits`) when the field is absent, and `proposal_mismatches`
then reports `invalid_manifest`. Absent `effect_limits` is never read as
"unbounded". Present `effect_limits` needs a non-null `max_amount` and a
non-empty `unit`, or `max_amount: 0` for an explicit non-monetary action;
otherwise E023 (`incomplete_effect_limits`).

Loading is bounded: `load_manifest` refuses files over `MAX_MANIFEST_BYTES`
(4 MiB), non-UTF-8 bytes and deeply nested documents with `ManifestLoadError`.
`dump_manifest` encodes before opening any file and replaces the target
atomically. CLI output escapes control and other non-printable characters.

See [Runtime consumption contract](runtime_consumption_contract.md) for exact
binding and migration semantics.

## Python models are not a schema-conformance check

The published JSON schemas under `schemas/` are stricter than the Python
models. Loading a document into the Pydantic models and passing
`validate_manifest` does not show that it conforms to those schemas; for
example, the models do not enforce every identifier, digest, version-pin and
uniqueness constraint the schemas express. Consumers that need schema
conformance should validate the JSON document against the published schema
separately.

`tests/test_schema_validator_parity.py` runs a fixture corpus through both. The
schema and the Python validator agree on every case except the rules a JSON
schema cannot express (uniqueness across items, references between
collections, existence and overlap rules over arrays); those cases are listed
in the test as known differences.
