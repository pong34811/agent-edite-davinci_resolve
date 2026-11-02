import os, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "highlight"))
# tests need a job to load; config.py has no default. Explicit HIGHLIGHT_JOB still wins.
os.environ.setdefault("HIGHLIGHT_JOB", str(ROOT / "work" / "highlight" / "hoshi" / "2026-10-03" / "job.json"))
