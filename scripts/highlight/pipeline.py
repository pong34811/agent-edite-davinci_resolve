"""Stage runner: python pipeline.py <inventory|features|shortlist|transcribe|sheets|packets|briefs>. Outputs are cached per stage."""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
import config

def ids():
    return [r["source_id"] for r in json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))]

def stage_inventory():
    import inventory; inventory.main()

def stage_features():
    import features
    with ThreadPoolExecutor(min(len(ids()), 8)) as ex:
        for sid, p in zip(ids(), ex.map(features.extract, ids())):
            print(sid, p, flush=True)

def stage_shortlist():
    import shortlist
    for sid in ids():
        res = shortlist.top(sid)
        starts = [w[0] for w in res]; ends = [w[1] for w in res]
        assert all(ends[i] < starts[i + 1] for i in range(len(res) - 1)), "overlap"
        print(sid, len(res), "windows", flush=True)

def stage_transcribe():
    import transcribe
    for sid in ids():
        print(sid, transcribe.run(sid), flush=True)

def stage_sheets():
    import contact_sheet; contact_sheet.run_all()

def stage_briefs():
    import briefs; briefs.run_all()

def stage_packets():
    import packets; packets.run_all()

if __name__ == "__main__":
    t = time.time(); globals()[f"stage_{sys.argv[1]}"](); print("done", round(time.time() - t, 1), "s")
