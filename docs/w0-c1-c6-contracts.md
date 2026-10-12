# W0 contract addendum: C1 exact action and C6 declaration projection

Status: W0 candidate contract. This document defines contract bytes and migration rules only; it does not grant authority or implement downstream enforcement.

## Baseline
- inspected main: `a56a15efd3d9524698b204dc43f5f874dcc4cd96`
- selected Manifest 1.1 revision remains `46c950bed37fe3812000895430bc0312d29e37ce`
- Manifest 1.1 and existing `RuntimeActionProposal` remain valid historical contracts.

## C1 generation: Runtime Action Proposal 1.2
W0 freezes a new tenant-aware proposal generation named `runtime-action-proposal/1.2`. Existing 1.1 bytes are not rewritten.

Required consequential fields:
- `tenant_id`: bounded opaque UTF-8 string, 1..128 characters after JSON decoding; no trimming, case folding, Unicode normalization or inference is performed by this contract.
- existing `manifest_id`, `manifest_version`, `manifest_digest`, `actor`, `principal`, `action_id`, `adapter_id`, `target`, `payload`, `payload_commitment`, `requested_permissions`, `amount`, `unit`, `effects`, authority/profile references and temporal fields.

`tenant_id` is supplied by trusted deployment/authority context. Caller metadata, target strings, payload values and adapter responses MUST NOT create or replace tenant scope.

Canonical proposal commitment is SHA-256 over compact sorted-key UTF-8 JSON using `ensure_ascii=false`, `allow_nan=false`; the complete 1.2 proposal includes `tenant_id`. Omitted and null are distinct JSON states. Numeric amount follows JSON number serialization used by the accepted commitment helper; non-finite values are invalid.

A tenant-only substitution therefore changes the proposal commitment and cannot reuse a prior authorization binding or effect identity.

## C6 declaration projection
The Manifest owns only the declaration-side exact projection:
`action_id + adapter_id + target + payload/parameter roles + tenant_id + profile generation`.

Optional flow/result-admission profiles may add source/sink/recipient/parameter role declarations, but:
- they cannot weaken the C1 required fields;
- an external flow allowance is not Cognous authority;
- result admission has a distinct result identity from dispatch/effect identity;
- unsupported or unmapped protected operations fail closed.

OpenAPPA PR #10 remains an unaccepted optional proposal and is not part of this baseline.

## Compatibility
- 1.1 decoders continue to decode historical 1.1 artifacts.
- 1.2 requires `tenant_id`; no default/backfill is permitted.
- A 1.1 artifact cannot be relabeled 1.2 or claim tenant-aware assurance.
- W1 owns implementation of producer validation/persistence. W4 owns any OpenAPPA-specific projection implementation.
