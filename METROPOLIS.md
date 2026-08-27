# `METROPOLIS.md` — candidate retirement notice (not yet live)

This candidate changes this path to a fail-closed retirement notice. It does
**not** prove that the live `main`/Pages path has changed and does not publish
a protocol, estate map, network beacon, registry, frame format, wire, or
conformance claim.

The former document is available only through git history at baseline commit
`24c8fdc1e770c790b98724002d719d515d5e5465`. Its exact SHA-256 was
`690f6109ad65fa313a3ad18d635b13dfbcb01ebbbb986568c171585a5c26e58d`.
Those historical bytes are not reproduced here.

## Exact authority

The normative RAPP/1 authority for this repository is:

- repository: `kody-w/rapp-1`
- commit: `d2cd5abed48d3f52b86bbb975ac3558286d1db41`
- path: `SPEC.md`
- document status: **Draft standard for ratification (rev-5)**
- bytes: `41952`
- SHA-256:
  `cea7847f98f9751734995f46fd4e1bde211c8eb9d03dbbb477934213865bb91a`
- immutable source:
  <https://raw.githubusercontent.com/kody-w/rapp-1/d2cd5abed48d3f52b86bbb975ac3558286d1db41/SPEC.md>

The machine-readable pin is
[`RAPP1_AUTHORITY.json`](RAPP1_AUTHORITY.json).

## Current disposition

- No identity is emitted from this path.
- No membership or estate-map edge is asserted.
- No frame is accepted or described as current.
- No endpoint is claimed as a conformant wire.
- No registry is mirrored or accepted.
- If this static publication is consumed as a mirror, it is subordinate to
  `kody-w/RAPP` under RAPP/1 section 11. It is not a Router and is not a
  protocol authority.

The baseline identity claims were provisional and had no verifiable
owner-signed re-anchor records in an authenticated, monotonic,
freshness-checked section 13 registry. This candidate therefore removes them
rather than converting, re-minting, or inferring them.

## Deployment boundary

The quarantine takes effect only when a reviewed commit containing these bytes
reaches `main` and byte-matching responses are verified from both raw GitHub
and GitHub Pages. Until then, the live path remains the baseline document.
Deployment verification is intentionally still open; follow the unchecked
checklist in [`RAPP1_STATUS.md`](RAPP1_STATUS.md).

See [`RAPP1_STATUS.md`](RAPP1_STATUS.md) for the audit disposition and
[`RAPP1_OWNER_ACTIONS.json`](RAPP1_OWNER_ACTIONS.json) for the owner-only
inputs that remain null.
