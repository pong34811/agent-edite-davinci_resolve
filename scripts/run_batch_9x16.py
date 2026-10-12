"""Run build_9x16_batch for a list of originals, one process per timeline, verify stills after each; stop on first failure.

Each build/verify is its own process (clean Resolve connection; the earlier hand-built run hung Resolve when many
timelines were created in one tight loop). A pause between timelines and an `is_rendering` check guard stability.

Usage: python -m scripts.run_batch_9x16 names.txt        (one original name per line)
Appends to exports/9x16-batch2/batch_log.jsonl
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "exports" / "9x16-batch2" / "batch_log.jsonl"
PAUSE = 6


def run(args, timeout=900):
    p = subprocess.run([sys.executable, "-m", "scripts.build_9x16_batch", *args], cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    names = [x.strip() for x in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if x.strip()]
    LOG.parent.mkdir(parents=True, exist_ok=True)
    for n in names:
        rec = {"name": n, "t": time.strftime("%H:%M:%S")}
        rc, out = run([n, "--apply"])
        rec["build_rc"] = rc
        rec["build_tail"] = out.strip().splitlines()[-1][:300] if out.strip() else ""
        if rc != 0 or "BUILD_OK" not in out or "protected_equal True" not in out:
            rec["status"] = "BUILD_FAIL"
            rec["detail"] = out[-1500:]
            LOG.open("a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
            print("STOP build failed:", n, flush=True)
            return 1
        time.sleep(PAUSE)
        rc, out = run(["--verify", n + "_9x16"])
        rec["verify_rc"] = rc
        rec["stills"] = [l[:400] for l in out.splitlines() if l.startswith("{'kind'")]
        bad = [l for l in rec["stills"] if "'dark_row_runs': []" not in l]
        rec["status"] = "OK" if rc == 0 and rec["stills"] and not bad else "VERIFY_ATTENTION"
        if bad:
            rec["dark_rows"] = bad
        LOG.open("a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(rec["status"], n, flush=True)
        if rc != 0:
            print("STOP verify failed:", n, flush=True)
            return 1
        time.sleep(PAUSE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
