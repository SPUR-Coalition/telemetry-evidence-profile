# Evidence working group charter

**Status:** Adopted 2 September 2026. The working group was authorised by the SPUR Steering Board during the v1 consultation (standard issue #18).

## Purpose

Produce the SPUR evidence profile: one optional profile, layered on the Content Telemetry standard, defining how telemetry claims are corroborated - by whom, with what evidence, supporting which bounded propositions.

## Scope

In scope:

- The four modules consolidated from the v1 consultation: fingerprint schemes, VPTS seeded observations, recomputable attribution, and entitlement credentials
- The profile's common frame: how a module states the proposition its evidence supports, how a consumer's trust policy accepts or rejects a scheme, and the V0-V3 workflow-maturity levels
- Conformance fixtures and reference verifiers for each module, reproducible from a clean checkout
- Requester authentication for click-token resolution and token-lifetime rules, deferred here by section 7.4.6 of the standard
- Grant validity as an enumerated verification basis within the entitlement module

Out of scope:

- Changes to the core wire format. Where a module needs a core hook that does not exist, the group files a proposal against the standard and waits for alignment; it does not fork core semantics.
- Redefining core event semantics or occurrence boundaries
- Entitlement, ownership, price, or compensation as legal or commercial conclusions
- Accreditation and the conformance mark (SPUR Content Telemetry Profile)

## Boundary rule

Every module is bound by the rule recorded in the consultation: access evidence never becomes proof of grounding, and cryptographic validity never becomes factual truth, completeness, or entitlement. A module that cannot state its proposition inside this rule does not enter the profile.

## Deliverables and bar

The reference bar is open-repository specification text with reproducible fixtures. For the seeded-observations module specifically, a reference implementation needs reproducible marker statistics, an elicited-versus-organic distinction usable for settlement, and no dependency on a sole-operator ledger.

Deliverables: the profile document, per-module conformance fixtures with negative vectors, and at least two independently implemented verifiers demonstrating interoperability before any module is marked stable.

## Membership and roles

- **Chair:** Alex Springer (alex@spurcoalition.org)
- **Co-authors:** @erik-sv, @pwright-bf, @abnerguzman, @ReadBridge (accepted on standard issue #18)
- **Contributors:** open to anyone under CONTRIBUTING.md; @romainbenabdelkader (detached provenance anchor), @RedHorseMane (fingerprint schemes), and @jchomat (C2PA survivability fixtures) have offered specific work

Editors per module are recorded in the README table as modules take shape.

## Process and decisions

Work happens in this repository. Proposals follow the standard's human-written-proposal policy (CONTRIBUTING.md); a maintainer records every disposition on the tracker; the SPUR Steering Board approves profile releases. The tracker and pull-request history are the public decision record.

## Duration and cadence

The group is chartered from 2 September 2026. The first working session takes place in early October 2026 and is announced on this tracker with joining details; sessions are announced the same way thereafter. The group reviews its continuation at each profile release, and at least every six months.

## Relationship to the standard

The profile pins the core version it targets (currently 1.0) and references it; the standard does not reference the profile. Material the group needs in core arrives through the standard's own proposal process.
