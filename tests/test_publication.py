#!/usr/bin/env python3
"""Deterministic publication and evidence checks for rapp-estate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
# The draft is built in four steps, one commit each: 1 estate.json, 2 the beacon, 3 the release
# manifests (which pin this repository at the beacon commit), 4 lts-pins.json.
STAGE = 3
BASELINE = "24c8fdc1e770c790b98724002d719d515d5e5465"
QUARANTINE_COMMIT = "acc17dca283619f288274f237c8c61f437d014f3"
AUTHORITY_COMMIT = "d2cd5abed48d3f52b86bbb975ac3558286d1db41"
AUTHORITY_SHA256 = "cea7847f98f9751734995f46fd4e1bde211c8eb9d03dbbb477934213865bb91a"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
PUBLIC_REPOSITORY_RE = re.compile(r"^kody-w/[A-Za-z0-9._-]+$")
RAPPID_RE = re.compile(
    r"^rappid:@([a-z0-9]+(?:-[a-z0-9]+)*)/([a-z0-9]+(?:-[a-z0-9]+)*):([0-9a-f]{64})$"
)
PARTICLE_SPACE = "rapp/1:particle"
MANIFEST_SCHEMA = "rapp/1-release-manifest"
MANIFEST_MEMBERS = {"schema", "release_scope", "release", "components"}
COMPONENT_MEMBERS = {
    "id",
    "kind",
    "rappid",
    "identity_path",
    "repository",
    "object_format",
    "commit",
    "immutable_ref",
    "files",
}
FILE_MEMBERS = {"path", "sha256", "size_bytes"}
RELEASES = {
    "6163b310659800fea34486baedc78f293156795ac3eadf4f5c1308c2a270f408": {
        "release": "rapp-1-lts-2026.09",
        "release_scope": "https://kody-w.github.io/RAPP/releases/rapp-1-lts/brainstem-v0.6.9",
        "channel": "rapp1-lts",
        "kernel_ref": "refs/tags/brainstem-v0.6.9",
        "components": 235,
        "bytes": 76212,
        "sha256": "bf17f1b4b53c5bd43d5bfc71fca762c67029f802f157498577f25b11fb073645",
    },
    "291dbe7955780a79a857869d96bd0c3405e5c7382c87e13fd40fcda8728c0a1c": {
        "release": "brainstem-v0.6.16",
        "release_scope": "https://kody-w.github.io/RAPP/releases/brainstem-v0.6.16",
        "channel": "newest",
        "kernel_ref": "refs/tags/brainstem-v0.6.16",
        "components": 310,
        "bytes": 94060,
        "sha256": "3473531d2bfc6efd849697564ab3b51ba32228c86b13ca9ca7833846ba42ae6a",
    },
}
RELEASE_FILES = {f"releases/{manifest_hash}.json" for manifest_hash in RELEASES}
CHANNEL_MANIFESTS = {
    release["channel"]: manifest_hash for manifest_hash, release in RELEASES.items()
}
THIS_REPOSITORY = "https://github.com/kody-w/rapp-estate"
RAW_THIS_REPOSITORY = "https://raw.githubusercontent.com/kody-w/rapp-estate/"
HIVE_PUBLIC_COMMIT = "eafa6de7e04a3d536c21976c1d85e845a499cd7b"
OPERATOR_RAPPID = (
    "rappid:@kody-w/estate-owner:"
    "b5814e45e9988df835dfd58d152a6fb05b6510a087a35c24374a1c4ab833c122"
)
ESTATE_SCHEMA = "rapp-estate/1.1"
ESTATE_MEMBERS = {"schema", "owner", "created", "member", "hives", "updated_at"}
ENTRY_MEMBERS = {"rappid", "added_at", "via"}
ENTRY_VIA = {"created", "scan", "manual", "import", "published-by-other"}
CRAWL_FINISHED_UTC = "2026-09-25T18:16:15Z"
EXPECTED_DOORS = 30
SECOND_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
HIVE_ROOT = {
    "hive": "af02504304365b6d8b068553156b5e6d",
    "name": "rapp-hive",
    "root": "https://raw.githubusercontent.com/kody-w/rapp-hive-public/",
    "commit": HIVE_PUBLIC_COMMIT,
    "published_sha256": "3deeab22ba4995558c1647c50e6545e9fb2f2bcd2df5f6b64600868b63083291",
}
BEACON_SCHEMA = "rapp-network-beacon/1.1"
BEACON_PATH = ".well-known/rapp-network.json"
# What the release manifests pin of this repository (sorted bytewise, as a manifest lists them).
ESTATE_COMPONENT_FILES = [".well-known/rapp-network.json", "estate.json"]
# The beacon field allowlist of RAPP pages/docs/PUBLIC_PRIVATE_BOUNDARY.md section 4.5.
BEACON_FIELDS = {
    "schema",
    "operator_rappid",
    "github",
    "estate_url",
    "grail_url",
    "protocol.spec_version",
    "protocol.estate_schema",
    "protocol.implements",
    "protocol.spec_url",
    "discovery.indexable",
    "discovery.consent",
    "discovery.federation_hints",
    "private_estate_pointer",
    "private_estate_commitment",
    "private_door_count",
    "minted_at",
}
BEACON_IMPLEMENTS = ["article-xlvi", "article-xlvii", "article-xlviii"]
GRAIL_URL = "https://kody-w.github.io/rapp-estate/"
PRIVATE_ESTATE_POINTER = "https://github.com/kody-w/rapp-estate-private"
ESTATE_URL_RE = re.compile(
    r"^https://raw\.githubusercontent\.com/kody-w/rapp-estate/([0-9a-f]{40})/estate\.json$"
)
LTS_PINS_URL_RE = re.compile(
    r"^https://raw\.githubusercontent\.com/kody-w/rapp-estate/([0-9a-f]{40})/lts-pins\.json$"
)
HISTORICAL_FILES = ("RAPP1_AUTHORITY.json", "RAPP1_EVIDENCE.json")
HISTORICAL_HEADING = "\n## Historical record (kept as written)\n"
METROPOLIS_NOTE = (
    "> **Note of 2026-09-25.** On 2026-09-25 raw GitHub at `main` and GitHub\n"
    "> Pages served this notice exactly as written below, without this note (see\n"
    "> [`RAPP1_STATUS.md`](RAPP1_STATUS.md)). It is kept as `main` carried it at\n"
    "> `acc17dc` and covers only this path; the distributed Hive activation\n"
    "> drafted in this repository is described in `RAPP1_STATUS.md`.\n"
)
EXPECTED_FILES = {
    ".nojekyll",
    ".well-known/rapp-network.json",
    "METROPOLIS.md",
    "RAPP1_AUTHORITY.json",
    "RAPP1_EVIDENCE.json",
    "RAPP1_OWNER_ACTIONS.json",
    "RAPP1_STATUS.md",
    "estate.json",
    "index.html",
    "tests/test_publication.py",
    *({".gitattributes", *RELEASE_FILES} if STAGE >= 3 else set()),
    *({"lts-pins.json"} if STAGE >= 4 else set()),
}


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise AssertionError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    assert raw.endswith(b"\n"), f"{path} must end with LF"
    assert not raw.startswith(b"\xef\xbb\xbf"), f"{path} has a BOM"
    assert b"\r\n" not in raw, f"{path} has CRLF"
    return json.loads(raw, object_pairs_hook=reject_duplicate_keys)


def refuse_constant(value: str) -> object:
    raise AssertionError(f"non-I-JSON number: {value}")


def strict_json(raw: bytes) -> object:
    return json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=refuse_constant,
        parse_float=refuse_constant,
    )


def canonical(value: object) -> str:
    """RFC 8785 over RAPP/1's exact-value domain, as kody-w/rapp-1 rapp.canonical."""
    if value is None or isinstance(value, bool):
        return json.dumps(value)
    if isinstance(value, int):
        assert abs(value) <= 2**53 - 1, "integer outside the I-JSON range"
        return json.dumps(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ",".join(canonical(item) for item in value) + "]"
    if isinstance(value, dict):
        keys = sorted(value, key=lambda key: key.encode("utf-16-be"))
        return "{" + ",".join(
            json.dumps(key, ensure_ascii=False) + ":" + canonical(value[key])
            for key in keys
        ) + "}"
    raise AssertionError(f"not a RAPP/1 value: {type(value).__name__}")


def particle_hash(value: object) -> str:
    """H("rapp/1:particle", value), as kody-w/rapp-1 rapp.H."""
    return hashlib.sha256(
        PARTICLE_SPACE.encode("utf-8") + b"\n" + canonical(value).encode("utf-8")
    ).hexdigest()


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"{commit}:{path}"]
    )


def is_ancestor_of_head(commit: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", commit, "HEAD"],
        check=False,
    ).returncode == 0


def adding_commits(path: str) -> list[str]:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "log", "--diff-filter=A", "--format=%H", "--", path],
        text=True,
    ).split()


def is_ancestor(older: str, newer: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", older, newer]
    ).returncode == 0


def last_commit(path: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "log", "-1", "--format=%H", "--", path], text=True
    ).strip()


def baseline_json(path: str) -> dict[str, object]:
    raw = git_bytes(BASELINE, path)
    return json.loads(raw, object_pairs_hook=reject_duplicate_keys)


def test_static_tree() -> None:
    files = {
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    assert files == EXPECTED_FILES
    assert not any(
        re.search(r"\.(zip|tar|tgz|gz|bz2|xz|7z|rar|egg)$", path, re.IGNORECASE)
        for path in files
    )
    for relative_path in files:
        raw = (ROOT / relative_path).read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf"), relative_path
        assert b"\r" not in raw, relative_path
        if relative_path in RELEASE_FILES:
            assert not raw.endswith(b"\n"), relative_path
        elif raw:
            assert raw.endswith(b"\n"), relative_path

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    allowed_external = {
        (
            "https://raw.githubusercontent.com/kody-w/rapp-1/"
            f"{AUTHORITY_COMMIT}/SPEC.md"
        ),
        (
            "https://github.com/kody-w/rapp-estate/tree/"
            "24c8fdc1e770c790b98724002d719d515d5e5465"
        ),
        (
            "https://github.com/kody-w/rapp-hive-public/blob/"
            f"{HIVE_PUBLIC_COMMIT}/PUBLISHED.md"
        ),
    }
    for href in re.findall(r'href="([^"]+)"', html):
        if href.startswith("https://"):
            assert href in allowed_external
        else:
            assert (ROOT / href.split("#", 1)[0]).is_file(), href

    status = (ROOT / "RAPP1_STATUS.md").read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", status):
        if target.startswith("https://"):
            assert target in allowed_external
        else:
            assert (ROOT / target.split("#", 1)[0]).is_file(), target

    current_text = "\n".join(
        (ROOT / relative_path).read_text(encoding="utf-8")
        for relative_path in sorted(files)
    )
    for home_marker in ("/" + "Users" + "/", "/" + "home" + "/", "\\" + "Users" + "\\"):
        assert home_marker not in current_text
    assert "file:" + "//" not in current_text
    stop = r"[^\s\"'<>)`]"
    # Every raw GitHub URL names a full commit, or is a bare raw base ending in "/".
    for owner, repository, rest in re.findall(
        rf"https://raw\.githubusercontent\.com/({stop}+?)/({stop}+?)/({stop}*)",
        current_text,
    ):
        assert rest == "" or re.match(r"^[0-9a-f]{40}/", rest), (owner, repository, rest)
    # Every GitHub blob, tree, raw or commit link names a full commit.
    for kind, ref in re.findall(
        rf"https://github\.com/{stop}+?/{stop}+?/(blob|tree|raw|commit)/([^/\s\"'<>)`]+)",
        current_text,
    ):
        assert COMMIT_RE.fullmatch(ref), (kind, ref)
    # This repository's Pages site appears only as its front door.
    for tail in re.findall(r"https://kody-w\.github\.io/rapp-estate/(" + stop + "*)", current_text):
        assert tail == "", tail
    assert not re.search(
        r"https://raw\.githubusercontent\.com/[^/\s]+/[^/\s]+/main/",
        current_text,
    )


def demote_headings(text: str) -> str:
    return "".join(
        "##" + line if re.match(r"^#{1,6} ", line) else line
        for line in text.splitlines(keepends=True)
    )


def test_historical_record(actions: dict[str, object]) -> None:
    """The 2026-07-17 audit and its evidence stay exactly as main carried them."""
    for path in HISTORICAL_FILES:
        assert (ROOT / path).read_bytes() == git_bytes(QUARANTINE_COMMIT, path), path

    status = (ROOT / "RAPP1_STATUS.md").read_text(encoding="utf-8")
    original = git_bytes(QUARANTINE_COMMIT, "RAPP1_STATUS.md").decode("utf-8")
    assert status.count(HISTORICAL_HEADING) == 1
    record = status.split(HISTORICAL_HEADING, 1)[1]
    intro, separator, kept = record.partition("\n\n### ")
    assert separator and "exactly as `main` carried" in intro
    assert "### " + kept == demote_headings(original)

    metropolis = (ROOT / "METROPOLIS.md").read_text(encoding="utf-8")
    title, rest = git_bytes(QUARANTINE_COMMIT, "METROPOLIS.md").decode("utf-8").split(
        "\n", 1
    )
    assert metropolis == f"{title}\n\n{METROPOLIS_NOTE}{rest}"

    # The ledger only appends a blocker: every original byte stays in place.
    original = git_bytes(QUARANTINE_COMMIT, "RAPP1_OWNER_ACTIONS.json")
    cut = b'\n    }\n  ],\n  "prohibited_substitutes"'
    assert original.count(cut) == 1
    before, after = original.split(cut, 1)
    ledger = (ROOT / "RAPP1_OWNER_ACTIONS.json").read_bytes()
    assert ledger.startswith(before + b"\n    },\n    {\n"), "first blocker changed"
    assert ledger.endswith(cut + after), "ledger tail changed"
    original_actions = json.loads(original, object_pairs_hook=reject_duplicate_keys)
    assert set(actions) == set(original_actions)
    assert len(actions["blockers"]) == len(original_actions["blockers"]) + 1
    assert actions["blockers"][0] == original_actions["blockers"][0]


def test_release_manifests() -> dict[str, dict[str, object]]:
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "releases/*.json -text" in attributes.splitlines()
    manifests: dict[str, dict[str, object]] = {}
    for relative_path in sorted(RELEASE_FILES):
        raw = (ROOT / relative_path).read_bytes()
        manifest_hash = relative_path[len("releases/"):-len(".json")]
        expected = RELEASES[manifest_hash]
        manifest = strict_json(raw)
        assert raw == canonical(manifest).encode("utf-8"), relative_path
        assert particle_hash(manifest) == manifest_hash, relative_path
        assert len(raw) == expected["bytes"], relative_path
        assert hashlib.sha256(raw).hexdigest() == expected["sha256"], relative_path
        assert isinstance(manifest, dict) and set(manifest) == MANIFEST_MEMBERS
        assert manifest["schema"] == MANIFEST_SCHEMA
        assert manifest["release"] == expected["release"]
        assert manifest["release_scope"] == expected["release_scope"]
        components = manifest["components"]
        assert len(components) == expected["components"]
        ids = [component["id"] for component in components]
        assert ids == sorted(ids) and len(ids) == len(set(ids)), relative_path
        bound = [c["rappid"] for c in components if c["rappid"] is not None]
        assert len(bound) == len(set(bound)), relative_path
        kernels = [c for c in components if c["kind"] == "kernel"]
        assert [c["immutable_ref"] for c in kernels] == [expected["kernel_ref"]]
        for component in components:
            assert set(component) == COMPONENT_MEMBERS, component["id"]
            assert component["object_format"] == "sha1", component["id"]
            assert COMMIT_RE.fullmatch(component["commit"]), component["id"]
            assert component["repository"].startswith("https://github.com/")
            paths = []
            for item in component["files"]:
                assert set(item) == FILE_MEMBERS, component["id"]
                assert SHA256_RE.fullmatch(item["sha256"]), component["id"]
                assert type(item["size_bytes"]) is int and item["size_bytes"] >= 0
                paths.append(item["path"])
            assert paths == sorted(paths, key=lambda path: path.encode("utf-8"))
            if component["rappid"] is None:
                assert component["identity_path"] is None, component["id"]
            else:
                assert RAPPID_RE.fullmatch(component["rappid"]), component["id"]
                assert component["identity_path"] in paths, component["id"]
        # The release pins cover the beacon (proposal 0020 D2): each manifest pins this repository at
        # the commit that wrote the current beacon, never at the commit that carries the manifest.
        own = [c for c in components if c["repository"] == THIS_REPOSITORY]
        assert len(own) == 1 and own[0]["kind"] == "estate", relative_path
        pinned_at = own[0]["commit"]
        assert pinned_at == last_commit(BEACON_PATH), "the manifests pin the current beacon's commit"
        assert pinned_at not in adding_commits(relative_path), relative_path
        assert is_ancestor_of_head(pinned_at), relative_path
        assert [item["path"] for item in own[0]["files"]] == ESTATE_COMPONENT_FILES, relative_path
        for item in own[0]["files"]:
            pinned = git_bytes(pinned_at, item["path"])
            assert pinned == (ROOT / item["path"]).read_bytes(), item["path"]
            assert hashlib.sha256(pinned).hexdigest() == item["sha256"], item["path"]
            assert len(pinned) == item["size_bytes"], item["path"]
        manifests[manifest_hash] = manifest
    return manifests


def test_lts_pins(
    pins: dict[str, object], manifests: dict[str, dict[str, object]]
) -> list[tuple[str, bytes]]:
    raw = (ROOT / "lts-pins.json").read_bytes()
    assert raw.decode("utf-8") == json.dumps(pins, indent=2, ensure_ascii=False) + "\n"
    assert pins["schema"] == "rapp1-lts-pins/1"
    assert pins["status"] == "prepared-unsigned"
    assert pins["signed"] is False
    assert pins["note"].startswith("PREPARED AND UNSIGNED.")
    assert pins["rapp1"]["revision"] == "rev-17"
    assert pins["rapp1"]["status"] == "draft"
    assert pins["portfolio"] == {
        "repository": "https://github.com/kody-w/rapp-hive-public",
        "commit": HIVE_PUBLIC_COMMIT,
    }
    assert set(pins["channels"]) == set(CHANNEL_MANIFESTS)
    pinned: list[tuple[str, bytes]] = []
    for channel, manifest_hash in sorted(CHANNEL_MANIFESTS.items()):
        entry = pins["channels"][channel]
        release = RELEASES[manifest_hash]
        assert entry["manifest_hash"] == manifest_hash
        assert entry["release"] == release["release"]
        assert entry["release_scope"] == release["release_scope"]
        assert entry["components"] == release["components"]
        locator = entry["manifest"]
        path = f"releases/{manifest_hash}.json"
        assert locator["repository"] == THIS_REPOSITORY
        assert locator["path"] == path
        commit = locator["commit"]
        assert COMMIT_RE.fullmatch(commit), channel
        assert is_ancestor_of_head(commit), channel
        # The locator is the commit that added the manifest or a later one that still carries it.
        added = adding_commits(path)
        assert len(added) == 1 and (added[0] == commit or is_ancestor(added[0], commit)), channel
        assert git_bytes(commit, path) == (ROOT / path).read_bytes(), channel
        kernel = next(
            c for c in manifests[manifest_hash]["components"] if c["kind"] == "kernel"
        )
        assert entry["kernel"]["commit"] == kernel["commit"]
        assert "refs/tags/" + entry["kernel"]["tag"] == kernel["immutable_ref"]
        assert entry["kernel"]["repository"] == kernel["repository"]
        pinned.append((f"{RAW_THIS_REPOSITORY}{commit}/{path}", (ROOT / path).read_bytes()))

    repositories: set[str] = set()
    for component in manifests[CHANNEL_MANIFESTS["rapp1-lts"]]["components"]:
        repository = component["repository"].removeprefix("https://github.com/")
        repositories.add(repository)
        if component["kind"] == "kernel":
            continue
        pin = pins["pins"][repository]
        assert pin["commit"] == component["commit"], repository
        assert pin["component"] == component["id"], repository
        assert pin["rappid"] == component["rappid"], repository
        assert pin["channel"] == "rapp1-lts", repository
    assert set(pins["pins"]) == repositories
    assert repositories.isdisjoint(pins["not_in_lts"])
    return pinned


def test_baseline_accounting(evidence: dict[str, object]) -> None:
    estate = baseline_json("estate.json")
    beacon = baseline_json(".well-known/rapp-network.json")
    estate_values = [estate["owner"]["rappid"]]
    estate_values.extend(entry["rappid"] for entry in estate["created"])
    emitted_values = estate_values + [beacon["operator_rappid"]]

    assert len(estate_values) == 17
    assert len(estate["created"]) == 16
    assert len(emitted_values) == 18
    assert len(set(emitted_values)) == 17
    assert beacon["operator_rappid"] == estate["owner"]["rappid"]

    accounting = evidence["occurrence_accounting"]
    assert accounting["estate_json"] == {
        "owner_rappid_occurrences": 1,
        "created_rappid_occurrences": 16,
        "subtotal": 17,
    }
    assert accounting["network_beacon"] == {
        "operator_rappid_occurrences": 1,
        "subtotal": 1,
    }
    assert accounting["total_provisional_emitted_occurrences"] == 18
    assert accounting["distinct_baseline_identifier_values"] == 17
    assert accounting["lookup_records"] == 17
    assert accounting["distinct_source_repository_paths"] == 16
    assert accounting["resolved_lookup_records"] == 16
    assert accounting["resolved_distinct_public_source_paths"] == 15
    assert accounting["unresolved_lookup_records"] == 1


def test_evidence(evidence: dict[str, object]) -> list[str]:
    assert evidence["disposition"] == "non-authoritative-observation"
    assert evidence["authoritative"] is False
    assert evidence["can_establish_identity_mint_authorization_registry_or_trust"] is False
    assert evidence["authority"]["commit"] == AUTHORITY_COMMIT
    assert evidence["authority"]["sha256"] == AUTHORITY_SHA256
    assert evidence["collection"]["moving_ref_policy"].startswith(
        "refs/heads/main was discovery-only"
    )
    observed_utc = evidence["collection"]["observed_utc"]
    assert UTC_RE.fullmatch(observed_utc)

    lookups = evidence["lookups"]
    assert len(lookups) == 17
    assert len({item["lookup_id"] for item in lookups}) == 17
    expected_occurrences = {
        "estate.json#/owner/rappid",
        ".well-known/rapp-network.json#/operator_rappid",
        *(f"estate.json#/created/{index}/rappid" for index in range(16)),
    }
    actual_occurrences = [
        occurrence
        for item in lookups
        for occurrence in item["baseline_occurrences"]
    ]
    assert len(actual_occurrences) == 18
    assert set(actual_occurrences) == expected_occurrences
    assert len(actual_occurrences) == len(set(actual_occurrences))

    resolved_urls: list[str] = []
    unresolved = 0
    resolved_repositories: set[tuple[str, str]] = set()
    for item in lookups:
        assert set(item).isdisjoint(
            {"rappid", "identity_value", "record", "record_contents"}
        )
        source = item["source"]
        observation = item["observation"]
        assessment = item["candidate_assessment"]
        assert source["path"] == "rappid.json"
        assert source["discovery_ref"] == "refs/heads/main"
        assert source["discovery_ref_role"] == "discovery-only"
        assert observation["observed_utc"] == observed_utc
        assert assessment["trust_promotion"] is False
        assert assessment["owner_authorization"] in {
            "not-established",
        }
        assert assessment["registry_acceptance"] == "not-established"

        if observation["status"] == "resolved-public":
            repository = source["repository"]
            commit = observation["resolved_commit"]
            assert PUBLIC_REPOSITORY_RE.fullmatch(repository)
            assert COMMIT_RE.fullmatch(commit)
            assert observation["http_status"] == 200
            assert isinstance(observation["bytes"], int) and observation["bytes"] > 0
            assert SHA256_RE.fullmatch(observation["sha256"])
            assert observation["freshness"] == "point-in-time-only"
            assert assessment["section_6_1_grammar"] is True
            assert assessment["mint_provenance"] == "not-established"
            expected_url = (
                f"https://raw.githubusercontent.com/{repository}/{commit}/"
                f"{source['path']}"
            )
            assert observation["pinned_url"] == expected_url
            resolved_urls.append(expected_url)
            resolved_repositories.add((repository, source["path"]))
        else:
            unresolved += 1
            assert observation["status"] == "unresolved-publicly"
            assert source["repository"] is None
            assert source["repository_disposition"] == (
                "withheld-non-public-baseline-locator"
            )
            assert observation["resolved_commit"] is None
            assert observation["pinned_url"] is None
            assert observation["http_status"] == 404
            assert observation["bytes"] is None
            assert observation["sha256"] is None
            assert observation["freshness"] == "unresolved-at-observation"
            assert assessment["section_6_1_grammar"] is None
            assert assessment["mint_provenance"] == "not-observed"

    assert len(resolved_urls) == 16
    assert len(set(resolved_urls)) == 15
    assert len(resolved_repositories) == 15
    assert unresolved == 1
    return sorted(set(resolved_urls))




def hive_text_sha256(raw: bytes) -> str:
    """The Hive hash rule: SHA-256 of the UTF-8 text with LF line ends, in NFC."""
    text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(unicodedata.normalize("NFC", text).encode("utf-8")).hexdigest()


def test_estate(
    estate: dict[str, object],
    manifests: dict[str, dict[str, object]] | None,
    pins: dict[str, object] | None,
) -> list[tuple[str, str]]:
    assert set(estate) == ESTATE_MEMBERS
    assert estate["schema"] == ESTATE_SCHEMA
    assert estate["owner"] == {"rappid": OPERATOR_RAPPID, "github": "kody-w"}
    owner_match = RAPPID_RE.fullmatch(OPERATOR_RAPPID)
    assert owner_match and owner_match.group(1) == estate["owner"]["github"]
    assert SECOND_UTC_RE.fullmatch(estate["updated_at"])
    assert estate["member"] == []

    created = estate["created"]
    assert len(created) == EXPECTED_DOORS
    rappids = [entry["rappid"] for entry in created]
    assert rappids == sorted(rappids) and len(set(rappids)) == len(rappids)
    for entry in created:
        assert set(entry) == ENTRY_MEMBERS, entry
        match = RAPPID_RE.fullmatch(entry["rappid"])
        assert match and match.group(1) == "kody-w", entry
        assert entry["rappid"] != OPERATOR_RAPPID
        assert SECOND_UTC_RE.fullmatch(entry["added_at"]), entry
        assert entry["via"] in ENTRY_VIA, entry
        assert entry["added_at"] == CRAWL_FINISHED_UTC and entry["via"] == "scan"

    def bound(manifest_hash: str) -> set[str]:
        return {
            component["rappid"]
            for component in manifests[manifest_hash]["components"]
            if component["rappid"] is not None
        }

    if pins is not None:
        scanned = {p["rappid_json"] for p in pins["pins"].values() if p.get("rappid_json")}
        scanned |= {e["rappid_json"] for e in pins["not_in_lts"].values() if e.get("rappid_json")}
        assert set(rappids) == scanned, "created[] is every station's valid rappid.json (lts-pins.json rappid_json)"
    if manifests is not None:
        assert bound(CHANNEL_MANIFESTS["newest"]) <= set(rappids)
        assert bound(CHANNEL_MANIFESTS["rapp1-lts"]) <= bound(CHANNEL_MANIFESTS["newest"])

    hives = estate["hives"]
    assert isinstance(hives, list) and len(hives) == 1
    hive = hives[0]
    assert set(hive) == set(HIVE_ROOT), "a hives[] entry has exactly five members (proposal 0020 D3)"
    assert {key: hive[key] for key in HIVE_ROOT} == HIVE_ROOT
    assert re.fullmatch(r"[0-9a-f]{32}", hive["hive"])
    if pins is not None:
        assert pins["portfolio"]["commit"] == hive["commit"]
        assert pins["pins"]["kody-w/rapp-hive-public"]["commit"] == hive["commit"]
    return [
        (f"{hive['root']}{hive['commit']}/PUBLISHED.md", hive["published_sha256"]),
    ]


def beacon_fields(beacon: dict[str, object]) -> set[str]:
    fields: set[str] = set()
    for key, value in beacon.items():
        if key in {"protocol", "discovery"}:
            assert isinstance(value, dict), key
            fields.update(f"{key}.{inner}" for inner in value)
        else:
            fields.add(key)
    return fields


def test_beacon(
    beacon: dict[str, object],
    estate: dict[str, object],
    authority: dict[str, object],
) -> tuple[list[tuple[str, bytes]], list[tuple[str, str]]]:
    assert beacon_fields(beacon) == BEACON_FIELDS
    # tools/sniff_network.py keeps a beacon only with one of its two beacon
    # schemas and an exact RAPP/1 6.1 operator_rappid, and honors indexable.
    assert beacon["schema"] == BEACON_SCHEMA
    assert beacon["operator_rappid"] == OPERATOR_RAPPID == estate["owner"]["rappid"]
    assert RAPPID_RE.fullmatch(beacon["operator_rappid"])
    assert beacon["github"] == estate["owner"]["github"] == "kody-w"
    match = ESTATE_URL_RE.fullmatch(beacon["estate_url"])
    assert match, beacon["estate_url"]
    commit = match.group(1)
    assert is_ancestor_of_head(commit)
    estate_raw = (ROOT / "estate.json").read_bytes()
    assert git_bytes(commit, "estate.json") == estate_raw, (
        "the beacon must pin the current estate.json bytes"
    )
    assert beacon["grail_url"] == GRAIL_URL
    protocol = beacon["protocol"]
    assert protocol["spec_version"] == "rapp/1"
    assert protocol["estate_schema"] == ESTATE_SCHEMA == estate["schema"]
    assert protocol["implements"] == BEACON_IMPLEMENTS
    assert protocol["spec_url"] == authority["raw_url"]
    discovery = beacon["discovery"]
    assert discovery["indexable"] is True
    assert discovery["consent"] == "public-discovery-ok"
    assert discovery["federation_hints"] == []
    # Article XLVIII values carried forward from the last published beacon.
    published = baseline_json(".well-known/rapp-network.json")
    for key in (
        "private_estate_pointer",
        "private_estate_commitment",
        "private_door_count",
    ):
        assert beacon[key] == published[key], key
    assert beacon["private_estate_pointer"] == PRIVATE_ESTATE_POINTER
    assert SHA256_RE.fullmatch(beacon["private_estate_commitment"])
    assert type(beacon["private_door_count"]) is int
    assert SECOND_UTC_RE.fullmatch(beacon["minted_at"])
    # The Hive root is reached only through estate.json hives[] (proposal 0020, D3).
    serialized = json.dumps(beacon)
    assert "hives" not in serialized and "rapp-hive-public" not in serialized
    return (
        [(beacon["estate_url"], estate_raw)],
        [(protocol["spec_url"], AUTHORITY_SHA256)],
    )


def test_status_pages() -> None:
    status = (ROOT / "RAPP1_STATUS.md").read_text(encoding="utf-8")
    current = " ".join(status.split(HISTORICAL_HEADING, 1)[0].split())
    for phrase in (
        "## Where things stand on 2026-09-26",
        "RAPP proposal 0020 (a draft that the owner has not accepted",
        "Nothing is signed.",
        "Network acceptance awaits the owner's signed registry",
        "registry_seq 3",
        "the quarantine was live",
        "## The estate inventory (`estate.json`)",
        "that RAPP proposal 0020 proposes",
        "## How the draft was checked",
        "Before signing, accept RAPP proposal 0020 (pull request #133) with its",
        "this branch is not merged as drafted",
        "a `grail-kernel` entry for each release scope",
        "Have the estate kit add one status commit",
        "without rewriting it (fast-forward or a merge commit, never a squash or a rebase)",
        "by then registry_seq 3 is published and covers the beacon, as D2 asks",
        "The publication is drafted in steps.",
        "## The beacon (`.well-known/rapp-network.json`)",
        "carried forward, not recomputed",
        "compare its `computed_commitment` with this beacon's value",
        "Both are `null` on RAPP `main` today",
        "## Release manifests (candidate)",
        "RAPP/1 rev-17 is a draft and not in force",
        "registry_seq 3 covers the beacon.",
        "A manifest never pins the commit that carries it",
    ):
        assert phrase in current, phrase
    for manifest_hash in RELEASES:
        assert f"releases/{manifest_hash}.json" in current

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    html_text = " ".join(html.split())
    for phrase in (
        "Drafted — nothing is signed",
        "The publication is drafted.",
        "a draft that the owner has not accepted",
        "Before signing, accept or refuse RAPP proposal 0020",
        "Nothing is signed.",
        "awaits the owner's signed registry",
        "registry_seq 3",
        "Estate inventory (drafted)",
        "History: the 2026-07-17 quarantine",
        "Beacon (drafted)",
        "Release manifests (candidate)",
        "Its release pins cover this beacon",
    ):
        assert phrase in html_text, phrase
    for forbidden in (
        "<script",
        "onerror=",
        "onclick=",
        "innerHTML",
        "fetch(",
        "navigator.",
        'target="_blank"',
        "javascript:",
    ):
        assert forbidden not in html


OWNER_ACTION_IDS = [
    "verify-private-estate-commitment",
    "accept-proposal-0020",
    "sign-registry-seq-3",
    "record-post-signing-status",
    "merge-without-rewriting",
    "accept-in-rapp-seed",
]


def test_owner_actions(actions: dict[str, object]) -> None:
    assert actions["status"] == "blocked-on-owner"
    assert actions["authoritative"] is False
    assert actions["can_mint_reanchor_sign_or_accept"] is False
    blockers = actions["blockers"]
    assert [blocker["id"] for blocker in blockers] == [
        "rapp1-identity-authorization-and-registry",
        "rapp1-distributed-hive-activation",
    ]
    for blocker in blockers:
        assert blocker["state"] == "open"
        assert blocker["owner_inputs"]
        assert all(value is None for value in blocker["owner_inputs"].values())
    activation = blockers[1]
    assert activation["drafted_on_branch"] == "experimental/rapp1-distributed-hive"
    assert "registry_seq 3" in activation["why"]
    assert "proposal 0020 (a draft" in activation["why"]
    assert [item["id"] for item in activation["required_actions"]] == OWNER_ACTION_IDS
    action = {item["id"]: item["action"] for item in activation["required_actions"]}
    assert "grail-kernel entry for each release scope" in action["sign-registry-seq-3"]
    assert "covers the beacon" in action["sign-registry-seq-3"]
    assert "not merged as drafted" in action["accept-proposal-0020"]
    assert action["accept-proposal-0020"].startswith("Before signing")
    assert "tag the commit the release pins name" in action["sign-registry-seq-3"]
    assert action["merge-without-rewriting"].startswith(
        "Only after proposal 0020 is accepted with the recommended D2 and D3"
    )
    assert "never a squash or a rebase" in action["merge-without-rewriting"]
    assert "merged_commit" not in activation["owner_inputs"]
    assert "owner-gated" in action["accept-in-rapp-seed"]
    assert "covers the beacon" in action["accept-in-rapp-seed"]
    assert "computed_commitment" in activation["required_actions"][0]["action"]
    tests = {item["id"]: item["assertion"] for item in activation["acceptance_tests"]}
    assert "covers the beacon" in tests["release-pins-cover-the-beacon"]


def test_authority(pin: dict[str, object]) -> None:
    assert pin["commit"] == AUTHORITY_COMMIT
    assert pin["bytes"] == 41952
    assert pin["sha256"] == AUTHORITY_SHA256
    assert pin["authenticated_registry_acceptance"] is False


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "rapp-estate-publication-test"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        assert response.status == 200, url
        return response.read()


def verify_publication_online(
    pinned: list[tuple[str, bytes]], hashed: list[tuple[str, str]]
) -> None:
    for url, expected in pinned:
        assert fetch(url) == expected, url
    for url, expected_sha256 in hashed:
        raw = fetch(url)
        if url.endswith("/PUBLISHED.md"):
            assert hive_text_sha256(raw) == expected_sha256, url
            frontmatter = raw.decode("utf-8").split("\n---\n", 1)[0]
            assert f"\nhive: {HIVE_ROOT['hive']}" in frontmatter, url
        else:
            assert hashlib.sha256(raw).hexdigest() == expected_sha256, url


def verify_pinned_sources_online(
    evidence: dict[str, object], resolved_urls: list[str]
) -> None:
    by_url = {
        item["observation"]["pinned_url"]: item["observation"]
        for item in evidence["lookups"]
        if item["observation"]["status"] == "resolved-public"
    }
    for url in resolved_urls:
        request = urllib.request.Request(
            url, headers={"User-Agent": "rapp-estate-publication-test"}
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            assert response.status == 200
        observation = by_url[url]
        assert len(raw) == observation["bytes"], url
        assert hashlib.sha256(raw).hexdigest() == observation["sha256"], url


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--online",
        action="store_true",
        help=(
            "Refetch immutable public evidence URLs and this publication's "
            "commit-pinned URLs, and verify bytes."
        ),
    )
    args = parser.parse_args()

    json_paths = sorted(
        path
        for path in ROOT.rglob("*.json")
        if ".git" not in path.parts
        and str(path.relative_to(ROOT)) not in RELEASE_FILES
    )
    documents = {
        str(path.relative_to(ROOT)): load_json(path) for path in json_paths
    }
    expected_json = {
        ".well-known/rapp-network.json",
        "RAPP1_AUTHORITY.json",
        "RAPP1_EVIDENCE.json",
        "RAPP1_OWNER_ACTIONS.json",
        "estate.json",
        *({"lts-pins.json"} if STAGE >= 4 else set()),
    }
    assert set(documents) == expected_json

    evidence = documents["RAPP1_EVIDENCE.json"]
    test_static_tree()
    test_historical_record(documents["RAPP1_OWNER_ACTIONS.json"])
    test_baseline_accounting(evidence)
    resolved_urls = test_evidence(evidence)
    pinned: list[tuple[str, bytes]] = []
    hashed: list[tuple[str, str]] = []
    manifests = test_release_manifests() if STAGE >= 3 else None
    pins = documents["lts-pins.json"] if STAGE >= 4 else None
    if STAGE >= 4:
        pinned += test_lts_pins(pins, manifests)
    hashed += test_estate(documents["estate.json"], manifests, pins)
    if STAGE >= 2:
        beacon_pinned, beacon_hashed = test_beacon(
            documents[".well-known/rapp-network.json"],
            documents["estate.json"],
            documents["RAPP1_AUTHORITY.json"],
        )
        pinned += beacon_pinned
        hashed += beacon_hashed
    else:
        assert (ROOT / BEACON_PATH).read_bytes() == git_bytes(QUARANTINE_COMMIT, BEACON_PATH), (
            "the beacon is still the quarantine status document at this step"
        )
    test_status_pages()
    test_owner_actions(documents["RAPP1_OWNER_ACTIONS.json"])
    test_authority(documents["RAPP1_AUTHORITY.json"])
    if args.online:
        verify_pinned_sources_online(evidence, resolved_urls)
        verify_publication_online(pinned, hashed)

    mode = "offline+online" if args.online else "offline"
    print(
        f"PASS publication tests ({mode}, step {STAGE} of 4): 18 occurrences, 17 lookups; "
        f"{len(manifests or {})} release manifests; "
        f"estate.json {len(documents['estate.json']['created'])} doors, "
        f"{len(documents['estate.json']['hives'])} Hive root"
        + (f"; beacon {documents['.well-known/rapp-network.json']['schema']}" if STAGE >= 2 else "")
        + ("; lts-pins.json prepared-unsigned" if STAGE >= 4 else "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
