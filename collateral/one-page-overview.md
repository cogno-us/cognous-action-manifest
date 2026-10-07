# Agent Action Manifest — One-Page Overview

## Purpose

A lightweight format, Python validator and CLI for describing the actions an AI agent may propose. Manifest 1.1 adds deterministic runtime bindings so a downstream controller can compare a proposal with a specific declared action.

## Problem

A tool name is not a sufficient policy boundary. The same integration can read information, draft a message, issue a payment or delete a record. Reviewers need an explicit action inventory and developers need stable identifiers and constraints that survive handoff to runtime control.

## What It Provides

- **Action inventory:** Identify tools, action types, owners and the intended scope of an agent before execution.
- **Governance requirements:** Declare authority, review and reliance requirements without issuing grants.
- **Payload handling:** Describe sensitive fields and redaction hints for downstream record handling.
- **Runtime binding:** Bind stable action and adapter IDs, finite targets, effect limits and Authority Context references under the 1.1 profile.

## Where It Fits

A reviewer declares a routine refund and its allowed adapter, target and effect limits. The runtime binds a proposal to that manifest commitment. The Control Plane then independently resolves institutional authority and checks the actual proposal; matching the declaration alone never authorizes the refund.

A valid signature, chain inclusion, message receipt, reasoning instruction or evidence-package digest does not authorize execution. Institutional authority must be supplied and evaluated through the appropriate trusted boundary.

## Evidence and Limits

The [accepted hub lock](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/component-lock.json) selects this component at `46c950bed37fe3812000895430bc0312d29e37ce`. Read the component's [README](../README.md) for version-specific acceptance and the [hub support ledger](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md) for the executed scope. Component acceptance is not automatic adoption of newer revisions or production qualification.

This is declaration and validation, not a security boundary or runtime access-control system. A valid manifest does not establish institutional legitimacy, current approval, a completed effect or compliance. Redaction hints must be applied by the exporting system.

## Practical Next Step

Choose one bounded example and follow the [README](../README.md). Compare expected and observed results and retain uncertainty. The [business collateral](business-collateral.md) supplies evaluation questions and the component's wider context.

[Cognous](https://cogno.us) · [Source](https://github.com/cogno-us/cognous-agent-action-manifest) · [All stack components](https://github.com/cogno-us/cognous-open-control-stack). Existing licenses and notices apply.
