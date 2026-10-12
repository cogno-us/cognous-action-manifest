# Optional OpenAPPA declaration binding

This opt-in helper produces a Cognous declaration record, not an OpenAPPA wire
request, policy decision, grant or execution permission. It is not imported by
the default runtime path. The `authority_effect` export is always `none`.

Resumed against Manifest main `911f177822d9ec067e800594e8ecf7a0bb265bdc`.
The associated hub profile is PR #44. Source acceptance does not update the
hub's selected component lock or establish an operational adapter.

The helper binds Manifest 1.1 digest, action/tool/adapter identities, finite
allowed targets, complete parameter-role declarations and explicit sinks.
It rejects blank, padded/control-character or duplicate identities, duplicate
or contradictory payload fields, incomplete/unknown roles and invalid sinks.
It does not normalize identities silently. Returned tuples do not alias the
mutable manifest; exported record lists do not mutate the binding.

Sink declarations are not evidence of interception or proof of target coverage.
A future runtime join must bind actual operation, tenant, target, payload,
policy and current authority separately. It must validate the complete native
proposal and preserve effect/attempt distinctions; this helper grants nothing.

Validation: Python 3.12, full suite 138 passed, including 21 binding cases.
The initial run before editable installation failed CLI tests because `aam`
was absent; after normal dev installation all tests passed. No upstream runtime
or wire-conformance tests were executed. Existing example validation is a
separate repository check. Protocol-1 fixtures and two-sided runtime denial
qualification remain the next gate; no credentials or production effects.
