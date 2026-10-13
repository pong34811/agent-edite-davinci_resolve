"""Shared Resolve helpers for the batch pipeline (see scripts/pipeline/README.md).
Env: PW = per-project work dir (or TMPDIR), SFX_DIR / GIF_DIR / BGM_DIR = asset library folders."""
import sys, json, os, time
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ.setdefault("RESOLVE_SCRIPT_LIB", r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll")
import DaVinciResolveScript as dvr
W = os.environ.get("PW") or os.environ["TMPDIR"]
os.makedirs(W, exist_ok=True)
S = os.environ.get("SFX_DIR", r"G:\My Drive\Projects.1_sfx"); G = os.environ.get("GIF_DIR", r"G:\My Drive\Projects.gif"); B = os.environ.get("BGM_DIR", r"G:\My Drive\Projects.bgm")
r = dvr.scriptapp("Resolve"); pm = r.GetProjectManager(); p = pm.GetCurrentProject(); mp = p.GetMediaPool()
D = 1.2

def tl_by_id(uid):
    for i in range(1, p.GetTimelineCount()+1):
        t = p.GetTimelineByIndex(i)
        if t.GetUniqueId() == uid: return t

def activate(t):
    assert p.SetCurrentTimeline(t)
    time.sleep(1.0)
    assert p.GetCurrentTimeline().GetUniqueId() == t.GetUniqueId()

def bin_folder():
    root = mp.GetRootFolder()
    for f in root.GetSubFolderList():
        if f.GetName() == "Enrichment": return f
    time.sleep(D); return mp.AddSubFolder(root, "Enrichment")

def pool_map(folder):
    return {c.GetClipProperty("File Path"): c for c in (folder.GetClipList() or [])}

def ensure_imported(paths):
    f = bin_folder(); mp.SetCurrentFolder(f); m = pool_map(f)
    need = [x for x in paths if x not in m]
    if need:
        time.sleep(D); got = mp.ImportMedia(need); print("imported", len(got or []), "of", len(need))
        time.sleep(D); m = pool_map(f)
    return m, f
