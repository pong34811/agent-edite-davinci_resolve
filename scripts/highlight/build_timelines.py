"""Candidates -> Resolve clip_infos / timeline names. Resolve calls themselves go through the Resolve MCP."""
import glob, json, pathlib, re, sys
from string import Formatter
import config

def to_clip_infos(c: dict, clip_id: str, fps: float) -> list[dict]:
    """start/end frames are SOURCE-file frames, so fps must be that file's own fps (from inventory.json)."""
    start = round(c["start_s"] * fps)
    return [{"clip_id": clip_id, "start_frame": start,
             "end_frame": start + round((c["end_s"] - c["start_s"]) * fps),   # end exclusive
             "record_frame": 0}]

_BAD = r'[\\/:*?"<>|]'

def timeline_name(c: dict, game: str, limit: int = 60) -> str:
    """Format a title using the current job's timeline template; defaults to the legacy format."""
    template = config.TIMELINE_NAME_FORMAT or "{title}-{game}-vdo"
    try:
        fields = [field for _, field, _, _ in Formatter().parse(template) if field]
    except ValueError as exc:
        raise ValueError(f"invalid timeline name format: {exc}") from exc

    title_fields = [field for field in fields if field in {"title", "ชื่อคลิป"}]
    if len(title_fields) != 1:
        raise ValueError("timeline name format must contain exactly one title placeholder")
    allowed_fields = {"title", "ชื่อคลิป", "game", "ชื่อเกม"}
    unknown_fields = set(fields) - allowed_fields
    if unknown_fields:
        raise ValueError(f"unsupported timeline name placeholder: {sorted(unknown_fields)[0]}")

    title_field = title_fields[0]
    title = re.sub(_BAD, " ", c["title_th"]).strip()
    safe_game = re.sub(_BAD, " ", game or "").strip()
    game_fields = {"game", "ชื่อเกม"}
    if any(field in game_fields for field in fields) and not safe_game:
        raise ValueError("game name is required for the timeline name")

    values = {"title": title, "ชื่อคลิป": title, "game": safe_game, "ชื่อเกม": safe_game}

    def render_name() -> str:
        try:
            formatted = template.format(**values)
        except (IndexError, KeyError, ValueError) as exc:
            raise ValueError(f"invalid timeline name format: {exc}") from exc
        return re.sub(_BAD, " ", formatted).strip()

    name = render_name()
    if len(name) > limit:
        excess = len(name) - limit
        values[title_field] = values[title_field][:max(0, len(values[title_field]) - excess)].rstrip()
        name = render_name()
    if len(name) > limit:
        raise ValueError(f"non-title text exceeds the {limit}-character timeline-name limit")
    return name

def game_from_filename(filename: str, overrides: dict | None = None) -> str:
    """Game name from a footage file name. `overrides` maps a file-name substring to a game name and wins."""
    for key, game in (overrides or {}).items():
        if key in filename:
            return game
    s = pathlib.Path(filename).stem
    s = re.sub(r"^\d{8}_", "", s)
    s = re.sub(r"_\[[^\]]+\]$", "", s)
    s = s.replace("【LIVE】", "").split(" #")[0]
    s = re.sub(r"\s+-\s+\d+\s*$", "", s)
    return re.sub(r"\s+", " ", s).strip()

def project_for_source(source_id: str, projects: dict) -> str | None:
    """Resolve project that owns a source_id; None when the job uses no project split."""
    if not projects:
        return None
    for name, ids in projects.items():
        if source_id in ids:
            return name
    raise KeyError(f"{source_id} is not assigned to any RESOLVE_PROJECTS entry")

def merge_reviews(review_dir: pathlib.Path | None = None) -> list[dict]:
    review_dir = pathlib.Path(review_dir or config.WORK_DIR / "review")
    out = []
    for f in sorted(glob.glob(str(review_dir / "v??.json"))):
        out += sorted(json.loads(pathlib.Path(f).read_text(encoding="utf-8")), key=lambda c: c["start_s"])
    return out

def calls(plan: list[dict], start: int = 0, end: int | None = None, project: str | None = None) -> list[dict]:
    """Ready-to-send Resolve MCP payloads (one `media_pool create_timeline_from_clips` per planned timeline)."""
    if project is not None:
        plan = [x for x in plan if x.get("project") == project]
    return [{"name": "mcp__davinci_resolve__media_pool",
             "arguments": {"action": "create_timeline_from_clips",
                           "params": {"name": x["name"], "clip_infos": x["clip_infos"], "if_exists": "fail"}}}
            for x in plan[start:end]]

def main() -> None:
    cands = merge_reviews()
    (config.WORK_DIR / "candidates.json").write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
    clips = json.loads((config.WORK_DIR / "resolve_clips.json").read_text(encoding="utf-8"))
    inv = {r["source_id"]: r for r in json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))}
    plan = []
    for c in cands:
        row = inv[c["source_id"]]
        game = game_from_filename(pathlib.Path(row["file"]).name, config.GAME_OVERRIDES)
        plan.append({"name": timeline_name(c, game), "clip_infos": to_clip_infos(c, clips[c["source_id"]], row["fps"]),
                     "candidate": c["id"], "game": game,
                     "project": project_for_source(c["source_id"], config.RESOLVE_PROJECTS)})
    (config.WORK_DIR / "timeline_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(plan), "timelines planned")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "calls":
        plan = json.loads((config.WORK_DIR / "timeline_plan.json").read_text(encoding="utf-8"))
        args = sys.argv[2:]
        proj = None
        if "--project" in args:
            i = args.index("--project"); proj = args[i + 1]; del args[i:i + 2]
        a = int(args[0]) if len(args) > 0 else 0
        z = int(args[1]) if len(args) > 1 else None
        print(json.dumps(calls(plan, a, z, proj), ensure_ascii=False, separators=(",", ":")))
    else:
        main()
