"""Enrichment Assets Ingestion and Safety Backup Module for DaVinci Resolve.

Provides functions to:
- Validate presence of SFX, BGM, and GIF directories
- Select mood-appropriate BGM for specific games
- Safely export pre-flight .drp project backup
- Create Media Pool bins (Enrichment_SFX, Enrichment_BGM, Enrichment_GIF) and ingest curated assets
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

SFX_ROOT = r"G:\My Drive\Projects\2.1_sfx"
BGM_ROOT = r"G:\My Drive\Projects\1.bgm"
GIF_ROOT = r"G:\My Drive\Projects\3.gif"
BACKUP_DEFAULT_PATH = r"G:\My Drive\Projects\Katy404\2026-09-29\KT404_2026-09-29_pre_enrichment.drp"

# Curated SFX per design spec
CURATED_SFX = [
    "1_ตลกตบมุก_1.mp3",
    "2.ตบมุก.mp3",
    "3.ตบมุก.mp3",
    "(mafioso) scream.mp3",
    "3.ฟ้าผ่า.mp3",
    "_RUN_ vine effect sound.mp3",
    "3. WINK _DING_.mp3",
    "_Click_ Nice.mp3",
    "_Wow!_ (anime voice accent).mp3",
]

# Curated BGM per design spec
CURATED_BGM = [
    "NCSน่ารัก.mp3",
    "FREE BGM 4 LOOP.wav",
    "2025-02-04_-_Wishing_Well_-_www.FesliyanStudios.com_.mp3",
    "Top 50 NoCopyrightSounds Songs 2025 🎧 Best Free EDM & Gaming Music Mix🔥 Best of NCS ✨.mp3",
    "Gaming Music 2023 ♫ 1 Hour Gaming Music Mix ♫ Copyright Free Music.mp3",
    "ncs_mix_2025_resolve.wav",
    "payday.mp3",
    "YEAT - DISRESPECTFUL (PROD. SKY x KEENEX) (slowed+reverb).mp3",
    "aphextwin.m4a",
]

# Curated GIF per design spec
CURATED_GIF = [
    "Anime - Shocked Reaction.gif",
    "Reaction - What Confused Minion.gif",
    "Reaction - OMG No Funny.gif",
    "Reaction - Iconic Laugh.gif",
    "Reaction - Laughing Pointing.gif",
    "Reaction - Well Done Laughing.gif",
    "Cute - Dancing Cat.gif",
    "Cute - Happy Dancing Cat.gif",
    "Anime - Thumbs Up.gif",
    "Anime - Angry Chibi.gif",
    "Thai Meme - Clenched Fist Angry Cute.gif",
]

GAME_BGM_MAP = {
    "Minecraft": "NCSน่ารัก.mp3",
    "Terraria": "Top 50 NoCopyrightSounds Songs 2025 🎧 Best Free EDM & Gaming Music Mix🔥 Best of NCS ✨.mp3",
    "Monster Hunter World": "payday.mp3",
    "Soul Walker": "YEAT - DISRESPECTFUL (PROD. SKY x KEENEX) (slowed+reverb).mp3",
}


def get_resolve():
    """Obtain running DaVinci Resolve instance on Windows."""
    if sys.platform == "win32":
        os.environ.setdefault(
            "RESOLVE_SCRIPT_LIB",
            r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll",
        )
        resolve_dir = r"C:\Program Files\Blackmagic Design\DaVinci Resolve"
        if hasattr(os, "add_dll_directory") and os.path.isdir(resolve_dir):
            try:
                os.add_dll_directory(resolve_dir)
            except Exception:
                pass
        script_module_dir = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules"
        if os.path.isdir(script_module_dir) and script_module_dir not in sys.path:
            sys.path.append(script_module_dir)
    try:
        import DaVinciResolveScript as dvr_script
        return dvr_script.scriptapp("Resolve")
    except Exception:
        return None


def validate_asset_directories(sfx_dir: str, bgm_dir: str, gif_dir: str) -> bool:
    """Validate that asset directories exist."""
    return os.path.isdir(sfx_dir) and os.path.isdir(bgm_dir) and os.path.isdir(gif_dir)


def select_bgm_for_game(game_name: str) -> str:
    """Select appropriate BGM file path or filename for the specified game."""
    if game_name in GAME_BGM_MAP:
        return GAME_BGM_MAP[game_name]
    lower = game_name.lower()
    if "mine" in lower:
        return "NCSน่ารัก.mp3"
    elif "terra" in lower:
        return "Top 50 NoCopyrightSounds Songs 2025 🎧 Best Free EDM & Gaming Music Mix🔥 Best of NCS ✨.mp3"
    elif "monster" in lower or "mhw" in lower:
        return "payday.mp3"
    elif "soul" in lower:
        return "YEAT - DISRESPECTFUL (PROD. SKY x KEENEX) (slowed+reverb).mp3"
    return "Gaming Music 2023 ♫ 1 Hour Gaming Music Mix ♫ Copyright Free Music.mp3"


def export_project_backup(backup_path: str, resolve_obj=None) -> bool:
    """Safely export current project to a .drp archive."""
    resolve = resolve_obj or get_resolve()
    if not resolve:
        raise RuntimeError("Could not connect to DaVinci Resolve.")
    pm = resolve.GetProjectManager()
    if not pm:
        raise RuntimeError("Could not get ProjectManager.")
    project = pm.GetCurrentProject()
    if not project:
        raise RuntimeError("No current project open in DaVinci Resolve.")
    project_name = project.GetName()

    parent_dir = os.path.dirname(backup_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    success = pm.ExportProject(project_name, backup_path)
    return bool(success)


def ingest_enrichment_assets(
    resolve_obj=None,
    sfx_dir: Optional[str] = None,
    bgm_dir: Optional[str] = None,
    gif_dir: Optional[str] = None,
) -> Dict[str, List[Any]]:
    """Create bins (Enrichment_SFX, Enrichment_BGM, Enrichment_GIF) and ingest curated assets."""
    sfx_dir = sfx_dir or SFX_ROOT
    bgm_dir = bgm_dir or BGM_ROOT
    gif_dir = gif_dir or GIF_ROOT

    resolve = resolve_obj or get_resolve()
    if not resolve:
        raise RuntimeError("Could not connect to DaVinci Resolve.")
    pm = resolve.GetProjectManager()
    if not pm:
        raise RuntimeError("Could not get ProjectManager.")
    project = pm.GetCurrentProject()
    if not project:
        raise RuntimeError("No current project open in DaVinci Resolve.")
    media_pool = project.GetMediaPool()
    if not media_pool:
        raise RuntimeError("Could not get MediaPool.")
    root_folder = media_pool.GetRootFolder()
    if not root_folder:
        raise RuntimeError("Could not get MediaPool RootFolder.")

    bin_configs = [
        ("Enrichment_SFX", sfx_dir, CURATED_SFX),
        ("Enrichment_BGM", bgm_dir, CURATED_BGM),
        ("Enrichment_GIF", gif_dir, CURATED_GIF),
    ]

    catalog: Dict[str, List[Any]] = {}

    for bin_name, src_dir, file_list in bin_configs:
        subfolders = root_folder.GetSubFolderList() or []
        folder = next((f for f in subfolders if f.GetName() == bin_name), None)
        if folder is None:
            folder = media_pool.AddSubFolder(root_folder, bin_name)

        if not folder:
            raise RuntimeError(f"Failed to create or access subfolder '{bin_name}'.")

        media_pool.SetCurrentFolder(folder)

        existing_clips = folder.GetClipList() or []
        existing_names = {c.GetName() for c in existing_clips}

        paths_to_import = []
        for filename in file_list:
            full_path = os.path.join(src_dir, filename)
            if os.path.exists(full_path):
                if filename not in existing_names:
                    paths_to_import.append(full_path)
            else:
                if not os.path.exists(src_dir) or filename not in existing_names:
                    paths_to_import.append(full_path)

        if paths_to_import:
            media_pool.ImportMedia(paths_to_import)

        final_clips = folder.GetClipList() or []
        catalog[bin_name] = final_clips

    return catalog


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enrichment assets and pre-flight backup")
    parser.add_argument("--backup", action="store_true", help="Perform .drp pre-flight backup")
    parser.add_argument("--backup-path", default=BACKUP_DEFAULT_PATH, help="Path for .drp backup")
    parser.add_argument("--ingest", action="store_true", help="Ingest assets into Media Pool")
    args = parser.parse_args()

    if args.backup:
        print(f"Exporting pre-flight backup to {args.backup_path}...")
        ok = export_project_backup(args.backup_path)
        print("Backup result:", ok)

    if args.ingest:
        print("Ingesting enrichment assets into Media Pool...")
        cat = ingest_enrichment_assets()
        for b_name, clips in cat.items():
            print(f"Bin {b_name}: {len(clips)} items")
