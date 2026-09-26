# RAPP estate publication status

This page says what `kody-w/rapp-estate` publishes, what is drafted here, and
what waits for the estate owner. The owner's steps are also recorded,
machine-readably, in [`RAPP1_OWNER_ACTIONS.json`](RAPP1_OWNER_ACTIONS.json).

## Where things stand on 2026-09-26

- **The publication is drafted in steps.** The estate kit writes the
  distributed Hive activation on the branch
  `experimental/rapp1-distributed-hive`, one commit per step, following RAPP
  proposal 0020 (a draft that the owner has not accepted; its Migration
  step 3 gives the estate kit `estate.json`, the beacon and the seed's pins).
  This commit adds the release manifests; the LTS pins follow in the next
  commits of the branch. The branch is experimental: it has no pull request
  and nothing on it is merged.
- **Nothing is signed.** No file in this repository carries a signature, and
  the kody-w estate registry (`kody-w/rapp-map`, `ecosystem-spec.json`, signed
  registry_seq 2 of 2026-09-02) has no entry for any file here.
- **Network acceptance awaits the owner's signed registry**, the estate kit's
  registry_seq 3. Until the estate owner signs and publishes it, a consumer may
  read and hash-check these files but accepts none of them.
- **registry_seq 3 covers the beacon.** Both release manifests pin this
  repository at the beacon commit
  `674776841610f9b4b1c23dafacc4314897a22e4c` (the beacon and
  `estate.json`, by SHA-256 and length). Once the estate owner signs the
  `release-pin` entries that name them, a verified entry of the estate's
  signed registry covers the beacon: the condition RAPP proposal 0020 D2 sets
  before the network seed accepts the operator.
- **What `main` served before this draft.** `main` was the 2026-07-17
  quarantine status at commit `acc17dca283619f288274f237c8c61f437d014f3`. At
  21:49:30 UTC on 2026-09-25 every tracked path fetched from raw GitHub at
  `main` and from GitHub Pages matched that commit byte for byte (Pages last
  modified 2026-08-27), so the quarantine was live. The historical record below
  still says "not yet live" because it was written before that deployment, and
  its checklist was never recorded as complete.

## The estate inventory (`estate.json`)

[`estate.json`](estate.json) is now a real `rapp-estate/1.1` inventory (RAPP
`pages/docs/ESTATE_SPEC.md` §3.1), drafted and unsigned.

- `owner` is the operator: `github: "kody-w"` and the rappid
  `rappid:@kody-w/estate-owner:b5814e45e9988df835dfd58d152a6fb05b6510a087a35c24374a1c4ab833c122`,
  the keyed estate-owner trust anchor that the `kody-w/rapp-1` README publishes
  out of band ("Trust anchor", RAPP/1 §13.1).
- `created` has one entry per public station whose `rappid.json`, at its
  portfolio evidence commit, is a valid RAPP/1 §6.1 identity: 30 stations of
  the portfolio in `kody-w/rapp-hive-public` at commit `eafa6de`. Each entry is
  exactly `{rappid, added_at, via}` (Article XLVI.3), sorted by `rappid`, with
  `via: "scan"` and `added_at` set to the portfolio crawl's finish time,
  2026-09-25T18:16:15Z (`crawl.finished_utc` of
  `portfolio/versions/2026-09-25-0/pulse.json`). No derived field is stored
  (XLVI.5). `member` is empty.
- These 30 rappids are the stations' own valid `rappid.json` identities.
  A release manifest binds a rappid as a door of record only when the
  station's card (`.rapp/member.md`) states the same rappid at the pinned
  commit, and no station has a card at its pinned commit yet. This draft
  accepts none of them.
- `hives` is the one optional field that RAPP proposal 0020 proposes; it is
  not part of the estate schema until the owner accepts that proposal. Its
  entry pins the Hive root: Hive `af02504304365b6d8b068553156b5e6d`
  (`rapp-hive`), public copy `kody-w/rapp-hive-public` at commit
  `eafa6de7e04a3d536c21976c1d85e845a499cd7b`, whose
  [`PUBLISHED.md`](https://github.com/kody-w/rapp-hive-public/blob/eafa6de7e04a3d536c21976c1d85e845a499cd7b/PUBLISHED.md)
  hashes to `3deeab22ba4995558c1647c50e6545e9fb2f2bcd2df5f6b64600868b63083291`
  under the Hive hash rule (SHA-256 of the UTF-8 text with LF line ends, in
  NFC; here the same as the raw SHA-256) and whose frontmatter `hive:` is that
  id. It has exactly the five members proposal 0020 names (`hive`, `name`,
  `root`, `commit`, `published_sha256`).
- The Hive root's portfolio lists every public station (317 at `eafa6de`), and
  it publishes a station pointer for each (`members/<station>.md`), 4 of them
  with an LTS commit. When the network lead adds the LTS commits of
  `lts-pins.json` to the rest (proposal 0020, Migration step 5), the estate kit
  re-pins `hives[]` and every pin above it.

## The beacon (`.well-known/rapp-network.json`)

[`.well-known/rapp-network.json`](.well-known/rapp-network.json) is now a real
`rapp-network-beacon/1.1` beacon (Articles XLVII and XLVIII), drafted and
unsigned. It carries exactly the fields that RAPP's
`pages/docs/PUBLIC_PRIVATE_BOUNDARY.md` §4.5 allows, and no other.

- `operator_rappid` is the estate-owner trust anchor, the same rappid as
  `estate.json` `owner.rappid`, and `github` is `kody-w`.
- `estate_url` names `estate.json` on raw GitHub at the commit that wrote
  this inventory (`bb2b9ce`). A sniffer lets the beacon's `estate_url` win over the
  seed's, so the seed's moving `estate_url` changes nothing.
- `grail_url` is this repository's GitHub Pages front door. Front doors stay
  editable, so it is not pinned.
- `protocol`: `spec_version` is `rapp/1` and `spec_url` is the RAPP/1 rev-5
  authority that `RAPP1_AUTHORITY.json` pins. (The historical beacon named
  `rapp-protocol/1.0` and RAPP's `specs/SPEC.md`, which RAPP now marks
  superseded.) `estate_schema` is `rapp-estate/1.1`, and `implements` lists
  `article-xlvi`, `article-xlvii` and `article-xlviii`. The historical beacon
  also claimed `article-xlvi.6`; this draft does not, because XLVI.6 rebuilds
  an estate from each door's `parent_rappid`, and no door here names the
  operator as its parent.
- `discovery`: `indexable: true`, because the operator wants to be found
  (Article XLVII.3); `consent: "public-discovery-ok"`; no federation hints.
- The Article XLVIII fields: `private_estate_pointer` is
  `https://github.com/kody-w/rapp-estate-private`, the estate's private
  repository. `private_estate_commitment`
  (`c87e38be4ef5bf4fae3dc416aec8640d06fc02adfd3e855bb19d4ad280fda432`) and
  `private_door_count` (`0`) are the values this estate last published in its
  public beacon, in commits `445ff41` to `4287741` on 2026-05-10. They are
  carried forward, not recomputed: nothing here reads the private estate. The
  owner re-verifies the commitment with RAPP's own
  `tools/private_estate_init.py --verify-commitment` (see below).
- The beacon reaches the Hive root only through `estate.json` `hives[]`
  (proposal 0020, D3), and it adds no field: there is no hash of
  `estate.json` in it, because the commit in `estate_url` fixes those bytes.
  The RAPP network seed is where the beacon gets pinned: its operator entry
  has `reference_state.commit_pin` and `reference_state.sha256` for that.
  Both are `null` on RAPP `main` today; the draft branch
  `experimental/rapp1-network-seed-acceptance` in `kody-w/RAPP` fills them in
  with this beacon's commit and SHA-256.

## Release manifests (candidate)

| File | Release | Channel | Components | Bytes | SHA-256 of the file |
|---|---|---|---:|---:|---|
| [`releases/e3cc75de2ebdb36aa882edf2c2c1a50cfd2a8d93b916065e6c1046316bf60a87.json`](releases/e3cc75de2ebdb36aa882edf2c2c1a50cfd2a8d93b916065e6c1046316bf60a87.json) | `rapp-1-lts-2026.09` | `rapp1-lts`, kernel `brainstem-v0.6.9` | 249 | 79562 | `ab3301b0e4d39fed19fdf4dddaba1a64e119ef9363f342044417d06f61407ad4` |
| [`releases/291dbe7955780a79a857869d96bd0c3405e5c7382c87e13fd40fcda8728c0a1c.json`](releases/291dbe7955780a79a857869d96bd0c3405e5c7382c87e13fd40fcda8728c0a1c.json) | `brainstem-v0.6.16` | `newest`, kernel `brainstem-v0.6.16` | 310 | 94060 | `3473531d2bfc6efd849697564ab3b51ba32228c86b13ca9ca7833846ba42ae6a` |

- Each file is a `rapp/1-release-manifest` and is exactly `canonical(manifest)`:
  no whitespace and no line terminator. `.gitattributes` turns end-of-line
  conversion off for `releases/*.json`, so git keeps and serves those bytes.
- Each file's name is its `manifest_hash`, `H("rapp/1:particle", manifest)`,
  as RAPP/1 rev-17 §13.5 defines it (`kody-w/rapp-1`, branch
  `experimental/rapp1-core-rev17`, commit
  `65a35c145a9a74c047f32661cde307158a913f77`, `rapp.H`).
- Both pin this repository as the component `rapp-estate` (kind `estate`) at
  the beacon commit `6747768`: `.well-known/rapp-network.json` and
  `estate.json`, by SHA-256 and length. A manifest never pins the commit that
  carries it, so the manifests come in the commit after the beacon.
- They are **candidate**. RAPP/1 rev-17 is a draft and not in force, and a
  manifest pins its release only after the estate owner signs a `release-pin`
  entry that names its `manifest_hash` in the kody-w estate registry, together
  with the `grail-kernel` entry of its release scope (each manifest has a
  kernel component). The estate kit prepares those entries for
  registry_seq 3.
- To check them, run `python3 tests/test_publication.py`: it recomputes the
  canonical form and the hash with the Python standard library. rapp-1's own
  `rapp_registry.validate_release_manifest` (rev-17 draft, `65a35c1`) also
  accepts both.

## How the draft was checked

- `python3 tests/test_publication.py` passes at every commit of the draft. It
  re-implements RAPP/1 `canonical` and `H` with the Python standard library
  (as `rapp.canonical` and `rapp.H` define them in `kody-w/rapp-1` at
  `65a35c1`) and checks the estate entry shape and the `hives[]` values, the exact beacon field set and its pinned `estate_url`, and the release files and their pin of this repository at the beacon commit, every commit-pinned URL,
  and that the historical record and evidence are unchanged. With `--online`
  it also refetches the pinned URLs and compares the bytes.
- rapp-1's `rapp_registry.validate_release_manifest` accepts both manifests,
  and `rapp.H` gives each file's name.
- RAPP's `tools/sniff_network.py` (at `8afc973`) keeps this beacon: its schema
  is one of the two beacon schemas it accepts, `door_from_rappid` accepts
  `operator_rappid`, and `indexable` is true. It ran without touching the
  network, twice: on a captured observation (`--source-data`, 30 door claims),
  and as its breadth-first walk from a seed file on disk (the `file` substrate
  of Article XLVII.5) whose operator entry points at a copy of this beacon
  (`--online` with a reviewed source binding that allows only that folder).
  The walk observed the operator and took the beacon's `estate_url` as the
  estate to read. Every record said `accepted: false`.

## What the owner does

Only the estate owner can do these. No tool in this repository signs, mints or
accepts anything.

1. Re-verify `private_estate_commitment`. Run RAPP's
   `tools/private_estate_init.py --handle kody-w --verify-commitment --online`
   with a reviewed source binding, and compare its `computed_commitment` with
   this beacon's value. (Its `matches` field compares with the beacon on
   `main`, which carries no commitment until this branch is merged, so before
   the merge it reports drift whatever the private state is.) If they differ,
   or if the private estate's `meta.json` gives another `private_door_count`,
   the estate kit replaces the values, with their test, in new commits: a new
   beacon, new manifests that pin it, and a new pin in the RAPP seed.
2. Sign and publish registry_seq 3, which the estate kit prepares, with the
   entries these manifests need under RAPP/1 rev-17 §13.5: a `release-pin`
   entry for each manifest in `releases/`, and a `grail-kernel` entry for each
   release scope, because both manifests carry a kernel component. The
   manifests pin this repository at the beacon commit, so once registry_seq 3
   verifies, a signed entry covers the beacon (proposal 0020 D2).
3. Accept RAPP proposal 0020 with its decisions D2 and D3, or refuse it. It is
   a draft on RAPP's `experimental/proposal-0020-distributed-hive` branch. This
   draft follows the recommended D2 and D3 and adds no beacon field (not the
   `estate_sha256` that D3 lists as an alternative). Steps 4 to 6 hold only if
   the owner accepts the proposal with those decisions. If the owner refuses it
   or chooses otherwise, this branch is not merged as drafted: the estate kit
   redrafts `estate.json`, the beacon and the manifests in new commits (without
   `hives[]`, or in the chosen shape), re-pins them, and updates the tests.
4. Have the estate kit add one status commit to this branch that records
   registry_seq 3 and the decision on proposal 0020 (status words, owner
   inputs, tests). It changes none of the pinned files.
5. Merge this branch into `main` without rewriting it (fast-forward or a merge
   commit, never a squash or a rebase), so that every commit-pinned URL stays
   reachable from `main`. Keep the branch until then.
6. In `kody-w/RAPP`, the draft branch
   `experimental/rapp1-network-seed-acceptance` pins this beacon in the
   network seed (its first commit) and marks the operator accepted (its second
   commit, owner-gated). Merge both after step 5: by then registry_seq 3 is
   published and covers the beacon, as D2 asks. (If RAPP `main` has moved, the
   estate kit first rebases the branch and refreshes
   `tests/fixtures/rapp1-doc-scope.json`.) The estate kit then prepares a last
   status commit, for the owner to merge, that closes this blocker.

The 2026-07-17 blocker `rapp1-identity-authorization-and-registry` in the
ledger is kept as written. Since then the estate-owner rappid has been
published out of band and the kody-w registry has reached signed
registry_seq 2. Whether the steps above close that blocker is the owner's
decision.

## Files

| Path | Role |
|---|---|
| `index.html` | Static human-readable status; no script |
| `RAPP1_STATUS.md` | This status, then the historical record |
| `RAPP1_OWNER_ACTIONS.json` | Owner-only steps, with null owner inputs |
| `RAPP1_AUTHORITY.json` | Exact RAPP/1 authority pin (rev-5) |
| `RAPP1_EVIDENCE.json` | Non-authoritative 2026-07-17 lookup observations |
| `releases/<manifest_hash>.json` | Candidate release manifests (rev-17 draft), exactly canonical |
| `estate.json` | `rapp-estate/1.1` inventory: 30 doors and one Hive root (drafted, unsigned) |
| `.well-known/rapp-network.json` | `rapp-network-beacon/1.1` beacon (drafted, unsigned) |
| `METROPOLIS.md` | Retirement notice for the former metropolis document |
| `tests/test_publication.py` | Offline checks; `--online` refetches the pinned evidence |
| `.gitattributes` | Keeps `releases/*.json` byte-exact |
| `.nojekyll` | GitHub Pages serves files literally |

## Historical record (kept as written)

Everything below is the 2026-07-17 quarantine audit exactly as `main` carried
it at `acc17dc`, with each heading moved two levels down. It describes the
files as they were then. Where it says "candidate", "this branch" or "not yet
live", read it as written on 2026-07-17.

### RAPP estate publication status — CANDIDATE QUARANTINE (NOT YET LIVE)

This branch proposes a deterministic, read-only status surface for
`kody-w/rapp-estate`. It is **not yet the live publication** and does not prove
that GitHub `main` or Pages has changed.

#### Candidate deployment status

The **quarantine takes effect only when** a reviewed commit containing these
bytes reaches `main` and byte-matching responses are verified from both raw
GitHub and GitHub Pages. At this candidate's audit time, remote `main` and live
Pages still served baseline
`24c8fdc1e770c790b98724002d719d515d5e5465`.

`live_deployment_verified` is therefore `false`; the verified commit and UTC
are `null`. The Parent/release coordinator will push and verify before closing
the review. Until that verification completes, consumers must treat the live
site as the unremediated baseline, not as quarantined.

#### Exact authority

| Field | Value |
|---|---|
| Repository | `kody-w/rapp-1` |
| Commit | `d2cd5abed48d3f52b86bbb975ac3558286d1db41` |
| Path | `SPEC.md` |
| Status in document | Draft standard for ratification (rev-5) |
| Bytes | `41952` |
| SHA-256 | `cea7847f98f9751734995f46fd4e1bde211c8eb9d03dbbb477934213865bb91a` |

Immutable authority:
<https://raw.githubusercontent.com/kody-w/rapp-1/d2cd5abed48d3f52b86bbb975ac3558286d1db41/SPEC.md>.
The same pin is machine-readable in
[`RAPP1_AUTHORITY.json`](RAPP1_AUTHORITY.json).

#### Audit basis

- Baseline:
  `24c8fdc1e770c790b98724002d719d515d5e5465`
- Baseline surface: exactly five tracked files; no archives.
- At audit time, every baseline byte matched both local git and the live
  `main` raw publication. All five paths were also served by GitHub Pages.
- The two baseline JSON surfaces emitted **18 provisional occurrences**:
  `estate.json` emitted 17 (one `owner.rappid` plus 16
  `created[].rappid`), and the network beacon emitted one
  `operator_rappid`.
- The beacon value duplicated the estate owner value, so those 18 occurrences
  represented **17 distinct baseline identifier values/lookups**. The estate
  contained no membership entries.
- Of those 17 lookup records, 16 resolved publicly across 15 distinct public
  repository paths; one did not resolve publicly. All resolved source records exposed
  syntactically current 64-hex candidates and migration assertions.
- No owner-signed re-anchor record, out-of-band estate-owner anchor, or
  authenticated, monotonic, freshness-checked section 13 registry was found.
  Syntax and GitHub authorship are not substitutes for that evidence.
- [`RAPP1_EVIDENCE.json`](RAPP1_EVIDENCE.json) records every lookup as a
  public-safe, non-authoritative point-in-time observation. Moving refs were
  discovery-only; the manifest cannot promote trust.

#### Findings and fixes

1. **Identity:** the baseline surfaces emitted 18 provisional occurrences
   representing 17 distinct lookups. This candidate removes them rather than
   converting or re-minting them. Current candidates in other repositories
   were not copied because their required authorization evidence is absent.
2. **Labels and authority:** the estate, beacon, and metropolis labels were
   defined outside the pinned authority and were presented as canonical. This
   candidate does not emit them as protocol schemas or specifications.
3. **Frames, wire, and registry:** the retired metropolis prose described a
   different frame shape and extra substrate behavior, while also denying the
   registry that RAPP/1 section 13 requires. The candidate path makes no such
   claim; the live baseline remains unchanged pending deployment.
4. **Map semantics:** created inventory was presented as ownership and
   reachability. The candidate surface exposes only aggregate historical
   counts and empty current claim sets.
5. **Moving links:** moving authority links, moving identity paths, an
   unresolved non-public target, and a missing well-known path are removed from
   candidate trust-bearing output. The authority link is commit-pinned and
   hash-pinned.
6. **Rendering safety:** client-side fetch, HTML injection sinks, generated
   links, and inline event handlers are removed by the candidate. Its
   `index.html` is static and carries no script or external asset.
7. **Public data:** personal display text and non-public repository locators
   are removed from candidate bytes. Historical bytes remain available through
   git history only.

#### Candidate surfaces

| Path | Candidate role |
|---|---|
| `index.html` | Static human-readable quarantine status |
| `estate.json` | Fail-closed machine-readable publication status |
| `.well-known/rapp-network.json` | Fail-closed discovery status; not a beacon |
| `METROPOLIS.md` | Candidate retirement notice; not a specification |
| `RAPP1_AUTHORITY.json` | Exact structural authority pin |
| `RAPP1_EVIDENCE.json` | Non-authoritative, commit-pinned lookup observations |
| `RAPP1_OWNER_ACTIONS.json` | Owner-only blocker with null inputs |
| `RAPP1_STATUS.md` | Candidate status and live deployment checklist |
| `tests/test_publication.py` | Offline invariants and optional pinned-source verification |
| `.nojekyll` | GitHub Pages literal-file control |

No candidate identity, membership, frame, wire, or registry claim is accepted.
This statement becomes the live publication posture only after the deployment
condition above is verified.

#### Role and subordination

The normative authority above is technical and commit-pinned. Under RAPP/1
section 11, any Router/Mirror is subordinate to `kody-w/RAPP`. This repository
does not route. If its static status is treated as a mirror, that mirror is
subordinate and must serve provenance-stamped, hash-matching bytes only.

#### Remaining owner action

The owner-only decision and evidence fields remain `null` in
[`RAPP1_OWNER_ACTIONS.json`](RAPP1_OWNER_ACTIONS.json). Until they are supplied
and independently verified, consumers must refuse this repository as a live
estate, beacon, registry, or identity source.

#### Live deployment verification checklist

The Parent/release coordinator must complete and record every item before
closing:

- [ ] Review the candidate commit, complete diff, file ledger, and public-safe
  handoff.
- [ ] Run `python3 tests/test_publication.py --online` and retain the passing
  result.
- [ ] Run the RAPP floor from the exact pinned authority checkout and retain
  the `CLEAN` result.
- [ ] Push or merge the reviewed candidate commit to `main` without rewriting
  it.
- [ ] Resolve remote `main` to a full 40-hex commit and confirm it contains the
  reviewed candidate.
- [ ] Fetch every tracked raw path at that resolved commit and verify its byte
  count and SHA-256 against the git tree.
- [ ] Poll GitHub Pages until the index, both machine status surfaces, authority
  pin, evidence, owner actions, status, and retirement notice all return HTTP
  200 with the reviewed bytes.
- [ ] Confirm the live index is script-free and both live machine surfaces
  remain fail-closed with empty/null claims.
- [ ] Re-fetch the immutable authority and verify `41952` bytes and SHA-256
  `cea7847f98f9751734995f46fd4e1bde211c8eb9d03dbbb477934213865bb91a`.
- [ ] Record the deployed commit, verification UTC, raw/Page hashes, and final
  result in the parent handoff before closing.

This status is dated `2026-07-17`. A moving branch is not provenance:
consumers must resolve and pin the serving commit before citing these bytes.
