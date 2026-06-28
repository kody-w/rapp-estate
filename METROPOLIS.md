# rapp-metropolis/1.0

**The mesh-composition tier: how signed neighborhoods compose upward into estate, then metropolis, over GitHub-as-substrate.**

- **spec_id:** `rapp-metropolis/1.0`
- **status:** Canonical (load-bearing)
- **home:** `kody-w/rapp-estate/METROPOLIS.md`
- **per-node manifest:** `estate.json` (`rapp-estate/1.1`)
- **depends on:** `rapp-neighborhood-protocol/1.0` (§6 twin-chat envelope), `rapp-eternity/1.0` (rappid identity), `rapp-frame` (append-only frame ordering), `rapp-commons-event/1.0` + `rapp-resident` (signed twin-chat events)
- **excludes:** `rapp-distro/1.0`, `rapp-frame/2.0` (formalized separately)

---

## 0. Tier model

The RAPP estate is a strict containment hierarchy. Each tier is a pure composition of the tier below it — there is no new runtime, no new daemon, and no new wire. The only wire is `/chat` (CONSTITUTION Art. XXV); the only substrate is GitHub.

| Tier | Name | Unit | Governed by | Manifest |
|------|------|------|-------------|----------|
| 0 | **Atom** | one brainstem | rapp-installer (the grail kernel) | `VERSION`, `agents/` |
| 1 | **Neighborhood** | brainstems that twin-chat each other | `rapp-neighborhood-protocol/1.0` | §6 twin-chat envelope |
| 2 | **Estate** | one operator's full set of neighborhoods | `rapp-metropolis/1.0` (this spec) | `estate.json` (`rapp-estate/1.1`) |
| 3 | **Metropolis** | many operators' estates, mutually discoverable | `rapp-metropolis/1.0` (this spec) | the union of all discoverable `estate.json` |

Definitions:

- A **brainstem** (atom) is a single-file kernel serving `/chat`. It is the only thing that executes agents.
- A **neighborhood** is a set of brainstems that exchange signed §6 twin-chat events. It is owned by exactly one operator (a GitHub identity) and addressed by a `rappid`.
- An **estate** is *one operator's* set of neighborhoods and twins, declared in a single `estate.json` published at that operator's well-known path. The estate is the unit of *ownership*.
- A **metropolis** is the emergent graph formed when estates discover and read one another. **No one owns the metropolis.** It has no manifest of its own — it *is* the transitive closure of every discoverable `estate.json` reachable by following `member` edges. The metropolis is the unit of *composition*.

> **North-star fit:** the metropolis is literally "use everyone else's hardware → neighborhoods → estate → metropolis." Each operator pays for their own atoms; composition is read-only and free, because reads are served by GitHub Pages / raw-CDN, which the operator already pays nothing for.

An estate conforms to `rapp-metropolis/1.0` iff it satisfies §7. The metropolis is not a thing you build; it is a thing that *happens* when ≥2 conformant estates name each other.

---

## 1. GitHub IS the substrate

There is no RAPP server. There is no central registry, no broker, no relay that the protocol requires. Every primitive of metropolis composition is a native GitHub feature:

| Need | GitHub primitive | RAPP usage |
|------|------------------|------------|
| **Cross-node async write** | **Issues** | An Issue on the *target* estate repo is a mailbox message. The Issue body carries a signed §6 twin-chat event. The target's twin polls/reacts; Issue comments form the reply thread. |
| **Membership / joining (consent)** | **Pull Requests** | To become a `member` of an estate you open a PR that adds your `rappid` to the target's `estate.json`. **A merged PR is consent.** Merge authority = `gh-collaborator` on the target repo. |
| **Read path / edge** | **Pages** | Each estate publishes `estate.json` and its frame snapshots via GitHub Pages (`https://<op>.github.io/<repo>/...`). Pages is the CDN edge; it is read-only, cached, and survives the operator's host being offline. |
| **Bulk / programmatic reads** | **raw-CDN** | `https://raw.githubusercontent.com/<op>/<repo>/main/estate.json` for crawlers that want the source-of-truth commit, not the Pages render. |
| **Ordering / history** | **git commits** | Commit timestamps + the append-only frame log (§4) give a verifiable, UTC-anchored event order. |

**Writes are slow and consensual; reads are fast and free.** This is the asymmetry the whole tier is built on:

- **Mailbox writes (Issues)** and **membership writes (PRs)** go through GitHub's auth and the target operator's consent. They are deliberately the *only* mutation paths into another operator's estate. There is no unauthenticated write. (This is the metropolis-tier analogue of closing the unauth `/api/agent` hole: nothing mutates another node without a GitHub identity behind it.)
- **Reads (Pages / raw-CDN)** require nothing. Anyone — human, crawler, or another estate's twin — can read any published `estate.json` and any published frame snapshot. Discovery is therefore permissionless; participation is consensual.

> A metropolis message never travels over a private wire. If two operators are composing, an outside observer can, in principle, read the public Issues, PRs, and Pages that constitute their relationship. Privacy at this tier is achieved by *sealing* payloads (`rapp-neighborhood-protocol` `sealed` mode), not by hiding the substrate.

---

## 2. Discovery & beacons

### 2.1 The well-known beacon

Every conformant estate **MUST** publish a beacon at a discoverable, stable URL. Two equivalent locations are recognized; a crawler tries them in order:

1. `https://<operator>.github.io/rapp-estate/.well-known/estate.json` (Pages edge — preferred)
2. `https://raw.githubusercontent.com/<operator>/rapp-estate/main/estate.json` (raw-CDN — source of truth)

The beacon **is** the `estate.json` document (`rapp-estate/1.1`). An estate with no published beacon is invisible to the metropolis (it may still be a valid private estate; it is simply not composed).

### 2.2 estate.json (`rapp-estate/1.1`) — the per-node manifest

`estate.json` is the single manifest this protocol composes. It is the per-node *instance* of metropolis membership.

```json
{
  "schema": "rapp-estate/1.1",
  "owner": {
    "rappid": "rappid:@kody-w/estate:9f2c…<64hex>",
    "github": "kody-w"
  },
  "created": [
    {
      "rappid": "rappid:@kody-w/neighborhood-batcave:a1b2…<64hex>",
      "type": "neighborhood",
      "added_at": "2026-05-09T23:34:15Z",
      "via": "rebuild"
    },
    {
      "rappid": "rappid:@kody-w/twin-kody:c3d4…<64hex>",
      "type": "twin",
      "added_at": "2026-05-09T23:34:40Z",
      "via": "rebuild"
    }
  ],
  "member": [
    {
      "rappid": "rappid:@alice/estate:7e8f…<64hex>",
      "estate_url": "https://alice.github.io/rapp-estate/.well-known/estate.json",
      "added_at": "2026-06-20T14:02:00Z",
      "via": "pr#42",
      "consent": { "kind": "gh-collaborator", "pr": "kody-w/rapp-estate#42", "merged_by": "kody-w" }
    }
  ],
  "updated_at": "2026-06-28T00:00:00Z"
}
```

Field rules:

- **`schema`** — MUST be `rapp-estate/1.1`. Readers MUST accept any `rapp-estate/1.x` and ignore unknown fields (forward-compatible).
- **`owner.rappid`** — the estate's own rappid, per `rapp-eternity/1.0` (content-addressed sha256, PKI-free). `owner.github` — the GitHub login that holds merge authority over this repo. The pair binds an *identity* (rappid) to a *substrate authority* (gh login).
- **`created[]`** — entities *this operator* owns: their own neighborhoods and twins. `type ∈ {neighborhood, twin}`. These are the *inward* composition (estate ⊃ neighborhoods).
- **`member[]`** — *other operators' estates* this estate has consented to peer with. Each entry carries the peer's beacon URL and the consent record (§3). These are the *outward* composition (metropolis edges). A `member` edge means "I read this peer's frames and accept its signed twin-chat."
- **`updated_at`** — UTC, RFC 3339, `Z`-suffixed. Used for staleness/offline-degrade decisions (§5).
- **All timestamps MUST be UTC `Z`-suffixed** (UTC-first, §4).

### 2.3 The metropolis crawl

A metropolis crawler enumerates the graph by transitive closure over `member` edges:

```
seed   := one or more known estate beacon URLs
seen   := {}
queue  := seed
while queue not empty:
    url := queue.pop()
    if url in seen: continue
    seen.add(url)
    doc := GET url            # Pages first, raw-CDN fallback (§5)
    yield doc
    for m in doc.member:
        queue.push(m.estate_url)
```

Properties:

- **Permissionless** — the crawl uses only public reads; no auth, no token, no central index.
- **Decentralized** — there is no master list. `rapp-map` (the estate map) is a *convenience cache* of one crawl, not an authority. The authority is the live beacons.
- **Convergent** — because edges are content-addressed by rappid and reads are idempotent, two crawlers from different seeds that reach the same estates produce the same subgraph.
- **rappid-addressed** — every node and edge is named by a `rapp-eternity/1.0` rappid; the `estate_url` is a *hint* for where to fetch, the rappid is the *identity*. If a URL moves, the rappid is unchanged and the hash still verifies.

---

## 3. Consent & trust

The metropolis trust model is the same one that governs the whole estate: **gh-collaborator + sha256, with keypairs optional and never required.**

### 3.1 Membership = PR-consent (default)

To add an edge `A → B` (estate A becomes a `member` of estate B, i.e. B agrees to peer with A):

1. A opens a **PR against B's `rapp-estate` repo** adding A's entry to `B/estate.json`'s `member[]`.
2. A B-side **gh-collaborator merges the PR.** The merge **is** the consent. No signature, no key, no ceremony beyond the merge button.
3. The merged commit is the durable, auditable consent record. The entry records `"consent": { "kind": "gh-collaborator", "pr": "...", "merged_by": "..." }`.

This is the default and it is sufficient. It inherits GitHub's identity and audit log for free, and it requires **no PKI** (MASTER_PLAN §3 — no mandatory PKI).

### 3.2 Optional signed membership (opt-in sovereignty)

An operator MAY additionally bind a membership edge to a `rapp-eternity/1.0` keypair signature for sovereignty that survives the substrate (takedown, account loss, death — MASTER_PLAN §4):

```json
"consent": {
  "kind": "gh-collaborator+signed",
  "pr": "kody-w/rapp-estate#42",
  "merged_by": "kody-w",
  "sig_suite": "ed25519",
  "sig": "base64…",
  "signed_over": "sha256(rappid_A + rappid_B + added_at)"
}
```

Rules:

- A signature is **purely additive**. `kind: "gh-collaborator"` (no signature) is a complete, valid, first-class consent. A reader MUST NOT reject an unsigned edge.
- No component of the metropolis tier may *require* a keypair. Signing is opt-in sovereignty, never a gate. (`rappid eternity` is PKI-free sha256; keypair binding is optional — this is the keypair-OPTIONAL resolution applied at the mesh tier.)
- This is how MASTER_PLAN §3 (no mandatory PKI) and §4 (un-shutdownable) coexist: the default path needs no keys and rides GitHub; the sovereign path adds keys so an edge can be re-proven on a *different* substrate if GitHub disappears.

### 3.3 No central registry

There is no metropolis authority that can admit, evict, or rename a node. Membership is purely pairwise and consensual: B decides who is a member of B, and only B. The "metropolis" is just what those pairwise consents add up to. Evicting a peer is a commit that removes the `member` entry — local, unilateral, no quorum.

---

## 4. Frame ordering & convergence

Composition needs a shared sense of "before" across operators who share no clock and no server. The metropolis uses **UTC-first ordering over append-only frames**, aligned with `rapp-frame`.

### 4.1 The frame envelope

Every metropolis-visible event (a twin-chat broadcast, a membership change, a snapshot) is a **frame**: an append-only record carrying a §6 twin-chat envelope plus ordering metadata.

```json
{
  "frame_id": "rappid:@kody-w/frame:…<64hex>",
  "ts": "2026-06-28T00:00:00.000Z",
  "prev": "rappid:@kody-w/frame:…<64hex>",
  "origin": "rappid:@kody-w/estate:…",
  "envelope": { "...": "rapp-neighborhood-protocol §6 twin-chat event (signed)" },
  "hash": "sha256(canonical(frame_minus_hash))"
}
```

- **`ts`** — UTC, `Z`-suffixed, millisecond precision. **UTC-first:** the primary sort key across the entire metropolis is `ts`. Operators MUST stamp frames in UTC; there are no local-time frames on the wire.
- **`prev`** — the previous frame's `frame_id` in this origin's local chain (append-only; each origin has a hash-linked chain — `rapp-frame`).
- **`hash`** — content address of the frame, making it tamper-evident and giving every frame a rappid.

### 4.2 Ordering rule

Across nodes, total order is defined by the tuple, in priority order:

```
(ts, origin_rappid, hash)
```

1. **`ts`** (UTC) is primary. Earlier UTC wins.
2. On exact `ts` tie, **`origin_rappid`** lexical order breaks it (deterministic, operator-independent).
3. On the impossible event of an `origin`+`ts` collision, **`hash`** breaks it.

This yields a total order computable independently by every reader from public data, with no coordination round.

### 4.3 Convergence / conflict resolution by hash

- Frames are **append-only and content-addressed**, so the same event has the same `hash` everywhere — duplicates dedupe by `hash`, not by position.
- Two operators that concurrently produce conflicting state (e.g. both claim a name) do not *merge* — both frames exist; readers apply the deterministic order and the metropolis converges on the same winner everywhere. **Conflict resolution is by ordered hash, never by overwrite.** (Aligns with the estate-wide rule: never rewrite identity in place; the hash is the join key.)
- Because resolution is a pure function of the public frame set, two readers with the same frames always agree. There is no split-brain that survives a full read.

---

## 5. Offline-degrade

The metropolis must stay *readable* even when operators' hosts are down. This is the answer to the estate's standing tension (a single always-on relay contradicting the no-central-server north star): **availability is provided by the substrate edge, not by anyone's host.**

### 5.1 Read degradation

A reader fetching a peer follows this ladder, taking the first that succeeds:

1. **Pages edge** — `https://<op>.github.io/...` — fast, cached, served by GitHub even if the operator's atom (brainstem) is offline.
2. **raw-CDN** — `https://raw.githubusercontent.com/<op>/.../estate.json` — source-of-truth at the latest commit.
3. **Last-known snapshot** — a previously crawled copy held by the reader (or by `rapp-map`), tagged with the `updated_at`/`ts` it was read at.

A node whose *host* (brainstem) is offline still appears in the metropolis at **its last-published Pages snapshot.** Its frames up to its last commit remain ordered and readable. The metropolis never goes dark because a brainstem went to sleep — only *new writes* from that node pause.

### 5.2 Staleness, not unavailability

A reader MUST treat a peer as **stale** (degraded), not **gone**, when its host is unreachable:

- `degraded` iff the live host (`/chat`) does not answer but a Pages/raw snapshot resolves.
- `dark` iff *no* snapshot resolves anywhere (rare — implies the repo itself was deleted).
- `stale_for = now - estate.updated_at`; readers MAY surface this but MUST NOT drop the node.

### 5.3 Rejoin semantics

When an offline node returns:

- It **resumes its append-only frame chain** from its last `frame_id` (`prev` still points at the pre-outage tip). No re-handshake, no re-consent — membership edges in `estate.json` are durable git state and were never lost.
- Frames authored during the outage by *others* are simply read and ordered by `ts` on return; UTC-first ordering means a returning node sees exactly the same total order as everyone else, no replay protocol required.
- Consent does not expire. A merged-PR membership stays valid across arbitrary downtime; only an explicit commit removing the `member` entry revokes it.

---

## 6. Relationship to a single neighborhood

`rapp-metropolis/1.0` is a **strict superset** layered *on top of* the `rapp-neighborhood-protocol/1.0` §6 twin-chat envelope. It adds nothing inside the envelope and changes nothing about how two brainstems talk.

- The **payload** crossing the metropolis is *exactly* a §6 signed twin-chat event. Metropolis adds the *outer* frame (§4) for cross-operator ordering and the *substrate* routing (Issues/PRs/Pages, §1) — it never reaches into the envelope.
- **A neighborhood need not know it is in a metropolis.** A conformant neighborhood that has never published an `estate.json` is a complete, valid system. Wrapping it in an estate and consenting to peers is purely additive; the neighborhood's brainstems and agents are byte-identical either way.
- This preserves "never break userspace": the agent ABI (`BasicAgent.metadata` + `perform(**kwargs) -> str`, `/chat`, auto-discovery) and the §6 envelope are untouched. Metropolis is composition, not a new runtime.
- Because Leviathan fleet messaging is *also* defined as signed twin-chat over `/chat` (per `rapp-commons-event/1.0` + `rapp-resident`), a fleet is just a neighborhood whose members happen to share a controller — and it composes into the metropolis through the same `estate.json` with zero special-casing.

> Inward, an estate *contains* neighborhoods (`created[]`). Outward, an estate *peers* with estates (`member[]`). The metropolis is the outward closure; the neighborhood is the inward atom of ownership. Same envelope at every layer.

---

## 7. Conformance

An estate is **`rapp-metropolis/1.0`-conformant** iff **all** of the following hold:

1. **Discoverable beacon.** It publishes an `estate.json` (`rapp-estate/1.1`) at a well-known Pages URL, with a raw-CDN fallback (§2.1). Unknown fields are ignored; `rapp-estate/1.x` is accepted.
2. **PR-consent membership.** Membership edges are added only via a merged PR against the estate repo; merge authority is `gh-collaborator` (§3.1). Each `member` entry records its consent provenance. Optional signatures are accepted but never required (§3.2).
3. **Pages/raw reads.** It reads peers over Pages/raw-CDN (not over any private wire), following the offline-degrade ladder (§5.1), and treats unreachable peers as `degraded`, not dropped (§5.2).
4. **UTC-first ordering.** Every metropolis-visible frame is UTC `Z`-stamped and totally ordered by `(ts, origin_rappid, hash)` (§4.2); conflicts resolve by hash, never by overwrite (§4.3).
5. **Envelope fidelity.** Cross-node payloads are unmodified `rapp-neighborhood-protocol/1.0` §6 twin-chat events (§6). No new wire is introduced; `/chat` remains the only execution wire.
6. **No central dependency.** Conformance requires no RAPP-operated server, registry, or relay — only the operator's own GitHub repo and atoms.

A metropolis is conformant iff every estate reachable in the crawl (§2.3) is individually conformant. There is no metropolis-level object to certify — conformance is purely the AND of its nodes.

---

## 8. Worked example

Two independent operators, **kody-w** and **alice**, each run their own atoms. Neither has ever met a server. They compose into a two-node metropolis.

**Step 1 — Each publishes a beacon.**
`kody-w` ships `https://kody-w.github.io/rapp-estate/.well-known/estate.json` listing one neighborhood (`neighborhood-batcave`) and one twin (`twin-kody`) in `created[]`; `member[]` is empty. `alice` does the same with her own neighborhood. Two isolated estates now exist. The metropolis size is 1 from each seed (no edges yet).

**Step 2 — alice asks to peer (PR-consent).**
alice opens a PR against `kody-w/rapp-estate` adding to `member[]`:

```json
{
  "rappid": "rappid:@alice/estate:7e8f…",
  "estate_url": "https://alice.github.io/rapp-estate/.well-known/estate.json",
  "added_at": "2026-06-28T15:00:00Z",
  "via": "pr#42",
  "consent": { "kind": "gh-collaborator", "pr": "kody-w/rapp-estate#42", "merged_by": "kody-w" }
}
```

kody-w reviews and **merges PR #42**. The merge is the consent — no keys exchanged. (alice could symmetrically merge kody-w into *her* `member[]`; edges are directional, and a mutual peering is two merges.)

**Step 3 — The crawl now joins them.**
Any crawler seeded with *either* beacon now reaches *both* estates by following the new `member` edge. `rapp-map` re-crawls and caches a 2-node graph — but the cache is just a convenience; the live beacons are the truth.

**Step 4 — A twin-chat crosses the mesh.**
`twin-kody` wants to tell alice's neighborhood something. It does **not** open a socket. It writes a §6 signed twin-chat event, wraps it in a frame, and delivers it as an **Issue on `alice/rapp-estate`**:

```json
{
  "frame_id": "rappid:@kody-w/frame:11aa…",
  "ts": "2026-06-28T15:30:00.000Z",
  "prev": "rappid:@kody-w/frame:00ff…",
  "origin": "rappid:@kody-w/estate:9f2c…",
  "envelope": { "type": "twin-chat", "from": "rappid:@kody-w/twin-kody:…", "body": "…", "sig": "…(§6)…" },
  "hash": "sha256(…)"
}
```

alice's twin (polling its repo's Issues) reads the frame, verifies the §6 envelope, and replies in the Issue thread with its own frame. The whole exchange is public, async, and rides Issues — no private wire, no shared server.

**Step 5 — kody-w's host goes offline.**
kody-w's laptop sleeps; `/chat` stops answering. alice fetches `kody-w`'s beacon: the Pages edge still serves the last snapshot (§5.1). alice marks kody-w `degraded`, keeps the membership edge, and keeps reading kody-w's frames up to his last commit, ordered by UTC. The 2-node metropolis is still fully readable.

**Step 6 — kody-w returns.**
The laptop wakes. `twin-kody` resumes its frame chain from `frame:11aa…` (`prev` intact), reads alice's outage-period frames, and orders the merged stream by `(ts, origin_rappid, hash)`. Both operators independently compute the identical total order. No re-handshake, no re-consent, no replay protocol. The mesh converged.

---

## Appendix A — Authority order (on disagreement)

When sources disagree about the metropolis state, trust in this order:

1. **The live beacon** (`estate.json` at Pages/raw) — source of truth for membership.
2. **The merged-PR git history** — source of truth for consent.
3. **The append-only frame chains** — source of truth for events and order.
4. **`rapp-map` / `rapp-god` caches** — convenience only; may lag (they are known to drift). Never authoritative over a live beacon.

## Appendix B — Glossary

- **atom** — one brainstem (kernel) serving `/chat`.
- **neighborhood** — brainstems exchanging §6 twin-chat; one operator; `rapp-neighborhood-protocol/1.0`.
- **estate** — one operator's full set, manifested in `estate.json` (`rapp-estate/1.1`); the unit of ownership.
- **metropolis** — the transitive closure of discoverable estates over `member` edges; the unit of composition; owned by no one.
- **beacon** — the well-known published `estate.json`.
- **rappid** — `rapp-eternity/1.0` content-addressed sha256 identity (PKI-free; keypair optional).
- **frame** — append-only, UTC-stamped, hash-linked record carrying a §6 envelope (`rapp-frame`-aligned).
- **PR-consent** — membership granted by a gh-collaborator merging a PR; the default trust act.
- **degraded** — a node whose host is offline but whose Pages snapshot still resolves.
