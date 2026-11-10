# Anonymized coding outputs

Review the requested behavior, scope, readability, and unnecessary complexity. Original files and candidate patches follow. No generating condition or prior grade is supplied.

## Case: providers

Task:
Add assistant selection to this small workflow planner. Claude remains the default. Support claude, firstmate, and astro through an optional assistant setting in the config and a --assistant command-line flag. The flag overrides config; config overrides the default. An unsupported selection must produce a clear error, never silently switch to another assistant. Keep the existing task/stage output. Update the usage documentation and relevant tests. This planner only prints plans; it must not launch an assistant.

### Starting files

File: README.md
```
# Workflow planner

Python standard library only. Run `python3 -m unittest discover -s tests -v`.
`python3 planner.py TASK [--config config.json]` prints a plan as JSON.
Config can contain `stages`, a list included unchanged in the plan.
`make_plan(task, config=None)` returns the same plan for Python callers.
Planning has no execution side effects.

```

File: planner.py
```
import argparse
import json

def make_plan(task, config=None):
    config = config or {}
    return {"task": task, "assistant": "claude", "stages": config.get("stages", ["build", "review"])}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    parser.add_argument("--config")
    args = parser.parse_args()
    config = {}
    if args.config:
        with open(args.config) as stream:
            config = json.load(stream)
    print(json.dumps(make_plan(args.task, config)))

if __name__ == "__main__":
    main()

```

File: tests/test_planner.py
```
import unittest
from planner import make_plan

class ExistingPlanTests(unittest.TestCase):
    def test_default(self):
        self.assertEqual(make_plan("ship"), {"task": "ship", "assistant": "claude", "stages": ["build", "review"]})
    def test_custom_stages(self):
        self.assertEqual(make_plan("ship", {"stages": ["test"]})["stages"], ["test"])

```

### Variant providers-A

```diff
--- before/README.md
+++ after/README.md
@@ -1,7 +1,19 @@
 # Workflow planner
 
 Python standard library only. Run `python3 -m unittest discover -s tests -v`.
-`python3 planner.py TASK [--config config.json]` prints a plan as JSON.
-Config can contain `stages`, a list included unchanged in the plan.
-`make_plan(task, config=None)` returns the same plan for Python callers.
-Planning has no execution side effects.
+`python3 planner.py TASK [--config config.json] [--assistant {claude,firstmate,astro}]` prints a plan as JSON.
+Config can contain `stages`, a list included unchanged in the plan, and an optional
+`assistant`: `claude`, `firstmate`, or `astro`. For example:
+
+```json
+{"assistant": "firstmate", "stages": ["build", "review"]}
+```
+
+The `--assistant` flag overrides config; config overrides the default, `claude`.
+For example, `python3 planner.py ship --config config.json --assistant astro`
+selects `astro` regardless of the config assistant.
+An unsupported selection is an error and produces no plan.
+`make_plan(task, config=None, assistant=None)` returns the same plan for Python
+callers; a non-`None` assistant argument overrides config, and an unsupported
+selection raises `ValueError`.
+Planning only prints or returns plans; it never launches an assistant.
--- before/planner.py
+++ after/planner.py
@@ -1,20 +1,31 @@
 import argparse
 import json
 
-def make_plan(task, config=None):
+ASSISTANTS = ("claude", "firstmate", "astro")
+
+def make_plan(task, config=None, assistant=None):
     config = config or {}
-    return {"task": task, "assistant": "claude", "stages": config.get("stages", ["build", "review"])}
+    if assistant is None:
+        assistant = config.get("assistant", "claude")
+    if assistant not in ASSISTANTS:
+        raise ValueError(f"Unsupported assistant {assistant!r}; choose from {', '.join(ASSISTANTS)}")
+    return {"task": task, "assistant": assistant, "stages": config.get("stages", ["build", "review"])}
 
 def main():
     parser = argparse.ArgumentParser()
     parser.add_argument("task")
     parser.add_argument("--config")
+    parser.add_argument("--assistant", choices=ASSISTANTS, help="override the config assistant (default: claude)")
     args = parser.parse_args()
     config = {}
     if args.config:
         with open(args.config) as stream:
             config = json.load(stream)
-    print(json.dumps(make_plan(args.task, config)))
+    try:
+        plan = make_plan(args.task, config, args.assistant)
+    except ValueError as error:
+        parser.error(str(error))
+    print(json.dumps(plan))
 
 if __name__ == "__main__":
     main()
--- before/tests/test_planner.py
+++ after/tests/test_planner.py
@@ -1,4 +1,9 @@
 import unittest
+import json
+from pathlib import Path
+import subprocess
+import sys
+import tempfile
 from planner import make_plan
 
 class ExistingPlanTests(unittest.TestCase):
@@ -6,3 +11,63 @@
         self.assertEqual(make_plan("ship"), {"task": "ship", "assistant": "claude", "stages": ["build", "review"]})
     def test_custom_stages(self):
         self.assertEqual(make_plan("ship", {"stages": ["test"]})["stages"], ["test"])
+
+    def test_config_assistants(self):
+        for assistant in ("claude", "firstmate", "astro"):
+            with self.subTest(assistant=assistant):
+                self.assertEqual(make_plan("ship", {"assistant": assistant, "stages": []}),
+                                 {"task": "ship", "assistant": assistant, "stages": []})
+
+    def test_explicit_assistant_overrides_config(self):
+        self.assertEqual(make_plan("ship", {"assistant": "astro"}, "firstmate")["assistant"], "firstmate")
+        self.assertEqual(make_plan("ship", {"assistant": "unsupported"}, "claude")["assistant"], "claude")
+
+    def test_invalid_assistants(self):
+        for assistant in ("unsupported", "", "Claude", None, 42, []):
+            with self.subTest(assistant=assistant):
+                with self.assertRaisesRegex(ValueError, "Unsupported assistant"):
+                    make_plan("ship", {"assistant": assistant})
+        with self.assertRaisesRegex(ValueError, "Unsupported assistant"):
+            make_plan("ship", {"assistant": "claude"}, "unsupported")
+
+
+class CommandLineTests(unittest.TestCase):
+    def run_planner(self, *args, config=None):
+        with tempfile.TemporaryDirectory() as directory:
+            command = [sys.executable, str(Path(__file__).resolve().parents[1] / "planner.py"), "ship"]
+            if config is not None:
+                path = Path(directory) / "config.json"
+                path.write_text(json.dumps(config))
+                command.extend(["--config", str(path)])
+            return subprocess.run(command + list(args), capture_output=True, text=True)
+
+    def test_default(self):
+        result = self.run_planner()
+        self.assertEqual(result.returncode, 0, result.stderr)
+        self.assertEqual(json.loads(result.stdout), make_plan("ship"))
+
+    def test_config_and_flag_selection(self):
+        for assistant in ("claude", "firstmate", "astro"):
+            with self.subTest(assistant=assistant):
+                for args, config in (
+                    ((), {"assistant": assistant, "stages": ["test"]}),
+                    (("--assistant", assistant), {"assistant": "unsupported", "stages": ["test"]}),
+                ):
+                    result = self.run_planner(*args, config=config)
+                    self.assertEqual(result.returncode, 0, result.stderr)
+                    self.assertEqual(json.loads(result.stdout),
+                                     {"task": "ship", "assistant": assistant, "stages": ["test"]})
+
+    def test_invalid_selection_prints_error_without_plan(self):
+        for args, config in (
+            (("--assistant", "unsupported"), {"assistant": "claude"}),
+            (("--assistant", ""), None),
+            ((), {"assistant": "unsupported"}),
+            ((), {"assistant": None}),
+        ):
+            with self.subTest(args=args, config=config):
+                result = self.run_planner(*args, config=config)
+                self.assertNotEqual(result.returncode, 0)
+                self.assertEqual(result.stdout, "")
+                self.assertIn("assistant", result.stderr)
+                self.assertIn("claude", result.stderr)

```

### Variant providers-B

```diff
--- before/README.md
+++ after/README.md
@@ -1,7 +1,17 @@
 # Workflow planner
 
 Python standard library only. Run `python3 -m unittest discover -s tests -v`.
-`python3 planner.py TASK [--config config.json]` prints a plan as JSON.
-Config can contain `stages`, a list included unchanged in the plan.
-`make_plan(task, config=None)` returns the same plan for Python callers.
-Planning has no execution side effects.
+`python3 planner.py TASK [--config config.json] [--assistant {claude,firstmate,astro}]` prints a plan as JSON.
+Config can contain `stages`, a list included unchanged in the plan, and an optional
+`assistant` setting: `claude`, `firstmate`, or `astro`.
+The command-line flag overrides config; config overrides the default, `claude`.
+For example, with config `{"assistant": "firstmate", "stages": ["test"]}`,
+`python3 planner.py ship --config config.json --assistant astro` prints
+`{"task": "ship", "assistant": "astro", "stages": ["test"]}`.
+
+`make_plan(task, config=None, assistant=None)` returns the same plan for Python
+callers. A supplied `assistant` argument overrides config; `None` means no override.
+Unsupported selections raise `ValueError` for Python callers and produce a clear
+error with a nonzero exit status on the command line. They never fall back to
+another assistant.
+Planning only prints or returns a plan; it never launches an assistant.
--- before/planner.py
+++ after/planner.py
@@ -1,20 +1,30 @@
 import argparse
 import json
 
-def make_plan(task, config=None):
+ASSISTANTS = ("claude", "firstmate", "astro")
+
+def make_plan(task, config=None, assistant=None):
     config = config or {}
-    return {"task": task, "assistant": "claude", "stages": config.get("stages", ["build", "review"])}
+    selected = config.get("assistant", "claude") if assistant is None else assistant
+    if selected not in ASSISTANTS:
+        raise ValueError(f"Unsupported assistant {selected!r}; choose from: {', '.join(ASSISTANTS)}")
+    return {"task": task, "assistant": selected, "stages": config.get("stages", ["build", "review"])}
 
 def main():
     parser = argparse.ArgumentParser()
     parser.add_argument("task")
     parser.add_argument("--config")
+    parser.add_argument("--assistant", choices=ASSISTANTS)
     args = parser.parse_args()
     config = {}
     if args.config:
         with open(args.config) as stream:
             config = json.load(stream)
-    print(json.dumps(make_plan(args.task, config)))
+    try:
+        plan = make_plan(args.task, config, args.assistant)
+    except ValueError as error:
+        parser.error(str(error))
+    print(json.dumps(plan))
 
 if __name__ == "__main__":
     main()
--- before/tests/test_planner.py
+++ after/tests/test_planner.py
@@ -1,4 +1,9 @@
 import unittest
+import json
+from pathlib import Path
+import subprocess
+import sys
+import tempfile
 from planner import make_plan
 
 class ExistingPlanTests(unittest.TestCase):
@@ -6,3 +11,85 @@
         self.assertEqual(make_plan("ship"), {"task": "ship", "assistant": "claude", "stages": ["build", "review"]})
     def test_custom_stages(self):
         self.assertEqual(make_plan("ship", {"stages": ["test"]})["stages"], ["test"])
+
+class AssistantSelectionTests(unittest.TestCase):
+    def test_config_selections_preserve_task_and_stages(self):
+        for assistant in ("claude", "firstmate", "astro"):
+            with self.subTest(assistant=assistant):
+                self.assertEqual(
+                    make_plan("ship", {"assistant": assistant, "stages": ["test"]}),
+                    {"task": "ship", "assistant": assistant, "stages": ["test"]},
+                )
+
+    def test_argument_overrides_config(self):
+        for assistant in ("claude", "firstmate", "astro"):
+            with self.subTest(assistant=assistant):
+                self.assertEqual(
+                    make_plan("ship", {"assistant": "unsupported"}, assistant)["assistant"],
+                    assistant,
+                )
+
+    def test_invalid_config_selection(self):
+        for assistant in ("unknown", "", "Claude", None, False, []):
+            with self.subTest(assistant=assistant):
+                with self.assertRaisesRegex(ValueError, "Unsupported assistant"):
+                    make_plan("ship", {"assistant": assistant})
+
+    def test_invalid_argument_selection(self):
+        with self.assertRaisesRegex(ValueError, "Unsupported assistant"):
+            make_plan("ship", {"assistant": "claude"}, "unknown")
+
+class PlannerCommandTests(unittest.TestCase):
+    def run_planner(self, *arguments, config=None):
+        command = [sys.executable, str(Path(__file__).resolve().parents[1] / "planner.py"), "ship"]
+        with tempfile.TemporaryDirectory() as directory:
+            if config is not None:
+                config_path = Path(directory) / "config.json"
+                config_path.write_text(json.dumps(config))
+                command.extend(["--config", str(config_path)])
+            return subprocess.run(command + list(arguments), capture_output=True, text=True)
+
+    def assert_plan(self, result, assistant, stages=None):
+        self.assertEqual(result.returncode, 0, result.stderr)
+        self.assertEqual(result.stderr, "")
+        self.assertEqual(json.loads(result.stdout), {
+            "task": "ship", "assistant": assistant,
+            "stages": ["build", "review"] if stages is None else stages,
+        })
+
+    def test_default(self):
+        self.assert_plan(self.run_planner(), "claude")
+
+    def test_config_selections(self):
+        for assistant in ("claude", "firstmate", "astro"):
+            with self.subTest(assistant=assistant):
+                self.assert_plan(self.run_planner(config={"assistant": assistant}), assistant)
+
+    def test_flag_selections(self):
+        for assistant in ("claude", "firstmate", "astro"):
+            with self.subTest(assistant=assistant):
+                self.assert_plan(self.run_planner("--assistant", assistant), assistant)
+
+    def test_flag_overrides_config_and_preserves_stages(self):
+        for configured in ("firstmate", "unsupported"):
+            with self.subTest(configured=configured):
+                self.assert_plan(self.run_planner(
+                    "--assistant", "astro", config={"assistant": configured, "stages": ["test"]},
+                ), "astro", ["test"])
+
+    def test_invalid_config_selection(self):
+        for assistant in ("unknown", "", None):
+            with self.subTest(assistant=assistant):
+                result = self.run_planner(config={"assistant": assistant})
+                self.assertNotEqual(result.returncode, 0)
+                self.assertEqual(result.stdout, "")
+                self.assertIn("Unsupported assistant", result.stderr)
+                self.assertNotIn("Traceback", result.stderr)
+
+    def test_invalid_flag_does_not_fall_back_to_config(self):
+        result = self.run_planner("--assistant", "unknown", config={"assistant": "firstmate"})
+        self.assertNotEqual(result.returncode, 0)
+        self.assertEqual(result.stdout, "")
+        self.assertIn("invalid choice", result.stderr)
+        self.assertIn("unknown", result.stderr)
+        self.assertNotIn("Traceback", result.stderr)

```

### Variant providers-C

```diff
--- before/README.md
+++ after/README.md
@@ -1,7 +1,16 @@
 # Workflow planner
 
 Python standard library only. Run `python3 -m unittest discover -s tests -v`.
-`python3 planner.py TASK [--config config.json]` prints a plan as JSON.
-Config can contain `stages`, a list included unchanged in the plan.
-`make_plan(task, config=None)` returns the same plan for Python callers.
-Planning has no execution side effects.
+`python3 planner.py TASK [--config config.json] [--assistant {claude,firstmate,astro}]` prints a plan as JSON.
+Config can contain `stages`, a list included unchanged in the plan, and an optional
+`assistant` string: `claude`, `firstmate`, or `astro`.
+For example, `{"assistant": "firstmate", "stages": ["build", "review"]}` selects FirstMate.
+The `--assistant` flag overrides config; config overrides the default, `claude`.
+For example, `python3 planner.py ship --config config.json --assistant astro`
+selects Astro even when config selects FirstMate.
+
+`make_plan(task, config=None, assistant=None)` returns the same plan for Python callers.
+A non-`None` assistant argument overrides config. Unsupported selections raise
+`ValueError`; the command line reports an error and exits unsuccessfully without
+printing a plan. Names are case-sensitive.
+Planning only produces a plan; it never launches an assistant.
--- before/planner.py
+++ after/planner.py
@@ -1,20 +1,30 @@
 import argparse
 import json
 
-def make_plan(task, config=None):
+ASSISTANTS = ("claude", "firstmate", "astro")
+
+def make_plan(task, config=None, assistant=None):
     config = config or {}
-    return {"task": task, "assistant": "claude", "stages": config.get("stages", ["build", "review"])}
+    selected = assistant if assistant is not None else config.get("assistant", "claude")
+    if selected not in ASSISTANTS:
+        raise ValueError(f"Unsupported assistant {selected!r}; choose from {', '.join(ASSISTANTS)}")
+    return {"task": task, "assistant": selected, "stages": config.get("stages", ["build", "review"])}
 
 def main():
     parser = argparse.ArgumentParser()
     parser.add_argument("task")
     parser.add_argument("--config")
+    parser.add_argument("--assistant", choices=ASSISTANTS, help="Override the config assistant (default: claude)")
     args = parser.parse_args()
     config = {}
     if args.config:
         with open(args.config) as stream:
             config = json.load(stream)
-    print(json.dumps(make_plan(args.task, config)))
+    try:
+        plan = make_plan(args.task, config, args.assistant)
+    except ValueError as error:
+        parser.error(str(error))
+    print(json.dumps(plan))
 
 if __name__ == "__main__":
     main()
--- before/tests/test_planner.py
+++ after/tests/test_planner.py
@@ -1,4 +1,9 @@
 import unittest
+import json
+from pathlib import Path
+import subprocess
+import sys
+import tempfile
 from planner import make_plan
 
 class ExistingPlanTests(unittest.TestCase):
@@ -6,3 +11,67 @@
         self.assertEqual(make_plan("ship"), {"task": "ship", "assistant": "claude", "stages": ["build", "review"]})
     def test_custom_stages(self):
         self.assertEqual(make_plan("ship", {"stages": ["test"]})["stages"], ["test"])
+
+    def test_config_assistants(self):
+        for assistant in ("claude", "firstmate", "astro"):
+            with self.subTest(assistant=assistant):
+                self.assertEqual(make_plan("ship", {"assistant": assistant, "stages": ["test"]}),
+                                 {"task": "ship", "assistant": assistant, "stages": ["test"]})
+
+    def test_assistant_argument_overrides_config(self):
+        for assistant in ("claude", "firstmate", "astro"):
+            with self.subTest(assistant=assistant):
+                self.assertEqual(make_plan("ship", {"assistant": "unknown"}, assistant)["assistant"], assistant)
+
+    def test_unsupported_config_assistant(self):
+        for assistant in ("unknown", "Claude", "", None, 1, [], {}):
+            with self.subTest(assistant=assistant):
+                with self.assertRaisesRegex(ValueError, "Unsupported assistant"):
+                    make_plan("ship", {"assistant": assistant})
+
+    def test_unsupported_argument_does_not_fall_back(self):
+        for assistant in ("unknown", ""):
+            with self.subTest(assistant=assistant):
+                with self.assertRaisesRegex(ValueError, "Unsupported assistant"):
+                    make_plan("ship", {"assistant": "astro"}, assistant)
+
+
+class CommandLineTests(unittest.TestCase):
+    def run_planner(self, *args, config=None):
+        with tempfile.TemporaryDirectory() as directory:
+            command = [sys.executable, str(Path(__file__).resolve().parents[1] / "planner.py"), "ship"]
+            if config is not None:
+                path = Path(directory) / "config.json"
+                path.write_text(json.dumps(config))
+                command.extend(["--config", str(path)])
+            return subprocess.run(command + list(args), capture_output=True, text=True)
+
+    def test_default(self):
+        result = self.run_planner()
+        self.assertEqual(result.returncode, 0, result.stderr)
+        self.assertEqual(json.loads(result.stdout), make_plan("ship"))
+
+    def test_config_and_flag_selection(self):
+        for assistant in ("claude", "firstmate", "astro"):
+            for use_flag in (False, True):
+                with self.subTest(assistant=assistant, use_flag=use_flag):
+                    args = ["--assistant", assistant] if use_flag else []
+                    config = {"assistant": "unknown" if use_flag else assistant, "stages": ["test"]}
+                    result = self.run_planner(*args, config=config)
+                    self.assertEqual(result.returncode, 0, result.stderr)
+                    self.assertEqual(json.loads(result.stdout),
+                                     {"task": "ship", "assistant": assistant, "stages": ["test"]})
+
+    def test_invalid_selection_prints_error_without_plan(self):
+        for args, config in (([], {"assistant": "unknown"}),
+                             ([], {"assistant": None}),
+                             (["--assistant", "unknown"], {"assistant": "astro"}),
+                             (["--assistant", ""], {"assistant": "astro"})):
+            with self.subTest(args=args, config=config):
+                result = self.run_planner(*args, config=config)
+                self.assertEqual(result.returncode, 2)
+                self.assertEqual(result.stdout, "")
+                self.assertIn("error:", result.stderr)
+                self.assertIn("assistant", result.stderr)
+                for assistant in ("claude", "firstmate", "astro"):
+                    self.assertIn(assistant, result.stderr)

```

### Variant providers-D

```diff
--- before/README.md
+++ after/README.md
@@ -1,7 +1,14 @@
 # Workflow planner
 
 Python standard library only. Run `python3 -m unittest discover -s tests -v`.
-`python3 planner.py TASK [--config config.json]` prints a plan as JSON.
-Config can contain `stages`, a list included unchanged in the plan.
-`make_plan(task, config=None)` returns the same plan for Python callers.
-Planning has no execution side effects.
+`python3 planner.py TASK [--config config.json] [--assistant {claude,firstmate,astro}]` prints a plan as JSON.
+Config can contain `stages`, a list included unchanged in the plan, and an optional
+`assistant`: `claude`, `firstmate`, or `astro`.
+For example: `{"assistant": "firstmate", "stages": ["build", "review"]}`.
+The command-line flag overrides config; config overrides the default, `claude`.
+An unsupported selected assistant produces an error and no plan.
+
+`make_plan(task, config=None, assistant=None)` returns the same plan for Python callers.
+Its optional `assistant` argument overrides config when supplied; unsupported
+selections raise `ValueError`.
+Planning only prints or returns a plan; it never launches an assistant.
--- before/planner.py
+++ after/planner.py
@@ -1,20 +1,30 @@
 import argparse
 import json
 
-def make_plan(task, config=None):
+ASSISTANTS = ("claude", "firstmate", "astro")
+
+def make_plan(task, config=None, assistant=None):
     config = config or {}
-    return {"task": task, "assistant": "claude", "stages": config.get("stages", ["build", "review"])}
+    selected = assistant if assistant is not None else config.get("assistant", "claude")
+    if selected not in ASSISTANTS:
+        raise ValueError(f"Unsupported assistant {selected!r}; choose from {', '.join(ASSISTANTS)}")
+    return {"task": task, "assistant": selected, "stages": config.get("stages", ["build", "review"])}
 
 def main():
     parser = argparse.ArgumentParser()
     parser.add_argument("task")
     parser.add_argument("--config")
+    parser.add_argument("--assistant", choices=ASSISTANTS, help="Override the configured assistant (default: claude)")
     args = parser.parse_args()
     config = {}
     if args.config:
         with open(args.config) as stream:
             config = json.load(stream)
-    print(json.dumps(make_plan(args.task, config)))
+    try:
+        plan = make_plan(args.task, config, args.assistant)
+    except ValueError as error:
+        parser.error(str(error))
+    print(json.dumps(plan))
 
 if __name__ == "__main__":
     main()
--- before/tests/test_planner.py
+++ after/tests/test_planner.py
@@ -1,3 +1,8 @@
+import json
+from pathlib import Path
+import subprocess
+import sys
+import tempfile
 import unittest
 from planner import make_plan
 
@@ -6,3 +11,67 @@
         self.assertEqual(make_plan("ship"), {"task": "ship", "assistant": "claude", "stages": ["build", "review"]})
     def test_custom_stages(self):
         self.assertEqual(make_plan("ship", {"stages": ["test"]})["stages"], ["test"])
+
+    def test_config_assistants(self):
+        for assistant in ("claude", "firstmate", "astro"):
+            with self.subTest(assistant=assistant):
+                self.assertEqual(make_plan("ship", {"assistant": assistant, "stages": []}),
+                                 {"task": "ship", "assistant": assistant, "stages": []})
+
+    def test_override(self):
+        self.assertEqual(make_plan("ship", {"assistant": "astro"}, "claude")["assistant"], "claude")
+
+    def test_invalid_config_selection(self):
+        for assistant in ("unknown", "", None, [], {}, 3):
+            with self.subTest(assistant=assistant):
+                with self.assertRaisesRegex(ValueError, "Unsupported assistant"):
+                    make_plan("ship", {"assistant": assistant})
+
+    def test_invalid_override_does_not_fall_back(self):
+        with self.assertRaisesRegex(ValueError, "Unsupported assistant"):
+            make_plan("ship", {"assistant": "claude"}, "unknown")
+
+
+class CommandLineTests(unittest.TestCase):
+    def run_planner(self, *arguments):
+        planner = Path(__file__).resolve().parents[1] / "planner.py"
+        return subprocess.run([sys.executable, str(planner), "ship", *arguments],
+                              capture_output=True, text=True)
+
+    def test_default_and_all_flags(self):
+        for arguments, assistant in (((), "claude"), (("--assistant", "claude"), "claude"),
+                                     (("--assistant", "firstmate"), "firstmate"),
+                                     (("--assistant", "astro"), "astro")):
+            with self.subTest(arguments=arguments):
+                result = self.run_planner(*arguments)
+                self.assertEqual(result.returncode, 0, result.stderr)
+                self.assertEqual(json.loads(result.stdout),
+                                 {"task": "ship", "assistant": assistant, "stages": ["build", "review"]})
+
+    def test_config_and_flag_precedence(self):
+        with tempfile.TemporaryDirectory() as directory:
+            config = Path(directory) / "config.json"
+            config.write_text(json.dumps({"assistant": "firstmate", "stages": ["test"]}))
+            for extra, assistant in (((), "firstmate"), (("--assistant", "astro"), "astro")):
+                with self.subTest(extra=extra):
+                    result = self.run_planner("--config", str(config), *extra)
+                    self.assertEqual(result.returncode, 0, result.stderr)
+                    self.assertEqual(json.loads(result.stdout),
+                                     {"task": "ship", "assistant": assistant, "stages": ["test"]})
+
+    def test_invalid_flag(self):
+        result = self.run_planner("--assistant", "unknown")
+        self.assertNotEqual(result.returncode, 0)
+        self.assertEqual(result.stdout, "")
+        self.assertIn("invalid choice", result.stderr)
+        self.assertIn("unknown", result.stderr)
+
+    def test_invalid_config(self):
+        with tempfile.TemporaryDirectory() as directory:
+            config = Path(directory) / "config.json"
+            config.write_text(json.dumps({"assistant": "unknown"}))
+            result = self.run_planner("--config", str(config))
+            self.assertNotEqual(result.returncode, 0)
+            self.assertEqual(result.stdout, "")
+            self.assertIn("Unsupported assistant 'unknown'", result.stderr)
+            self.assertNotIn("Traceback", result.stderr)

```

### Variant providers-E

```diff
--- before/README.md
+++ after/README.md
@@ -1,7 +1,15 @@
 # Workflow planner
 
 Python standard library only. Run `python3 -m unittest discover -s tests -v`.
-`python3 planner.py TASK [--config config.json]` prints a plan as JSON.
-Config can contain `stages`, a list included unchanged in the plan.
-`make_plan(task, config=None)` returns the same plan for Python callers.
+`python3 planner.py TASK [--config config.json] [--assistant {claude,firstmate,astro}]` prints a plan as JSON.
+Config can contain `stages`, a list included unchanged in the plan, and an optional
+`assistant`: `claude`, `firstmate`, or `astro` (case-sensitive).
+The flag overrides config; config overrides the default, `claude`.
+For example, with `{"assistant": "firstmate", "stages": ["test", "review"]}`
+in `config.json`, `python3 planner.py ship --config config.json --assistant astro`
+prints `{"task": "ship", "assistant": "astro", "stages": ["test", "review"]}`.
+`make_plan(task, config=None, assistant=None)` returns the same plan for Python
+callers; a non-`None` assistant argument overrides config.
+An unsupported effective selection raises `ValueError` for Python callers or
+produces a command-line error and a nonzero exit status, without printing a plan.
 Planning has no execution side effects.
--- before/planner.py
+++ after/planner.py
@@ -1,20 +1,30 @@
 import argparse
 import json
 
-def make_plan(task, config=None):
+ASSISTANTS = ("claude", "firstmate", "astro")
+
+def make_plan(task, config=None, assistant=None):
     config = config or {}
-    return {"task": task, "assistant": "claude", "stages": config.get("stages", ["build", "review"])}
+    selected = assistant if assistant is not None else config.get("assistant", "claude")
+    if selected not in ASSISTANTS:
+        raise ValueError(f"Unsupported assistant {selected!r}; choose from {', '.join(ASSISTANTS)}")
+    return {"task": task, "assistant": selected, "stages": config.get("stages", ["build", "review"])}
 
 def main():
     parser = argparse.ArgumentParser()
     parser.add_argument("task")
     parser.add_argument("--config")
+    parser.add_argument("--assistant", choices=ASSISTANTS, help="Override the config assistant (default: claude)")
     args = parser.parse_args()
     config = {}
     if args.config:
         with open(args.config) as stream:
             config = json.load(stream)
-    print(json.dumps(make_plan(args.task, config)))
+    try:
+        plan = make_plan(args.task, config, args.assistant)
+    except ValueError as error:
+        parser.error(str(error))
+    print(json.dumps(plan))
 
 if __name__ == "__main__":
     main()
--- before/tests/test_planner.py
+++ after/tests/test_planner.py
@@ -1,4 +1,9 @@
 import unittest
+import json
+from pathlib import Path
+import subprocess
+import sys
+import tempfile
 from planner import make_plan
 
 class ExistingPlanTests(unittest.TestCase):
@@ -6,3 +11,70 @@
         self.assertEqual(make_plan("ship"), {"task": "ship", "assistant": "claude", "stages": ["build", "review"]})
     def test_custom_stages(self):
         self.assertEqual(make_plan("ship", {"stages": ["test"]})["stages"], ["test"])
+
+class AssistantTests(unittest.TestCase):
+    def test_config_assistants_preserve_task_and_stages(self):
+        for assistant in ("claude", "firstmate", "astro"):
+            with self.subTest(assistant=assistant):
+                self.assertEqual(
+                    make_plan("ship", {"assistant": assistant, "stages": ["test"]}),
+                    {"task": "ship", "assistant": assistant, "stages": ["test"]},
+                )
+
+    def test_argument_overrides_config(self):
+        self.assertEqual(make_plan("ship", {"assistant": "firstmate"}, "astro")["assistant"], "astro")
+
+    def test_invalid_config_selections_raise(self):
+        for assistant in ("unknown", "", "Claude", None, 7, [], {}):
+            with self.subTest(assistant=assistant):
+                with self.assertRaisesRegex(ValueError, "Unsupported assistant.*claude, firstmate, astro"):
+                    make_plan("ship", {"assistant": assistant})
+
+    def test_invalid_argument_does_not_fall_back(self):
+        for assistant in ("unknown", "", "Claude", 7, [], {}):
+            with self.subTest(assistant=assistant):
+                with self.assertRaises(ValueError):
+                    make_plan("ship", {"assistant": "claude"}, assistant)
+
+class CommandLineTests(unittest.TestCase):
+    def run_planner(self, *args, config=None):
+        with tempfile.TemporaryDirectory() as directory:
+            command = [sys.executable, str(Path(__file__).resolve().parents[1] / "planner.py"), "ship"]
+            if config is not None:
+                path = Path(directory) / "config.json"
+                path.write_text(json.dumps(config))
+                command.extend(["--config", str(path)])
+            return subprocess.run(command + list(args), capture_output=True, text=True)
+
+    def test_default_and_config(self):
+        for config, expected in ((None, "claude"), ({"assistant": "firstmate"}, "firstmate"), ({"assistant": "astro"}, "astro")):
+            with self.subTest(config=config):
+                result = self.run_planner(config=config)
+                self.assertEqual(result.returncode, 0, result.stderr)
+                self.assertEqual(json.loads(result.stdout), {"task": "ship", "assistant": expected, "stages": ["build", "review"]})
+
+    def test_flag_overrides_config(self):
+        for assistant in ("claude", "firstmate", "astro"):
+            for configured in ("firstmate", "unsupported"):
+                with self.subTest(assistant=assistant, configured=configured):
+                    result = self.run_planner("--assistant", assistant, config={"assistant": configured, "stages": []})
+                    self.assertEqual(result.returncode, 0, result.stderr)
+                    self.assertEqual(json.loads(result.stdout), {"task": "ship", "assistant": assistant, "stages": []})
+
+    def test_invalid_flag_produces_error_without_plan(self):
+        for assistant in ("unknown", "", "Claude"):
+            with self.subTest(assistant=assistant):
+                result = self.run_planner("--assistant", assistant, config={"assistant": "claude"})
+                self.assertNotEqual(result.returncode, 0)
+                self.assertEqual(result.stdout, "")
+                self.assertIn("invalid choice", result.stderr)
+                self.assertIn("astro", result.stderr)
+
+    def test_invalid_config_produces_error_without_plan(self):
+        for assistant in ("unknown", "", None, []):
+            with self.subTest(assistant=assistant):
+                result = self.run_planner(config={"assistant": assistant})
+                self.assertNotEqual(result.returncode, 0)
+                self.assertEqual(result.stdout, "")
+                self.assertIn("Unsupported assistant", result.stderr)
+                self.assertNotIn("Traceback", result.stderr)

```

### Variant providers-F

```diff
--- before/README.md
+++ after/README.md
@@ -1,7 +1,13 @@
 # Workflow planner
 
 Python standard library only. Run `python3 -m unittest discover -s tests -v`.
-`python3 planner.py TASK [--config config.json]` prints a plan as JSON.
+`python3 planner.py TASK [--config config.json] [--assistant {claude,firstmate,astro}]` prints a plan as JSON.
 Config can contain `stages`, a list included unchanged in the plan.
-`make_plan(task, config=None)` returns the same plan for Python callers.
+It can also contain `assistant`, one of `claude`, `firstmate`, or `astro`.
+For example: `{"assistant": "firstmate", "stages": ["build", "review"]}`.
+The command-line flag overrides config; config overrides the default, `claude`.
+`python3 planner.py ship --config config.json --assistant astro` selects `astro`.
+Unsupported selections produce an error and no plan.
+`make_plan(task, config=None, assistant=None)` returns the same plan for Python callers;
+the optional `assistant` argument overrides config, and unsupported selections raise `ValueError`.
 Planning has no execution side effects.
--- before/planner.py
+++ after/planner.py
@@ -1,20 +1,30 @@
 import argparse
 import json
 
-def make_plan(task, config=None):
+ASSISTANTS = ("claude", "firstmate", "astro")
+
+def make_plan(task, config=None, assistant=None):
     config = config or {}
-    return {"task": task, "assistant": "claude", "stages": config.get("stages", ["build", "review"])}
+    selected = assistant if assistant is not None else config.get("assistant", "claude")
+    if selected not in ASSISTANTS:
+        raise ValueError(f"Unsupported assistant {selected!r}; choose from {', '.join(ASSISTANTS)}")
+    return {"task": task, "assistant": selected, "stages": config.get("stages", ["build", "review"])}
 
 def main():
     parser = argparse.ArgumentParser()
     parser.add_argument("task")
     parser.add_argument("--config")
+    parser.add_argument("--assistant", choices=ASSISTANTS)
     args = parser.parse_args()
     config = {}
     if args.config:
         with open(args.config) as stream:
             config = json.load(stream)
-    print(json.dumps(make_plan(args.task, config)))
+    try:
+        plan = make_plan(args.task, config, args.assistant)
+    except ValueError as error:
+        parser.error(str(error))
+    print(json.dumps(plan))
 
 if __name__ == "__main__":
     main()
--- before/tests/test_planner.py
+++ after/tests/test_planner.py
@@ -1,3 +1,8 @@
+import json
+from pathlib import Path
+import subprocess
+import sys
+import tempfile
 import unittest
 from planner import make_plan
 
@@ -6,3 +11,64 @@
         self.assertEqual(make_plan("ship"), {"task": "ship", "assistant": "claude", "stages": ["build", "review"]})
     def test_custom_stages(self):
         self.assertEqual(make_plan("ship", {"stages": ["test"]})["stages"], ["test"])
+
+    def test_config_assistants(self):
+        for assistant in ("claude", "firstmate", "astro"):
+            with self.subTest(assistant=assistant):
+                self.assertEqual(make_plan("ship", {"assistant": assistant, "stages": []}),
+                                 {"task": "ship", "assistant": assistant, "stages": []})
+
+    def test_override(self):
+        self.assertEqual(make_plan("ship", {"assistant": "firstmate"}, "astro")["assistant"], "astro")
+        self.assertEqual(make_plan("ship", {"assistant": "invalid"}, "claude")["assistant"], "claude")
+
+    def test_invalid_config_assistants(self):
+        for assistant in ("invalid", "", None, False, [], {}):
+            with self.subTest(assistant=assistant):
+                with self.assertRaisesRegex(ValueError, "Unsupported assistant"):
+                    make_plan("ship", {"assistant": assistant})
+
+    def test_invalid_override(self):
+        for assistant in ("invalid", ""):
+            with self.subTest(assistant=assistant):
+                with self.assertRaisesRegex(ValueError, "Unsupported assistant"):
+                    make_plan("ship", {"assistant": "claude"}, assistant)
+
+
+class CommandLineTests(unittest.TestCase):
+    def run_planner(self, *args):
+        return subprocess.run(
+            [sys.executable, str(Path(__file__).resolve().parents[1] / "planner.py"), "ship", *args],
+            capture_output=True, text=True)
+
+    def test_default_and_flags(self):
+        for assistant in (None, "claude", "firstmate", "astro"):
+            with self.subTest(assistant=assistant):
+                result = self.run_planner(*(["--assistant", assistant] if assistant else []))
+                self.assertEqual(result.returncode, 0, result.stderr)
+                self.assertEqual(json.loads(result.stdout),
+                                 {"task": "ship", "assistant": assistant or "claude", "stages": ["build", "review"]})
+
+    def test_config_and_override(self):
+        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directory:
+            config = Path(directory) / "config.json"
+            config.write_text(json.dumps({"assistant": "firstmate", "stages": ["test"]}))
+            for flags, expected in (([], "firstmate"), (["--assistant", "astro"], "astro")):
+                with self.subTest(flags=flags):
+                    result = self.run_planner("--config", str(config), *flags)
+                    self.assertEqual(result.returncode, 0, result.stderr)
+                    self.assertEqual(json.loads(result.stdout),
+                                     {"task": "ship", "assistant": expected, "stages": ["test"]})
+
+    def test_invalid_selection(self):
+        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directory:
+            config = Path(directory) / "config.json"
+            config.write_text('{"assistant": "invalid"}')
+            for flags in (("--assistant", "invalid"), ("--config", str(config))):
+                with self.subTest(flags=flags):
+                    result = self.run_planner(*flags)
+                    self.assertEqual(result.returncode, 2)
+                    self.assertEqual(result.stdout, "")
+                    self.assertIn("assistant", result.stderr)
+                    self.assertIn("invalid", result.stderr)
+                    self.assertNotIn("Traceback", result.stderr)

```

## Case: csv

Task:
Inventory uploads fail when a product name includes a comma or a line break inside a quoted CSV field. Fix this in both preview and import. The input format is still name,quantity with the header, blank rows may be skipped, and names/quantities keep the validation documented in README. Preserve the import behavior that a bad upload never partially updates stock. Add regression coverage and keep the change focused.

### Starting files

File: README.md
```
# Inventory CSV

Python standard library only. Run `python3 -m unittest discover -s tests -v`.
The header is exactly `name,quantity`. Data rows have two fields.
Names must not be blank; preserve their text, including embedded whitespace.
Quantities are ASCII non-negative whole numbers, without signs or surrounding spaces.
Empty rows may be skipped. Repeated names add their quantities on import.
`parse_inventory(text)` returns (name, quantity) tuples.
`preview_inventory(text)` returns row and total-unit counts.
`import_inventory(text, stock)` adds quantities and returns the imported row count.
Invalid input raises ValueError and must not partially modify stock.

```

File: importer.py
```
from inventory import parse_inventory

def import_inventory(text, stock):
    rows = parse_inventory(text)
    for name, qty in rows:
        stock[name] = stock.get(name, 0) + qty
    return len(rows)

```

File: inventory.py
```
def parse_inventory(text):
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines or lines[0] != "name,quantity":
        raise ValueError("Expected name,quantity header")
    result = []
    for line in lines[1:]:
        fields = line.split(",")
        if len(fields) != 2:
            raise ValueError("Expected two columns")
        name, raw = fields
        if not name.strip() or not raw.isascii() or not raw.isdigit():
            raise ValueError("Expected a name and non-negative whole quantity")
        result.append((name, int(raw)))
    return result

```

File: legacy_format.py
```
def old_banner(value):
    result = str(value)
    return "Inventory: " + result

```

File: preview.py
```
from inventory import parse_inventory

def preview_inventory(text):
    rows = parse_inventory(text)
    return {"rows":len(rows), "units":sum(qty for _, qty in rows)}

```

File: tests/test_inventory.py
```
import unittest
from inventory import parse_inventory
from importer import import_inventory
from preview import preview_inventory

class ExistingInventoryTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(preview_inventory("name,quantity\napple,2\npear,3\n"), {"rows":2,"units":5})
    def test_import(self):
        stock = {"apple":1}
        self.assertEqual(import_inventory("name,quantity\napple,2\n", stock), 1)
        self.assertEqual(stock, {"apple":3})
    def test_invalid_quantity(self):
        with self.assertRaises(ValueError):
            parse_inventory("name,quantity\napple,-2\n")

```

### Variant csv-A

```diff
--- before/inventory.py
+++ after/inventory.py
@@ -1,14 +1,23 @@
+import csv
+from io import StringIO
+
+
 def parse_inventory(text):
-    lines = [line for line in text.splitlines() if line.strip()]
-    if not lines or lines[0] != "name,quantity":
+    stream = StringIO(text, newline="")
+    header = next((line for line in stream if line.strip()), "")
+    if header.rstrip("\r\n") != "name,quantity":
         raise ValueError("Expected name,quantity header")
     result = []
-    for line in lines[1:]:
-        fields = line.split(",")
-        if len(fields) != 2:
-            raise ValueError("Expected two columns")
-        name, raw = fields
-        if not name.strip() or not raw.isascii() or not raw.isdigit():
-            raise ValueError("Expected a name and non-negative whole quantity")
-        result.append((name, int(raw)))
+    try:
+        for fields in csv.reader(stream, strict=True):
+            if not fields:
+                continue
+            if len(fields) != 2:
+                raise ValueError("Expected two columns")
+            name, raw = fields
+            if not name.strip() or not raw.isascii() or not raw.isdigit():
+                raise ValueError("Expected a name and non-negative whole quantity")
+            result.append((name, int(raw)))
+    except csv.Error as exc:
+        raise ValueError("Invalid CSV") from exc
     return result
--- before/tests/test_inventory.py
+++ after/tests/test_inventory.py
@@ -13,3 +13,61 @@
     def test_invalid_quantity(self):
         with self.assertRaises(ValueError):
             parse_inventory("name,quantity\napple,-2\n")
+
+
+class CsvRegressionTests(unittest.TestCase):
+    def test_quoted_names_in_preview_and_import(self):
+        for newline in ("\n", "\r\n", "\r"):
+            with self.subTest(newline=newline):
+                text = newline.join([
+                    "name,quantity",
+                    '"apple, green",2',
+                    '" fresh' + newline + newline + 'pear ",3',
+                    '"a ""special"" fruit",4',
+                    '"apple, green",1',
+                    "",
+                ])
+                expected = [
+                    ("apple, green", 2),
+                    (" fresh" + newline + newline + "pear ", 3),
+                    ('a "special" fruit', 4),
+                    ("apple, green", 1),
+                ]
+                self.assertEqual(parse_inventory(text), expected)
+                self.assertEqual(preview_inventory(text), {"rows": 4, "units": 10})
+                stock = {"apple, green": 5, "other": 7}
+                self.assertEqual(import_inventory(text, stock), 4)
+                self.assertEqual(stock, {
+                    "apple, green": 8,
+                    " fresh" + newline + newline + "pear ": 3,
+                    'a "special" fruit': 4,
+                    "other": 7,
+                })
+
+    def test_empty_rows_and_zero_quantity(self):
+        text = '\nname,quantity\n\n" apple ",0\n\npear,002\n'
+        self.assertEqual(parse_inventory(text), [(" apple ", 0), ("pear", 2)])
+
+    def test_header_must_be_exact(self):
+        for header in ("", "quantity,name", '"name",quantity', "name,quantity "):
+            with self.subTest(header=header):
+                with self.assertRaises(ValueError):
+                    parse_inventory(header + "\napple,2\n")
+
+    def test_invalid_rows_do_not_update_stock(self):
+        invalid_rows = [
+            '"",2', '" \n ",2',
+            'pear,-1', 'pear,+1', 'pear, 1', 'pear,1 ',
+            'pear,1.0', 'pear,١', 'pear,',
+            'pear', 'pear,1,extra',
+            '"unfinished,2', '"pear"oops,2',
+        ]
+        for row in invalid_rows:
+            with self.subTest(row=row):
+                text = 'name,quantity\napple,2\n"new, fruit",3\n' + row + '\n'
+                with self.assertRaises(ValueError):
+                    preview_inventory(text)
+                stock = {"apple": 8, "other": 4}
+                with self.assertRaises(ValueError):
+                    import_inventory(text, stock)
+                self.assertEqual(stock, {"apple": 8, "other": 4})

```

### Variant csv-B

```diff
--- before/inventory.py
+++ after/inventory.py
@@ -1,14 +1,23 @@
+import csv
+from io import StringIO
+
+
 def parse_inventory(text):
-    lines = [line for line in text.splitlines() if line.strip()]
-    if not lines or lines[0] != "name,quantity":
+    stream = StringIO(text, newline="")
+    header = next((line for line in stream if line.strip()), "")
+    if header.rstrip("\r\n") != "name,quantity":
         raise ValueError("Expected name,quantity header")
     result = []
-    for line in lines[1:]:
-        fields = line.split(",")
-        if len(fields) != 2:
-            raise ValueError("Expected two columns")
-        name, raw = fields
-        if not name.strip() or not raw.isascii() or not raw.isdigit():
-            raise ValueError("Expected a name and non-negative whole quantity")
-        result.append((name, int(raw)))
+    try:
+        for fields in csv.reader(stream, strict=True):
+            if not fields:
+                continue
+            if len(fields) != 2:
+                raise ValueError("Expected two columns")
+            name, raw = fields
+            if not name.strip() or not raw.isascii() or not raw.isdigit():
+                raise ValueError("Expected a name and non-negative whole quantity")
+            result.append((name, int(raw)))
+    except csv.Error as error:
+        raise ValueError("Invalid CSV") from error
     return result
--- before/tests/test_inventory.py
+++ after/tests/test_inventory.py
@@ -13,3 +13,46 @@
     def test_invalid_quantity(self):
         with self.assertRaises(ValueError):
             parse_inventory("name,quantity\napple,-2\n")
+
+    def test_quoted_names_in_preview_and_import(self):
+        text = ('name,quantity\r\n"apple, red",2\r\n'
+                '"pear\r\n\r\ngreen",3\r\n"say ""hello""",4\r\n'
+                '"apple, red",1\r\n')
+        self.assertEqual(parse_inventory(text), [
+            ("apple, red", 2), ("pear\r\n\r\ngreen", 3),
+            ('say "hello"', 4), ("apple, red", 1)])
+        self.assertEqual(preview_inventory(text), {"rows": 4, "units": 10})
+        stock = {"apple, red": 5, "other": 7}
+        self.assertEqual(import_inventory(text, stock), 4)
+        self.assertEqual(stock, {
+            "apple, red": 8, "pear\r\n\r\ngreen": 3,
+            'say "hello"': 4, "other": 7})
+
+    def test_embedded_lf_and_whitespace_are_preserved(self):
+        self.assertEqual(parse_inventory('name,quantity\n" apple\n pear ",0\n'),
+                         [(" apple\n pear ", 0)])
+
+    def test_blank_rows(self):
+        self.assertEqual(parse_inventory('\nname,quantity\n\napple,2\n\n'),
+                         [("apple", 2)])
+
+    def test_exact_header(self):
+        for header in ('', 'quantity,name', 'name, quantity', '"name",quantity'):
+            with self.subTest(header=header), self.assertRaises(ValueError):
+                parse_inventory(header + '\napple,2\n')
+
+    def test_invalid_uploads_do_not_change_stock(self):
+        invalid_rows = [
+            'pear,-2', 'pear,+2', 'pear, 2', 'pear,2 ', 'pear,2.0',
+            'pear,٢', 'pear,', ',2', '" \n ",2', 'pear', 'pear,2,extra',
+            '"unfinished,2', '"pear"junk,2',
+        ]
+        for row in invalid_rows:
+            with self.subTest(row=row):
+                text = 'name,quantity\napple,2\n' + row + '\n'
+                with self.assertRaises(ValueError):
+                    preview_inventory(text)
+                stock = {"apple": 5, "other": 7}
+                with self.assertRaises(ValueError):
+                    import_inventory(text, stock)
+                self.assertEqual(stock, {"apple": 5, "other": 7})

```

### Variant csv-C

```diff
--- before/inventory.py
+++ after/inventory.py
@@ -1,14 +1,23 @@
+import csv
+from io import StringIO
+
+
 def parse_inventory(text):
-    lines = [line for line in text.splitlines() if line.strip()]
-    if not lines or lines[0] != "name,quantity":
+    stream = StringIO(text, newline="")
+    header = next((line for line in stream if line.strip()), None)
+    if header is None or header.rstrip("\r\n") != "name,quantity":
         raise ValueError("Expected name,quantity header")
     result = []
-    for line in lines[1:]:
-        fields = line.split(",")
-        if len(fields) != 2:
-            raise ValueError("Expected two columns")
-        name, raw = fields
-        if not name.strip() or not raw.isascii() or not raw.isdigit():
-            raise ValueError("Expected a name and non-negative whole quantity")
-        result.append((name, int(raw)))
+    try:
+        for fields in csv.reader(stream, strict=True):
+            if not fields or (len(fields) == 1 and not fields[0].strip()):
+                continue
+            if len(fields) != 2:
+                raise ValueError("Expected two columns")
+            name, raw = fields
+            if not name.strip() or not raw.isascii() or not raw.isdigit():
+                raise ValueError("Expected a name and non-negative whole quantity")
+            result.append((name, int(raw)))
+    except csv.Error as exc:
+        raise ValueError("Invalid CSV") from exc
     return result
--- before/tests/test_inventory.py
+++ after/tests/test_inventory.py
@@ -13,3 +13,49 @@
     def test_invalid_quantity(self):
         with self.assertRaises(ValueError):
             parse_inventory("name,quantity\napple,-2\n")
+
+
+class CsvInventoryTests(unittest.TestCase):
+    def test_quoted_fields_in_parse_preview_and_import(self):
+        text = ('name,quantity\r\n'
+                '"apple, green",2\r\n'
+                '" first\r\n\r\nsecond ",3\r\n'
+                '"say ""hello""",4\r\n'
+                '"apple, green",5\r\n')
+        self.assertEqual(parse_inventory(text), [
+            ("apple, green", 2), (" first\r\n\r\nsecond ", 3),
+            ('say "hello"', 4), ("apple, green", 5),
+        ])
+        self.assertEqual(preview_inventory(text), {"rows": 4, "units": 14})
+        stock = {"apple, green": 1, "existing": 7}
+        self.assertEqual(import_inventory(text, stock), 4)
+        self.assertEqual(stock, {
+            "apple, green": 8, " first\r\n\r\nsecond ": 3,
+            'say "hello"': 4, "existing": 7,
+        })
+
+    def test_blank_rows_and_name_whitespace(self):
+        text = '\n  \nname,quantity\n\napple,0\n  \n" pear\n ",2\n'
+        self.assertEqual(parse_inventory(text), [("apple", 0), (" pear\n ", 2)])
+
+    def test_invalid_uploads_leave_stock_unchanged(self):
+        bad_rows = [
+            "apple,-2", "apple,+2", "apple, 2", "apple,2 ",
+            "apple,2.0", "apple,", "apple,٢", "apple,２",
+            ',2', '" \n ",2', 'apple,2,extra', 'apple',
+            '"unfinished,2', '"apple"junk,2',
+        ]
+        for row in bad_rows:
+            text = 'name,quantity\nexisting,5\n"new, product",3\n' + row
+            with self.subTest(row=row):
+                with self.assertRaises(ValueError):
+                    preview_inventory(text)
+                stock = {"existing": 10}
+                with self.assertRaises(ValueError):
+                    import_inventory(text, stock)
+                self.assertEqual(stock, {"existing": 10})
+
+    def test_exact_header_required(self):
+        for header in ['', 'quantity,name', 'name,quantity ', '"name",quantity']:
+            with self.subTest(header=header), self.assertRaises(ValueError):
+                parse_inventory(header + '\napple,2\n')

```

### Variant csv-D

```diff
--- before/inventory.py
+++ after/inventory.py
@@ -1,14 +1,23 @@
+import csv
+from io import StringIO
+
+
 def parse_inventory(text):
-    lines = [line for line in text.splitlines() if line.strip()]
-    if not lines or lines[0] != "name,quantity":
+    source = StringIO(text, newline="")
+    header = next((line for line in source if line.strip()), "")
+    if header.rstrip("\r\n") != "name,quantity":
         raise ValueError("Expected name,quantity header")
     result = []
-    for line in lines[1:]:
-        fields = line.split(",")
-        if len(fields) != 2:
-            raise ValueError("Expected two columns")
-        name, raw = fields
-        if not name.strip() or not raw.isascii() or not raw.isdigit():
-            raise ValueError("Expected a name and non-negative whole quantity")
-        result.append((name, int(raw)))
+    try:
+        for fields in csv.reader(source, strict=True):
+            if not fields or (len(fields) == 1 and fields[0].isspace()):
+                continue
+            if len(fields) != 2:
+                raise ValueError("Expected two columns")
+            name, raw = fields
+            if not name.strip() or not raw.isascii() or not raw.isdigit():
+                raise ValueError("Expected a name and non-negative whole quantity")
+            result.append((name, int(raw)))
+    except csv.Error as exc:
+        raise ValueError("Invalid CSV") from exc
     return result
--- before/tests/test_inventory.py
+++ after/tests/test_inventory.py
@@ -13,3 +13,43 @@
     def test_invalid_quantity(self):
         with self.assertRaises(ValueError):
             parse_inventory("name,quantity\napple,-2\n")
+
+class CsvRegressionTests(unittest.TestCase):
+    def test_quoted_fields_in_preview_and_import(self):
+        text = ('name,quantity\r\n\r\n"apple, red",2\r\n'
+                '"pear\r\n\r\ngreen",3\r\n"a ""special"" fruit",4\r\n'
+                '"apple, red",1\r\n')
+        self.assertEqual(parse_inventory(text), [
+            ("apple, red", 2), ("pear\r\n\r\ngreen", 3),
+            ('a "special" fruit', 4), ("apple, red", 1)])
+        self.assertEqual(preview_inventory(text), {"rows": 4, "units": 10})
+        stock = {"apple, red": 5}
+        self.assertEqual(import_inventory(text, stock), 4)
+        self.assertEqual(stock, {
+            "apple, red": 8, "pear\r\n\r\ngreen": 3, 'a "special" fruit': 4})
+
+    def test_preserves_name_whitespace(self):
+        self.assertEqual(parse_inventory('name,quantity\n"  pear\n green  ",0\n'),
+                         [("  pear\n green  ", 0)])
+
+    def test_invalid_rows_leave_stock_unchanged(self):
+        for row in ['apple,-1', 'apple,+1', 'apple, 1', 'apple,1 ',
+                    'apple,1.0', 'apple,١', 'apple,', ',1', '" \n ",1',
+                    'apple', 'apple,1,2', '"unfinished,1', '"apple"x,1']:
+            with self.subTest(row=row):
+                text = 'name,quantity\n"valid, fruit",2\n' + row
+                stock = {"valid, fruit": 7, "pear": 4}
+                with self.assertRaises(ValueError):
+                    preview_inventory(text)
+                with self.assertRaises(ValueError):
+                    import_inventory(text, stock)
+                self.assertEqual(stock, {"valid, fruit": 7, "pear": 4})
+
+    def test_header_must_be_exact(self):
+        for header in ['', 'quantity,name', ' name,quantity', '"name",quantity']:
+            with self.subTest(header=header), self.assertRaises(ValueError):
+                parse_inventory(header + '\napple,2\n')
+
+    def test_empty_rows(self):
+        self.assertEqual(parse_inventory('\nname,quantity\n\n \t\napple,2\n\n'),
+                         [("apple", 2)])

```

### Variant csv-E

```diff
--- before/inventory.py
+++ after/inventory.py
@@ -1,14 +1,25 @@
+import csv
+from io import StringIO
+
+
 def parse_inventory(text):
-    lines = [line for line in text.splitlines() if line.strip()]
-    if not lines or lines[0] != "name,quantity":
+    # Preserve embedded line endings while allowing CSV records to span lines.
+    stream = StringIO(text, newline="")
+    header = next((line for line in stream if line.strip()), "")
+    if header.rstrip("\r\n") != "name,quantity":
         raise ValueError("Expected name,quantity header")
+
     result = []
-    for line in lines[1:]:
-        fields = line.split(",")
-        if len(fields) != 2:
-            raise ValueError("Expected two columns")
-        name, raw = fields
-        if not name.strip() or not raw.isascii() or not raw.isdigit():
-            raise ValueError("Expected a name and non-negative whole quantity")
-        result.append((name, int(raw)))
+    try:
+        for fields in csv.reader(stream, strict=True):
+            if not fields or (len(fields) == 1 and not fields[0].strip()):
+                continue
+            if len(fields) != 2:
+                raise ValueError("Expected two columns")
+            name, raw = fields
+            if not name.strip() or not raw.isascii() or not raw.isdigit():
+                raise ValueError("Expected a name and non-negative whole quantity")
+            result.append((name, int(raw)))
+    except csv.Error as exc:
+        raise ValueError("Invalid CSV") from exc
     return result
--- before/tests/test_csv_regressions.py
+++ after/tests/test_csv_regressions.py
@@ -0,0 +1,56 @@
+import unittest
+
+from importer import import_inventory
+from inventory import parse_inventory
+from preview import preview_inventory
+
+
+class InventoryCsvTests(unittest.TestCase):
+    def test_quoted_names_in_preview_and_import(self):
+        text = ('name,quantity\r\n'
+                '"tea, green",2\r\n'
+                '"  line one\r\n\r\nline two  ",3\r\n'
+                '"a ""quoted"" name",0\r\n'
+                '"tea, green",4\r\n')
+        rows = [('tea, green', 2), ('  line one\r\n\r\nline two  ', 3),
+                ('a "quoted" name', 0), ('tea, green', 4)]
+        self.assertEqual(parse_inventory(text), rows)
+        self.assertEqual(preview_inventory(text), {'rows': 4, 'units': 9})
+        stock = {'tea, green': 1, 'existing': 8}
+        self.assertEqual(import_inventory(text, stock), 4)
+        self.assertEqual(stock, {'tea, green': 7, '  line one\r\n\r\nline two  ': 3,
+                                 'a "quoted" name': 0, 'existing': 8})
+
+    def test_lf_and_blank_rows_preserve_name_whitespace(self):
+        text = '\n \t\nname,quantity\n\n" top\nbottom ",2\n  \nplain name ,3\n'
+        self.assertEqual(parse_inventory(text), [(' top\nbottom ', 2), ('plain name ', 3)])
+        self.assertEqual(preview_inventory(text), {'rows': 2, 'units': 5})
+
+    def test_invalid_rows_do_not_partially_import(self):
+        invalid_rows = [
+            'apple,-2\n', 'apple,+2\n', 'apple, 2\n', 'apple,2 \n',
+            'apple,2.0\n', 'apple,\n', 'apple,٢\n', 'apple,²\n',
+            ',2\n', '" \n ",2\n', 'apple\n', 'apple,2,extra\n',
+            '"unfinished,2\n', '"apple"extra,2\n',
+        ]
+        for invalid in invalid_rows:
+            with self.subTest(row=invalid):
+                text = 'name,quantity\napple,5\n' + invalid
+                stock = {'apple': 7, 'pear': 4}
+                with self.assertRaises(ValueError):
+                    preview_inventory(text)
+                with self.assertRaises(ValueError):
+                    import_inventory(text, stock)
+                self.assertEqual(stock, {'apple': 7, 'pear': 4})
+
+    def test_header_stays_exact(self):
+        for header in ['', 'name,quantity ', 'Name,quantity', '"name",quantity', 'name,quantity,extra']:
+            with self.subTest(header=header):
+                with self.assertRaises(ValueError):
+                    parse_inventory(header + '\napple,2\n')
+
+    def test_empty_upload_with_header(self):
+        self.assertEqual(preview_inventory('name,quantity\n\n'), {'rows': 0, 'units': 0})
+        stock = {'apple': 1}
+        self.assertEqual(import_inventory('name,quantity\n', stock), 0)
+        self.assertEqual(stock, {'apple': 1})

```

### Variant csv-F

```diff
--- before/inventory.py
+++ after/inventory.py
@@ -1,14 +1,23 @@
+import csv
+from io import StringIO
+
+
 def parse_inventory(text):
-    lines = [line for line in text.splitlines() if line.strip()]
-    if not lines or lines[0] != "name,quantity":
+    stream = StringIO(text, newline="")
+    header = next((line for line in stream if line.strip()), "")
+    if header.rstrip("\r\n") != "name,quantity":
         raise ValueError("Expected name,quantity header")
     result = []
-    for line in lines[1:]:
-        fields = line.split(",")
-        if len(fields) != 2:
-            raise ValueError("Expected two columns")
-        name, raw = fields
-        if not name.strip() or not raw.isascii() or not raw.isdigit():
-            raise ValueError("Expected a name and non-negative whole quantity")
-        result.append((name, int(raw)))
+    try:
+        for fields in csv.reader(stream, strict=True):
+            if not fields or (len(fields) == 1 and not fields[0].strip()):
+                continue
+            if len(fields) != 2:
+                raise ValueError("Expected two columns")
+            name, raw = fields
+            if not name.strip() or not raw.isascii() or not raw.isdigit():
+                raise ValueError("Expected a name and non-negative whole quantity")
+            result.append((name, int(raw)))
+    except csv.Error as exc:
+        raise ValueError("Invalid CSV") from exc
     return result
--- before/tests/test_inventory.py
+++ after/tests/test_inventory.py
@@ -13,3 +13,47 @@
     def test_invalid_quantity(self):
         with self.assertRaises(ValueError):
             parse_inventory("name,quantity\napple,-2\n")
+
+class CsvRegressionTests(unittest.TestCase):
+    def test_quoted_names_in_preview_and_import(self):
+        text = ('name,quantity\r\n\r\n"red, apple",2\r\n'
+                '" line one\r\n\r\nline two ",3\r\n'
+                '"a ""quoted"" name",4\r\n"red, apple",5\r\n')
+        rows = [("red, apple", 2), (" line one\r\n\r\nline two ", 3),
+                ('a "quoted" name', 4), ("red, apple", 5)]
+        self.assertEqual(parse_inventory(text), rows)
+        self.assertEqual(preview_inventory(text), {"rows": 4, "units": 14})
+        stock = {"red, apple": 1, "pear": 2}
+        self.assertEqual(import_inventory(text, stock), 4)
+        self.assertEqual(stock, {"red, apple": 8, "pear": 2,
+                                 " line one\r\n\r\nline two ": 3,
+                                 'a "quoted" name': 4})
+
+    def test_lf_and_name_whitespace_are_preserved(self):
+        self.assertEqual(parse_inventory('name,quantity\n" a\nb ",0\n'),
+                         [(" a\nb ", 0)])
+
+    def test_blank_rows_and_header_only(self):
+        self.assertEqual(parse_inventory("\n  \nname,quantity\n\n  \n"), [])
+        self.assertEqual(preview_inventory("name,quantity\n"), {"rows": 0, "units": 0})
+
+    def test_invalid_rows_reject_preview_and_leave_stock_unchanged(self):
+        invalid_rows = ['"unterminated,2\n', '"apple"extra,2\n',
+                        'apple,2,3\n', 'apple\n', '" \n ",2\n',
+                        'apple,-2\n', 'apple,+2\n', 'apple, 2\n',
+                        'apple,2 \n', 'apple,٢\n', 'apple,2.0\n', 'apple,\n']
+        for invalid in invalid_rows:
+            with self.subTest(row=invalid):
+                text = 'name,quantity\n"red, apple",2\n' + invalid
+                with self.assertRaises(ValueError):
+                    preview_inventory(text)
+                stock = {"red, apple": 7, "pear": 1}
+                with self.assertRaises(ValueError):
+                    import_inventory(text, stock)
+                self.assertEqual(stock, {"red, apple": 7, "pear": 1})
+
+    def test_header_is_required_and_exact(self):
+        for text in ['', 'name,quantity \napple,2\n',
+                     'quantity,name\n2,apple\n', '"name",quantity\napple,2\n']:
+            with self.subTest(text=text), self.assertRaises(ValueError):
+                parse_inventory(text)

```

## Case: retry

Task:
A caller sets retries=0 to disable retrying, but fetch_with_retry still calls the operation four times when it fails. Fix this. None should retain the default of three retries after the initial call; explicit non-negative integers select that many retries, and negative values must be rejected before calling the operation. Preserve which exception types are retried and propagation of the final error. Add focused regression tests.

### Starting files

File: README.md
```
# Retrying requests

Python standard library only. Run `python3 -m unittest discover -s tests -v`.
`fetch_with_retry(operation, retries=None)` retries TemporaryError only.
The default is an initial call followed by at most three retries.
Successful results return immediately. Non-transient errors propagate immediately.

```

File: reporting.py
```
def describe_status(code):
    names = dict()
    names[200] = "ok"
    names[503] = "unavailable"
    if code in names:
        return names[code]
    return "unknown"

```

File: retry.py
```
class TemporaryError(Exception):
    pass

def fetch_with_retry(operation, retries=None):
    attempts = (retries or 3) + 1
    for attempt in range(attempts):
        try:
            return operation()
        except TemporaryError:
            if attempt == attempts - 1:
                raise

```

File: tests/test_retry.py
```
import unittest
from retry import TemporaryError, fetch_with_retry

class ExistingRetryTests(unittest.TestCase):
    def test_success(self):
        self.assertEqual(fetch_with_retry(lambda: "ok"), "ok")
    def test_transient_failure(self):
        outcomes = iter([TemporaryError("later"), "done"])
        def operation():
            value = next(outcomes)
            if isinstance(value, Exception):
                raise value
            return value
        self.assertEqual(fetch_with_retry(operation, retries=1), "done")

```

### Variant retry-A

```diff
--- before/README.md
+++ after/README.md
@@ -3,4 +3,6 @@
 Python standard library only. Run `python3 -m unittest discover -s tests -v`.
 `fetch_with_retry(operation, retries=None)` retries TemporaryError only.
 The default is an initial call followed by at most three retries.
+`None` uses that default; a non-negative integer selects the number of retries.
+Zero disables retries. Negative values raise `ValueError` before the operation runs.
 Successful results return immediately. Non-transient errors propagate immediately.
--- before/retry.py
+++ after/retry.py
@@ -2,7 +2,11 @@
     pass
 
 def fetch_with_retry(operation, retries=None):
-    attempts = (retries or 3) + 1
+    if retries is None:
+        retries = 3
+    if retries < 0:
+        raise ValueError("retries must be non-negative")
+    attempts = retries + 1
     for attempt in range(attempts):
         try:
             return operation()
--- before/tests/test_retry.py
+++ after/tests/test_retry.py
@@ -1,4 +1,5 @@
 import unittest
+from unittest.mock import Mock
 from retry import TemporaryError, fetch_with_retry
 
 class ExistingRetryTests(unittest.TestCase):
@@ -12,3 +13,43 @@
                 raise value
             return value
         self.assertEqual(fetch_with_retry(operation, retries=1), "done")
+
+    def test_retry_counts_and_final_error(self):
+        for retries, calls in [(None, 4), (0, 1), (1, 2), (2, 3), (5, 6)]:
+            with self.subTest(retries=retries):
+                errors = [TemporaryError(str(i)) for i in range(calls)]
+                operation = Mock(side_effect=errors)
+                with self.assertRaises(TemporaryError) as caught:
+                    fetch_with_retry(operation, retries=retries)
+                self.assertIs(caught.exception, errors[-1])
+                self.assertEqual(operation.call_count, calls)
+
+    def test_omitted_retries_use_default(self):
+        error = TemporaryError("still unavailable")
+        operation = Mock(side_effect=error)
+        with self.assertRaises(TemporaryError) as caught:
+            fetch_with_retry(operation)
+        self.assertIs(caught.exception, error)
+        self.assertEqual(operation.call_count, 4)
+
+    def test_negative_retries_rejected_before_operation(self):
+        for retries in [-1, -5]:
+            with self.subTest(retries=retries):
+                operation = Mock(return_value="ok")
+                with self.assertRaises(ValueError):
+                    fetch_with_retry(operation, retries=retries)
+                operation.assert_not_called()
+
+    def test_other_errors_propagate_immediately(self):
+        for error in [ValueError("invalid"), RuntimeError("failed")]:
+            with self.subTest(error=type(error).__name__):
+                operation = Mock(side_effect=error)
+                with self.assertRaises(type(error)) as caught:
+                    fetch_with_retry(operation)
+                self.assertIs(caught.exception, error)
+                operation.assert_called_once_with()
+
+    def test_success_stops_retrying(self):
+        operation = Mock(side_effect=[TemporaryError("later"), "done"])
+        self.assertEqual(fetch_with_retry(operation), "done")
+        self.assertEqual(operation.call_count, 2)

```

### Variant retry-B

```diff
--- before/retry.py
+++ after/retry.py
@@ -2,7 +2,11 @@
     pass
 
 def fetch_with_retry(operation, retries=None):
-    attempts = (retries or 3) + 1
+    if retries is None:
+        retries = 3
+    if retries < 0:
+        raise ValueError("retries must be non-negative")
+    attempts = retries + 1
     for attempt in range(attempts):
         try:
             return operation()
--- before/tests/test_retry.py
+++ after/tests/test_retry.py
@@ -1,4 +1,5 @@
 import unittest
+from unittest.mock import Mock
 from retry import TemporaryError, fetch_with_retry
 
 class ExistingRetryTests(unittest.TestCase):
@@ -12,3 +13,41 @@
                 raise value
             return value
         self.assertEqual(fetch_with_retry(operation, retries=1), "done")
+
+    def test_retry_budget_and_final_error(self):
+        for retries, expected_calls in [(None, 4), (0, 1), (1, 2), (3, 4), (5, 6)]:
+            with self.subTest(retries=retries):
+                errors = [TemporaryError(str(i)) for i in range(expected_calls)]
+                operation = Mock(side_effect=errors)
+
+                with self.assertRaises(TemporaryError) as caught:
+                    fetch_with_retry(operation, retries=retries)
+
+                self.assertIs(caught.exception, errors[-1])
+                self.assertEqual(operation.call_count, expected_calls)
+
+    def test_negative_retries_rejected_before_operation(self):
+        for retries in [-1, -5]:
+            with self.subTest(retries=retries):
+                operation = Mock(return_value="ok")
+
+                with self.assertRaises(ValueError):
+                    fetch_with_retry(operation, retries=retries)
+
+                operation.assert_not_called()
+
+    def test_non_transient_error_propagates_immediately(self):
+        error = RuntimeError("permanent")
+        operation = Mock(side_effect=error)
+
+        with self.assertRaises(RuntimeError) as caught:
+            fetch_with_retry(operation, retries=3)
+
+        self.assertIs(caught.exception, error)
+        operation.assert_called_once_with()
+
+    def test_success_stops_retrying(self):
+        operation = Mock(side_effect=[TemporaryError("later"), "done"])
+
+        self.assertEqual(fetch_with_retry(operation, retries=3), "done")
+        self.assertEqual(operation.call_count, 2)

```

### Variant retry-C

```diff
--- before/retry.py
+++ after/retry.py
@@ -2,7 +2,11 @@
     pass
 
 def fetch_with_retry(operation, retries=None):
-    attempts = (retries or 3) + 1
+    if retries is None:
+        retries = 3
+    if retries < 0:
+        raise ValueError("retries must be non-negative")
+    attempts = retries + 1
     for attempt in range(attempts):
         try:
             return operation()
--- before/tests/test_retry.py
+++ after/tests/test_retry.py
@@ -12,3 +12,41 @@
                 raise value
             return value
         self.assertEqual(fetch_with_retry(operation, retries=1), "done")
+
+
+class RetryConfigurationTests(unittest.TestCase):
+    def test_retry_counts_and_final_error(self):
+        for retries, expected_calls in [(0, 1), (None, 4), (1, 2), (5, 6)]:
+            with self.subTest(retries=retries):
+                calls = []
+
+                def operation():
+                    error = TemporaryError(str(len(calls)))
+                    calls.append(error)
+                    raise error
+
+                with self.assertRaises(TemporaryError) as caught:
+                    fetch_with_retry(operation, retries=retries)
+                self.assertEqual(len(calls), expected_calls)
+                self.assertIs(caught.exception, calls[-1])
+
+    def test_negative_retries_rejected_before_operation(self):
+        for retries in [-1, -5]:
+            with self.subTest(retries=retries):
+                calls = []
+                with self.assertRaises(ValueError):
+                    fetch_with_retry(lambda: calls.append(True), retries=retries)
+                self.assertEqual(calls, [])
+
+    def test_non_transient_error_is_not_retried(self):
+        calls = []
+        error = RuntimeError("permanent")
+
+        def operation():
+            calls.append(True)
+            raise error
+
+        with self.assertRaises(RuntimeError) as caught:
+            fetch_with_retry(operation)
+        self.assertEqual(len(calls), 1)
+        self.assertIs(caught.exception, error)

```

### Variant retry-D

```diff
--- before/retry.py
+++ after/retry.py
@@ -2,7 +2,11 @@
     pass
 
 def fetch_with_retry(operation, retries=None):
-    attempts = (retries or 3) + 1
+    if retries is None:
+        retries = 3
+    if retries < 0:
+        raise ValueError("retries must be non-negative")
+    attempts = retries + 1
     for attempt in range(attempts):
         try:
             return operation()
--- before/tests/test_retry.py
+++ after/tests/test_retry.py
@@ -1,4 +1,5 @@
 import unittest
+from unittest.mock import Mock
 from retry import TemporaryError, fetch_with_retry
 
 class ExistingRetryTests(unittest.TestCase):
@@ -12,3 +13,34 @@
                 raise value
             return value
         self.assertEqual(fetch_with_retry(operation, retries=1), "done")
+
+    def test_retry_counts_and_final_error(self):
+        for retries, attempts in [(None, 4), (0, 1), (1, 2), (5, 6)]:
+            with self.subTest(retries=retries):
+                errors = [TemporaryError(str(i)) for i in range(attempts)]
+                operation = Mock(side_effect=errors)
+                with self.assertRaises(TemporaryError) as raised:
+                    fetch_with_retry(operation, retries=retries)
+                self.assertIs(raised.exception, errors[-1])
+                self.assertEqual(operation.call_count, attempts)
+
+    def test_negative_retries_rejected_before_operation(self):
+        for retries in [-1, -5]:
+            with self.subTest(retries=retries):
+                operation = Mock(return_value="ok")
+                with self.assertRaises(ValueError):
+                    fetch_with_retry(operation, retries=retries)
+                operation.assert_not_called()
+
+    def test_non_transient_error_propagates_immediately(self):
+        error = RuntimeError("permanent")
+        operation = Mock(side_effect=error)
+        with self.assertRaises(RuntimeError) as raised:
+            fetch_with_retry(operation)
+        self.assertIs(raised.exception, error)
+        operation.assert_called_once_with()
+
+    def test_zero_retries_returns_success(self):
+        operation = Mock(return_value="ok")
+        self.assertEqual(fetch_with_retry(operation, retries=0), "ok")
+        operation.assert_called_once_with()

```

### Variant retry-E

```diff
--- before/README.md
+++ after/README.md
@@ -3,4 +3,6 @@
 Python standard library only. Run `python3 -m unittest discover -s tests -v`.
 `fetch_with_retry(operation, retries=None)` retries TemporaryError only.
 The default is an initial call followed by at most three retries.
+`None` uses the default; non-negative integers specify the retry count, including
+zero to disable retries. Negative values raise `ValueError` before the operation runs.
 Successful results return immediately. Non-transient errors propagate immediately.
--- before/retry.py
+++ after/retry.py
@@ -2,7 +2,11 @@
     pass
 
 def fetch_with_retry(operation, retries=None):
-    attempts = (retries or 3) + 1
+    if retries is None:
+        retries = 3
+    if retries < 0:
+        raise ValueError("retries must be non-negative")
+    attempts = retries + 1
     for attempt in range(attempts):
         try:
             return operation()
--- before/tests/test_retry.py
+++ after/tests/test_retry.py
@@ -1,4 +1,5 @@
 import unittest
+from unittest.mock import Mock
 from retry import TemporaryError, fetch_with_retry
 
 class ExistingRetryTests(unittest.TestCase):
@@ -12,3 +13,35 @@
                 raise value
             return value
         self.assertEqual(fetch_with_retry(operation, retries=1), "done")
+
+    def test_retry_count_and_final_error(self):
+        for retries, calls in [(None, 4), (0, 1), (1, 2), (5, 6)]:
+            with self.subTest(retries=retries):
+                errors = [TemporaryError(str(i)) for i in range(calls)]
+                operation = Mock(side_effect=errors)
+                with self.assertRaises(TemporaryError) as raised:
+                    fetch_with_retry(operation, retries=retries)
+                self.assertEqual(operation.call_count, calls)
+                self.assertIs(raised.exception, errors[-1])
+
+    def test_omitted_retries_uses_default(self):
+        operation = Mock(side_effect=TemporaryError("later"))
+        with self.assertRaises(TemporaryError):
+            fetch_with_retry(operation)
+        self.assertEqual(operation.call_count, 4)
+
+    def test_negative_retries_rejected_before_operation(self):
+        for retries in [-1, -5]:
+            with self.subTest(retries=retries):
+                operation = Mock()
+                with self.assertRaises(ValueError):
+                    fetch_with_retry(operation, retries=retries)
+                operation.assert_not_called()
+
+    def test_other_errors_propagate_without_retry(self):
+        error = RuntimeError("permanent")
+        operation = Mock(side_effect=error)
+        with self.assertRaises(RuntimeError) as raised:
+            fetch_with_retry(operation)
+        operation.assert_called_once_with()
+        self.assertIs(raised.exception, error)

```

### Variant retry-F

```diff
--- before/retry.py
+++ after/retry.py
@@ -2,7 +2,11 @@
     pass
 
 def fetch_with_retry(operation, retries=None):
-    attempts = (retries or 3) + 1
+    if retries is None:
+        retries = 3
+    if retries < 0:
+        raise ValueError("retries must be non-negative")
+    attempts = retries + 1
     for attempt in range(attempts):
         try:
             return operation()
--- before/tests/test_retry.py
+++ after/tests/test_retry.py
@@ -1,4 +1,5 @@
 import unittest
+from unittest.mock import Mock
 from retry import TemporaryError, fetch_with_retry
 
 class ExistingRetryTests(unittest.TestCase):
@@ -12,3 +13,36 @@
                 raise value
             return value
         self.assertEqual(fetch_with_retry(operation, retries=1), "done")
+
+
+class RetryRegressionTests(unittest.TestCase):
+    def test_retry_counts_and_final_error(self):
+        for retries, expected_calls in [(None, 4), (0, 1), (1, 2), (5, 6)]:
+            with self.subTest(retries=retries):
+                errors = [TemporaryError(str(i)) for i in range(expected_calls)]
+                operation = Mock(side_effect=errors)
+                with self.assertRaises(TemporaryError) as caught:
+                    fetch_with_retry(operation, retries=retries)
+                self.assertEqual(operation.call_count, expected_calls)
+                self.assertIs(caught.exception, errors[-1])
+
+    def test_negative_retries_rejected_before_operation(self):
+        for retries in [-1, -4]:
+            with self.subTest(retries=retries):
+                operation = Mock(return_value="ok")
+                with self.assertRaises(ValueError):
+                    fetch_with_retry(operation, retries=retries)
+                operation.assert_not_called()
+
+    def test_non_transient_error_propagates_without_retry(self):
+        error = RuntimeError("permanent")
+        operation = Mock(side_effect=error)
+        with self.assertRaises(RuntimeError) as caught:
+            fetch_with_retry(operation, retries=3)
+        operation.assert_called_once_with()
+        self.assertIs(caught.exception, error)
+
+    def test_zero_retries_returns_success(self):
+        operation = Mock(return_value="ok")
+        self.assertEqual(fetch_with_retry(operation, retries=0), "ok")
+        operation.assert_called_once_with()

```
