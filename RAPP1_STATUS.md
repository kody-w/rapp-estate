# RAPP estate publication status — QUARANTINED

`kody-w/rapp-estate` is currently a deterministic, read-only status surface.
It is **not** a live estate manifest, network beacon, registry, protocol
authority, Router, or identity directory.

## Exact authority

| Field | Value |
|---|---|
| Repository | `kody-w/rapp-1` |
| Commit | `6723c7add2aed36bb68992fc71a56b0a4bd5ad81` |
| Path | `SPEC.md` |
| Status in document | Draft standard for ratification (rev-5) |
| Bytes | `41880` |
| SHA-256 | `6d06daba65d7c045716f3d6e95db8401ab58e727820e4114466d847f62cae49b` |

Immutable authority:
<https://raw.githubusercontent.com/kody-w/rapp-1/6723c7add2aed36bb68992fc71a56b0a4bd5ad81/SPEC.md>.
The same pin is machine-readable in
[`RAPP1_AUTHORITY.json`](RAPP1_AUTHORITY.json).

## Audit basis

- Baseline:
  `24c8fdc1e770c790b98724002d719d515d5e5465`
- Baseline surface: exactly five tracked files; no archives.
- At audit time, every baseline byte matched both local git and the live
  `main` raw publication. All five paths were also served by GitHub Pages.
- The baseline contained 17 provisional identity occurrences: one owner claim
  and 16 created entries. It contained no membership entries.
- Of those 17 lookups, 16 resolved publicly across 15 distinct repositories;
  one did not resolve as public. All resolved source records exposed
  syntactically current 64-hex candidates and migration assertions.
- No owner-signed re-anchor record, out-of-band estate-owner anchor, or
  authenticated, monotonic, freshness-checked section 13 registry was found.
  Syntax and GitHub authorship are not substitutes for that evidence.

## Findings and fixes

1. **Identity:** the live manifest emitted 32-hex provisional identifiers.
   They were removed, not converted or re-minted. Current candidates in other
   repositories were not copied because their required authorization evidence
   is absent.
2. **Labels and authority:** the estate, beacon, and metropolis labels were
   defined outside the pinned authority and were presented as canonical. They
   are no longer emitted as protocol schemas or specifications.
3. **Frames, wire, and registry:** the retired metropolis prose described a
   different frame shape and extra substrate behavior, while also denying the
   registry that RAPP/1 section 13 requires. The path now makes no live claim.
4. **Map semantics:** created inventory was presented as ownership and
   reachability. The public surface now exposes only aggregate historical
   counts and empty current claim sets.
5. **Moving links:** moving authority links, moving identity paths, an
   unresolved non-public target, and a missing well-known path were removed
   from trust-bearing output. The authority link is commit-pinned and
   hash-pinned.
6. **Rendering safety:** client-side fetch, HTML injection sinks, generated
   links, and inline event handlers were removed. `index.html` is static and
   carries no script or external asset.
7. **Public data:** personal display text and non-public repository locators
   were removed from current bytes. Historical bytes remain available through
   git history only.

## Current surfaces

| Path | Current role |
|---|---|
| `index.html` | Static human-readable quarantine status |
| `estate.json` | Fail-closed machine-readable publication status |
| `.well-known/rapp-network.json` | Fail-closed discovery status; not a beacon |
| `METROPOLIS.md` | Retirement notice; not a specification |
| `RAPP1_AUTHORITY.json` | Exact structural authority pin |
| `RAPP1_OWNER_ACTIONS.json` | Owner-only blocker with null inputs |
| `.nojekyll` | GitHub Pages literal-file control |

No current identity, membership, frame, wire, or registry claim is accepted.

## Role and subordination

The normative authority above is technical and commit-pinned. Under RAPP/1
section 11, any Router/Mirror is subordinate to `kody-w/RAPP`. This repository
does not route. If its static status is treated as a mirror, that mirror is
subordinate and must serve provenance-stamped, hash-matching bytes only.

## Remaining owner action

The owner-only decision and evidence fields remain `null` in
[`RAPP1_OWNER_ACTIONS.json`](RAPP1_OWNER_ACTIONS.json). Until they are supplied
and independently verified, consumers must refuse this repository as a live
estate, beacon, registry, or identity source.

This status is dated `2026-07-17`. A moving branch is not provenance:
consumers must resolve and pin the serving commit before citing these bytes.
