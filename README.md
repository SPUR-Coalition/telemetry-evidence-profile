# SPUR Evidence Profile

**Evidence mechanisms for Content Telemetry claims.**

This repository holds the SPUR evidence profile: an optional profile layered on the [Content Telemetry standard](https://github.com/SPUR-Coalition/telemetry) that defines how telemetry claims can be corroborated. It is a working draft; nothing here is normative yet.

Core telemetry events are claims by identified emitters (SCOPE.md in the standard). Core deliberately answers only the first of its five conformance questions - syntactic validity. This profile takes up the next three: cryptographic validity, trust-policy acceptance, and factual truth and completeness. Entitlement as a legal conclusion belongs to governing terms and is out of scope here as it is in core.

## What the profile builds on

Version 1.0 of the standard carries the hooks this profile uses, and nothing more:

- Events are claims; no field raises its own evidentiary status (standard, sections 5.2.3 and 6.8, SCOPE.md)
- `content_fingerprint` on grounding events: `scheme`, `detected`, `value`, detection only (section 6.4)
- The generic evidence slot on content events: `scheme`, detached `ref`, `digest` (section 6.8)
- Manifest signing keys (section 8.4) and the `Content-Telemetry-ID` retrieval correlation (section 7.2)

The profile pins the core version it targets and cannot redefine core event semantics.

## Modules

One profile, four modules. Each module states the bounded proposition its evidence supports. The boundary rule binds all of them: access evidence never becomes proof of grounding, and cryptographic validity never becomes factual truth, completeness, or entitlement.

| Module | Proposition supported | Origin | Editors |
|--------|----------------------|--------|---------|
| [Fingerprint schemes](./modules/) | A declared scheme's signal was checked in an identified representation | Standard issues #5, #16, #17; PR #21 | [TBC] |
| [VPTS seeded observations](./modules/) | A publisher-seeded marker was observed in reported or sampled output | Standard issue #18 | [TBC] |
| [Recomputable attribution](./modules/) | A disclosed attribution result recomputes from disclosed inputs | Standard issues #19, #20 | [TBC] |
| [Entitlement credentials](./modules/) | A signed, unrevoked grant from an identified issuer covered the reported access | Standard issue #22; PR #34 | [TBC] |

Module maturity is described as workflow levels V0-V3 within the profile; the levels describe how far a module's tooling and fixtures have progressed, not a ladder of assertion strength.

The recomputable-attribution module also specifies the attribution report shape its recomputation check runs over. That carrier travels as a namespaced extension in the standard's `data` container, which profiles may define (SCOPE.md in the standard); listing it as a known extension in the core repository is a separate step, taken once two independent estimators exchange the same shape (standard issue #19).

## Participating

The working group is chartered in [CHARTER.md](./CHARTER.md). Contribution does not require SPUR membership: file issues here, and propose new capabilities as short human-written notes per [CONTRIBUTING.md](./CONTRIBUTING.md). Decisions are recorded publicly on this tracker.

## Licence

Apache License 2.0. See [LICENSE](./LICENSE).
