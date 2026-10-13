"""Create a 9x16 vertical for one source, then apply the verified crop fix.

Two-step pipeline, both already independently verified this session:
1. scripts.armigon_9x16_batch_one.main(source_id) builds the full vertical
   timeline structure (tracks, subtitle/audio preservation, focus overlay).
2. scripts.apply_group_fix.apply_fix(new_id) overwrites the V1/V3/V6 crop
   transforms with the verified non-duplicating geometry.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from scripts import armigon_9x16_batch_one as creator
from scripts.apply_group_fix import apply_fix

OUT = Path(".hermes/reports/vertical-layout-qc/group-calibration")
LOG = OUT / "create-and-fix-log.json"


def run_one(source_id):
    record = {"source_id": source_id}
    try:
        create_result = creator.main(source_id)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        record["create_status"] = "FAILED"
        record["create_error"] = repr(exc)
        return record
    record["create_status"] = "PASS"
    return record


def main():
    ids = sys.argv[1:]
    existing = json.loads(LOG.read_text(encoding="utf-8")) if LOG.is_file() else []
    done = {row["source_id"] for row in existing if row.get("fix_status") == "PASS"}
    for sid in ids:
        if sid in done:
            print(json.dumps({"source_id": sid, "status": "SKIPPED_ALREADY_DONE"}))
            continue
        record = {"source_id": sid}
        try:
            before_logs = set(creator.OUT_DIR.glob(f"batch_{sid}_*.json"))
            creator.main(sid)
            after_logs = set(creator.OUT_DIR.glob(f"batch_{sid}_*.json")) - before_logs
            assert len(after_logs) == 1, f"expected exactly one new batch log, found {after_logs}"
            create_payload = json.loads(next(iter(after_logs)).read_text(encoding="utf-8"))
            assert create_payload.get("status") == "PASS", create_payload.get("error")
            target_id = create_payload["target_id"]
            record["create_status"] = "PASS"
            record["target_id"] = target_id
            time.sleep(1.0)
            fix_record = apply_fix(target_id)
            fix_record["fix_status"] = fix_record.pop("status", "UNKNOWN")
            record.update(fix_record)
        except Exception as exc:  # noqa: BLE001
            record["error"] = repr(exc)
            record.setdefault("create_status", "FAILED")
        existing.append(record)
        LOG.write_text(json.dumps(existing, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(json.dumps(record, ensure_ascii=False, default=str))
        time.sleep(1.5)


if __name__ == "__main__":
    main()
