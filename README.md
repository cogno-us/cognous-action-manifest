<!-- cognous-banner:start -->
```text
──────────────────────────────────────────────────
   __________  _______   ______  __  _______
  / ____/ __ \/ ____/ | / / __ \/ / / / ___/
 / /   / / / / / __/  |/ / / / / / / /\__ \
/ /___/ /_/ / /_/ / /|  / /_/ / /_/ /___/ /
\____/\____/\____/_/ |_/\____/\____//____/
              AGENT ACTION MANIFEST
       g o v e r n e d   b y   d e s i g n
  github.com/cogno-us/cognous-open-control-stack
──────────────────────────────────────────────────
```
<!-- cognous-banner:end -->

# Agent Action Manifest

**Declare the action before evaluating permission.**

## Overview

A lightweight format, Python validator and CLI for describing the actions an AI agent may propose. Manifest 1.1 adds deterministic runtime bindings so a downstream controller can compare a proposal with a specific declared action.

**Implementation status:** this README describes merged public reference work. Component acceptance, selection in the hub and execution of a qualification are separate facts. The selected revision for this component is `46c950bed37fe3812000895430bc0312d29e37ce`; the [hub lock](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/component-lock.json) is the source of that integration choice.

## Purpose and intended users

A tool name is not a sufficient policy boundary. The same integration can read information, draft a message, issue a payment or delete a record. Reviewers need an explicit action inventory and developers need stable identifiers and constraints that survive handoff to runtime control.

Engineers can inspect the reference contracts and examples; enterprise architecture, security and governance reviewers can examine the boundary and evidence. Evaluate this component for its named responsibility rather than as a complete governance platform.

## Key features

| Capability | Implemented or specified responsibility |
|---|---|
| **Action inventory** | Identify tools, action types, owners and the intended scope of an agent before execution. |
| **Governance requirements** | Declare authority, review and reliance requirements without issuing grants. |
| **Payload handling** | Describe sensitive fields and redaction hints for downstream record handling. |
| **Runtime binding** | Bind stable action and adapter IDs, finite targets, effect limits and Authority Context references under the 1.1 profile. |
| **Validation and inspection** | Use Pydantic models, JSON schemas and the aam CLI to validate, summarize and list actions. |

## How it works

A reviewer declares a routine refund and its allowed adapter, target and effect limits. The runtime binds a proposal to that manifest commitment. The Control Plane then independently resolves institutional authority and checks the actual proposal; matching the declaration alone never authorizes the refund.

A valid signature, chain inclusion, message receipt, reasoning instruction or evidence-package digest does not authorize execution. Institutional authority must be supplied and evaluated through the appropriate trusted boundary.

## Getting started

From a fresh repository checkout, use Python 3.11+ and an activated virtual environment. Install only into that environment. Package installation needs network access; the commands below exercise local reference tooling. For the full selected integration, use the [hub quickstart](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/quickstart.md), whose runner supplies exact producer checkouts and test wiring.

```bash
python -m pip install -e ".[dev]"
aam validate examples/refund_integration_v1_1.manifest.json
aam summarize examples/customer_service_agent.manifest.json
aam check-examples
```

## Evidence and supported scope

The hub selects Manifest 1.1 at `46c950bed37fe3812000895430bc0312d29e37ce`. The package version and the runtime consumption profile are different version axes. The bounded refund fixture is integration evidence; the other domain examples demonstrate declaration structure, not deployed sector assurance.

The accepted [hub persistence-generation evidence](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/examples/control-plane-store-adoption/qualification-summary.json) records 915 Python tests in each of two repetitions, 35 matrix entries satisfying their gates and 120 separate mocked OpenShell tests. Those are aggregate hub results, not a per-component test count or a claim of production readiness. Optional behavioral layers receive static checks only. The [support ledger](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md) separates implementation, execution and adoption.

## Limitations and deployment decisions

This is declaration and validation, not a security boundary or runtime access-control system. A valid manifest does not establish institutional legitimacy, current approval, a completed effect or compliance. Redaction hints must be applied by the exporting system.

Review original artifacts and their exact source revisions before extending a claim to a new environment. New dependencies, authority sources, destinations or enforcement mechanisms need their own compatibility and qualification. A passing reference case is not a certification of an enterprise deployment.

## Repository guide

Use these sources for details; their historical checkpoints retain the status and scope of the work they recorded:

- [docs/runtime_consumption_contract.md](docs/runtime_consumption_contract.md)
- [docs/manifest_format.md](docs/manifest_format.md)
- [docs/integration_with_agent_control_plane.md](docs/integration_with_agent_control_plane.md)
- [docs/examples.md](docs/examples.md)

For a nontechnical introduction, read the [business overview](collateral/business-collateral.md) and [one-page overview](collateral/one-page-overview.md). Both describe this component's role and evidence limits, not additional runtime features.

## Contributing and attribution

[Contribution guidance](CONTRIBUTING.md) describes review and validation expectations. Keep evidence-linked claims, preserve historical records and separate proposed features from accepted implementation.

See [LICENSE](LICENSE) and [attribution](NOTICE) for the existing terms and third-party scope. Developed by [Cognous](https://cogno.us); no licensing change is part of this documentation update.

---

## Bibliography

Selected external sources from the October 2026 research review. These inform evaluation questions; they do not establish Cognous implementation, adoption, conformance or production qualification.

- [OWASP GenAI Security Project. *State of Agentic AI Security and Governance*, version 2.01 (June 2026)](https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/). Security synthesis covering agent identity, delegated permissions, tool access and containment.
- [John M. Willis. *Runtime Governance Body of Knowledge for Artificial Intelligence and Other Autonomous Systems — Glossary* (19 July 2026)](https://sustainablefuturetech.com/asg-wg-runtime-governance-glossary/). Discussion draft on authority, execution and evidence terminology; not an adopted standard or Cognous conformance requirement.
- [OECD. *Agentic AI in organisations: Early insights from practitioner interviews*. OECD Artificial Intelligence Papers, No. 65 (2026)](https://doi.org/10.1787/1257a26f-en). Qualitative practitioner research on bounded autonomy, oversight and organizational deployment.

See the [research bibliography](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/research-bibliography.md) for review scope and source-verification limits.

## Cognous stack components

[Stack hub](https://github.com/cogno-us/cognous-open-control-stack) · [Selected pins](https://github.com/cogno-us/cognous-open-control-stack/blob/main/component-lock.json) · [Evidence and limits](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md)

Component links are navigation, not a requirement to install every component. The hub lock determines its supported integration.

| Component | Responsibility |
|---|---|
| [Agent Control Plane](https://github.com/cogno-us/cognous-agent-control-plane) | Evaluate proposals against authority and preserve the decision record |
| [Agent Replay Bundle](https://github.com/cogno-us/cognous-agent-replay-bundle) | Reconstruct what the retained records support |
| [Agent Governance Evidence Pack](https://github.com/cogno-us/cognous-agent-governance-evidence-pack) | Turn traceable runtime records into reviewable governance evidence |
| [Open Decision Evidence Standard](https://github.com/cogno-us/open-decision-evidence-standard) | Portable decision evidence across system and organizational boundaries |
| [Alvorada Experimental Workbench](https://github.com/cogno-us/alvorada) | Governed exchange and continuity for a bounded synthetic workflow |
| [Moltbot Safe](https://github.com/cogno-us/moltbot-safe) | Constrained execution beneath independent current authorization |
| [BitRep](https://github.com/cogno-us/bitrep) | Verify issuer signatures under explicit trust assumptions |
| [The Index](https://github.com/cogno-us/the-index) | A local blockchain reference for claims, evidence commitments and lifecycle history |
| [Portable Reasoning Protocol v1.0](https://github.com/cogno-us/portable-reasoning-protocol) | Portable instructions for evidence-bounded reasoning |
| [Research Intelligence Protocol v1.0](https://github.com/cogno-us/research-intelligence-protocol) | Disciplined discovery and cross-domain abstraction, kept separate |
| [TFA Protocol (S43)](https://github.com/cogno-us/truth-freedom-agency-protocol) | Truth · Freedom · Agency |
| [Constitutional Governance for Institutions](https://github.com/cogno-us/constitutional-governance-for-institutions) | Alvorada: authority, challenge and correction for institutions |
