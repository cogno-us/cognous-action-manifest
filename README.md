<!-- cognous-banner:start -->
```text
──────────────────────────────────────────────────
   __________  _______   ______  __  _______
  / ____/ __ \/ ____/ | / / __ \/ / / / ___/
 / /   / / / / / __/  |/ / / / / / / /\__ \
/ /___/ /_/ / /_/ / /|  / /_/ / /_/ /___/ /
\____/\____/\____/_/ |_/\____/\____//____/
             COGNOUS ACTION MANIFEST
       g o v e r n e d   b y   d e s i g n
  github.com/cogno-us/cognous-open-control-stack
──────────────────────────────────────────────────
```
<!-- cognous-banner:end -->

# Cognous Action Manifest

**Declare the action before evaluating permission.**

| | |
|---|---|
| Lock status | **selected**: lock key `action_manifest`, interface Manifest 1.1 (see [Selection and compatibility](#selection-and-compatibility)) |
| Stack group | 03 Declaration & Policy Control (siblings: [Control Plane](https://github.com/cogno-us/cognous-control-plane)); see [where it fits](#cognous-stack-components) |
| Package and command | package `agent-action-manifest` 0.1.0, import `agent_action_manifest`, command `aam` ([naming](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/naming.md)) |
| Requirements | Python 3.11 or newer; Linux is the supported platform |
| Documentation | [Documentation index](docs/README.md) |

## What it is, who it is for, what it does not do

**What it is.** A lightweight format, Python validator and command-line tool for describing the actions an AI agent may propose: which tools and actions exist, what authority, review, reliance and payload rules each declares, and which fields carry redaction hints. Manifest 1.1 adds deterministic runtime bindings (stable action and adapter identities, finite targets, effect limits and Authority Context references) so a downstream controller can compare a proposal with one specific declared action.

**Who it is for.** Engineers who write or consume action declarations, and reviewers who need an explicit inventory of what an agent can propose before they look at runtime control. Engineers can inspect the reference contracts and examples; architecture, security and governance reviewers can examine the boundary and evidence.

**What it does not do.** It is declaration and validation. It is not a permission system, a security boundary or runtime access control. A valid manifest does not establish institutional legitimacy, current approval, a completed effect or compliance, and a manifest cannot authorize an attempt. A passing example is not a certification of any deployment. The [known limits](#known-limits) are listed below.

**Synthetic example.** A manifest declares a synthetic refund action and its allowed adapter, target and effect limits. The runtime binds a proposal to that manifest commitment; the [Control Plane](https://github.com/cogno-us/cognous-control-plane) then independently resolves institutional authority and checks the actual proposal. Matching the declaration alone never authorizes the refund.

## Quick start (about one minute)

Prerequisites: Python 3.11 or newer, `git`, and network access for package installation (the `pydantic` dependency; the `dev` extra adds `pytest` and `jsonschema`). Run the commands from the repository root: `aam check-examples` reads `examples/` from the current directory.

```bash
git clone https://github.com/cogno-us/cognous-action-manifest
cd cognous-action-manifest
python3 -m venv .venv && . .venv/bin/activate
python -m pip install -e ".[dev]"
aam validate examples/refund_integration_v1_1.manifest.json
aam summarize examples/customer_service_agent.manifest.json
aam list-actions examples/customer_service_agent.manifest.json
aam check-examples
```

Expected output, with exit code 0 for each command:

```text
$ aam validate examples/refund_integration_v1_1.manifest.json
Validation result: VALID
Manifest ID:       refund-integration-pilot-v1
No issues found.

$ aam summarize examples/customer_service_agent.manifest.json
Manifest ID:          customer-service-agent-v1
Agent name:           Customer Service Agent
Environment:          production
Tools:                3
Actions:              4
...

$ aam list-actions examples/customer_service_agent.manifest.json
action_name   tool_name   action_type    posture   authority_scopes                review_mode
----------------------------------------------------------------------------------------------
crm_read      crm_tool    read           escalate  (none)                          none
...

$ aam check-examples
VALID       examples/customer_service_agent.manifest.json (0 warning(s))
...
VALID       examples/refund_integration_v1_1.manifest.json (0 warning(s))
```

Exit codes: `0` valid; `1` invalid manifest (for `validate`, or any invalid example for `check-examples`); `2` usage error, missing file, or a file that fails to load. For example, removing `effect_limits` from the first action of the refund example makes `aam validate` print `Validation result: INVALID` and `[E022] ... must declare explicit effect_limits in v1.1.` and exit with `1`. The CLI has no help flag: running `aam` without a command prints the usage list and exits `2`.

**What this does not prove.** `VALID` means the document passed this package's checks. It is a declaration only: it is not permission, not evidence that any action ran, and not a conformance claim by itself (see [schemas and Python checks](docs/manifest_format.md#schemas-and-python-checks-are-complementary)).

To see the manifest, replay and evidence-pack commands run together offline, use `cognous-ocs demo` from the [ergonomics repository](https://github.com/cogno-us/cognous-open-control-stack-ergonomics) (its README and `docs/demo.md` state what the demo does and does not prove). For the full selected integration, use the [hub quickstart](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/quickstart.md), whose runner supplies exact producer checkouts and test wiring.

Run the tests with `python -m pytest` and the example check with `aam check-examples` (the same two commands the CI workflow runs; see [CONTRIBUTING](CONTRIBUTING.md)).

## What ships

Status labels: **merged** = merged in this repository; **selected** = pinned in the hub lock; **known limit**; **proposed**. See the [stack map](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/stack-map.md#status-labels). A newer commit here is not selected until the hub lock changes.

### Command-line tool `aam`

| Command | Purpose | Label |
|---|---|---|
| `aam validate <manifest.json>` | Validate a manifest and report errors and warnings. | selected |
| `aam summarize <manifest.json>` | Summarize the declared actions and their requirements. | selected |
| `aam list-actions <manifest.json>` | Table of actions with posture, authority scopes and review mode. | selected |
| `aam check-examples` | Validate every `examples/*.manifest.json` file. | selected |

### Manifest versions and contracts

| Item | What it is | Label | Details |
|---|---|---|---|
| Manifest 1.0 | The base format; still loads and validates. It is not the runtime-consumption profile. | merged | [format](docs/manifest_format.md) |
| Manifest 1.1 | Runtime-consumption profile: stable `action_id` and `adapter_id`, `target_policy`, `effect_limits`, `authority_context` references; canonical manifest, payload and proposal commitments; deterministic declaration matching. | selected | [contract](docs/runtime_consumption_contract.md) |
| Stricter 1.1 checks after the lock | E022 and E023 (explicit, usable `effect_limits`), proposal mismatch reports `action_blocked`, `missing_effect_limits` and `missing_amount_limit`, strict number handling, bounded loader. | merged | [contract](docs/runtime_consumption_contract.md), [CHANGELOG](CHANGELOG.md) |
| Runtime Action Proposal 1.2 | Tenant-aware proposal generation: requires `tenant_id` (refused in 1.1); no generation label is carried yet. A W0 candidate contract. | merged, not selected | [W0 contract](docs/w0-c1-c6-contracts.md) |
| OpenAPPA declaration binding | Optional helper that builds a declaration record from a 1.1 manifest. It is not imported by the default path, asks OpenAPPA for nothing and grants nothing. | merged, not selected | [binding page](docs/integrations/openappa-binding.md) |

### Python modules (`src/agent_action_manifest/`)

| Module | Purpose |
|---|---|
| `models` | Pydantic models for the manifest, actions, requirements and the runtime proposals (1.1 and 1.2). |
| `loader` | `load_manifest`, `load_manifest_json`, `dump_manifest`; bounded and atomic file handling. |
| `validator` | `validate_manifest`, returning a `ValidationReport` with error and warning codes. |
| `binding` | Manifest, payload and proposal digests; `resolve_action`; `proposal_mismatches`. |
| `openappa_binding` | Optional OpenAPPA declaration binding (see above). |
| `cli` | The `aam` entry point. |

### JSON schemas (`schemas/`)

| Schema | Describes |
|---|---|
| `agent_action_manifest.schema.json` | The manifest document (includes the 1.1 conditions). |
| `tool_action.schema.json` | One action declaration. |
| `authority_requirement.schema.json`, `authority_context_requirement.schema.json` | Authority scope requirements and Authority Context references. |
| `review_requirement.schema.json`, `reliance_requirement.schema.json` | Review mode and reliance requirements. |
| `payload_policy.schema.json`, `redaction_hint.schema.json` | Payload field rules and redaction hints. |
| `target_policy.schema.json`, `effect_limits.schema.json` | Finite targets and explicit effect limits (1.1). |
| `runtime_action_proposal.schema.json`, `runtime_action_proposal_v1_2.schema.json` | The runtime proposal in generations 1.1 and 1.2. |
| `validation_report.schema.json` | The validation report. |

The schemas and the Python validator each check rules the other does not; a conforming consumer runs both.

### Examples (`examples/`)

| File | Shows |
|---|---|
| `customer_service_agent.manifest.json` | Declaration structure for a customer service agent (four actions). |
| `finance_workflow_agent.manifest.json` | Dual-control approval and audit export declarations. |
| `internal_research_agent.manifest.json` | Read, summarize and export declarations with human review. |
| `procurement_agent.manifest.json` | Purchase order and vendor email declarations. |
| `refund_integration_v1_1.manifest.json` | The synthetic bounded refund fixture for the 1.1 runtime-consumption profile. |
| `runtime_action_proposal_v1_2.json` | An example tenant-aware proposal (1.2). |

The refund fixture is integration evidence; the other domain examples demonstrate declaration structure, not deployed sector assurance. See [examples](docs/examples.md).

## Documentation

The [documentation index](docs/README.md) lists every page in this repository by role, with historical pages labelled. Start with:

- [Concepts](docs/concepts.md) and the [manifest format](docs/manifest_format.md).
- The [runtime consumption contract](docs/runtime_consumption_contract.md) for Manifest 1.1.
- [Integration with the Control Plane](docs/integration_with_agent_control_plane.md).
- [Examples](docs/examples.md).

For a nontechnical introduction, read the [business overview](collateral/business-collateral.md) and [one-page overview](collateral/one-page-overview.md). Both describe this component's role and evidence limits, not additional runtime features.

## Selection and compatibility

Use the [current component lock](https://github.com/cogno-us/cognous-open-control-stack/blob/main/component-lock.json) for integration selection and the [central test hub](https://github.com/cogno-us/cognous-stack-qualification/blob/main/results/readme-commentary/index.md) for revision-specific qualification commentary. Source acceptance, selection and deployment approval remain separate decisions. The package version and the runtime consumption profile are different version axes.

<!-- pin-round: the lock pin for action_manifest is 46c950bed37f; the "merged, not selected" and "after the lock" labels above and in docs/README.md describe what main adds. Re-read them when the pin moves. -->

Operational deployment trust is still [HOLD under orchestrator #30](https://github.com/cogno-us/cognous-stack-orchestrator/issues/30). No signature, evidence package, successful test or source merge creates a production grant, proves external settlement, or changes selected release authority. Test results, run commentary and historical qualification records are read against their recorded source revisions.

## Where it fits: Cognous stack components

<a id="cognous-stack-components"></a>

<!-- stack-map:start -->
<!-- Canonical block: identical text in every component README. Source: docs/stack-map.md in the hub. Refresh at the pin round. -->
The Open Control Stack groups its repositories by responsibility. The groups are a navigation map, not an execution sequence and not a requirement to install every component. The hub [component lock](https://github.com/cogno-us/cognous-open-control-stack/blob/main/component-lock.json) is the only source of selected revisions; [release status](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md) states their evidence and limits. Last checked against `component-lock.json` at hub commit `dcc9bd7533ef`.

| Group | Members |
| --- | --- |
| **01 Knowledge & Provenance** | [Evidence Registry (The Index)](https://github.com/cogno-us/cognous-evidence-registry) · [Evidence Attestation (BitRep)](https://github.com/cogno-us/cognous-evidence-attestation) |
| **02 Institutional Governance** | [Institutional Governance (Alvorada)](https://github.com/cogno-us/cognous-institutional-governance) |
| **03 Declaration & Policy Control** | [Action Manifest](https://github.com/cogno-us/cognous-action-manifest) · [Control Plane](https://github.com/cogno-us/cognous-control-plane) |
| **04 Constrained Execution** | [Execution Runtime](https://github.com/cogno-us/cognous-execution-runtime) |
| **05 Replay & Evidence** | [Replay Bundle](https://github.com/cogno-us/cognous-replay-bundle) · [Governance Evidence Pack](https://github.com/cogno-us/cognous-governance-evidence-pack) · [ODES](https://github.com/cogno-us/open-decision-evidence-standard) |
| **Cross-cutting exchange** | [Governed Exchange (GAX/IMX)](https://github.com/cogno-us/cognous-governed-exchange) |
| **Tooling and qualification** (side group) | [Ergonomics (`cognous-ocs`)](https://github.com/cogno-us/cognous-open-control-stack-ergonomics) · [Verifier](https://github.com/cogno-us/cognous-open-control-stack-verifier) · [Orchestrator](https://github.com/cogno-us/cognous-stack-orchestrator) · [Qualification](https://github.com/cogno-us/cognous-stack-qualification) |

Status labels used in this README: **merged** (reviewed and merged in the owning repository; not by itself selected), **selected** (pinned in the hub lock), **known limit** (a limitation that is stated and kept visible) and **proposed** (draft or planned work, not a supported interface). Full map, names and commands: [stack map](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/stack-map.md), [naming](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/naming.md), [profiles and tools](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/profiles-and-tools.md). A signature, registry entry, message receipt or evidence summary does not grant execution authority.
<!-- stack-map:end -->

## Known limits

Each item below is **known limit** documented in this repository.

- A declaration is not permission to execute. A valid manifest, digest or matching proposal is never an authorization token; the Control Plane resolves current authority separately ([contract](docs/runtime_consumption_contract.md#declaration-matching-is-not-authorization)).
- The JSON schemas and the Python validator each check rules the other does not; a conforming consumer runs both ([format](docs/manifest_format.md#schemas-and-python-checks-are-complementary)).
- The payload policy checks field names, not values. A payload field that selects a recipient, resource or amount must be expressed as the action's `target` or `amount`; a field with an in-scope name and a wrong value passes this check. A per-field value constraint is not part of this contract ([format](docs/manifest_format.md#payload-policy-checks-field-names-not-values)).
- An action with no declared `effect_limits` gets an implicit ceiling of amount 0 and one effect when matched; it is never read as unbounded.
- Redaction hints are advisory; the exporting system must apply them.
- Sink declarations in the optional OpenAPPA binding are not evidence of interception or of target coverage.
- Review original artifacts and exact source revisions before extending a claim to a new environment. New dependencies, authority sources, destinations or enforcement mechanisms need their own compatibility and qualification.

More shared scope and limits are stated once in the hub [guarantees and limits](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/guarantees-and-limits.md).

## Contributing and attribution

[Contribution guidance](CONTRIBUTING.md) describes review and validation expectations; see also the [security policy](SECURITY.md), the [code of conduct](CODE_OF_CONDUCT.md) and the [changelog](CHANGELOG.md). Keep evidence-linked claims, preserve historical records and separate proposed features from accepted implementation.

See [LICENSE](LICENSE) and [attribution](NOTICE) for the existing terms and third-party scope. Developed by [Cognous](https://cogno.us).

## Repository locations

See the [repository rename map and compatibility notes](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/repository-renames.md) for current component URLs. Existing package names, schema identifiers and retained producer identities are unchanged.

---

## Bibliography

Selected external sources from the October 2026 research review. These inform evaluation questions; they do not establish Cognous implementation, adoption, conformance or production qualification.

- [OWASP GenAI Security Project. *State of Agentic AI Security and Governance*, version 2.01 (June 2026)](https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/). Security synthesis covering agent identity, delegated permissions, tool access and containment.
- [John M. Willis. *Runtime Governance Body of Knowledge for Artificial Intelligence and Other Autonomous Systems — Glossary* (19 July 2026)](https://sustainablefuturetech.com/asg-wg-runtime-governance-glossary/). Discussion draft on authority, execution and evidence terminology; not an adopted standard or Cognous conformance requirement.
- [OECD. *Agentic AI in organisations: Early insights from practitioner interviews*. OECD Artificial Intelligence Papers, No. 65 (2026)](https://doi.org/10.1787/1257a26f-en). Qualitative practitioner research on bounded autonomy, oversight and organizational deployment.

See the [research bibliography](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/research-bibliography.md) for review scope and source-verification limits.

<!-- Retained anchors for existing documentation links. -->
<a id="current-selection-historical-evidence-and-a-bounded-example"></a>
<a id="evidence-and-supported-scope"></a>
