# Changelog

## Unreleased

- Added E022 (`missing_effect_limits`): non-blocked effectful v1.1 actions must declare explicit `effect_limits`; the docs now describe it as required, and state that the Python models are not a schema-conformance check.
- Added backward-compatible manifest v1.1 runtime-consumption profile with stable action and adapter identities.
- Added finite target/effect declarations and reference-only Alvorada Authority Context 0.1.0 mappings.
- Added canonical manifest, payload, and full-proposal commitments plus deterministic declaration matching; these do not authorize execution.
- Runtime proposals now carry actor/principal, requested permissions, temporal bounds, risk metadata, expected side effects, correlation/run IDs, and evidence references for downstream binding.
- Added synthetic refund pilot fixture and adversarial tests for unknown actions, adapter/target/payload substitution, digest/version mismatch, amount limits, and authority requirement substitution.
- Pinned bounded Alvorada integration baseline `fb3d97938969a89e149e8ff8db2756091d1233fc`; no deployment or institutional adoption is claimed.

- Added semantic alias for E008: privileged_action_missing_authority.
- Added customer-service email draft reliance requirement.
- Confirmed E015 disallowed-tool validation behavior.
- Updated validation report schema for ValidationIssue.alias.
