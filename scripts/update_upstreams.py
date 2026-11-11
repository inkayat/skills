#!/usr/bin/env python3
"""Refresh only this repository's declared upstream tree; never install skills."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import stat
import subprocess
import sys
from urllib.parse import quote, unquote, urlsplit


MAX_FILE = 2 << 20
MAX_RESPONSE = 8 << 20
MAX_TOTAL = 32 << 20
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
LEGAL = re.compile(r"(?:licen[cs]e|notice|copying|copyright)(?:\.[^/]+)?\Z", re.I)
INSTRUCTIONS = {"agents.md", "agents.override.md", "claude.md"}


class Refusal(Exception):
    def __init__(self, code, detail):
        self.code, self.detail = code, detail
        super().__init__(detail)


def require(condition, code, detail):
    if not condition:
        raise Refusal(code, detail)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def blob_id(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def safe_path(value):
    require(isinstance(value, str) and 0 < len(value) <= 512, "unsafe_path", "Invalid relative path")
    parts = value.split("/")
    require(not any(p in ("", ".", "..", ".git", ".hg", ".svn") for p in parts)
            and "\\" not in value and ":" not in value
            and not any(ord(c) < 32 or ord(c) == 127 for c in value),
            "unsafe_path", f"Unsafe relative path: {value!r}")
    return value


def plain(path, limit=MAX_RESPONSE):
    require(not path.is_symlink(), "unsafe_path", f"Symbolic link refused: {path}")
    require(path.is_file() and stat.S_ISREG(path.stat().st_mode), "local_drift", f"Not a plain file: {path}")
    require(path.stat().st_size <= limit, "unsupported_source", f"File exceeds bound: {path}")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, "unsupported_source", f"File exceeds bound: {path}")
    return data


def json_bytes(data):
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()


def load_manifest(root):
    raw = plain(root / "upstreams.json")
    config = json.loads(raw)
    require(config["schema"] == 1 and isinstance(config["sources"], list) and config["sources"],
            "invalid_manifest", "Expected schema 1 and nonempty sources")
    ids, repositories = set(), set()
    for source in config["sources"]:
        sid, repo = source["id"], source["repository"]
        require(isinstance(sid, str) and re.fullmatch(r"[a-z][a-z0-9-]{0,63}", sid)
                and sid not in ids, "invalid_manifest", "Invalid or duplicate source ID")
        require(isinstance(repo, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*", repo)
                and repo.casefold() not in repositories and type(source["repository_id"]) is int
                and source["repository_id"] > 0, "invalid_manifest", "Invalid repository identity")
        ids.add(sid)
        repositories.add(repo.casefold())
        ref = source["ref"]
        require(isinstance(ref, str) and 0 < len(ref) <= 200 and not any(ord(c) < 32 for c in ref),
                "invalid_manifest", "Invalid tracking ref")
        require(isinstance(source["include"], list) and source["include"] and source["skills"],
                "invalid_manifest", "Selection and entrypoints are required")
        for path in [*source["include"], *source["skills"], *source["terms"]["files"]]:
            safe_path(path)
        require(source["terms"]["files"] and all(isinstance(h, str) and HEX64.fullmatch(h)
                for h in source["terms"]["files"].values()), "invalid_manifest", "Reviewed legal-file hashes required")
        require(set(source["terms"]["skill_headers"]) == set(source["skills"]),
                "invalid_manifest", "Every entrypoint needs a reviewed license-header value")
    return config, digest(raw)


def load_lock(root):
    path = root / "upstreams.lock.json"
    require(not path.is_symlink(), "unsafe_path", "Lock must not be a symbolic link")
    if not path.exists():
        return None
    lock = json.loads(plain(path))
    require(lock["schema"] == 1 and lock["files"] and lock["sources"], "invalid_lock", "Incomplete lock")
    for path, entry in lock["files"].items():
        safe_path(path)
        require(path.split("/")[0] in lock["sources"] and entry["mode"] in ("100644", "100755")
                and HEX64.fullmatch(entry["sha256"]) and HEX40.fullmatch(entry["git_blob"]),
                "invalid_lock", "Invalid locked file identity")
    for source in lock["sources"].values():
        require(HEX40.fullmatch(source["commit"]) and HEX40.fullmatch(source["tree"]),
                "invalid_lock", "Full commit/tree pins required")
    return lock


def local_state(root, lock, allow_missing=False):
    tree = root / "upstream"
    require(not tree.is_symlink(), "unsafe_path", "Managed root is a symbolic link")
    if not tree.exists():
        require(lock is None or allow_missing, "local_drift", "Managed tree missing; explicit update --locked required to restore")
        return {}
    require(tree.is_dir() and lock is not None, "local_drift", "Existing tree has no ownership lock")
    expected = lock["files"]
    expected_dirs = {str(parent) for p in expected for parent in PurePosixPath(p).parents if str(parent) != "."}
    found, dirs = {}, set()
    for directory, children, files in os.walk(tree, followlinks=False):
        for name in [*children, *files]:
            path = Path(directory) / name
            require(not path.is_symlink(), "unsafe_path", f"Managed symbolic link refused: {path}")
        for name in children:
            dirs.add((Path(directory) / name).relative_to(tree).as_posix())
        for name in files:
            path = Path(directory) / name
            rel = path.relative_to(tree).as_posix()
            require(rel in expected, "local_drift", f"Unowned local file: {rel}")
            entry = expected[rel]
            data = plain(path, MAX_FILE)
            executable = bool(path.stat().st_mode & stat.S_IXUSR)
            require(digest(data) == entry["sha256"] and blob_id(data) == entry["git_blob"]
                    and executable == (entry["mode"] == "100755"),
                    "local_drift", f"Local edit or mode drift: {rel}")
            found[rel] = data
    require(set(found) == set(expected) and dirs == expected_dirs,
            "local_drift", "Missing files or unowned directories in managed tree")
    return found


def api_get(endpoint, offline):
    if offline is not None:
        path = offline / (digest(endpoint.encode()) + ".json")
        require(path.exists(), "missing_source", f"Offline response missing: {endpoint}; no network fallback")
        return json.loads(plain(path))
    # gh-axi's documented --jq/--full interface emits this lossless scalar wrapper.
    # No shell, arbitrary host, installer, provider call or credential-file access.
    with __import__("tempfile").TemporaryFile() as stdout, __import__("tempfile").TemporaryFile() as stderr:
        result = subprocess.run(["gh-axi", "api", endpoint, "--jq", "tojson|@base64", "--full"],
                                stdout=stdout, stderr=stderr, timeout=45, check=False)
        stdout.seek(0)
        raw = stdout.read(MAX_RESPONSE + 1)
        require(result.returncode == 0 and len(raw) <= MAX_RESPONSE, "api_error", f"GitHub GET failed or exceeded bound: {endpoint}")
    match = re.fullmatch(rb"api_response:\n  body: ([A-Za-z0-9+/=]+)\n  truncated: false\n?", raw)
    require(match is not None, "api_error", "Unsupported/truncated gh-axi serialization; inspect current gh-axi api --help")
    return json.loads(base64.b64decode(match[1], validate=True))


def fields(data):
    head = data[:8192].splitlines()
    require(head and head[0] == b"---", "invalid_skill", "Missing frontmatter")
    end = next((i for i, line in enumerate(head[1:], 1) if line in (b"---", b"...")), None)
    require(end is not None, "invalid_skill", "Frontmatter must close within first 8 KiB")
    lines = [line.decode("utf-8") for line in head[:end + 1]]
    out, i = {}, 1
    while i < end:
        match = re.fullmatch(r"([a-z][a-z-]*):\s*(.*)", lines[i])
        i += 1
        if not match or match[1] not in ("name", "description", "license"):
            continue
        key, value = match.groups()
        require(key not in out, "invalid_skill", f"Duplicate {key}")
        if value in ("|", ">", "|-", ">-", "|+", ">+"):
            block = []
            while i < end and (not lines[i] or lines[i][0].isspace()):
                block.append(lines[i].strip())
                i += 1
            value = " ".join(block).strip()
        elif value.startswith('"'):
            value = json.loads(value)
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1].replace("''", "'")
        out[key] = value
    require(isinstance(out.get("name"), str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", out["name"])
            and len(out["name"]) <= 64 and isinstance(out.get("description"), str)
            and 0 < len(out["description"]) <= 1024, "invalid_skill", "Invalid name/description")
    return out


def references(data):
    # Ignore code examples, including nested fences; validate actual file links.
    lines, fence = [], None
    for line in data.decode("utf-8").splitlines():
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= fence[1] and not match[2].strip():
                fence = None
        elif match:
            fence = (match[1][0], len(match[1]))
        else:
            lines.append(line)
    prose = "\n".join(lines)
    # Explicit relative resource paths in inline code also occur in Addy's skills.
    paths = re.findall(r"`((?:\.\.?/|references/)[^`\s]+\.[A-Za-z0-9]+)`", prose)
    prose = re.sub(r"(`+).*?\1", "", prose)
    paths += re.findall(r"!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)", prose)
    return paths


def validate_resources(config, contents):
    layout = []
    for source in config["sources"]:
        sid = source["id"]
        relative = {p[len(sid) + 1:]: data for p, data in contents.items() if p.startswith(sid + "/")}
        for path, data in relative.items():
            if not path.endswith((".md", ".mdx")):
                continue
            for link in references(data):
                url = urlsplit(link)
                if url.scheme or url.netloc or not url.path:
                    continue
                target = unquote(url.path)
                require(not target.startswith("/"), "unsafe_path", f"Absolute resource link in {sid}/{path}")
                target = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
                safe_path(target)
                require(target in relative or any(p.startswith(target + "/") for p in relative),
                        "missing_reference", f"Missing resource {sid}/{target} referenced by {path}")
        for path, name in source["skills"].items():
            require(path in relative, "missing_source", f"Missing entrypoint {sid}/{path}")
            header = fields(relative[path])
            require(header["name"] == name, "invalid_skill", f"Entrypoint name drift: {sid}/{path}")
            folder = posixpath.dirname(path)
            own = [p for p in relative if not folder or p.startswith(folder + "/")]
            # This is a source-layout observation, not a native-loader or behavior test.
            outside = []
            for link in references(relative[path]):
                url = urlsplit(link)
                if not url.scheme and not url.netloc and url.path:
                    target = posixpath.normpath(posixpath.join(folder, unquote(url.path)))
                    if folder and not target.startswith(folder + "/"):
                        outside.append(target)
            layout.append({"source": sid, "name": name, "path": path,
                           "folder_files": len(own), "folder_bytes": sum(len(relative[p]) for p in own),
                           "outside_folder_references": sorted(set(outside))})
    return layout


def make_plan(config, manifest_sha, old, local, offline, locked):
    contents, files, sources = {}, {}, {}
    for source in config["sources"]:
        sid, repo = source["id"], source["repository"]
        base = "/repos/" + repo
        metadata = api_get(base, offline)
        require(metadata["id"] == source["repository_id"] and metadata["full_name"].casefold() == repo.casefold(),
                "identity_mismatch", f"Repository identity changed: {repo}")
        require(not metadata.get("archived") and not metadata.get("disabled"), "unsupported_source", f"Source unavailable for refresh: {repo}")
        if locked:
            require(old is not None and sid in old["sources"], "invalid_lock", f"Missing pin: {sid}")
            pin = old["sources"][sid]
            require(pin["repository"] == repo and pin["repository_id"] == source["repository_id"],
                    "identity_mismatch", f"Locked repository differs: {sid}")
            ref = pin["commit"]
        else:
            ref = source["ref"]
        commit = api_get(base + "/commits/" + quote(ref, safe=""), offline)
        revision, tree_id = commit["sha"], commit["commit"]["tree"]["sha"]
        require(HEX40.fullmatch(revision) and HEX40.fullmatch(tree_id)
                and (not locked or revision == ref), "integrity_mismatch", f"Invalid resolved pin: {repo}")
        tree = api_get(base + "/git/trees/" + tree_id + "?recursive=1", offline)
        require(tree["sha"] == tree_id and tree["truncated"] is False, "unsupported_source", f"Missing/truncated tree: {repo}")
        entries = {}
        for entry in tree["tree"]:
            path = safe_path(entry["path"])
            require(path not in entries, "integrity_mismatch", f"Duplicate upstream path: {path}")
            entries[path] = entry
        for path in source["skills"]:
            require(path in entries, "missing_source", f"Missing entrypoint: {repo}/{path}")
        included = {p for p, entry in entries.items() if entry["type"] != "tree"
                    and any(p == root or p.startswith(root + "/") for root in source["include"])}
        require({p for p in included if posixpath.basename(p) == "SKILL.md"} == set(source["skills"]),
                "unsupported_source", f"Selected entrypoint set changed: {repo}")
        for root in source["include"]:
            require(root in entries or any(p.startswith(root + "/") for p in entries),
                    "missing_source", f"Missing selected path: {repo}/{root}")
        ancestors = {""}
        for root in source["include"]:
            ancestors.update(str(p) if str(p) != "." else "" for p in PurePosixPath(root).parents)
            if root in entries and entries[root]["type"] == "tree":
                ancestors.add(root)
        legal_dirs = tuple((posixpath.join(a, d) + "/").casefold()
                           for a in ancestors for d in ("LICENSES", "LICENCES"))
        legal = {p for p, entry in entries.items() if entry["type"] != "tree"
                 and (LEGAL.fullmatch(posixpath.basename(p))
                      or any(part.casefold() in ("licenses", "licences") for part in p.split("/")))
                 and (p in included or posixpath.dirname(p) in ancestors
                      or p.casefold().startswith(legal_dirs))}
        require(legal == set(source["terms"]["files"]), "terms_changed", f"Legal/NOTICE file set changed: {repo}")
        chosen = included | legal
        require(all(type(entries[p].get("size")) is int and 0 <= entries[p]["size"] <= MAX_FILE
                    for p in chosen), "unsupported_source", f"Invalid/oversized selected blob: {repo}")
        require(sum(map(len, contents.values())) + sum(entries[p]["size"] for p in chosen) <= MAX_TOTAL,
                "unsupported_source", "Selected content exceeds 32 MiB before blob retrieval")
        seen = {}
        for path in sorted(chosen):
            for parent in [PurePosixPath(path), *PurePosixPath(path).parents]:
                text = str(parent)
                require(seen.setdefault(text.casefold(), text) == text, "unsafe_path", f"Case collision: {repo}/{path}")
            require(PurePosixPath(path).name.casefold() not in INSTRUCTIONS, "unsafe_path", f"Project instruction file not imported: {path}")
            entry = entries[path]
            require(entry["type"] == "blob" and entry["mode"] in ("100644", "100755"),
                    "unsupported_source", f"Symlink/submodule/special file: {repo}/{path}")
            require(HEX40.fullmatch(entry["sha"]) and type(entry["size"]) is int and 0 <= entry["size"] <= MAX_FILE,
                    "unsupported_source", f"Invalid/oversized blob: {repo}/{path}")
            dest = sid + "/" + path
            data = local.get(dest)
            if data is None or blob_id(data) != entry["sha"]:
                response = api_get(base + "/git/blobs/" + entry["sha"], offline)
                require(response["encoding"] == "base64" and response["sha"] == entry["sha"],
                        "integrity_mismatch", f"Unexpected blob identity: {repo}/{path}")
                data = base64.b64decode("".join(response["content"].split()), validate=True)
                require(response["size"] == len(data), "integrity_mismatch", f"Blob size mismatch: {repo}/{path}")
            require(len(data) == entry["size"] and blob_id(data) == entry["sha"],
                    "integrity_mismatch", f"Blob integrity mismatch: {repo}/{path}")
            require(not data.startswith(b"version https://git-lfs.github.com/spec/v1\n"),
                    "unsupported_source", f"LFS material not supported: {repo}/{path}")
            contents[dest] = data
            files[dest] = {"sha256": digest(data), "git_blob": entry["sha"], "mode": entry["mode"]}
        actual_terms = {p: digest(contents[sid + "/" + p]) for p in legal}
        require(actual_terms == source["terms"]["files"], "terms_changed", f"License/NOTICE bytes changed: {repo}")
        for path, expected in source["terms"]["skill_headers"].items():
            require(sid + "/" + path in contents, "missing_source", f"Entrypoint not selected: {path}")
            require(fields(contents[sid + "/" + path]).get("license") == expected,
                    "terms_changed", f"Skill license header changed: {repo}/{path}")
        sources[sid] = {"repository": repo, "repository_id": source["repository_id"],
                        "commit": revision, "tree": tree_id, "ref": source["ref"]}
    layout = validate_resources(config, contents)
    lock = {"schema": 1, "manifest_sha256": manifest_sha, "sources": sources, "files": files}
    require(not locked or lock == old, "integrity_mismatch", "Locked reconstruction does not match exact lock/config")
    return lock, contents, layout


def install(root, old, lock, contents, locked):
    work = root / ".upstream-update"
    try:
        work.mkdir(mode=0o700)
    except FileExistsError:
        raise Refusal("busy", "Update/recovery directory exists; inspect it, never auto-remove it")
    previous, installed, committed = False, False, False
    try:
        require(load_lock(root) == old, "local_drift", "Lock changed while preparing update")
        local_state(root, old, allow_missing=locked)
        require(digest(plain(root / "upstreams.json")) == lock["manifest_sha256"],
                "local_drift", "Manifest changed while preparing update")
        next_tree = work / "next-tree"
        next_tree.mkdir()
        for rel, data in contents.items():
            path = next_tree / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            path.chmod(0o755 if lock["files"][rel]["mode"] == "100755" else 0o644)
        (work / "next-lock").write_bytes(json_bytes(lock))
        if old is not None:
            (work / "previous-lock").write_bytes(plain(root / "upstreams.lock.json"))
        if (root / "upstream").exists():
            os.replace(root / "upstream", work / "previous-tree")
            previous = True
        os.replace(next_tree, root / "upstream")
        installed = True
        os.replace(work / "next-lock", root / "upstreams.lock.json")
        committed = True
    except Exception:
        if installed:
            os.replace(root / "upstream", work / "failed-tree")
        if previous:
            os.replace(work / "previous-tree", root / "upstream")
        if (work / "previous-lock").exists():
            os.replace(work / "previous-lock", root / "upstreams.lock.json")
        shutil.rmtree(work)
        raise
    if committed:
        shutil.rmtree(work)
    # Interrupts leave recovery material in place. There is no auto-clean/retry.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["verify", "check", "update"])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--offline", type=Path, help="Read endpoint-SHA256 JSON snapshots only; never use network")
    parser.add_argument("--locked", action="store_true", help="Reconstruct exact existing lock; allows only wholly missing tree restoration")
    args = parser.parse_args()
    try:
        root = args.root.resolve(strict=True)
        require(not (root / ".upstream-update").exists() and not (root / ".upstream-update").is_symlink(),
                "busy", "Update/recovery material exists; inspect before continuing")
        config, manifest_sha = load_manifest(root)
        old = load_lock(root)
        require(not args.locked or args.command == "update", "invalid_manifest", "--locked applies only to update")
        local = local_state(root, old, allow_missing=args.locked)
        if args.command == "verify":
            require(old is not None and old["manifest_sha256"] == manifest_sha,
                    "invalid_lock", "Lock/config missing or changed; verification is not an update")
            layout = validate_resources(config, local)
            result = {"status": "verified", "remote_freshness_checked": False}
        else:
            new, contents, layout = make_plan(config, manifest_sha, old, local, args.offline, args.locked)
            changed = new != old or not (root / "upstream").exists()
            if args.command == "update" and changed:
                install(root, old, new, contents, args.locked)
            result = {"status": "update_available" if changed and args.command == "check" else "updated" if changed else "current"}
        result.update(sources=len(config["sources"]), skills=len(layout), files=len(local) if args.command == "verify" else len(contents), layout=layout)
        print(json.dumps(result, sort_keys=True))
        return 1 if result["status"] == "update_available" else 0
    except Refusal as error:
        print(json.dumps({"status": "refused", "error": error.code, "detail": error.detail}), file=sys.stderr)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "refused", "error": "unsupported_source", "detail": str(error)}), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
