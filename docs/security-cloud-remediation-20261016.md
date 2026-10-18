# Security Cloud remediation proposal — cognous-action-manifest

Scan: https://chatgpt.com/codex/cloud/security/runs/wfr_c0b32cbd56ce15d30ad6bc205f39363591aaec580e5196bfa1ba8d5e64892746
Scanned/base revision: `6789b0768eb64596df614d0fee6c5d04fa876e8f`.

Status update (2026-10-18): the corrections below are merged in `f9ae8527` (#20: `extra="forbid"`, nonfinite rejection, CLI escaping, each with tests); the suite was 159 tests at that head and later hardening is in #21. The text below is the original proposal, kept as written; owner disposition of each finding is not recorded here.

Reject unknown policy/tenant fields, nonfinite limits and metadata; require mandatory authority; reject invalid declarations during binding; visibly escape terminal control bytes. Historical 1.1 stays tenant-unaware and now rejects tenant-bearing input instead of silently discarding it.

## Finding coverage

- `csf_9e0019407c08ac07b2f5abfd` (medium): Public model parsing silently discards schema-invalid policy and tenant fields. Proposed code correction; final disposition pending review and source-bound checks.
- `csf_9edaf94a1bd90f36c396dbca` (medium): Optional authority entries bypass mandatory authority validation and permission binding. Proposed code correction; final disposition pending review and source-bound checks.
- `csf_d0a4c99db59c663295896d09` (low): Accepted non-finite values break canonical matching and produce non-standard dumps. Proposed code correction; final disposition pending review and source-bound checks.
- `csf_254a9b3977d42ce8bbaece46` (low): Manifest-controlled strings can inject terminal control sequences into CLI output. Proposed code correction; final disposition pending review and source-bound checks.

## Validation and limits

145 tests passed.

Component changes require integrated qualification before any selected hub pin advances. These are proposed repairs; passing local checks is not independent security certification. The package frozen at hub `7f335099ca52a68533b6e78c2e35166a9109e35c` has not been regenerated or relabeled as containing these edits. No publication or production authorization is granted. No paid model trials, production probes or external communications ran.
