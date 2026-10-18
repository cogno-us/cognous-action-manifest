# Changelog

## Unreleased

### Changed - input validation hardening (fix round 2)
- `proposal_mismatches` reports `action_blocked`, `missing_effect_limits` and `missing_amount_limit`.
- The shared structure walker refuses unpaired surrogates in strings and dictionary keys.
- `dump_manifest` creates new files with fixed mode 0600 via `os.open` and no longer reads or sets the process umask; existing files keep their mode.
- JSON schema: non-blank `manifest_version`/`manifest_id`/`agent_name`/`field_path`, supported `manifest_version` values, v1.1 `action_id`, finite `target_policy` and `authority_context` for effectful non-blocked actions, `reviewer_role` for `approval_required`. `EffectLimits.max_amount` and `max_effects` no longer coerce strings or booleans.
- Added a schema-versus-validator parity test with its known differences listed.

### Fixed — scan remediation (stream C, manifest)
- v1.1 validator: effectful, non-blocked actions need `effect_limits` with a non-null `max_amount` and a non-empty `unit`, or `max_amount` 0 as an explicit non-monetary mode (new E023 `incomplete_effect_limits`). Schema (`$defs/effect_limits_v1_1`) and docs aligned. An empty `effect_limits` object that previously validated is now invalid.
- `dump_manifest` encodes before opening a file and replaces atomically; unencodable text raises `ValueError` and leaves the existing file intact.
- `load_manifest` turns non-UTF-8 bytes and over-deep nesting into `ManifestLoadError` and refuses files over `MAX_MANIFEST_BYTES` (4 MiB).
- CLI escapes non-printable characters in untrusted values (`isprintable`, `\xNN`/`\uNNNN`) and no longer escapes its own line breaks.
- Removed the tracked build artefacts (`*.egg-info`, `__pycache__`); added `.gitignore`.

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
