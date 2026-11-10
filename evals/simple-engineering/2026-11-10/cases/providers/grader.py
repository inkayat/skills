import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
TARGET = Path(sys.argv.pop(1)).resolve()
sys.path.insert(0, str(TARGET))

class Contract(unittest.TestCase):
    def cli(self, config=None, assistant=None):
        with tempfile.TemporaryDirectory() as tmp:
            argv = [sys.executable, str(TARGET / "planner.py"), "release"]
            if config is not None:
                path = Path(tmp) / "config.json"
                path.write_text(json.dumps(config))
                argv += ["--config", str(path)]
            if assistant is not None:
                argv += ["--assistant", assistant]
            return subprocess.run(argv, cwd=TARGET, capture_output=True, text=True, timeout=10)
    def test_default_and_existing_stages(self):
        from planner import make_plan
        self.assertEqual(make_plan("x"), {"task":"x", "assistant":"claude", "stages":["build","review"]})
        self.assertEqual(make_plan("x", {"stages":[]})["stages"], [])
    def test_config_all_three(self):
        from planner import make_plan
        for name in ["claude", "firstmate", "astro"]:
            with self.subTest(name=name):
                self.assertEqual(make_plan("x", {"assistant":name})["assistant"], name)
    def test_cli_all_three(self):
        for name in ["claude", "firstmate", "astro"]:
            with self.subTest(name=name):
                result = self.cli(assistant=name)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["assistant"], name)
    def test_cli_precedence_and_output(self):
        result = self.cli({"assistant":"astro", "stages":["qa"]}, "firstmate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"task":"release", "assistant":"firstmate", "stages":["qa"]})
    def test_config_rejects_unknown(self):
        from planner import make_plan
        with self.assertRaises(ValueError):
            make_plan("x", {"assistant":"unknown-provider"})
        result = self.cli({"assistant":"unknown-provider"})
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.strip())
    def test_cli_rejects_unknown(self):
        result = self.cli(assistant="unknown-provider")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.strip())

if __name__ == "__main__":
    unittest.main(verbosity=2)
