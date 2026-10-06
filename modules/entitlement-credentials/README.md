# Entitlement credentials

**Bounded proposition:** a signed, unrevoked grant from an identified issuer covered the reported access.

**Workflow level:** not stated - the V0 to V3 definitions are not yet published - see #6

**Contents:** [`entitlement-evidence.md`](entitlement-evidence.md) (specification) · [`schema/`](schema/) (the credential schema; core's event and session schemas copied verbatim at tag `v1.0` under `schema/core/`) · [`fixtures/`](fixtures/) - eleven credential cases with stated expected outcomes, of which three verify, one verifies only with the issuer-signed snapshot, and seven fail, each failing case paired against a near-identical passing one; with eight events, the status lists and issuer documents · [`tests/`](tests/) - thirteen tests, run offline against the standard's v1 schemas, reproducible from a clean checkout with keys derived from committed seeds

The conditional case is central to how the module works, not an exception. If a grant is revoked after the reported use, it fails verification against the current status list, but verifies against a snapshot the issuer signed at or after the time of use in which the grant was still unrevoked.

**Origin:** re-filed from [telemetry#34](https://github.com/SPUR-Coalition/telemetry/pull/34) per the 12 August disposition and CHARTER.md. Core version targeted: Content Telemetry v1.0 (2026-09-02), tag `v1.0`.

**Reference implementation:** [ReadBridge/content-license-verify](https://github.com/ReadBridge/content-license-verify) - verifier (Python/TS) and the signed-outcome (DSSE) bridge example.

The module reports "grant evidence verified" or "grant evidence not verified" with an evidence class - evidence of a grant, never an adjudication of entitlement, per the charter's boundary rule and out-of-scope list.
