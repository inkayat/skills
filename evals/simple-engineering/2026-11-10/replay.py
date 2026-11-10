"""Replay recorded outputs: python3 replay.py [--posthoc] [r01 ...]."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile


def main():
    root = Path(__file__).resolve().parent
    runs = {row['id']: row for row in json.loads((root / 'runs.json').read_text())}
    arguments = sys.argv[1:]
    posthoc = '--posthoc' in arguments
    requested = [arg for arg in arguments if arg != '--posthoc'] or list(runs)
    unknown = set(requested) - runs.keys()
    if unknown:
        raise SystemExit('Unknown runs: ' + ', '.join(sorted(unknown)))
    failed = []
    for identifier in requested:
        case = root / 'cases' / runs[identifier]['case']
        with tempfile.TemporaryDirectory(prefix='simple-engineering-replay-') as temporary:
            target = Path(temporary) / 'workspace'
            shutil.copytree(case / 'fixture', target)
            subprocess.run(['git', 'init', '-q', str(target)], check=True)
            patch = root / 'results' / identifier / 'change.patch'
            subprocess.run(['git', 'apply', '--check', str(patch)], cwd=target, check=True)
            subprocess.run(['git', 'apply', str(patch)], cwd=target, check=True)
            public = [sys.executable, '-m', 'unittest', '-v'] if runs[identifier]['case'] == 'heldout' else [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']
            checks = [('public', public), ('contract', [sys.executable, str(case / 'grader.py'), str(target)])]
            if posthoc and runs[identifier]['case'] == 'csv':
                checks.append(('posthoc-csv', [sys.executable, str(root / 'diagnostics/csv_grader.py'), str(target)]))
            for label, command in checks:
                result = subprocess.run(command, cwd=target, capture_output=True, text=True, timeout=60)
                status = 'PASS' if result.returncode == 0 else 'FAIL'
                print(f'{identifier} {label}: {status}', flush=True)
                if result.returncode:
                    print(result.stdout + result.stderr)
                    failed.append((identifier, label))
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
