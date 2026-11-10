# Anonymized coding outputs

Review the requested behavior, scope, readability, and unnecessary complexity. Original files and candidate patches follow. No generating condition or prior grade is supplied.

## Case: heldout

Task:
The audit-export utility currently exports CSV. Add JSON Lines output for a downstream log consumer.

Add a keyword-only format="csv" option to export_events and a --format csv|jsonl CLI option, also defaulting to csv. Existing callers and default CLI behavior must keep working. Unsupported format values must be rejected before creating or changing the destination.

In JSONL mode, write one JSON object per exported event, followed by a newline. There is no header, and zero exported events produces an empty file. Objects must contain exactly the selected fields in the requested order; preserve integer IDs and string values. Unicode, quotes, and embedded line breaks must round-trip correctly. JSONL must not apply the spreadsheet-formula escaping used by CSV.

All existing behavior remains available in both formats: internal-event filtering, actor redaction unless explicitly enabled, selected fields, limits applied after filtering, return counts and CLI count messages, explicit overwrite, source/destination protection, and validation before a destination is created or overwritten. The existing CSV formula escaping must remain intact.

Keep this a focused standard-library-only change. You may add useful tests. Run the existing tests with: python3 -m unittest -v

### Starting files

File: audit_export.py
```
"""Export a local audit log for reviewers."""
import argparse
import csv
import json
from pathlib import Path


FIELDS = ("id", "actor", "action")


def _read_events(source):
    events = json.loads(Path(source).read_text(encoding="utf-8"))
    if not isinstance(events, list):
        raise ValueError("source must contain a JSON array")
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("each event must be an object")
        if type(event.get("id")) is not int:
            raise ValueError("event id must be an integer")
        if not all(isinstance(event.get(key), str) for key in ("actor", "action")):
            raise ValueError("event actor and action must be strings")
        if type(event.get("internal", False)) is not bool:
            raise ValueError("event internal must be a boolean")
    return events


def _csv_cell(value):
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + value
    return value


def export_events(source, destination, *, fields=FIELDS, include_internal=False,
                  show_actors=False, limit=None, overwrite=False):
    """Write CSV and return the number of exported events."""
    fields = tuple(fields)
    if not fields or len(set(fields)) != len(fields) or any(f not in FIELDS for f in fields):
        raise ValueError("fields must be distinct names from id, actor, action")
    if limit is not None and (type(limit) is not int or limit < 0):
        raise ValueError("limit must be a nonnegative integer")
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("source and destination must differ")
    events = _read_events(source)
    rows = []
    for event in events:
        if event.get("internal", False) and not include_internal:
            continue
        if limit is not None and len(rows) >= limit:
            break
        row = {field: event[field] for field in fields}
        if "actor" in row and not show_actors:
            row["actor"] = "[redacted]"
        rows.append(row)
    with destination.open("w" if overwrite else "x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: _csv_cell(value) for key, value in row.items()} for row in rows)
    return len(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("--fields", default=",".join(FIELDS))
    parser.add_argument("--include-internal", action="store_true")
    parser.add_argument("--show-actors", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    try:
        count = export_events(args.source, args.destination, fields=args.fields.split(","),
                              include_internal=args.include_internal, show_actors=args.show_actors,
                              limit=args.limit, overwrite=args.overwrite)
    except (ValueError, OSError) as error:
        parser.exit(2, f"error: {error}\n")
    print(f"Exported {count} events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

File: test_audit_export.py
```
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

```

### Variant heldout-A

```diff
--- before/audit_export.py
+++ after/audit_export.py
@@ -31,8 +31,10 @@
 
 
 def export_events(source, destination, *, fields=FIELDS, include_internal=False,
-                  show_actors=False, limit=None, overwrite=False):
-    """Write CSV and return the number of exported events."""
+                  show_actors=False, limit=None, overwrite=False, format="csv"):
+    """Write CSV or JSON Lines and return the number of exported events."""
+    if format not in ("csv", "jsonl"):
+        raise ValueError("format must be csv or jsonl")
     fields = tuple(fields)
     if not fields or len(set(fields)) != len(fields) or any(f not in FIELDS for f in fields):
         raise ValueError("fields must be distinct names from id, actor, action")
@@ -53,9 +55,13 @@
             row["actor"] = "[redacted]"
         rows.append(row)
     with destination.open("w" if overwrite else "x", encoding="utf-8", newline="") as stream:
-        writer = csv.DictWriter(stream, fieldnames=fields)
-        writer.writeheader()
-        writer.writerows({key: _csv_cell(value) for key, value in row.items()} for row in rows)
+        if format == "jsonl":
+            for row in rows:
+                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
+        else:
+            writer = csv.DictWriter(stream, fieldnames=fields)
+            writer.writeheader()
+            writer.writerows({key: _csv_cell(value) for key, value in row.items()} for row in rows)
     return len(rows)
 
 
@@ -63,6 +69,7 @@
     parser = argparse.ArgumentParser(description=__doc__)
     parser.add_argument("source")
     parser.add_argument("destination")
+    parser.add_argument("--format", choices=("csv", "jsonl"), default="csv")
     parser.add_argument("--fields", default=",".join(FIELDS))
     parser.add_argument("--include-internal", action="store_true")
     parser.add_argument("--show-actors", action="store_true")
@@ -72,7 +79,7 @@
     try:
         count = export_events(args.source, args.destination, fields=args.fields.split(","),
                               include_internal=args.include_internal, show_actors=args.show_actors,
-                              limit=args.limit, overwrite=args.overwrite)
+                              limit=args.limit, overwrite=args.overwrite, format=args.format)
     except (ValueError, OSError) as error:
         parser.exit(2, f"error: {error}\n")
     print(f"Exported {count} events")
--- before/test_audit_export.py
+++ after/test_audit_export.py
@@ -75,6 +75,133 @@
         self.assertEqual(result.stdout, "Exported 1 events\n")
         self.assertEqual(list(self.read_rows()[0]), ["action", "id"])
 
+    def test_jsonl_defaults_filter_redact_and_preserve_types(self):
+        self.assertEqual(export_events(self.source, self.output, format="jsonl"), 2)
+        raw = self.output.read_text(encoding="utf-8")
+        self.assertTrue(raw.endswith("\n"))
+        rows = [json.loads(line) for line in raw.splitlines()]
+        self.assertEqual(rows, [
+            {"id": 2, "actor": "[redacted]", "action": "=SUM(1,2)"},
+            {"id": 3, "actor": "[redacted]", "action": "café, opened"},
+        ])
+        self.assertEqual(list(rows[0]), ["id", "actor", "action"])
+        self.assertIs(type(rows[0]["id"]), int)
+
+    def test_jsonl_round_trips_strings_and_selected_order(self):
+        actions = ['=café "quoted"\nnext\rline', '+plus', '-minus', '@mention', '\ttab', '\rcarriage']
+        events = [{"id": i, "actor": 'Zoë "Z"\n名字', "action": action}
+                  for i, action in enumerate(actions)]
+        self.source.write_text(json.dumps(events), encoding="utf-8")
+        count = export_events(self.source, self.output, format="jsonl",
+                              fields=("action", "actor", "id"), show_actors=True)
+        self.assertEqual(count, len(events))
+        lines = self.output.read_text(encoding="utf-8").splitlines()
+        self.assertEqual(len(lines), len(events))
+        rows = [json.loads(line) for line in lines]
+        self.assertEqual(rows, events)
+        self.assertTrue(all(list(row) == ["action", "actor", "id"] for row in rows))
+
+    def test_jsonl_options_and_overwrite(self):
+        count = export_events(self.source, self.output, format="jsonl", fields=("actor", "id"),
+                              show_actors=True, limit=1)
+        self.assertEqual(count, 1)
+        row = json.loads(self.output.read_text())
+        self.assertEqual(row, {"actor": "alice@example.test", "id": 2})
+        self.assertEqual(list(row), ["actor", "id"])
+        count = export_events(self.source, self.output, format="jsonl", include_internal=True,
+                              overwrite=True, limit=1)
+        self.assertEqual(count, 1)
+        self.assertEqual(json.loads(self.output.read_text()),
+                         {"id": 1, "actor": "[redacted]", "action": "internal"})
+
+    def test_jsonl_zero_events_is_empty(self):
+        for events, options in ((self.events, {"limit": 0}), ([], {}), ([self.events[0]], {})):
+            with self.subTest(events=events, options=options):
+                self.source.write_text(json.dumps(events), encoding="utf-8")
+                count = export_events(self.source, self.output, format="jsonl", overwrite=True, **options)
+                self.assertEqual(count, 0)
+                self.assertEqual(self.output.read_bytes(), b"")
+
+    def test_jsonl_protects_existing_destination_and_source(self):
+        self.output.write_text("keep me", encoding="utf-8")
+        with self.assertRaises(FileExistsError):
+            export_events(self.source, self.output, format="jsonl")
+        self.assertEqual(self.output.read_text(), "keep me")
+        before = self.source.read_bytes()
+        with self.assertRaises(ValueError):
+            export_events(self.source, self.source, format="jsonl", overwrite=True)
+        self.assertEqual(self.source.read_bytes(), before)
+
+    def test_validation_preserves_destination_in_both_formats(self):
+        invalid_options = ({"fields": ()}, {"fields": ("id", "id")},
+                           {"fields": ("internal",)}, {"limit": -1}, {"limit": True})
+        invalid_sources = ({}, [None], [{"id": True, "actor": "x", "action": "y"}],
+                           [{"id": 1, "actor": None, "action": "y"}],
+                           [{"id": 1, "actor": "x", "action": "y", "internal": 1}])
+        for format in ("csv", "jsonl"):
+            cases = [(self.events, options) for options in invalid_options]
+            # Validate even records that would fall outside the export limit.
+            cases.extend((events, {"limit": 0}) for events in invalid_sources)
+            for events, options in cases:
+                for existing in (False, True):
+                    with self.subTest(format=format, events=events, options=options, existing=existing):
+                        self.source.write_text(json.dumps(events), encoding="utf-8")
+                        if existing:
+                            self.output.write_text("keep me", encoding="utf-8")
+                        else:
+                            self.output.unlink(missing_ok=True)
+                        with self.assertRaises(ValueError):
+                            export_events(self.source, self.output, format=format, overwrite=True, **options)
+                        if existing:
+                            self.assertEqual(self.output.read_text(), "keep me")
+                        else:
+                            self.assertFalse(self.output.exists())
+
+    def test_invalid_format_does_not_create_or_overwrite(self):
+        for format in ("xml", "JSONL", "", None):
+            for existing in (False, True):
+                with self.subTest(format=format, existing=existing):
+                    if existing:
+                        self.output.write_text("keep me", encoding="utf-8")
+                    else:
+                        self.output.unlink(missing_ok=True)
+                    with self.assertRaises(ValueError):
+                        export_events(self.source, self.output, format=format, overwrite=True)
+                    if existing:
+                        self.assertEqual(self.output.read_text(), "keep me")
+                    else:
+                        self.assertFalse(self.output.exists())
+
+    def test_cli_formats_and_invalid_format(self):
+        command = [sys.executable, str(Path(__file__).with_name("audit_export.py")),
+                   str(self.source), str(self.output)]
+        for format in ("csv", "jsonl"):
+            with self.subTest(format=format):
+                result = subprocess.run(command + ["--format", format, "--fields", "action,id",
+                                                   "--limit", "1", "--overwrite"],
+                                        capture_output=True, text=True)
+                self.assertEqual(result.returncode, 0, result.stderr)
+                self.assertEqual(result.stdout, "Exported 1 events\n")
+                if format == "jsonl":
+                    row = json.loads(self.output.read_text())
+                    self.assertEqual(row, {"action": "=SUM(1,2)", "id": 2})
+                else:
+                    row = self.read_rows()[0]
+                    self.assertEqual(row, {"action": "'=SUM(1,2)", "id": "2"})
+                self.assertEqual(list(row), ["action", "id"])
+        for existing in (False, True):
+            if existing:
+                self.output.write_text("keep me", encoding="utf-8")
+            else:
+                self.output.unlink()
+            result = subprocess.run(command + ["--format", "xml", "--overwrite"],
+                                    capture_output=True, text=True)
+            self.assertEqual(result.returncode, 2)
+            if existing:
+                self.assertEqual(self.output.read_text(), "keep me")
+            else:
+                self.assertFalse(self.output.exists())
+
 
 if __name__ == "__main__":
     unittest.main()

```

### Variant heldout-B

```diff
--- before/audit_export.py
+++ after/audit_export.py
@@ -31,8 +31,10 @@
 
 
 def export_events(source, destination, *, fields=FIELDS, include_internal=False,
-                  show_actors=False, limit=None, overwrite=False):
-    """Write CSV and return the number of exported events."""
+                  show_actors=False, limit=None, overwrite=False, format="csv"):
+    """Write CSV or JSON Lines and return the number of exported events."""
+    if format not in ("csv", "jsonl"):
+        raise ValueError("format must be csv or jsonl")
     fields = tuple(fields)
     if not fields or len(set(fields)) != len(fields) or any(f not in FIELDS for f in fields):
         raise ValueError("fields must be distinct names from id, actor, action")
@@ -53,9 +55,13 @@
             row["actor"] = "[redacted]"
         rows.append(row)
     with destination.open("w" if overwrite else "x", encoding="utf-8", newline="") as stream:
-        writer = csv.DictWriter(stream, fieldnames=fields)
-        writer.writeheader()
-        writer.writerows({key: _csv_cell(value) for key, value in row.items()} for row in rows)
+        if format == "jsonl":
+            for row in rows:
+                stream.write(json.dumps(row) + "\n")
+        else:
+            writer = csv.DictWriter(stream, fieldnames=fields)
+            writer.writeheader()
+            writer.writerows({key: _csv_cell(value) for key, value in row.items()} for row in rows)
     return len(rows)
 
 
@@ -63,6 +69,7 @@
     parser = argparse.ArgumentParser(description=__doc__)
     parser.add_argument("source")
     parser.add_argument("destination")
+    parser.add_argument("--format", choices=("csv", "jsonl"), default="csv")
     parser.add_argument("--fields", default=",".join(FIELDS))
     parser.add_argument("--include-internal", action="store_true")
     parser.add_argument("--show-actors", action="store_true")
@@ -72,7 +79,7 @@
     try:
         count = export_events(args.source, args.destination, fields=args.fields.split(","),
                               include_internal=args.include_internal, show_actors=args.show_actors,
-                              limit=args.limit, overwrite=args.overwrite)
+                              limit=args.limit, overwrite=args.overwrite, format=args.format)
     except (ValueError, OSError) as error:
         parser.exit(2, f"error: {error}\n")
     print(f"Exported {count} events")
--- before/test_audit_export.py
+++ after/test_audit_export.py
@@ -75,6 +75,103 @@
         self.assertEqual(result.stdout, "Exported 1 events\n")
         self.assertEqual(list(self.read_rows()[0]), ["action", "id"])
 
+    def test_jsonl_defaults_filter_redact_and_preserve_types(self):
+        self.assertEqual(export_events(self.source, self.output, format="jsonl"), 2)
+        text = self.output.read_text(encoding="utf-8")
+        self.assertTrue(text.endswith("\n"))
+        rows = [json.loads(line) for line in text.splitlines()]
+        self.assertEqual(rows, [
+            {"id": 2, "actor": "[redacted]", "action": "=SUM(1,2)"},
+            {"id": 3, "actor": "[redacted]", "action": "café, opened"},
+        ])
+        self.assertEqual(list(rows[0]), ["id", "actor", "action"])
+        self.assertIs(type(rows[0]["id"]), int)
+
+    def test_jsonl_fields_limits_and_special_strings(self):
+        self.events[1]["actor"] = '+"café 😀"\nnext\rline'
+        self.events[1]["action"] = '@"quoted"\nnext\rline'
+        self.source.write_text(json.dumps(self.events), encoding="utf-8")
+        self.assertEqual(export_events(self.source, self.output, format="jsonl",
+                                      fields=("action", "actor", "id"),
+                                      show_actors=True, limit=1), 1)
+        lines = self.output.read_text(encoding="utf-8").splitlines()
+        self.assertEqual(len(lines), 1)
+        row = json.loads(lines[0])
+        self.assertEqual(list(row), ["action", "actor", "id"])
+        self.assertEqual(row, self.events[1])
+        self.assertEqual(export_events(self.source, self.output, format="jsonl",
+                                      fields=("id",), include_internal=True,
+                                      overwrite=True, limit=1), 1)
+        self.assertEqual(json.loads(self.output.read_text()), {"id": 1})
+
+    def test_jsonl_empty_exports_have_no_header(self):
+        for options in ({"limit": 0}, {}):
+            if not options:
+                self.source.write_text("[]", encoding="utf-8")
+            with self.subTest(options=options):
+                self.assertEqual(export_events(self.source, self.output, format="jsonl",
+                                              overwrite=True, **options), 0)
+                self.assertEqual(self.output.read_bytes(), b"")
+
+    def test_jsonl_protects_destination_and_source(self):
+        self.output.write_text("keep me", encoding="utf-8")
+        with self.assertRaises(FileExistsError):
+            export_events(self.source, self.output, format="jsonl")
+        self.assertEqual(self.output.read_text(), "keep me")
+        before = self.source.read_bytes()
+        with self.assertRaises(ValueError):
+            export_events(self.source, self.source, format="jsonl", overwrite=True)
+        self.assertEqual(self.source.read_bytes(), before)
+
+    def test_validation_preserves_existing_or_absent_destination_in_both_formats(self):
+        for format in ("csv", "jsonl"):
+            for exists in (False, True):
+                for options in ({"fields": ()}, {"fields": ("id", "id")},
+                                {"fields": ("internal",)}, {"limit": -1},
+                                {"limit": True}, {"format": "xml"}, {"format": None}):
+                    with self.subTest(format=format, exists=exists, options=options):
+                        self.output.unlink(missing_ok=True)
+                        if exists:
+                            self.output.write_text("keep me", encoding="utf-8")
+                        kwargs = {"format": format, "overwrite": True, **options}
+                        with self.assertRaises(ValueError):
+                            export_events(self.source, self.output, **kwargs)
+                        if exists:
+                            self.assertEqual(self.output.read_text(), "keep me")
+                        else:
+                            self.assertFalse(self.output.exists())
+
+    def test_jsonl_validates_all_input_even_beyond_limit(self):
+        self.events.append({"id": True, "actor": "x", "action": "y"})
+        self.source.write_text(json.dumps(self.events), encoding="utf-8")
+        for exists in (False, True):
+            with self.subTest(exists=exists):
+                if exists:
+                    self.output.write_text("keep me", encoding="utf-8")
+                with self.assertRaises(ValueError):
+                    export_events(self.source, self.output, format="jsonl",
+                                  overwrite=True, limit=0)
+                if exists:
+                    self.assertEqual(self.output.read_text(), "keep me")
+                else:
+                    self.assertFalse(self.output.exists())
+
+    def test_cli_jsonl_and_invalid_format(self):
+        command = [sys.executable, str(Path(__file__).with_name("audit_export.py")),
+                   str(self.source), str(self.output)]
+        result = subprocess.run(command + ["--format", "jsonl", "--fields", "action,id",
+                                           "--limit", "1"], capture_output=True, text=True)
+        self.assertEqual(result.returncode, 0, result.stderr)
+        self.assertEqual(result.stdout, "Exported 1 events\n")
+        row = json.loads(self.output.read_text())
+        self.assertEqual(list(row), ["action", "id"])
+        self.assertEqual(row, {"action": "=SUM(1,2)", "id": 2})
+        before = self.output.read_bytes()
+        result = subprocess.run(command + ["--format", "xml", "--overwrite"],
+                                capture_output=True, text=True)
+        self.assertEqual(result.returncode, 2)
+        self.assertEqual(self.output.read_bytes(), before)
+
 
 if __name__ == "__main__":
     unittest.main()

```

### Variant heldout-C

```diff
--- before/audit_export.py
+++ after/audit_export.py
@@ -31,8 +31,10 @@
 
 
 def export_events(source, destination, *, fields=FIELDS, include_internal=False,
-                  show_actors=False, limit=None, overwrite=False):
-    """Write CSV and return the number of exported events."""
+                  show_actors=False, limit=None, overwrite=False, format="csv"):
+    """Write CSV or JSON Lines and return the number of exported events."""
+    if format not in ("csv", "jsonl"):
+        raise ValueError("format must be csv or jsonl")
     fields = tuple(fields)
     if not fields or len(set(fields)) != len(fields) or any(f not in FIELDS for f in fields):
         raise ValueError("fields must be distinct names from id, actor, action")
@@ -53,9 +55,13 @@
             row["actor"] = "[redacted]"
         rows.append(row)
     with destination.open("w" if overwrite else "x", encoding="utf-8", newline="") as stream:
-        writer = csv.DictWriter(stream, fieldnames=fields)
-        writer.writeheader()
-        writer.writerows({key: _csv_cell(value) for key, value in row.items()} for row in rows)
+        if format == "jsonl":
+            for row in rows:
+                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
+        else:
+            writer = csv.DictWriter(stream, fieldnames=fields)
+            writer.writeheader()
+            writer.writerows({key: _csv_cell(value) for key, value in row.items()} for row in rows)
     return len(rows)
 
 
@@ -63,6 +69,7 @@
     parser = argparse.ArgumentParser(description=__doc__)
     parser.add_argument("source")
     parser.add_argument("destination")
+    parser.add_argument("--format", choices=("csv", "jsonl"), default="csv")
     parser.add_argument("--fields", default=",".join(FIELDS))
     parser.add_argument("--include-internal", action="store_true")
     parser.add_argument("--show-actors", action="store_true")
@@ -72,7 +79,7 @@
     try:
         count = export_events(args.source, args.destination, fields=args.fields.split(","),
                               include_internal=args.include_internal, show_actors=args.show_actors,
-                              limit=args.limit, overwrite=args.overwrite)
+                              limit=args.limit, overwrite=args.overwrite, format=args.format)
     except (ValueError, OSError) as error:
         parser.exit(2, f"error: {error}\n")
     print(f"Exported {count} events")
--- before/test_audit_export.py
+++ after/test_audit_export.py
@@ -75,6 +75,110 @@
         self.assertEqual(result.stdout, "Exported 1 events\n")
         self.assertEqual(list(self.read_rows()[0]), ["action", "id"])
 
+    def test_jsonl_filters_redacts_and_preserves_types(self):
+        self.assertEqual(export_events(self.source, self.output, format="jsonl"), 2)
+        lines = self.output.read_text(encoding="utf-8").splitlines()
+        self.assertEqual([json.loads(line) for line in lines], [
+            {"id": 2, "actor": "[redacted]", "action": "=SUM(1,2)"},
+            {"id": 3, "actor": "[redacted]", "action": "café, opened"},
+        ])
+        self.assertTrue(self.output.read_bytes().endswith(b"\n"))
+
+    def test_jsonl_selected_fields_order_limits_and_overwrite(self):
+        count = export_events(self.source, self.output, format="jsonl",
+                              fields=("actor", "id"), show_actors=True, limit=1)
+        self.assertEqual(count, 1)
+        row = json.loads(self.output.read_text())
+        self.assertEqual(list(row), ["actor", "id"])
+        self.assertEqual(row, {"actor": "alice@example.test", "id": 2})
+        count = export_events(self.source, self.output, format="jsonl", fields=("id",),
+                              include_internal=True, overwrite=True, limit=1)
+        self.assertEqual(count, 1)
+        self.assertEqual(json.loads(self.output.read_text()), {"id": 1})
+
+    def test_jsonl_strings_round_trip_without_formula_escaping(self):
+        actions = ['=formula', '+plus', '-minus', '@mention', '\ttab', '\rreturn',
+                   'café 雪 😀 "quoted"\nnext line\\path']
+        events = [{"id": i, "actor": action, "action": action}
+                  for i, action in enumerate(actions)]
+        self.source.write_text(json.dumps(events), encoding="utf-8")
+        self.assertEqual(export_events(self.source, self.output, format="jsonl", show_actors=True),
+                         len(events))
+        lines = self.output.read_text(encoding="utf-8").splitlines()
+        self.assertEqual(len(lines), len(events))
+        self.assertEqual([json.loads(line) for line in lines], events)
+
+    def test_jsonl_zero_events_is_empty(self):
+        for events, options in ((self.events, {"limit": 0}), ([], {}),
+                                ([self.events[0]], {})):
+            with self.subTest(events=events, options=options):
+                self.source.write_text(json.dumps(events), encoding="utf-8")
+                self.assertEqual(export_events(self.source, self.output, format="jsonl",
+                                               overwrite=True, **options), 0)
+                self.assertEqual(self.output.read_bytes(), b"")
+
+    def test_jsonl_protects_existing_output_and_source(self):
+        self.output.write_text("keep me", encoding="utf-8")
+        with self.assertRaises(FileExistsError):
+            export_events(self.source, self.output, format="jsonl")
+        self.assertEqual(self.output.read_text(), "keep me")
+        before = self.source.read_bytes()
+        with self.assertRaises(ValueError):
+            export_events(self.source, self.source, format="jsonl", overwrite=True)
+        self.assertEqual(self.source.read_bytes(), before)
+
+    def test_jsonl_validates_all_input_before_writing(self):
+        self.events.append({"id": True, "actor": "x", "action": "y"})
+        self.source.write_text(json.dumps(self.events), encoding="utf-8")
+        for existing in (False, True):
+            with self.subTest(existing=existing):
+                if existing:
+                    self.output.write_text("keep me", encoding="utf-8")
+                with self.assertRaises(ValueError):
+                    export_events(self.source, self.output, format="jsonl", limit=1, overwrite=True)
+                if existing:
+                    self.assertEqual(self.output.read_text(), "keep me")
+                else:
+                    self.assertFalse(self.output.exists())
+
+    def test_invalid_options_protect_destination_in_both_formats(self):
+        for format in ("csv", "jsonl"):
+            for options in ({"fields": ()}, {"fields": ("id", "id")},
+                            {"fields": ("internal",)}, {"limit": -1}, {"limit": True},
+                            {"format": "xml"}, {"format": None}, {"format": []}):
+                for existing in (False, True):
+                    with self.subTest(format=format, options=options, existing=existing):
+                        self.output.unlink(missing_ok=True)
+                        if existing:
+                            self.output.write_text("keep me", encoding="utf-8")
+                        with self.assertRaises(ValueError):
+                            export_events(self.source, self.output, overwrite=True,
+                                          **({"format": format} | options))
+                        if existing:
+                            self.assertEqual(self.output.read_text(), "keep me")
+                        else:
+                            self.assertFalse(self.output.exists())
+
+    def test_jsonl_cli_and_invalid_format(self):
+        command = [sys.executable, str(Path(__file__).with_name("audit_export.py")),
+                   str(self.source), str(self.output)]
+        result = subprocess.run(command + ["--format", "jsonl", "--fields", "action,id",
+                                          "--limit", "1"], capture_output=True, text=True)
+        self.assertEqual(result.returncode, 0, result.stderr)
+        self.assertEqual(result.stdout, "Exported 1 events\n")
+        row = json.loads(self.output.read_text())
+        self.assertEqual(list(row), ["action", "id"])
+        self.assertEqual(row, {"action": "=SUM(1,2)", "id": 2})
+        before = self.output.read_bytes()
+        result = subprocess.run(command + ["--format", "xml", "--overwrite"],
+                                capture_output=True, text=True)
+        self.assertEqual(result.returncode, 2)
+        self.assertEqual(self.output.read_bytes(), before)
+        self.output.unlink()
+        result = subprocess.run(command + ["--format", "xml"], capture_output=True, text=True)
+        self.assertEqual(result.returncode, 2)
+        self.assertFalse(self.output.exists())
+
 
 if __name__ == "__main__":
     unittest.main()

```
