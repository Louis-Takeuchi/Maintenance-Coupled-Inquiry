from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent
for cache in root.rglob("__pycache__"):
    shutil.rmtree(cache, ignore_errors=True)
for pyc in root.rglob("*.pyc"):
    pyc.unlink(missing_ok=True)
env = os.environ.copy()
env["PYTHONDONTWRITEBYTECODE"] = "1"
env["PYTHONPATH"] = str(root / "src")
raise SystemExit(subprocess.run([sys.executable, "-B", "-m", "pytest", "-q"], cwd=root, env=env).returncode)
