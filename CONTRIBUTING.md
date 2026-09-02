# Contributing to the SPUR evidence profile

This repository follows the same contribution model as the [Content Telemetry standard](https://github.com/SPUR-Coalition/telemetry/blob/main/CONTRIBUTING.md).

## What belongs here

The evidence profile and its modules: specification text, conformance fixtures, and pointers to reference verifiers. Core wire-format changes belong in the standard's repository through its proposal process, not here.

## Proposing changes

Proposals for new capabilities or modules begin with the people who need them, not with generated specification text or code. Open an issue or a short Markdown note describing what you are seeing, what you would like the profile to express, and why it matters. It can be informal. Please do not ask an AI agent to expand the idea into a formal proposal or implementation before a maintainer has confirmed alignment.

A maintainer marks a proposal **aligned** when there is agreement on the direction; that is the gate for substantial implementation work. Alignment is not final acceptance of every detail, and every proposition a module supports must fit the charter's boundary rule: access evidence never becomes proof of grounding, and cryptographic validity never becomes factual truth, completeness, or entitlement.

## Implementation pull requests

Once aligned, a module PR should:

1. Link the aligned proposal or the standard-repo thread it descends from.
2. State the bounded proposition the evidence supports, in the module text itself.
3. Include conformance fixtures with negative vectors, reproducible from a clean checkout.
4. Pin the core standard version the module targets.

## Bugs and security

Concrete defects in fixtures or module text go straight to the issue tracker; no proposal needed. Report security vulnerabilities privately per [SECURITY.md](./SECURITY.md).

## Conventions

British English, sentence-case headings, snake_case fields, RFC 2119 keywords as defined in the standard's section 1.5.
