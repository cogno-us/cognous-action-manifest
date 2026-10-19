# Documentation index: Cognous Action Manifest

Every documentation page in this repository, by purpose. Historical and proposal pages are labelled rather than hidden: they stay valid for the revision or plan they describe and do not describe the current selection. Back to the [repository README](../README.md).

Labels follow the hub [stack map](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/stack-map.md#status-labels): **merged**, **selected**, **known limit**, **proposed**. Names are explained in the hub [naming table](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/naming.md).

## Start by role

| Your role | First page | Then |
|---|---|---|
| New reader | [Concepts](concepts.md) | [Manifest format](manifest_format.md), [examples](examples.md) |
| Writing a manifest | [Manifest format](manifest_format.md) | [Examples](examples.md), then `aam validate` (see the [README quick start](../README.md#quick-start-about-one-minute)) |
| Building a runtime or controller that consumes manifests | [Runtime consumption contract](runtime_consumption_contract.md) | [Control Plane integration](integration_with_agent_control_plane.md), [W0 contract](w0-c1-c6-contracts.md) |
| Reviewer judging what a manifest proves | [Runtime consumption contract](runtime_consumption_contract.md#declaration-matching-is-not-authorization) | [Known limits in the README](../README.md#known-limits), [security policy](../SECURITY.md) |
| Contributor | [CONTRIBUTING](../CONTRIBUTING.md) | [Changelog](../CHANGELOG.md), [code of conduct](../CODE_OF_CONDUCT.md) |

## Current pages

| Page | What it covers | Label |
|---|---|---|
| [Concepts](concepts.md) | The core concepts: manifest, tool, action, authority, review, reliance, payload policy, redaction hint, validation report. | merged |
| [Manifest format](manifest_format.md) | Every field, the action types and review modes, the 1.1 runtime-consumption fields, how the schemas and the Python checks differ, and why the payload policy checks field names and not values. | merged; 1.1 selected |
| [Runtime consumption contract](runtime_consumption_contract.md) | Manifest 1.1: canonical commitments, declaration matching, the Authority Context mapping and the required negative cases. | selected |
| [Integration with the Control Plane](integration_with_agent_control_plane.md) | How a manifest relates to the Control Plane, Replay Bundle and Evidence Pack. This repository implements only the manifest format. | merged |
| [Examples](examples.md) | What each example manifest declares. | merged |
| [OpenAPPA declaration binding](integrations/openappa-binding.md) | Optional helper that produces a declaration record, not a wire request, grant or permission. The page records the revision it was written against. | merged |
| [W0 contract: exact action and declaration projection](w0-c1-c6-contracts.md) | Runtime Action Proposal 1.2 (tenant-aware) and the declaration projection. A W0 candidate contract; contract bytes and migration rules only. | merged |

## Historical and planning pages

| Page | What it is | Label |
|---|---|---|
| [Roadmap](roadmap.md) | Planned and possible future work and the out-of-scope list. Items are plans, not features. | proposed |
| [Remediation proposal (October 2026)](security-cloud-remediation-20261016.md) | The original proposal for four findings, kept as written, with a status note that the corrections are merged. Its test count is a historical figure. | historical |
| [Changelog](../CHANGELOG.md) | Unreleased changes and earlier notes, newest first. | merged |

## Other files

- [README](../README.md): what it is, quick start, what ships, known limits.
- [SECURITY](../SECURITY.md): scope of the library and how to report an issue.
- [CONTRIBUTING](../CONTRIBUTING.md), [CODE_OF_CONDUCT](../CODE_OF_CONDUCT.md), [LICENSE](../LICENSE), [NOTICE](../NOTICE).
- [Business overview](../collateral/business-collateral.md) and [one-page overview](../collateral/one-page-overview.md): nontechnical introductions. They describe this component's role and evidence limits, not additional features.
- JSON schemas are in [`schemas/`](../schemas), examples in [`examples/`](../examples); the README lists each.
