"""Exercise real updater/filesystem behavior; only GitHub responses are fixtures."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import stat
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "update_upstreams.py"
BODY = b"---\nname: demo\ndescription: Use for fixture tasks.\nlicense: MIT\n---\nRead [guide](references/guide.md).\n"
GUIDE = b"A complete guide.\n"
TERMS = b"MIT License\nCopyright Fixture Author\nPermission granted for this fixture.\n"
COMMIT_A, COMMIT_B = "a" * 40, "c" * 40
TREE_A, TREE_B = "b" * 40, "d" * 40


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


class UpstreamTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root, self.api = self.base / "repo", self.base / "api"
        self.root.mkdir()
        self.api.mkdir()
        (self.root / "first-party").mkdir()
        (self.root / "first-party" / "mine.md").write_bytes(b"manual original\n")
        (self.root / "unrelated.txt").write_bytes(b"leave this alone\n")
        self.config = {"schema": 1, "sources": [{
            "id": "demo", "repository": "example/demo", "repository_id": 101,
            "ref": "main", "include": ["skills/demo"],
            "skills": {"skills/demo/SKILL.md": "demo"},
            "terms": {"files": {"LICENSE": sha(TERMS)},
                      "skill_headers": {"skills/demo/SKILL.md": "MIT"}},
        }]}
        self.write_config()
        self.files = {"skills/demo/SKILL.md": BODY,
                      "skills/demo/references/guide.md": GUIDE, "LICENSE": TERMS}
        self.executables = set()
        self.publish()

    def write_config(self):
        save(self.root / "upstreams.json", self.config)

    def response(self, endpoint, value):
        save(self.api / (sha(endpoint.encode()) + ".json"), value)

    def publish(self, commit=COMMIT_A, tree=TREE_A):
        self.response("/repos/example/demo", {"id": 101, "full_name": "example/demo",
                      "default_branch": "main", "archived": False, "disabled": False})
        record = {"sha": commit, "commit": {"tree": {"sha": tree}}}
        for ref in ("main", commit):
            self.response("/repos/example/demo/commits/" + ref, record)
        entries = []
        for path, data in self.files.items():
            oid = blob(data)
            entries.append({"path": path, "mode": "100755" if path in self.executables else "100644",
                            "type": "blob",
                            "sha": oid, "size": len(data)})
            self.response("/repos/example/demo/git/blobs/" + oid,
                          {"sha": oid, "size": len(data), "encoding": "base64",
                           "content": base64.b64encode(data).decode()})
        self.tree = {"sha": tree, "truncated": False, "tree": entries}
        self.tree_endpoint = "/repos/example/demo/git/trees/" + tree + "?recursive=1"
        self.response(self.tree_endpoint, self.tree)

    def command(self, command="update", *flags, expected=0, error=None):
        result = subprocess.run([sys.executable, str(SCRIPT), command, "--root", str(self.root),
                                 "--offline", str(self.api), *flags],
                                text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, expected, (result.stdout, result.stderr))
        try:
            output = json.loads(result.stdout if expected < 2 else result.stderr)
        except ValueError:
            self.fail(f"Updater did not return its structured result: {result.stdout!r} {result.stderr!r}")
        if error:
            self.assertEqual(output["error"], error)
        return output

    def snapshot(self):
        out = {}
        for p in self.root.rglob("*"):
            rel = p.relative_to(self.root).as_posix()
            if p.is_symlink():
                out[rel] = ("link", os.readlink(p))
            elif p.is_file():
                out[rel] = (p.read_bytes(), p.stat().st_mode & 0o777)
        return out

    def test_import_preserves_source_bytes_provenance_and_first_party(self):
        self.command()
        self.assertEqual((self.root / "upstream/demo/skills/demo/SKILL.md").read_bytes(), BODY)
        self.assertEqual((self.root / "upstream/demo/skills/demo/references/guide.md").read_bytes(), GUIDE)
        self.assertEqual((self.root / "upstream/demo/LICENSE").read_bytes(), TERMS)
        lock = json.loads((self.root / "upstreams.lock.json").read_text())
        self.assertEqual(lock["sources"]["demo"]["commit"], COMMIT_A)
        self.assertEqual(lock["sources"]["demo"]["repository_id"], 101)
        self.assertEqual(lock["files"]["demo/skills/demo/SKILL.md"]["sha256"], sha(BODY))
        self.assertEqual(lock["files"]["demo/skills/demo/SKILL.md"]["git_blob"], blob(BODY))
        self.assertEqual((self.root / "first-party/mine.md").read_bytes(), b"manual original\n")
        self.assertEqual((self.root / "unrelated.txt").read_bytes(), b"leave this alone\n")

    def test_idempotent_update_and_readonly_check_preserve_bytes_and_mtimes(self):
        self.command()
        before = self.snapshot()
        paths = [self.root / "upstreams.lock.json", self.root / "upstream/demo/skills/demo/SKILL.md"]
        times = [p.stat().st_mtime_ns for p in paths]
        self.assertEqual(self.command("check")["status"], "current")
        self.assertEqual(self.command()["status"], "current")
        self.assertEqual(self.snapshot(), before)
        self.assertEqual([p.stat().st_mtime_ns for p in paths], times)
        self.assertEqual(self.command("verify")["status"], "verified")

    def test_update_reports_new_pin_and_replaces_only_owned_content(self):
        self.command()
        self.files["skills/demo/references/guide.md"] = b"Revised guide.\n"
        self.files["skills/demo/extra.txt"] = b"New supporting material.\n"
        self.publish(COMMIT_B, TREE_B)
        before = self.snapshot()
        self.command("check", expected=1)
        self.assertEqual(self.snapshot(), before)
        self.command()
        self.assertEqual((self.root / "upstream/demo/skills/demo/references/guide.md").read_bytes(), b"Revised guide.\n")
        self.assertEqual((self.root / "upstream/demo/skills/demo/extra.txt").read_bytes(), b"New supporting material.\n")
        self.assertEqual(json.loads((self.root / "upstreams.lock.json").read_text())["sources"]["demo"]["commit"], COMMIT_B)
        self.assertEqual((self.root / "first-party/mine.md").read_bytes(), b"manual original\n")

    def test_upstream_removed_support_is_removed_only_when_unedited(self):
        self.command()
        self.files["skills/demo/SKILL.md"] = BODY.replace(b"Read [guide](references/guide.md).", b"Self contained.")
        del self.files["skills/demo/references/guide.md"]
        self.publish(COMMIT_B, TREE_B)
        self.command()
        self.assertFalse((self.root / "upstream/demo/skills/demo/references/guide.md").exists())
        self.command("verify")

    def test_locked_import_restores_missing_tree_at_exact_pin(self):
        self.command()
        before = self.snapshot()
        (self.root / "upstream").rename(self.base / "saved-upstream")
        self.files["skills/demo/references/guide.md"] = b"New upstream version.\n"
        self.publish(COMMIT_B, TREE_B)
        self.command("update", "--locked")
        self.assertEqual(self.snapshot(), before)

    def test_missing_local_tree_without_explicit_locked_import_is_drift(self):
        self.command()
        (self.root / "upstream").rename(self.base / "saved-upstream")
        before = self.snapshot()
        self.command(expected=2, error="local_drift")
        self.assertEqual(self.snapshot(), before)

    def test_local_content_mode_deletion_and_extra_file_are_preserved(self):
        self.command()
        path = self.root / "upstream/demo/skills/demo/SKILL.md"
        for kind in ("content", "mode", "missing", "extra"):
            with self.subTest(kind=kind):
                if kind == "content": path.write_bytes(b"manual edit\n")
                if kind == "mode": path.chmod(0o755)
                if kind == "missing": path.unlink()
                extra = self.root / "upstream/unrelated-manual.txt"
                if kind == "extra": extra.write_bytes(b"manual addition\n")
                before = self.snapshot()
                self.command(expected=2, error="local_drift")
                self.assertEqual(self.snapshot(), before)
                if kind == "extra": extra.unlink()
                path.write_bytes(BODY)
                path.chmod(0o644)

    def test_git_checkout_under_restrictive_umask_works_without_recovery_chmod(self):
        self.files["skills/demo/run.sh"] = b"#!/bin/sh\n"
        self.executables.add("skills/demo/run.sh")
        self.publish()
        self.command()
        tree = self.root / "upstream"
        script = tree / "demo/skills/demo/run.sh"
        plain_file = tree / "demo/skills/demo/SKILL.md"
        self.assertTrue(script.stat().st_mode & stat.S_IXUSR)

        def restrict():
            for p in tree.rglob("*"):
                if p.is_file():
                    p.chmod(0o700 if p == script else 0o600)

        def contents():
            return {rel: data for rel, (data, _) in self.snapshot().items()}

        restrict()
        before = self.snapshot()
        self.assertEqual(self.command("verify")["status"], "verified")
        self.assertEqual(self.command("check")["status"], "current")
        self.assertEqual(self.command()["status"], "current")
        self.assertEqual(self.snapshot(), before)

        self.files["skills/demo/references/guide.md"] = b"Revised guide.\n"
        self.publish(COMMIT_B, TREE_B)
        self.command()
        self.assertEqual((tree / "demo/skills/demo/references/guide.md").read_bytes(), b"Revised guide.\n")
        self.assertTrue(script.stat().st_mode & stat.S_IXUSR)
        self.assertFalse(plain_file.stat().st_mode & stat.S_IXUSR)
        self.assertEqual(self.command("verify")["status"], "verified")

        restrict()
        saved = contents()
        tree.rename(self.base / "saved-upstream")
        self.command("update", "--locked")
        self.assertEqual(self.command("verify")["status"], "verified")
        self.assertEqual(contents(), saved)
        self.assertEqual((self.root / "first-party/mine.md").read_bytes(), b"manual original\n")
        self.assertEqual((self.root / "unrelated.txt").read_bytes(), b"leave this alone\n")

        restrict()
        for victim, mode in ((script, 0o600), (plain_file, 0o700)):
            victim.chmod(mode)
            before = self.snapshot()
            self.command("verify", expected=2, error="local_drift")
            self.command(expected=2, error="local_drift")
            self.assertEqual(self.snapshot(), before)
            restrict()
        plain_file.write_bytes(b"manual edit\n")
        before = self.snapshot()
        self.command("verify", expected=2, error="local_drift")
        self.assertEqual(self.snapshot(), before)

    def test_local_symlink_escape_is_not_followed_or_overwritten(self):
        self.command()
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "secret").write_bytes(b"private sentinel\n")
        (self.root / "upstream").rename(self.base / "saved-upstream")
        (self.root / "upstream").symlink_to(outside, target_is_directory=True)
        self.command(expected=2, error="unsafe_path")
        self.assertTrue((self.root / "upstream").is_symlink())
        self.assertEqual((outside / "secret").read_bytes(), b"private sentinel\n")
        self.assertEqual(sorted(p.name for p in outside.iterdir()), ["secret"])

    def test_first_party_symlink_is_neither_followed_nor_modified(self):
        outside = self.base / "outside.txt"
        outside.write_bytes(b"outside original\n")
        (self.root / "first-party/link").symlink_to(outside)
        self.command()
        self.assertTrue((self.root / "first-party/link").is_symlink())
        self.assertEqual(outside.read_bytes(), b"outside original\n")

    def test_license_notice_and_skill_license_changes_require_review(self):
        self.command()
        original = dict(self.files)
        for kind in ("license", "notice", "header"):
            with self.subTest(kind=kind):
                self.files = dict(original)
                if kind == "license": self.files["LICENSE"] = TERMS + b"New restriction.\n"
                if kind == "notice": self.files["NOTICE"] = b"Required new notice.\n"
                if kind == "header": self.files["skills/demo/SKILL.md"] = BODY.replace(b"license: MIT", b"license: Proprietary")
                self.publish(COMMIT_B, TREE_B)
                before = self.snapshot()
                self.command(expected=2, error="terms_changed")
                self.assertEqual(self.snapshot(), before)

    def test_missing_entrypoint_missing_resource_and_truncated_tree_refuse(self):
        for kind, code in (("entry", "missing_source"), ("reference", "missing_reference"), ("truncated", "unsupported_source")):
            with self.subTest(kind=kind):
                original = dict(self.files)
                if kind == "entry": del self.files["skills/demo/SKILL.md"]
                if kind == "reference": del self.files["skills/demo/references/guide.md"]
                self.publish()
                if kind == "truncated":
                    self.tree["truncated"] = True
                    self.response(self.tree_endpoint, self.tree)
                before = self.snapshot()
                self.command(expected=2, error=code)
                self.assertEqual(self.snapshot(), before)
                self.files = original

    def test_repository_identity_and_blob_integrity_are_checked(self):
        for kind in ("identity", "blob"):
            with self.subTest(kind=kind):
                self.publish()
                if kind == "identity":
                    self.response("/repos/example/demo", {"id": 202, "full_name": "example/demo", "archived": False, "disabled": False})
                else:
                    self.response("/repos/example/demo/git/blobs/" + blob(BODY),
                                  {"sha": blob(BODY), "size": len(BODY), "encoding": "base64",
                                   "content": base64.b64encode(BODY.replace(b"fixture", b"corrupt")).decode()})
                before = self.snapshot()
                self.command(expected=2, error="identity_mismatch" if kind == "identity" else "integrity_mismatch")
                self.assertEqual(self.snapshot(), before)

    def test_remote_traversal_symlink_submodule_and_case_collision_refuse(self):
        for kind in ("traversal", "symlink", "submodule", "case", "instruction"):
            with self.subTest(kind=kind):
                self.publish()
                entry = next(e for e in self.tree["tree"] if e["path"].endswith("SKILL.md"))
                if kind == "traversal": entry["path"] = "../../first-party/mine.md"
                if kind == "symlink": entry["mode"] = "120000"
                if kind == "submodule": entry.update(mode="160000", type="commit")
                if kind == "case": self.tree["tree"].append(dict(entry, path="skills/demo/skill.md"))
                if kind == "instruction": self.tree["tree"].append(dict(entry, path="skills/demo/AGENTS.md"))
                self.response(self.tree_endpoint, self.tree)
                before = self.snapshot()
                self.command(expected=2, error="unsafe_path" if kind in ("traversal", "case", "instruction") else "unsupported_source")
                self.assertEqual(self.snapshot(), before)

    def test_manifest_traversal_and_lock_traversal_do_not_write_outside_tree(self):
        self.config["sources"][0]["include"] = ["../first-party"]
        self.write_config()
        self.command(expected=2, error="unsafe_path")
        self.config["sources"][0]["include"] = ["skills/demo"]
        self.write_config()
        self.command()
        lock_path = self.root / "upstreams.lock.json"
        lock = json.loads(lock_path.read_text())
        lock["files"]["../../outside.txt"] = next(iter(lock["files"].values()))
        save(lock_path, lock)
        before = self.snapshot()
        self.command(expected=2, error="unsafe_path")
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.base / "outside.txt").exists())

    def test_source_header_and_relative_reference_escape_are_rejected(self):
        for body, code in ((BODY.replace(b"name: demo", b"name: wrong-name"), "invalid_skill"),
                           (BODY.replace(b"Use for fixture tasks.", b"x" * 1025), "invalid_skill"),
                           (BODY.replace(b"references/guide.md", b"../../../../outside.md"), "unsafe_path")):
            with self.subTest(code=code):
                self.files["skills/demo/SKILL.md"] = body
                self.publish()
                before = self.snapshot()
                self.command(expected=2, error=code)
                self.assertEqual(self.snapshot(), before)

    def test_unknown_files_are_not_adopted_without_a_lock(self):
        (self.root / "upstream").mkdir()
        (self.root / "upstream/manual.txt").write_bytes(b"not yours\n")
        before = self.snapshot()
        self.command(expected=2, error="local_drift")
        self.assertEqual(self.snapshot(), before)

    def test_missing_offline_response_never_falls_back_to_network_or_current(self):
        self.command()
        (self.api / (sha(b"/repos/example/demo/commits/main") + ".json")).unlink()
        before = self.snapshot()
        self.command("check", expected=2, error="missing_source")
        self.assertEqual(self.snapshot(), before)

    def test_interrupted_update_is_reported_without_removing_recovery_material(self):
        self.command()
        recovery = self.root / ".upstream-update"
        recovery.mkdir()
        (recovery / "previous-tree").write_bytes(b"preserve recovery\n")
        before = self.snapshot()
        self.command(expected=2, error="busy")
        self.assertEqual(self.snapshot(), before)

    def test_new_nested_entrypoint_is_not_silently_imported(self):
        self.files["skills/demo/nested/SKILL.md"] = (
            BODY.replace(b"name: demo", b"name: unexpected")
                .replace(b"Read [guide](references/guide.md).", b"Self contained."))
        self.publish()
        before = self.snapshot()
        self.command(expected=2, error="unsupported_source")
        self.assertEqual(self.snapshot(), before)

    def test_ancestor_resource_outside_skill_folder_is_required_retained_and_reported(self):
        self.files["skills/demo/SKILL.md"] = BODY.replace(b"references/guide.md", b"../../references/standard.md")
        self.files["references/standard.md"] = b"Shared standard.\n"
        del self.files["skills/demo/references/guide.md"]
        self.publish()
        before = self.snapshot()
        self.command(expected=2, error="missing_reference")
        self.assertEqual(self.snapshot(), before)

        self.config["sources"][0]["include"] = ["skills/demo", "references/standard.md"]
        self.write_config()
        result = self.command()
        self.assertEqual((self.root / "upstream/demo/references/standard.md").read_bytes(), b"Shared standard.\n")
        self.assertEqual(result["layout"][0]["outside_folder_references"], ["references/standard.md"])
        self.assertEqual(self.command("verify")["status"], "verified")

    def test_ancestor_license_directory_requires_explicit_terms_review(self):
        self.files["LICENSES/third-party.txt"] = b"Additional legal terms.\n"
        self.publish()
        before = self.snapshot()
        self.command(expected=2, error="terms_changed")
        self.assertEqual(self.snapshot(), before)

    def test_utf8_body_crossing_header_read_bound_remains_valid(self):
        self.files["skills/demo/SKILL.md"] = BODY + b"x" * (8191 - len(BODY)) + "é".encode()
        self.publish()
        self.command()
        self.assertEqual((self.root / "upstream/demo/skills/demo/SKILL.md").read_bytes(),
                         self.files["skills/demo/SKILL.md"])

    def test_lowercase_instruction_filename_is_not_imported_on_case_insensitive_hosts(self):
        self.files["skills/demo/agents.md"] = b"Unapproved project instructions.\n"
        self.publish()
        before = self.snapshot()
        self.command(expected=2, error="unsafe_path")
        self.assertEqual(self.snapshot(), before)

    def test_aggregate_size_is_rejected_before_requesting_blob_contents(self):
        for index in range(17):
            self.tree["tree"].append({
                "path": f"skills/demo/asset-{index}.bin", "type": "blob",
                "mode": "100644", "sha": "e" * 40, "size": 2 << 20,
            })
        self.response(self.tree_endpoint, self.tree)
        before = self.snapshot()
        # No blob response exists: eager fetching would fail as missing_source.
        self.command(expected=2, error="unsupported_source")
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
