"""Single source of truth for job parameters. Reads job.json (see prompt.md variables table)."""
import json, os, pathlib, shutil

CODE_DIR = pathlib.Path(__file__).parent.resolve()
if not os.environ.get("HIGHLIGHT_JOB"):
    raise RuntimeError("HIGHLIGHT_JOB is not set. Point it at the job.json of the job to run, "
                       "e.g. work/highlight/<channel>/<job>/job.json (no default, so results never land in another channel's folder).")
JOB_FILE = pathlib.Path(os.environ["HIGHLIGHT_JOB"])
_job = json.loads(JOB_FILE.read_text(encoding="utf-8"))

FFBIN = pathlib.Path(r"C:\Users\warit\AppData\Local\hermes\tools\ffmpeg-9.0.1-win32-x64\bin")
def _tool(env: str, exe: str) -> str:
    """env override, then the bundled Hermes ffmpeg, then PATH."""
    if os.environ.get(env):
        return os.environ[env]
    bundled = FFBIN / (exe + ".exe")
    return str(bundled) if bundled.exists() else (shutil.which(exe) or exe)

FFMPEG = _tool("HIGHLIGHT_FFMPEG", "ffmpeg")
FFPROBE = _tool("HIGHLIGHT_FFPROBE", "ffprobe")

INPUT_DIR = pathlib.Path(_job["INPUT_DIR"])
CHANNEL = _job["CHANNEL"]
JOB = _job["JOB"]
WORK_DIR = JOB_FILE.parent
CLIP_MIN_S = _job["CLIP_MIN_S"]
CLIP_MAX_S = _job["CLIP_MAX_S"]
CATEGORIES = _job["CATEGORIES"]
LANGUAGE = _job["LANGUAGE"]
VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".webm", ".ts", ".m4v"}
GAME_OVERRIDES = _job.get("GAME_OVERRIDES", {})        # file-name substring -> game name
RESOLVE_PROJECTS = _job.get("RESOLVE_PROJECTS", {})    # Resolve project -> [source_id, ...]
TIMELINE_NAME_FORMAT = _job.get("TIMELINE_NAME_FORMAT")
