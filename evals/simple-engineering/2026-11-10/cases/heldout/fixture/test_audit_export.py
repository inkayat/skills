import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from audit_export import export_events


class ExistingExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / "events.json"
        self.output = Path(self.tmp.name) / "report.csv"
        self.events = [
            {"id": 1, "actor": "secret@example.test", "action": "internal", "internal": True},
            {"id": 2, "actor": "alice@example.test", "action": "=SUM(1,2)"},
            {"id": 3, "actor": "bob@example.test", "action": "café, opened"},
        ]
        self.source.write_text(json.dumps(self.events), encoding="utf-8")

    def read_rows(self):
        with self.output.open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_defaults_filter_redact_and_escape_csv(self):
        self.assertEqual(export_events(self.source, self.output), 2)
        self.assertEqual(self.read_rows(), [
            {"id": "2", "actor": "[redacted]", "action": "'=SUM(1,2)"},
            {"id": "3", "actor": "[redacted]", "action": "café, opened"},
        ])

    def test_options_and_limit_after_filtering(self):
        export_events(self.source, self.output, fields=("actor", "id"), limit=1, show_actors=True)
        self.assertEqual(self.read_rows(), [{"actor": "alice@example.test", "id": "2"}])
        export_events(self.source, self.output, include_internal=True, overwrite=True, limit=1)
        self.assertEqual(self.read_rows()[0]["id"], "1")

    def test_zero_limit_still_writes_header(self):
        self.assertEqual(export_events(self.source, self.output, limit=0), 0)
        self.assertEqual(self.output.read_text(), "id,actor,action\n")

    def test_existing_output_and_source_are_protected(self):
        self.output.write_text("keep me", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            export_events(self.source, self.output)
        self.assertEqual(self.output.read_text(), "keep me")
        before = self.source.read_bytes()
        with self.assertRaises(ValueError):
            export_events(self.source, self.source, overwrite=True)
        self.assertEqual(self.source.read_bytes(), before)

    def test_bad_input_is_validated_before_overwriting(self):
        self.output.write_text("keep me", encoding="utf-8")
        self.source.write_text('[{"id": true, "actor": "x", "action": "y"}]')
        with self.assertRaises(ValueError):
            export_events(self.source, self.output, overwrite=True)
        self.assertEqual(self.output.read_text(), "keep me")

    def test_invalid_options_do_not_create_output(self):
        for options in ({"fields": ()}, {"fields": ("id", "id")},
                        {"fields": ("internal",)}, {"limit": -1}, {"limit": True}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                export_events(self.source, self.output, **options)
            self.assertFalse(self.output.exists())

    def test_cli_reports_count_and_respects_fields(self):
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("audit_export.py")),
                                 str(self.source), str(self.output), "--fields", "action,id", "--limit", "1"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Exported 1 events\n")
        self.assertEqual(list(self.read_rows()[0]), ["action", "id"])


if __name__ == "__main__":
    unittest.main()
