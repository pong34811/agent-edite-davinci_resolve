import zipfile
from pathlib import Path

from scripts.backup_drp import export_verified


class FakePM:
    def __init__(self):
        self.paths = []

    def SaveProject(self):
        return True

    def ExportProject(self, name, path, with_stills):
        if not Path(path).is_absolute():  # mirrors Resolve: relative paths fail
            return False
        self.paths.append(path)
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("project.xml", "<p/>")
        return True


class FakeProject:
    def GetName(self):
        return "demo"


def test_relative_path_is_exported_as_absolute(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pm = FakePM()
    assert export_verified(pm, FakeProject(), "sub/backup.drp") > 0
    assert Path(pm.paths[0]) == (tmp_path / "sub" / "backup.drp").resolve()
