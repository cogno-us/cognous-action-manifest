# Agent Action Manifest — Business Collateral

## 1. Executive Summary

A lightweight format, Python validator and CLI for describing the actions an AI agent may propose. Manifest 1.1 adds deterministic runtime bindings so a downstream controller can compare a proposal with a specific declared action.

## 2. The Business Problem

A tool name is not a sufficient policy boundary. The same integration can read information, draft a message, issue a payment or delete a record. Reviewers need an explicit action inventory and developers need stable identifiers and constraints that survive handoff to runtime control.

## 3. The Component in One View

| Capability | Practical role |
|---|---|
| Action inventory | Identify tools, action types, owners and the intended scope of an agent before execution. |
| Governance requirements | Declare authority, review and reliance requirements without issuing grants. |
| Payload handling | Describe sensitive fields and redaction hints for downstream record handling. |
| Runtime binding | Bind stable action and adapter IDs, finite targets, effect limits and Authority Context references under the 1.1 profile. |
| Validation and inspection | Use Pydantic models, JSON schemas and the aam CLI to validate, summarize and list actions. |

## 4. Who Should Evaluate It

Engineers can inspect the reference contracts and examples; enterprise architecture, security and governance reviewers can examine the boundary and evidence. Evaluate this component for its named responsibility rather than as a complete governance platform.

## 5. A Bounded Workflow

A reviewer declares a routine refund and its allowed adapter, target and effect limits. The runtime binds a proposal to that manifest commitment. The Control Plane then independently resolves institutional authority and checks the actual proposal; matching the declaration alone never authorizes the refund.

This is a reference use case. Adopting the format or running the example does not establish a production deployment, institutional acceptance or measured business benefit.

## 6. Relationship to the Stack

This component contributes **declare the action before evaluating permission**. The [Cognous Open Control Stack](https://github.com/cogno-us/cognous-open-control-stack) connects declared proposals, independent authority, constrained execution and retained review evidence. Components remain separately owned and versioned; the [selected lock](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/component-lock.json) determines which revisions participate in the supported integration.

A valid signature, chain inclusion, message receipt, reasoning instruction or evidence-package digest does not authorize execution. Institutional authority must be supplied and evaluated through the appropriate trusted boundary.

## 7. What the Evidence Supports

The hub selects Manifest 1.1 at `46c950bed37fe3812000895430bc0312d29e37ce`. The package version and the runtime consumption profile are different version axes. The bounded refund fixture is integration evidence; the other domain examples demonstrate declaration structure, not deployed sector assurance.

The [accepted hub evidence](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/examples/control-plane-store-adoption/qualification-summary.json) supports bounded synthetic integration at its exact pins. Aggregate test totals do not establish deployment benefit, compliance or independent real-world verification. The [support ledger](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md) distinguishes the standard reference, separate protected-worker campaign and unqualified production work.

## 8. What It Does Not Establish

This is declaration and validation, not a security boundary or runtime access-control system. A valid manifest does not establish institutional legitimacy, current approval, a completed effect or compliance. Redaction hints must be applied by the exporting system.

## 9. Evaluation Questions

- Which exact input, output and source revision will the receiving system consume?
- Who supplies trusted authority or evidence, and which assumptions remain outside this component?
- Can a reviewer trace the result to retained sources, including rejected or missing information?
- Which documented checks were actually executed in the intended environment?
- What deployment-specific work is required before relying on the result?

## 10. Why Open Reference Material Matters

Public formats, source, examples and evidence allow reviewers to inspect the claimed boundary and reproduce its checks. They also expose what has not been tested. Openness supports review; it does not substitute for independent assurance or operating responsibility.

## 11. Practical Next Step

Follow the [README](../README.md) and select one bounded use case. Inspect its inputs and expected outputs, reproduce the documented checks where prerequisites are available, and record failures and unresolved assumptions alongside passes. Use the [one-page overview](one-page-overview.md) for initial stakeholder orientation.

## 12. Status and Attribution

This collateral summarizes merged public material at repository `b24ac11d5d63bccc7281cf22ba0f0b31a0510f27` and the accepted hub baseline `5737267d94d2b445735c95e8480a31de73a2abe8`. It does not anticipate pending branches. The protected-worker result applies only to its recorded Linux/bubblewrap fixture; live OpenShell and logical-intent prevention are not hub-supported at this snapshot.

[Cognous](https://cogno.us) · [Source repository](https://github.com/cogno-us/cognous-agent-action-manifest) · [Stack responsibilities](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/architecture.md). Existing licenses and third-party notices remain controlling.
