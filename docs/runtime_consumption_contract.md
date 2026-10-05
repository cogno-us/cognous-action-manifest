# Runtime consumption contract — manifest v1.1

This document defines the bounded consumption contract for an independent runtime.
It does **not** authorize actions, issue institutional grants, resolve Alvorada
authority, or execute tools.

## Pinned upstream authority baseline

For the bounded synthetic integration pilot, the accepted Alvorada baseline is:

- repository: `cogno-us/constitutional-governance-for-institutions`
- commit: `fb3d97938969a89e149e8ff8db2756091d1233fc`
- Authority Context schema: `0.1.0`
- pilot: simulated customer refund workflow with routine and higher-consequence cases

The Governor accepted the Authority Context consumer mapping, finite scopes,
narrowing delegation, and hold behavior on policy/status mismatches. The Control
Plane owns actual resolver integration. Real institutions retain mandate, grant,
approval, escalation, and remedy authority.

## What v1.1 adds

A v1.1 action declaration carries stable `action_id`, stable tool
`adapter_id`, finite `target_policy`, explicit `effect_limits`, and
reference-only `authority_context` requirements, alongside existing payload,
review, reliance, authority-scope, and redaction declarations.

A consumer must reject unsupported manifest versions rather than silently coercing
them. v1.0 remains loadable and valid for backward compatibility, but it is not
the runtime-consumption profile defined here.

## Canonical commitments

`manifest_digest` is SHA-256 over UTF-8 JSON produced from the complete Pydantic
manifest representation with keys sorted, compact separators, explicit nulls, and
NaN disallowed. The stored value is `sha256:<lowercase hex>`.

A runtime proposal must bind the exact manifest ID/version/digest, action ID,
adapter ID, target, payload, amount/unit/effect count, and Authority Context
requirement references used for evaluation.

Changing any bound field creates a materially different proposal and requires a
new downstream decision.

## Declaration matching is not authorization

`proposal_mismatches()` performs deterministic structural matching only. An
empty mismatch list establishes only that a proposal fits this declaration.

The Control Plane must separately resolve current institutional authority,
including actual grant/revision, issuer mandate, delegation chain, approval
records, policy versions, grant status/currentness, rule conflicts, and required
evidence. A valid manifest, valid digest, or matching proposal is never an
authorization token.

## Alvorada mapping

| Manifest field | Authority Context 0.1.0 concept | Consumer obligation |
|---|---|---|
| `authority_context.profile_ref` | selected implementation profile | require exact supported profile |
| `authority_context.requirement_id` | `requirement.requirement_id` | resolve current requirement |
| `authority_context.institution_id` | `institution.institution_id` | bind institutional domain |
| `authority_context.authority_domain` | `institution.authority_domain` | bind authority scope |
| `authority_context.consequence_tier` | `requirement.consequence.tier` | select corresponding process burden |
| `authority_context.evidence_obligation_ids` | `requirement.evidence[].obligation_id` | resolve required evidence |
| `target_policy.allowed_targets` | permission targets | proposal must stay within declaration and resolved grant |
| `effect_limits` | permission max amount/unit/effects | downstream grant may only narrow these limits |

The Manifest does not copy grants, approval records, status records, or mandate
records. Those are dynamic authority facts owned by institutional sources and
resolved downstream.

## Required negative cases

A conforming consumer test suite should reject or hold at least:

1. unknown action ID;
2. unsupported or changed manifest version;
3. changed manifest digest;
4. substituted adapter;
5. target outside the finite declaration;
6. payload fields outside the declared envelope;
7. amount/effect count above declaration limits;
8. Authority Context profile or requirement mismatch.

Policy/status mismatches, expired/revoked grants, approval failures, and
delegation-chain failures belong to the Control Plane resolver, not this module.
