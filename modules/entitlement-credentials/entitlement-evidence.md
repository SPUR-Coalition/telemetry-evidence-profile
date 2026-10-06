# Entitlement evidence profile

**Status:** module of the SPUR evidence profile (`SPUR-Coalition/telemetry-evidence-profile`), migrated from telemetry#34
**Targets:** Content Telemetry v1.0 (2026-09-02), tag `v1.0`
**Profile identifier:** `entitlement-evidence/0.2`
**Change from 0.1:** migrated to the evidence-profile repository, recut against Content Telemetry v1.0, and three normative sections added (provenance, reconciliation checks, reporting granularity).
**Depends on:** SPECIFICATION.md §5.2 (`license_ref`), §8 (manifest)
**Related:** SPUR-Coalition/telemetry#22 (motivating issue), SPUR-Coalition/telemetry#21 and SPUR-Coalition/telemetry#11 (evidence classifications), SPUR-Coalition/telemetry#4 and SPUR-Coalition/telemetry#3 (governing-terms reference), SPUR-Coalition/telemetry#25 (modality - see §7.2)

## 1. Purpose and scope

### 1.1 Purpose

This module supports one bounded proposition: **a signed, unrevoked grant from an identified issuer covered the reported access.**

Core v1 carries the claim and this module grades the evidence for it. Core §5.2.3 says of `license_ref` that *"it records which grant the emitter says applied. It does not establish that the grant existed, that it covered this content, that it was valid at the time of use, or that the use was permitted"*, and that it *"does not identify the party whose entitlement was used"*. This module defines how a `license_ref` resolves to a verifiable credential, and what a verifier may then report. The outcome is always **"grant evidence verified"** or **"grant evidence not verified"** with an evidence class: evidence of a grant, never an adjudication of entitlement, price or compensation.

Per-event signing is informational in core v1 (§8.4: *"Per-event signing remains informational in v1"*). This module does not wait for it: it signs its own outcomes, so the verification result is itself portable evidence even where the events it grades are not. The credentials it verifies attest grants and ride `license_ref`; core's deferral of W3C Verifiable Credentials in §8.9 (*"Manifest signing (W3C Verifiable Credentials, JWS proofs)"*) concerns manifest signing and does not reach this module.

### 1.2 Non-goals

Consistent with SCOPE.md ("telemetry does not determine ownership, permission, price or compensation") and §1.3, this profile does NOT:

- define license terms, tariffs, pricing or compensation logic;
- determine ownership or resolve competing claims - a credential proves a party made a *signed, revocable declaration* about an asset, never that it owns it;
- introduce new event types, envelope fields or transport requirements;
- make core conformance depend on any external registry, resolver or verification service.

An implementation that ignores this profile remains fully core-conformant. A `license_ref` that cannot be verified under this profile is **downgraded in evidence class, never invalidated as an event**.

### 1.3 Relationship to the governing-terms layer

This profile verifies that a grant *exists, was issued by an identifiable issuer to an identifiable grantee, and covered the reported use at the reported time*. What the grant permits in legal detail lives in a governing-terms document, referenced from the credential via `credentialSubject.terms_ref` (§4.2) - the terms-document locator kept distinct from `license_ref`, as proposed in SPUR-Coalition/telemetry#3 and SPUR-Coalition/telemetry#4. Governing-terms semantics are out of scope here.

## 2. Conformance language

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY and OPTIONAL are to be interpreted as described in RFC 2119 and RFC 8174 (§1.5).

## 3. Entitlement evidence classes

This profile applies the evidence classifications proposed in SPUR-Coalition/telemetry#11 and SPUR-Coalition/telemetry#21 to the entitlement axis. Core v1.0 did not adopt them: accreditation tiers "belong in profiles layered on this specification" (§1.3), and core does not "assign evidentiary status: an event remains a claim by its emitter" (§6.8). Both issues remain open and are routed to this evidence profile. This profile uses the classifications as proposed; should the common frame of this repository settle them under different names, this profile adopts the settled names, and the semantics stated here are what is normative.

| Class | Meaning for `license_ref` | Verification |
|---|---|---|
| `claim` | Opaque reference (§5.2.3 opaque form or unresolvable URI); resolvable bilaterally, not by third parties | none |
| `origin_corroborated` | Resolves to a well-formed entitlement credential whose declared issuer is identifiable | §5 steps 1–2 |
| `independently_verifiable` | Full recipe against a public trust anchor (the issuer's `did:web` DID document, §4.4) with a trusted timestamp for status (§5.4) - matching the SPUR-Coalition/telemetry#11 tier-3 test of "checkable by any party against a public trust anchor and a trusted timestamp" | §5 steps 1–6 |

Consumers producing settlement or dispute artefacts SHOULD record, per event, the evidence class established, the verification timestamp and (where §5.4(c) applies) the status-list snapshot used.

## 4. The entitlement credential

### 4.1 Format

An entitlement credential is a W3C Verifiable Credential (Data Model 2.0) secured as a JWT per VC-JOSE-COSE: the credential is the JWS payload, header `typ: "vc+jwt"`. The signing algorithm MUST be `EdDSA` (Ed25519); verifiers MUST reject other `alg` values. A header `kid` naming a key absent from the issuer's published keys MUST fail verification - verifiers MUST NOT fall back to another published key.

`license_ref` carries one of: an HTTPS URL dereferencing to the credential; the credential's grant identifier (the §5.2.3 JWT-`jti` form), resolvable against the issuer's declared credential endpoint; or the compact JWS embedded directly (NOT RECOMMENDED above ~4 KB).

### 4.2 Credential body

The decoded payload MUST validate against `schema/entitlement-credential.json`. In summary:

| Claim | Requirement |
|---|---|
| `issuer` | REQUIRED - `did:web` DID or HTTPS URL under the issuer's apex domain; the grantor or its licensing agent (publisher, collecting society or intermediary) |
| `validFrom` / `validUntil` | REQUIRED - validity window of the credential itself |
| `credentialStatus` | Bitstring Status List v1.0 entry with `statusPurpose: "revocation"` - the monotonic purpose (once set, never cleared). Suspension (reversible) MUST NOT be used for entitlement grants: §5.4(c)'s snapshot inference relies on monotonicity. OPTIONAL only when `validUntil − validFrom` ≤ 30 days, otherwise REQUIRED |
| `credentialSubject.grantee` | REQUIRED - MUST match the reporting session's `agent_id` or a declared parent operator (§5 step 5) |
| `credentialSubject.rights` | REQUIRED - rights object per §4.5, each entry carrying `granted` |
| `credentialSubject.scope.duration` | OPTIONAL `starts`/`ends` licence term, possibly narrower than the credential window; absent → the credential window is the term |
| `credentialSubject.asset.sha256` | per-asset grants: digest the grant binds to (§5 step 6) |
| `credentialSubject.scope.content` | blanket grants: apex domains and/or `content_id` patterns mirroring session `content_scope` (§5.1); at least one of `asset.sha256` / `scope.content` REQUIRED |
| `credentialSubject.terms_ref` | REQUIRED - URL of the governing-terms document; a grant without discoverable terms is not opposable |

Verifiers encountering a credential missing `grantee` or `terms_ref` cap the evidence class at `origin_corroborated` (downgrade, not invalidation).

### 4.3 Sandbox credentials

Credentials whose `type` marks them as sandbox-issued MUST be rejected by production verifiers and yield at most class `claim` with a diagnostic warning.

### 4.4 Issuer key discovery

The issuer's key comes only from the issuer's own DID document: consumers MUST resolve **`did:web`** - `https://<domain>/.well-known/did.json` - and use `verificationMethod` entries carrying `publicKeyJwk` (OKP/Ed25519). Consumers MUST NOT take an issuer key from a Content Telemetry manifest: core §8.4 defines manifest `keys` as *"Public keys used to sign telemetry events emitted by this participant"*, which are emitter keys, not grant-issuer keys. Key material MUST be fetched over TLS from the issuer's DID document. Consumers SHOULD cache keys and status lists with retrieval timestamps and MUST NOT require online resolution to accept an *event*: offline consumers record the evidence class their cached material supports.

### 4.5 Rights vocabulary and event mapping

Grants use the rights vocabulary `train, rag, embed, display, eval, derive, commercial`. Core telemetry covers inference-time use only (§1.3), so entitlement checks for core events consult:

| Core event type | Covering right |
|---|---|
| `content_retrieved` | `rag` (`embed` where retrieval is for embedding) |
| `content_grounded` | `rag` |
| `content_cited` | `rag` |
| `content_presented` | `display` |
| engagement events | `display` |

`train`, `eval`, `derive` and `commercial` are carried for the governing-terms layer and non-telemetry consumers; they play no role in classifying core inference-time events.

## 5. Verification recipe (normative)

Given an event `E` carrying `license_ref` `R`, occurrence time `t = E.timestamp`, verification time `T`:

1. **Resolve** `R` to a credential `C` per §4.1. Failure → `claim`; stop.
2. **Parse** `C` against the schema; confirm `issuer` is identifiable per §4.4. Failure → `claim`. Success → at least `origin_corroborated`.
3. **Verify signature** against the issuer key (strict `alg`/`kid`, §4.1). Failure → `claim`; the consumer SHOULD additionally flag the credential as malformed evidence. Flagging is diagnostic, never event-invalidating.
4. **Temporal validity and status:**
   (a) `validFrom ≤ t ≤ validUntil`, and `t` within `scope.duration` where present.
   (b) **Authenticate the status list before consulting it:** the status-list credential MUST itself be a signed `vc+jwt` whose signature verifies against the published key of its issuer, and its issuer MUST equal the entitlement credential's issuer (or a status issuer that issuer explicitly declares). An unauthenticated status list establishes nothing; treat it as unresolvable status.
   (c) Check `credentialStatus` against the authenticated list. **Revocation is retroactive by default for unverified events:** a set bit fails this step regardless of when the revocation occurred. The only exception is an **issuer-signed snapshot**: a status-list credential, signature-verified per (b), whose *own signed* `validFrom` is at or after `t`, in which the bit is clear - the issuer then attested, at a time at or after the use, that the grant was unrevoked, and the consumer MAY pass, recording the snapshot and its signed time. A locally recorded retrieval time carries no evidential weight: it proves when a party fetched a list, not what the issuer had published. Only time attested inside the issuer's signature (or, in future, an independent timestamping authority) qualifies a snapshot. Settlement-grade consumers SHOULD retain periodic issuer-signed snapshots for exactly this purpose. **The snapshot inference is sound only because revocation is monotonic** - a `revocation`-purpose bit, once set, is never cleared, so clear-at-`s ≥ t` implies clear-at-`t`. This is why §4.2 forbids the reversible `suspension` purpose for entitlement grants; verifiers MUST check that `statusPurpose` is `revocation` on both the `credentialStatus` entry and the status-list credential, and MUST NOT apply the snapshot exception to any other purpose.
   (d) A `statusListIndex` outside the decoded bitstring is an **error** (credential and list disagree), not "not revoked". Fail closed.
5. **Match grantee:** session `agent_id` (or declared parent operator) equals `credentialSubject.grantee`.
6. **Bind content:** for per-asset grants, `E`'s content digest (`content_hash`, or `data.content_fingerprint` where the SPUR-Coalition/telemetry#10 and SPUR-Coalition/telemetry#21 fields are present) equals `credentialSubject.asset.sha256`; for blanket grants, `E.content_url`/`E.content_id` falls within `scope.content`. `E.type` MUST be covered per §4.5. Digest binding is REQUIRED where both digests are available; URL-pattern matching alone caps a per-asset grant at `origin_corroborated`.

All six steps → `independently_verifiable`.

**Provenance.** Core says of `provenance` (§6.4): *"The field describes delivery path, not evidence quality."* A `content_grounded` event whose `provenance` is `third_party_sourced` therefore verifies exactly as an `agent_fetched` one when its `license_ref` resolves to a valid grant naming the reporting agent as grantee; the report echoes the `provenance` value and it does not alter the class. This is not the chained-grant case, in which the agent holds no grant of its own and relies on an intermediary's: that case is outside this version.

**Reconciliation checks (reported, not graded).** Where the event carries `terms_ref` (core §5.2.4), it is compared with the credential's `credentialSubject.terms_ref`, and a mismatch is flagged in the report. Where the emitter declares coverage in its manifest (`telemetry.coverage`, §8.5) and the governing terms also state a coverage mode (§5.7.6), disagreement between the two is noted in the report - a check that runs only where the verifier can reach the terms, or the credential states the coverage the grant requires, since governing terms are opaque to core; otherwise the report echoes the manifest's declaration unreconciled.

**Fail-closed scope.** Manifest resolution failures are tolerated by core at the routing layer (§8.7) and affect routing here too, never grading. A credential that cannot be checked is not verified.

**Reporting granularity.** Core v1 sets no default for reporting granularity and leaves it to profiles and deployments (README, *Open questions in v1*; §5.7.6). This module sets one for its own evidence classes, because the top class depends on it.

The `independently_verifiable` class REQUIRES a per-event record. The proposition this module verifies, that a signed, unrevoked grant from an identified issuer covered the reported access, is a proposition about one event: one `license_ref`, one credential, one access, one point in time. A verifier cannot bind grant evidence to an event it did not receive.

Accordingly: an event delivered individually, carrying its own `license_ref`, MAY reach `independently_verifiable` if the checks in §5 pass, whatever coverage mode the manifest declares for its type. Where the manifest (§8.5) declares an event type as `aggregated`, no per-event record exists for that type, and its grant evidence MUST NOT be graded above `origin_corroborated`. The verification report MUST echo the manifest's declared coverage mode for the event's type.

This is a grading rule, not a reporting mandate, and it is not a completeness judgement. Whether every qualifying event was reported is outside this module's scope under the charter's boundary rule; the echoed coverage mode is the honest vocabulary for that question, and it belongs to the consumer and to the modules whose proposition it is. Deployments under the SPUR profile meet this module's per-event precondition automatically: the Content Telemetry README records that *"The SPUR profile requires event-level delivery and does not permit aggregation"* (README, *Open questions in v1*, at tag `v1.0`).

The fail-closed behaviour relied on at steps 3, 4(b) and 4(d) is restated as testable module conformance requirements in §8.

**Reporting the outcome.** The result of this recipe is reported as **"grant evidence verified"** at the established class (or the specific failing step). It is deliberately narrower than "entitled" or "licensed": the recipe establishes that signed grant evidence of a stated class exists for the reported use - it does not adjudicate entitlement, which may turn on governing-terms content, competing claims, or facts outside telemetry. Consumers MUST NOT present the outcome as an adjudication. A credential properly signed by an issuer other than the content owner verifies as a credential; whether that issuer had standing to grant is outside what this module reports.

**Binding of the outcome.** Where the consuming context adopts the canonical assertion binding of SPUR-Coalition/telemetry#21, the verification result is itself an assertion over `E` and MUST be bound to `E` via its RFC 8785 canonical digest, so an outcome cannot be re-attached to a different event.

## 6. Privacy and operational considerations

Verification is consumer-side and read-only; issuers learn nothing about individual events beyond ordinary web traffic - status lists are bitstring documents, not per-credential endpoints, which is why Bitstring Status List is the required mechanism. Credentials identify parties and grants, not end users; events retain their core `privacy_level` semantics (§9) and this profile adds no personal data. Caching: keys ≤ 24 h or per document `expires`; status lists ≤ 15 min in settlement contexts, ≤ 24 h otherwise. A cached issuer-signed status-list credential *is* a §5.4(c) snapshot - its evidential weight comes entirely from the issuer's signature over its `validFrom`, never from when it was fetched; retrieval timestamps are operational metadata for cache management only. Offline operation is first-class: pinned DID documents plus issuer-signed snapshots reach `independently_verifiable` with zero network access.

## 7. Limitations and deferred work

### 7.1 Backwards compatibility

Purely additive. All fields are optional at core level; existing consumers ignore `license_ref` resolution entirely and remain conformant. No conformance-level designation is required (per CONTRIBUTING, optional fields carry none).

### 7.2 Derived and bounded representations (deferred; core §12.1)

This version binds **whole-asset digests and URL/identifier scopes only**. Events reporting a *derived or bounded* representation - a transcript of audio, a region of an image, a segment of video - will not digest-match the asset a grant names, and under this version cap at `origin_corroborated`. Rather than invent derivation semantics here, this profile defers: core v1 withdrew the pre-release output-reuse event type and states that *"v1 defines no output-side reuse reporting"* (§12.1), so the question rests with the fingerprint scheme-property model of SPUR-Coalition/telemetry#11: when the fingerprint layer can express "representation X derives from asset Y" verifiably, step 6 will consume that relation as-is. The `derive` right in §4.5 is the reserved hook for whether such a use is covered.

### 7.3 Reference implementations (informative)

The recipe is implemented independently in Python and TypeScript with an executable cross-runtime parity check (identical `(valid, checks)` on every fixture), from published standards only - W3C VC 2.0, VC-JOSE-COSE, `did:web`, Bitstring Status List v1.0. **The conformance requirements are §8; nothing in this section is normative.** **Both implementations meet E1–E3, and the cross-runtime parity check covers all three** - asserting for each not only an identical verdict but that the failure names the rule, since two runtimes failing for different reasons would otherwise register as parity. *(Corrected 2026-08-14: an earlier revision of this section stated the TypeScript verifier did not yet enforce all three. It did. The gap was test coverage, not enforcement - the parity suite exercised only E1 - and the claim was inferred from that absence rather than checked against the code.)* The fixtures in `fixtures/` are implementation-neutral: two unrelated issuers, no shared infrastructure, regenerable via the included script, and structurally validated by `tests/test_entitlement_examples.py` with the repository's existing jsonschema tooling.

### 7.4 Fixture inventory

The eight events in `fixtures/` are valid v1 standalone event documents (`document_type: event`, `schema_version: 1.0`, session context, §6.4 grounding-profile `data` including `content_hash`, `chars_ingested`, `provenance` and `cached`); the test suite validates them against core's `telemetry-event.json` at tag `v1.0`, vendored at `schema/core/`, so core conformance is enforced rather than asserted. Credentials cover: valid, expired (§5.4(a)), revoked (§5.4(c), retroactive default), tampered (§5.3), second-issuer (issuer neutrality), third-party-sourced (a valid grant whose event reports `provenance: third_party_sourced`; verifies, provenance echoed), unknown-`kid` (§4.1, no fallback), grantee-mismatch (§5.5), revoked-after-use with an issuer-signed snapshot (§5.4(c): bit set in the current list, clear in a snapshot whose signed `validFrom` is at or after the event time - the suite asserts both bits, the signed-time ordering, and issuer identity), unauthenticated status list (§8.2: a list bearing a genuine signature by the other issuer while declaring the licensor), and out-of-range status index (§8.3: index 999999 against a 131072-bit list). Status lists are signed by the same issuer as their credentials (§5.4(b)). The manifest states the expected outcome per fixture - phrased as "grant evidence verified" at the stated class, never as an adjudication of entitlement.

## 8. Module conformance requirements

The three rules below were previously stated inside the verification recipe and described in §7.3 as behaviour of the reference implementation. They are module conformance requirements: an implementation that does not meet them is not a conforming entitlement verifier, whatever class it reports. The form follows core's conformance levels (specification §5.7) - a named subject, testable MUSTs, and fixtures that exercise each.

These are **verification requirements**, not classifications. This profile continues to consume the evidence classifications of SPUR-Coalition/telemetry#11 and SPUR-Coalition/telemetry#21 rather than defining parallel ones (§3), and the adoption clause there governs renaming. In the framing of the SPUR-Coalition/telemetry#18 consolidation, grant validity is an **enumerated verification basis**, not a competing tier ladder; §8.4 records how a failure maps onto the classes this profile consumes.

### 8.1 E1 - Strict key identification

A conforming entitlement verifier MUST:

- reject a credential whose JWS header `alg` is any value other than `EdDSA`;
- fail verification when the header `kid` names a key absent from the issuer's published key set;
- **NOT** fall back to another published key of that issuer, including where the issuer publishes exactly one key.

*Why it fails closed:* a verifier that falls back accepts a credential the issuer did not sign with the named key, which is indistinguishable on the wire from key substitution. Exercised by `credential-unknown-kid.jwt` (MUST fail) against `credential-valid.jwt` (MUST pass).

### 8.2 E2 - Status-list authentication before consultation

A conforming entitlement verifier MUST:

- verify the status-list credential's own signature against its issuer's published key **before** decoding its bitstring;
- require the status-list issuer to equal the entitlement credential's issuer, or a status issuer that issuer explicitly declares;
- treat an unauthenticated, unresolvable or signature-invalid status list as **unresolvable status** - never as "not revoked";
- confirm `statusPurpose` is `revocation` on **both** the `credentialStatus` entry and the status-list credential, and NOT apply the §5.4(c) snapshot exception to any other purpose.

*Why it fails closed:* an unauthenticated list is an assertion by whoever served it. Reading a fetch failure or a bad signature as absence-of-revocation converts a transport fault or an attack into a pass. The `statusPurpose` constraint is what makes the snapshot inference sound - see §5.4(c) on monotonicity. Exercised by `credential-unauthenticated-statuslist.jwt` with `statuslist-unauthenticated.jwt` (MUST fail) against `credential-valid.jwt` with `statuslist-licensor.jwt` (MUST pass) - the unauthenticated list carries a **genuine signature by the other issuer** while declaring the licensor, so a verifier that decodes before authenticating reads it as authoritative and passes. `statusPurpose` monotonicity is exercised by the snapshot pair `credential-revoked-late.jwt` / `statuslist-licensor-snapshot.jwt`.

### 8.3 E3 - Out-of-range status index fails closed

A conforming entitlement verifier MUST treat a `statusListIndex` falling outside the decoded bitstring as an **error** - the credential and the list disagree about the list's shape - and MUST NOT interpret it as "not revoked".

*Why it fails closed:* an index past the end of the bitstring means the two artifacts disagree. Reading that as unrevoked lets a truncated or stale list silently clear every credential whose index it no longer covers. Exercised by `credential-index-out-of-range.jwt` (index 999999 against a 131072-bit list, MUST error) against `credential-valid.jwt` (in range, MUST pass).

### 8.4 Effect on the consumed classifications

A verifier that fails **any** of E1–E3 MUST NOT report a class above `claim` for the event concerned, and MUST report the specific failing requirement rather than a bare class.

This is an effect on the classes, not a redefinition of them: §3 remains the statement of what each class means for `license_ref`, and those classes come from SPUR-Coalition/telemetry#11 and SPUR-Coalition/telemetry#21.

### 8.5 Testability

Each requirement has at least one negative fixture that MUST fail and a positive counterpart that MUST pass. `tests/test_entitlement_examples.py` asserts each pair is genuinely discriminating rather than merely present. A conformance claim against this module is therefore checkable against `fixtures/` by a third party, without access to any implementation of it.