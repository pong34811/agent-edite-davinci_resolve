import os
import pytest
from unittest.mock import MagicMock
from scripts.enrichment_assets import (
    validate_asset_directories,
    select_bgm_for_game,
    export_project_backup,
    ingest_enrichment_assets,
)

def test_validate_asset_directories():
    sfx_dir = r"G:\My Drive\Projects\2.1_sfx"
    bgm_dir = r"G:\My Drive\Projects\1.bgm"
    gif_dir = r"G:\My Drive\Projects\3.gif"
    assert validate_asset_directories(sfx_dir, bgm_dir, gif_dir) is True


def test_validate_asset_directories_nonexistent(tmp_path):
    assert validate_asset_directories(str(tmp_path / "missing"), str(tmp_path), str(tmp_path)) is False


def test_select_bgm_for_game():
    assert "NCSน่ารัก" in select_bgm_for_game("Minecraft") or "FREE BGM" in select_bgm_for_game("Minecraft")
    assert "2025" in select_bgm_for_game("Terraria") or "Gaming" in select_bgm_for_game("Terraria") or "ncs_mix" in select_bgm_for_game("Terraria")
    assert "payday" in select_bgm_for_game("Monster Hunter World") or "Gaming" in select_bgm_for_game("Monster Hunter World") or "ncs_mix" in select_bgm_for_game("Monster Hunter World")
    assert "YEAT" in select_bgm_for_game("Soul Walker") or "Gaming" in select_bgm_for_game("Soul Walker")


def test_export_project_backup_mock(tmp_path):
    mock_resolve = MagicMock()
    mock_pm = MagicMock()
    mock_project = MagicMock()
    mock_project.GetName.return_value = "KT404_2026-09-29"
    mock_pm.GetCurrentProject.return_value = mock_project

    backup_path = str(tmp_path / "test_backup.drp")

    def mock_export(name, path):
        with open(path, "wb") as f:
            f.write(b"PK\x03\x04valid_mock_drp_data")
        return True

    mock_pm.ExportProject.side_effect = mock_export
    mock_resolve.GetProjectManager.return_value = mock_pm

    result = export_project_backup(backup_path, resolve_obj=mock_resolve)
    assert result is True
    assert mock_pm.ExportProject.call_count == 1
    args, kwargs = mock_pm.ExportProject.call_args
    assert args[0] == "KT404_2026-09-29"
    assert args[1] == backup_path


def test_export_project_backup_empty_file_fails(tmp_path):
    mock_resolve = MagicMock()
    mock_pm = MagicMock()
    mock_project = MagicMock()
    mock_project.GetName.return_value = "KT404_2026-09-29"
    mock_pm.GetCurrentProject.return_value = mock_project

    backup_path = str(tmp_path / "empty_backup.drp")

    # Simulate exporter creating a 0-byte file
    def mock_export_empty(name, path):
        with open(path, "wb") as f:
            pass
        return True

    mock_pm.ExportProject.side_effect = mock_export_empty
    mock_resolve.GetProjectManager.return_value = mock_pm

    result = export_project_backup(backup_path, resolve_obj=mock_resolve)
    assert result is False


def test_ingest_enrichment_assets_mock():
    mock_resolve = MagicMock()
    mock_pm = MagicMock()
    mock_project = MagicMock()
    mock_media_pool = MagicMock()
    mock_root_folder = MagicMock()
    mock_initial_folder = MagicMock()
    mock_initial_folder.GetName.return_value = "Master"

    mock_resolve.GetProjectManager.return_value = mock_pm
    mock_pm.GetCurrentProject.return_value = mock_project
    mock_project.GetMediaPool.return_value = mock_media_pool
    mock_media_pool.GetRootFolder.return_value = mock_root_folder
    mock_media_pool.GetCurrentFolder.return_value = mock_initial_folder
    mock_pm.SaveProject.return_value = True

    # Existing subfolders empty
    mock_root_folder.GetSubFolderList.return_value = []

    # Mock AddSubFolder and ImportMedia with clip tracking
    folder_map = {}
    folder_clips = {}
    current_folder = [mock_initial_folder]
    set_folder_history = []

    def mock_add_folder(*args, **kwargs):
        name = args[-1] if args else kwargs.get("name")
        f = MagicMock()
        f.GetName.return_value = name
        f.GetClipList.side_effect = lambda: folder_clips.get(name, [])
        folder_map[name] = f
        return f
    mock_media_pool.AddSubFolder.side_effect = mock_add_folder

    def mock_set_current_folder(folder):
        current_folder[0] = folder
        set_folder_history.append(folder)
        return True
    mock_media_pool.SetCurrentFolder.side_effect = mock_set_current_folder

    def mock_import(file_list):
        items = []
        for p in file_list:
            item = MagicMock()
            item.GetName.return_value = os.path.basename(p)
            items.append(item)
        if current_folder[0]:
            name = current_folder[0].GetName()
            folder_clips.setdefault(name, []).extend(items)
        return items
    mock_media_pool.ImportMedia.side_effect = mock_import

    catalog = ingest_enrichment_assets(resolve_obj=mock_resolve)
    assert "Enrichment_SFX" in catalog
    assert "Enrichment_BGM" in catalog
    assert "Enrichment_GIF" in catalog
    assert len(catalog["Enrichment_SFX"]) > 0
    assert len(catalog["Enrichment_BGM"]) > 0
    assert len(catalog["Enrichment_GIF"]) > 0

    # Verify SaveProject was called to persist
    mock_pm.SaveProject.assert_called_once()

    # Verify initial folder was restored
    assert set_folder_history[-1] == mock_initial_folder


def test_ingest_skips_nonexistent_files_when_dir_exists(tmp_path):
    mock_resolve = MagicMock()
    mock_pm = MagicMock()
    mock_project = MagicMock()
    mock_media_pool = MagicMock()
    mock_root_folder = MagicMock()
    mock_initial_folder = MagicMock()

    mock_resolve.GetProjectManager.return_value = mock_pm
    mock_pm.GetCurrentProject.return_value = mock_project
    mock_project.GetMediaPool.return_value = mock_media_pool
    mock_media_pool.GetRootFolder.return_value = mock_root_folder
    mock_media_pool.GetCurrentFolder.return_value = mock_initial_folder

    mock_root_folder.GetSubFolderList.return_value = []
    f = MagicMock()
    f.GetName.return_value = "Enrichment_SFX"
    f.GetClipList.return_value = []
    mock_media_pool.AddSubFolder.return_value = f

    # Create real directory with only ONE real file
    sfx_dir = tmp_path / "sfx"
    sfx_dir.mkdir()
    real_file = sfx_dir / "1_ตลกตบมุก_1.mp3"
    real_file.write_bytes(b"dummy_mp3")

    imported_paths = []
    def mock_import(paths):
        imported_paths.extend(paths)
        return [MagicMock()]
    mock_media_pool.ImportMedia.side_effect = mock_import

    # Only test SFX directory by mocking others as empty mock paths
    catalog = ingest_enrichment_assets(
        resolve_obj=mock_resolve,
        sfx_dir=str(sfx_dir),
        bgm_dir=str(tmp_path / "nonexistent_bgm"),
        gif_dir=str(tmp_path / "nonexistent_gif"),
    )

    # For sfx_dir, only the 1 existing file should have been passed to ImportMedia
    sfx_imports = [p for p in imported_paths if str(sfx_dir) in p]
    assert len(sfx_imports) == 1
    assert sfx_imports[0] == str(real_file)
