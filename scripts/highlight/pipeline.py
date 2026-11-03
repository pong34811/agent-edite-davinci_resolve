"""Stage runner: python pipeline.py <inventory|features|shortlist|transcribe|fulltext|readpacks|readbriefs|proposals|sheets|packets|briefs>. Outputs are cached per stage.
`fulltext` (whole video, word timestamps) is optional; when present, packets and snap.py use its sentences,
and `readpacks` -> reader subagents -> `proposals` let agents find moments by reading the whole stream."""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
import config

def ids():
    return [r["source_id"] for r in json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))]

def stage_inventory():
    import inventory; inventory.main()

def stage_features():
    import features
    # DEMUX_WORKERS: 8 parallel reads from G:/My Drive cut wavs short with exit 0; use 1-2 for cloud folders
    with ThreadPoolExecutor(min(len(ids()), int(config._job.get("DEMUX_WORKERS", 8)))) as ex:
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

def stage_fulltext():
    import fulltext
    for sid in sys.argv[2:] or ids():   # `pipeline.py fulltext [ids...]`
        print(sid, fulltext.run(sid), flush=True)

def stage_readpacks():
    import readpack; readpack.run_all(sys.argv[2:])   # `pipeline.py readpacks [ids...]`, needs fulltext

def stage_readbriefs():
    import briefs; briefs.run_readers(sys.argv[2:])   # one reader brief per reading pack

def stage_proposals():
    import proposals; proposals.run_all()             # merge review/<id>.read-NN.json -> <id>.proposals.md

def stage_sheets():
    import contact_sheet; contact_sheet.run_all()

def stage_briefs():
    import briefs; briefs.run_all(" ".join(sys.argv[2:]))   # `pipeline.py briefs <hint...>`

def stage_packets():
    import packets; packets.run_all()

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Thai/emoji filenames crash a cp1252 console
    t = time.time(); globals()[f"stage_{sys.argv[1]}"](); print("done", round(time.time() - t, 1), "s")
