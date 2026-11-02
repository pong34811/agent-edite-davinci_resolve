"""Map source_id -> Resolve clip id from a saved `media_pool probe_media_pool` result (JSON text from the MCP).

Usage: python resolve_clips.py <probe.json>   -> writes WORK_DIR/resolve_clips.json
"""
import json, pathlib, sys
import config

def _norm(p: str) -> str:
    return p.replace(chr(92), "/").lower()

def map_clips(probe: dict, inventory: list[dict]) -> dict:
    clips = list(probe.get("root", {}).get("clips", [])) + list(probe.get("current_folder", {}).get("clips", []))
    by_path = {_norm(c["file_path"]): c["id"] for c in clips if c.get("file_path")}
    out, missing = {}, []
    for r in inventory:
        cid = by_path.get(_norm(r["file"]))
        (out.__setitem__(r["source_id"], cid) if cid else missing.append(r["source_id"]))
    if missing:
        raise KeyError(f"not in Resolve media pool: {missing}")
    return out

def main(probe_path: str) -> None:
    text = pathlib.Path(probe_path).read_text(encoding="utf-8")
    probe = json.JSONDecoder().raw_decode(text[text.index("{"):])[0]
    inv = json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))
    m = map_clips(probe, inv)
    (config.WORK_DIR / "resolve_clips.json").write_text(json.dumps(m, indent=1), encoding="utf-8")
    print(m)

if __name__ == "__main__":
    main(sys.argv[1])
