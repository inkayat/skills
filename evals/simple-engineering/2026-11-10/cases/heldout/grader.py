"""Usage: python3 grader.py /absolute/path/to/solver/fixture"""
import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class HiddenBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / "input.json"
        self.output = Path(self.tmp.name) / "output.data"
        self.events = [
            {"id": 901, "actor": "private@example.test", "action": "internal event", "internal": True},
            {"id": 12, "actor": "Zoë@example.test", "action": '=run("東京")\nnext\rline'},
            {"id": 13, "actor": "+person@example.test", "action": "@formula,\tvalue"},
            {"id": 14, "actor": "last@example.test", "action": "ordinary"},
        ]
        self.source.write_text(json.dumps(self.events), encoding="utf-8")

    def export(self, **options):
        return MODULE.export_events(self.source, self.output, **options)

    def read_jsonl(self):
        raw = self.output.read_bytes()
        self.assertTrue(not raw or raw.endswith(b"\n"), "nonempty JSONL needs a final newline")
        lines = raw.decode("utf-8").splitlines()
        return [json.loads(line) for line in lines]

    def cli(self, *options):
        return subprocess.run([sys.executable, str(TARGET / "audit_export.py"),
                               str(self.source), str(self.output), *options],
                              text=True, capture_output=True, timeout=10)

    def test_jsonl_default_privacy_types_and_round_trip(self):
        self.assertEqual(self.export(format="jsonl"), 3)
        rows = self.read_jsonl()
        self.assertEqual(rows, [dict(id=e["id"], actor="[redacted]", action=e["action"])
                                for e in self.events[1:]])
        self.assertTrue(all(type(row["id"]) is int for row in rows))
        self.assertNotIn(b"@example.test", self.output.read_bytes())

    def test_jsonl_selected_field_order_and_explicit_options(self):
        self.assertEqual(self.export(format="jsonl", fields=("action", "actor", "id"),
                                     include_internal=True, show_actors=True, limit=2), 2)
        rows = self.read_jsonl()
        self.assertEqual(rows, [{k: e[k] for k in ("action", "actor", "id")}
                                for e in self.events[:2]])
        self.assertEqual([list(row) for row in rows], [["action", "actor", "id"]] * 2)

    def test_jsonl_limit_is_after_filtering_and_projection_is_exact(self):
        self.assertEqual(self.export(format="jsonl", fields=("id",), limit=1), 1)
        self.assertEqual(self.read_jsonl(), [{"id": 12}])

    def test_jsonl_zero_limit_is_empty(self):
        self.assertEqual(self.export(format="jsonl", limit=0), 0)
        self.assertEqual(self.output.read_bytes(), b"")

    def test_jsonl_no_eligible_events_is_empty(self):
        self.source.write_text(json.dumps(self.events[:1]), encoding="utf-8")
        self.assertEqual(self.export(format="jsonl"), 0)
        self.assertEqual(self.output.read_bytes(), b"")

    def test_jsonl_does_not_apply_csv_escaping(self):
        values = ["=x", "+x", "-x", "@x", "\tx", "\rx", 'quote"\\\n🌍']
        self.source.write_text(json.dumps([{"id": i, "actor": value, "action": value}
                                          for i, value in enumerate(values)]), encoding="utf-8")
        self.export(format="jsonl", show_actors=True)
        self.assertEqual(self.read_jsonl(), json.loads(self.source.read_text()))

    def test_explicit_csv_preserves_formula_safety(self):
        values = ["=x", "+x", "-x", "@x", "\tx", "\rx", "ordinary"]
        self.source.write_text(json.dumps([{"id": i, "actor": value, "action": value}
                                          for i, value in enumerate(values)]), encoding="utf-8")
        self.assertEqual(self.export(format="csv", show_actors=True), len(values))
        with self.output.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        expected = ["'" + value for value in values[:-1]] + values[-1:]
        self.assertEqual([row["actor"] for row in rows], expected)
        self.assertEqual([row["action"] for row in rows], expected)

    def test_default_csv_contract_independently(self):
        self.assertEqual(self.export(fields=("action", "id"), limit=1), 1)
        with self.output.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows, [{"action": "'" + self.events[1]["action"], "id": "12"}])
        self.assertEqual(list(rows[0]), ["action", "id"])

    def test_jsonl_overwrite_requires_opt_in(self):
        self.output.write_bytes(b"keep original\n")
        with self.assertRaises(FileExistsError):
            self.export(format="jsonl")
        self.assertEqual(self.output.read_bytes(), b"keep original\n")
        self.assertEqual(self.export(format="jsonl", overwrite=True, limit=1), 1)
        self.assertEqual(self.read_jsonl()[0]["id"], 12)

    def test_jsonl_cannot_overwrite_source(self):
        before = self.source.read_bytes()
        with self.assertRaises(ValueError):
            MODULE.export_events(self.source, self.source.parent / "." / self.source.name,
                                 format="jsonl", overwrite=True)
        self.assertEqual(self.source.read_bytes(), before)

    def test_invalid_formats_never_write(self):
        for bad_format in ("yaml", "JSONL", "", None):
            for existing in (False, True):
                with self.subTest(format=bad_format, existing=existing):
                    if self.output.exists():
                        self.output.unlink()
                    if existing:
                        self.output.write_bytes(b"original")
                    with self.assertRaises(ValueError):
                        self.export(format=bad_format, overwrite=True)
                    if existing:
                        self.assertEqual(self.output.read_bytes(), b"original")
                    else:
                        self.assertFalse(self.output.exists())

    def test_jsonl_invalid_options_never_write(self):
        invalid = ({"fields": ()}, {"fields": ("id", "id")}, {"fields": ("internal",)},
                   {"limit": -1}, {"limit": True}, {"limit": 1.5})
        for options in invalid:
            for existing in (False, True):
                with self.subTest(options=options, existing=existing):
                    if self.output.exists():
                        self.output.unlink()
                    if existing:
                        self.output.write_bytes(b"original")
                    with self.assertRaises(ValueError):
                        self.export(format="jsonl", overwrite=True, **options)
                    if existing:
                        self.assertEqual(self.output.read_bytes(), b"original")
                    else:
                        self.assertFalse(self.output.exists())

    def test_jsonl_invalid_source_never_writes(self):
        invalid_sources = ["not json", "{}", "[null]",
                           '[{"id": true, "actor": "a", "action": "b"}]',
                           '[{"id": 1, "actor": 9, "action": "b"}]',
                           '[{"id": 1, "actor": "a", "action": "b", "internal": "yes"}]']
        for source_text in invalid_sources:
            for existing in (False, True):
                with self.subTest(source=source_text, existing=existing):
                    self.source.write_text(source_text, encoding="utf-8")
                    if self.output.exists():
                        self.output.unlink()
                    if existing:
                        self.output.write_bytes(b"original")
                    with self.assertRaises(ValueError):
                        self.export(format="jsonl", overwrite=True)
                    if existing:
                        self.assertEqual(self.output.read_bytes(), b"original")
                    else:
                        self.assertFalse(self.output.exists())

    def test_cli_jsonl_options_and_count(self):
        result = self.cli("--format", "jsonl", "--fields", "actor,id", "--include-internal",
                          "--show-actors", "--limit", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Exported 2 events\n")
        rows = self.read_jsonl()
        self.assertEqual(rows, [{"actor": e["actor"], "id": e["id"]} for e in self.events[:2]])
        self.assertEqual([list(row) for row in rows], [["actor", "id"]] * 2)
        result = self.cli("--format", "jsonl", "--limit", "0", "--overwrite")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Exported 0 events\n")
        self.assertEqual(self.output.read_bytes(), b"")

    def test_cli_explicit_csv_and_bad_format(self):
        result = self.cli("--format", "csv", "--limit", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        before = self.output.read_bytes()
        result = self.cli("--format", "xml", "--overwrite")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.output.read_bytes(), before)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: grader.py TARGET_FIXTURE_DIRECTORY")
    TARGET = Path(sys.argv[1]).resolve()
    spec = importlib.util.spec_from_file_location("graded_audit_export", TARGET / "audit_export.py")
    MODULE = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(MODULE)
    sys.path.insert(0, str(TARGET))
    suite = unittest.TestSuite([
        unittest.defaultTestLoader.discover(str(TARGET), pattern="test_*.py"),
        unittest.defaultTestLoader.loadTestsFromTestCase(HiddenBehaviorTests),
    ])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
