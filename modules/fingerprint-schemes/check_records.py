#!/usr/bin/env python3
"""Check the fingerprint-schemes check-record vectors.

Applies the structural and consistency rules of module sections 5 to 7 to
each vector in fixtures/check-records.json and compares the error codes it
finds with the codes the vector expects. Signature and trusted-timestamp
formats are open question 1, so this checker tests that those members are
present, not that they verify.
"""

import hashlib
import json
import sys
from pathlib import Path

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "check-records.json"
RESULTS = {"found", "invalid", "not_found", "indeterminate"}
INVALID_REASONS = {"binding_mismatch", "signature_failure", "signer_not_validated"}
METHODS = {"reproducible", "attested"}
PARTIES = {"emitter", "content_owner", "scheme_operator"}
LINKS = {"ownership", "contract", "payment", "key_custody"}
REQUIRED = (
    "scheme",
    "declaration",
    "subject",
    "result",
    "method",
    "checker",
    "relationships",
    "checked_at",
    "signature",
    "trusted_timestamp",
)
IDENTITY_SIGNAL = ("signer", "trust_anchor", "work_id", "time_anchor")
MATCH_SIGNAL = ("registry", "entry", "policy")
# A match result names a registry entry; an identity result names a signer.
IDENTITY_MARKERS = ("signer", "trust_anchor")
MATCH_MARKERS = ("registry", "entry")


def declaration_digest(declaration):
    """SHA-256 over the declaration's canonical JSON (RFC 8785 for this data)."""
    canonical = json.dumps(
        declaration, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def check_record(record, declarations, events, emitter_manifest):
    """Return the sorted error codes for one check record."""
    errors = {f"missing_{name}" for name in REQUIRED if name not in record}

    declaration = None
    reference = record.get("declaration") or {}
    for candidate in declarations:
        if declaration_digest(candidate) == reference.get("digest"):
            declaration = candidate
    if "declaration" in record and declaration is None:
        errors.add("unknown_declaration")
    if declaration and record.get("scheme") != declaration["scheme"]:
        errors.add("scheme_mismatch")

    subject = record.get("subject")
    if "subject" in record and not (
        isinstance(subject, dict) and isinstance(subject.get("digest"), str)
    ):
        errors.add("multiple_subjects")
        subject = None

    result = record.get("result")
    if "result" in record and result not in RESULTS:
        errors.add("unknown_result")
    if "method" in record and record["method"] not in METHODS:
        errors.add("unknown_method")
    if result == "invalid" and record.get("invalid_reason") not in INVALID_REASONS:
        errors.add("missing_invalid_reason")
    if result != "invalid" and "invalid_reason" in record:
        errors.add("invalid_reason_outside_invalid")
    if result != "found" and "signal" in record:
        errors.add("signal_outside_found")

    if declaration:
        errors |= _signal_errors(record, declaration["class"])
        if (
            declaration["resolution"] == "document"
            and subject
            and "part_of" in subject
            and result != "indeterminate"
        ):
            errors.add("document_scheme_on_part")

    link = record.get("event")
    if link and subject:
        event = events.get(link.get("event_id"))
        if event is None:
            errors.add("unknown_event")
        elif event["data"].get("content_hash") != subject["digest"]:
            errors.add("subject_digest_mismatch")

    errors |= _relationship_errors(record, emitter_manifest)
    return sorted(errors)


def _signal_errors(record, scheme_class):
    if record.get("result") != "found":
        return set()
    signal = record.get("signal") or {}
    errors = set()
    if scheme_class == "match" and any(name in signal for name in IDENTITY_MARKERS):
        errors.add("match_presented_as_identity")
    if scheme_class == "identity" and any(name in signal for name in MATCH_MARKERS):
        errors.add("identity_presented_as_match")
    expected = IDENTITY_SIGNAL if scheme_class == "identity" else MATCH_SIGNAL
    if not all(signal.get(name) for name in expected):
        errors.add("found_without_validated_signal")
    return errors


def _relationship_errors(record, emitter_manifest):
    relationships = record.get("relationships")
    if relationships is None:
        return set()
    errors = set()
    for entry in relationships:
        if entry.get("party") not in PARTIES or entry.get("link") not in LINKS:
            errors.add("unknown_relationship")
    emitter_keys = {key["publicKey"] for key in emitter_manifest.get("keys", [])}
    checker_key = (record.get("checker") or {}).get("public_key")
    discloses_emitter = any(entry.get("party") == "emitter" for entry in relationships)
    if checker_key in emitter_keys and not discloses_emitter:
        errors.add("undisclosed_emitter_relationship")
    return errors


def run_checks():
    """Return (positive, negative, failures) counts for all vectors."""
    try:
        with FIXTURE_PATH.open(encoding="utf-8") as source:
            fixture = json.load(source)
    except (OSError, json.JSONDecodeError) as error:
        return 0, 0, [f"fixture could not be loaded: {error}"]

    positive = negative = 0
    failures = []
    for vector in fixture["vectors"]:
        expected = sorted(vector["expected_errors"])
        actual = check_record(
            vector["record"],
            fixture["declarations"],
            fixture["events"],
            fixture["emitter_manifest"],
        )
        if expected:
            negative += 1
        else:
            positive += 1
        if actual == expected:
            print(f"  PASS  {vector['id']}: {', '.join(actual) or 'valid'}")
        else:
            failures.append(f"{vector['id']}: expected {expected}, observed {actual}")
            print(f"  FAIL  {vector['id']}")
    return positive, negative, failures


def main():
    positive, negative, failures = run_checks()
    for failure in failures:
        print(f"ERROR: {failure}")
    status = "PASS" if not failures else "FAIL"
    print(
        f"Check records: {status} ({positive} valid vectors, "
        f"{negative} negative vectors, {len(failures)} failures)"
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
