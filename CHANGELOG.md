# Changelog

## Unreleased

- Added backward-compatible manifest v1.1 runtime-consumption profile with stable action and adapter identities.
- Added finite target/effect declarations and reference-only Alvorada Authority Context 0.1.0 mappings.
- Added canonical manifest/payload commitments and deterministic declaration-matching helpers; these do not authorize execution.
- Added synthetic refund pilot fixture and adversarial tests for unknown actions, adapter/target/payload substitution, digest/version mismatch, amount limits, and authority requirement substitution.
- Pinned bounded Alvorada integration baseline `fb3d97938969a89e149e8ff8db2756091d1233fc`; no deployment or institutional adoption is claimed.

- Added semantic alias for E008: privileged_action_missing_authority.
- Added customer-service email draft reliance requirement.
- Confirmed E015 disallowed-tool validation behavior.
- Updated validation report schema for ValidationIssue.alias.
