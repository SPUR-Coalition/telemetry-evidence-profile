# Fingerprint schemes

**Status:** Draft for discussion. Specification text plus one fixture set; workflow level to follow the common frame.
**Targets:** Content Telemetry 1.0.
**Origin:** Standard issues #5, #11, #16 and #17, and PR #21. The chair routed this work here on 2 September 2026.
**Editors:** To be confirmed. Proposed: @erik-sv. Offered: @jchomat (CMS fixtures), @RedHorseMane (match schemes, issue #1).

## 1. The problem

An agent grounds a 600-character chunk of an article and reports `detected: false` for the publisher's scheme. That could mean the article was never marked, the scheme cannot check a chunk, a pipeline stripped the mark, or the detector is wrong. Nobody reading the event can tell which.

Core leaves this open on purpose. `content_fingerprint.detected` is the emitter's claim (section 6.4), and the evidence slot in section 6.8 carries references without interpreting them. This module says what a scheme can support, who checked a signal, and what a result means.

## 2. What a check record shows

A check record shows one thing: a declared scheme's signal was checked in an identified representation, by an identified checker, with a stated result.

On its own it does not show that the content entered a model's context, that an output used it, who owns it, whether it was licensed, whether a missing signal was removed, or that every check was reported. Those need other evidence.

The module specifies how a check is reported. It does not prescribe how a consumer joins records to other data, counts them, scores them or settles on them.

## 3. Two kinds of scheme

- **Identity schemes** carry, or bind to the content, a signed statement of who marked it and which work it is. A C2PA manifest embedded in a media file is one example.
- **Match schemes** compare a fingerprint of the content with a registry. A match says the text matches entry E under decision policy P. The registrant's identity comes from the registry.

The two support different claims, and neither ranks above the other. A match result MUST NOT be presented as an identity result, or the reverse. They combine well: a match can find the source of text whose identity signal was lost.

## 4. Scheme declarations

A scheme operator publishes a declaration, fixed by its SHA-256 digest, so readers know what the scheme can and cannot do.

| Field | Meaning |
|-------|---------|
| `scheme`, `version` | Identifier used in `content_fingerprint.scheme`, and the version covered |
| `class` | `identity` or `match` |
| `content_borne` | Whether the signal travels in the content or in detachable metadata |
| `resolution` | `document` if a check needs the whole work; `segment` if the scheme declares smaller units that can each be checked on their own, with any preconditions stated |
| `time_anchors_supported` | Any of `none`, `signer_asserted`, `trusted_timestamp`, `transparency_log`, `registry_time` |
| `trust_anchors_supported` | Identity schemes: how a checker validates the signer, such as a public trust list |
| `check_methods` | `reproducible`, `attested`, or both |
| `survivability` | Reference and digest of a transform matrix (section 8) |
| `known_limits` | Plain limits, including paraphrase and summarisation, marked tested or untested |

All fields are required except `trust_anchors_supported` for match schemes. The three flags from issue #11 map as follows: `identity_bearing` becomes `class`, `verifiable` becomes `check_methods` and `trust_anchors_supported`, and `content_borne` stays.

A declaration is the operator's claim. Neither a declaration nor a place on a list raises the standing of an event or a check; consumer policy decides. The module keeps an informational list of schemes, not a registry.

## 5. Check records

A check record covers one representation. A grounding event that covers three chunks needs three records.

| Field | Meaning |
|-------|---------|
| `scheme`, `declaration` | Scheme identifier, and declaration reference and digest |
| `subject` | `role` (for example `grounded_content`) and `digest` of the exact bytes inspected |
| `event` | Optional `session_id` and `event_id` the check relates to |
| `result` | `found`, `invalid`, `not_found` or `indeterminate` |
| `invalid_reason` | With `invalid`: `binding_mismatch`, `signature_failure` or `signer_not_validated` |
| `signal` | With `found`. Identity: validated signer, trust anchor used, work identifier, and the time anchor actually present. Match: registry, entry, and decision policy identifier and digest |
| `method` | `reproducible` or `attested` |

**Results**

- `found`, identity schemes: the signal's binding to the content holds under the scheme's declared rules, its signature verifies, and its signer checks out against the named trust anchor. Finding a signal without validating it is not `found`.
- `found`, match schemes: the text meets the named decision policy for the named entry.
- `invalid`: a signal is present but did not validate. A binding mismatch alone does not distinguish deliberate alteration from ordinary transformation such as aggregation.
- `not_found`: no signal was located.
- `indeterminate`: the check could not be completed, or does not apply.

**Chunks.** If the checker knows it holds part of a document and the scheme's resolution is `document`, the result MUST be `indeterminate`. Agents often ground chunks (core section 6.4 hashes the chunk), so without this rule document-level schemes would report false negatives.

**Linking to events.** The `event` field is the checker's statement of which event a record relates to. Where an event covers one representation, the record counts for that event only if its subject digest equals the event's `content_hash`. A record about one chunk of a larger representation is evidence about that chunk only.

**Match records** need not disclose thresholds or scores. The decision policy identifier and digest show which policy was applied.

**Carriage.** A record travels as a detached reference in the core evidence slot (section 6.8): `data.evidence[]` with `scheme` set to the check-record identifier, `ref` pointing to the record, and `digest` binding it. This draft proposes `https://github.com/SPUR-Coalition/telemetry-evidence-profile/modules/fingerprint-schemes#check-record-v0` as the identifier; it need not resolve. A checker MAY also send records straight to the content owner. Core needs no change.

## 6. The envelope

Every record needs a checker identity, a disclosure of the checker's relationships, a signature and a trusted timestamp. The entitlement and seeded-observation modules need the same things, so this draft proposes that the common frame define them once. Until it does, a record carries:

| Field | Meaning |
|-------|---------|
| `checker` | Checker identifier, the operator's legal name, and signing key identifier |
| `relationships` | Any ownership, contract or payment link to the emitter, the content owner or the scheme operator. An empty list states that there is none |
| `checked_at` | Time of the check |
| signature | Over the whole record |
| trusted timestamp | Over the signature |

The signature shows the record was not altered. The timestamp shows it existed by that time. `checked_at` is the checker's word. None of them shows that every record was delivered: an emitter attaches the records it chooses. Catching withheld records needs delivery to the content owner or an append-only log.

## 7. Who checks

- **Self-checks.** A record from the emitter, or from a checker that shares its operator, group or key custody, counts as an emitter claim. The same applies to checkers on the content owner's side.
- **Reproducible checks.** Anyone with the bytes can repeat the check. A consumer that holds the bytes SHOULD repeat it.
- **Other checks.** The consumer usually lacks the bytes: the agent saw the chunk and the publisher did not. The consumer then relies on a checker that did see it. That checker discloses its relationships in the signed record, and consumer policy decides whether to accept it. An event cannot make that disclosure on the checker's behalf.

## 8. Survivability and unpublished methods

A survivability matrix has one row per transform, naming the transform, scheme version, fixtures, conditions and result. Untested rows say `not_tested`. A pass MUST NOT be generalised to another transform, corpus or version, and `content_borne: true` is not a survivability claim. Vectors MAY be synthetic and need not show where or how a signal is placed.

The first matrix, `fixtures/survivability-c2pa-text.json`, comes from PR #21. It tests whether the C2PA text wrapper can be recovered after each transform, and nothing more: its manifest is unsigned, and it verifies no signature or binding. `check_survivability.py` reruns its ten tested rows and reports the seven untested ones.

A scheme MAY keep its methods private. The module requires no disclosure of carriers, detector features, scores, thresholds, calibration data or keys. An attested check MUST still produce a record that anyone can verify for signature, subject, time and checker without the detector. Consumers will weigh attested and reproducible checks differently.

## 9. Fixtures to come

- @jchomat's WordPress 7.0.1 and SPIP 4.3.9 fixtures (erik-sv/telemetry#1), with his agreement and credit.
- Negative vectors for: a subject digest that does not match the event; a binding mismatch reported as `found`; a checker whose key appears in the emitter's manifest while its `relationships` list is empty; a missing timestamp; a match presented as identity; `not_found` on a known chunk under `document` resolution; one record covering two chunks.

Two independent checkers must agree on these vectors before the module is marked stable.

## 10. Open questions for October

1. Should records use COSE_Sign1, to match C2PA, or JWS, to match web tooling?
2. Do the envelope and relationship disclosure belong in the common frame, this module, or governing terms?
3. How should withheld records be caught: delivery to the owner, an append-only log, or both?
