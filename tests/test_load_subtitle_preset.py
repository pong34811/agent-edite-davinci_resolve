"""Offline tests for scripts/load_subtitle_preset.py (no Resolve calls)."""
from pathlib import Path
import os
import sqlite3
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import load_subtitle_preset as lsp  # noqa: E402

# Shapes observed on Resolve 21.1.0.17 (Sm2TiTrack.FieldsBlob, Type=2).
STUB_WITH_BOOL = bytes.fromhex(
    "0000000100000002" "00000012") + "NumLayers".encode("utf-16-be") + bytes.fromhex(
    "00000002" "00" "00000000" "0000003e") + "ExcludeTrackFromSequenceCaching".encode("utf-16-be") + bytes.fromhex(
    "00000001" "00" "01")
STYLE_A = bytes.fromhex("000000020000000481") + b"\x28\xb5\x2f\xfdAAAA"
STYLE_B = bytes.fromhex("000000020000000581") + b"\x28\xb5\x2f\xfdBBBBB"


def preset_map(items):
    out = [struct.pack(">II", 1, len(items))]
    for name, value in items:
        out += [lsp._qstring(name), lsp._qbytearray(value)]
    return b"".join(out)


class BlobTests(unittest.TestCase):
    def test_roundtrip_preserves_unknown_order_and_bool(self):
        header, entries = lsp.parse_fields_blob(STUB_WITH_BOOL)
        self.assertEqual([e[0] for e in entries], ["NumLayers", "ExcludeTrackFromSequenceCaching"])
        self.assertEqual(lsp.build_fields_blob(header, entries), STUB_WITH_BOOL)

    def test_set_appends_then_replaces_style_only(self):
        styled = lsp.set_bytearray(STUB_WITH_BOOL, lsp.STYLE_KEY, STYLE_A)
        self.assertEqual(lsp.get_bytearray(styled, lsp.STYLE_KEY), STYLE_A)
        restyled = lsp.set_bytearray(styled, lsp.STYLE_KEY, STYLE_B)
        self.assertEqual(lsp.get_bytearray(restyled, lsp.STYLE_KEY), STYLE_B)
        keys = [e[0] for e in lsp.parse_fields_blob(restyled)[1]]
        self.assertEqual(keys, ["NumLayers", "ExcludeTrackFromSequenceCaching", lsp.STYLE_KEY])
        self.assertTrue(restyled.startswith(STUB_WITH_BOOL[:4]))

    def test_unknown_type_and_trailing_bytes_refused(self):
        with self.assertRaises(lsp.BlobFormatError):
            lsp.parse_fields_blob(STUB_WITH_BOOL + b"\x00")
        bad = lsp.build_fields_blob(b"\x00\x00\x00\x01", [("Mystery", 64, b"\x00\x01")])
        with self.assertRaises(lsp.BlobFormatError):
            lsp.parse_fields_blob(bad)

    def test_preset_map_and_user_blob(self):
        data = preset_map([("Mitr Font", STYLE_A), ("mitr-short", STYLE_B)])
        user_blob = lsp.set_bytearray(bytes.fromhex("0000000100000000"), lsp.PRESETS_KEY, data)
        self.assertEqual(lsp.parse_preset_map(lsp.get_bytearray(user_blob, lsp.PRESETS_KEY)),
                         {"Mitr Font": STYLE_A, "mitr-short": STYLE_B})

    def test_dblist_drive_letter(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as d:
            Path(d, "dblist.conf").write_text(
                "Local Database:C\\Users\\x\\Lib::::DISK\r\ngoogle drive:G\\My Drive\\Lib:*:::DISK\r\n",
                encoding="utf-8")
            roots = lsp.library_roots(Path(d))
        self.assertEqual(str(roots["google drive"]), "G:\\My Drive\\Lib")
        self.assertEqual(str(roots["Local Database"]), "C:\\Users\\x\\Lib")


class DatabaseWriteTests(unittest.TestCase):
    def test_write_only_target_subtitle_rows(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as d:
            db = Path(d, "Project.db")
            con = sqlite3.connect(db)
            con.executescript("""
                CREATE TABLE Sm2Timeline(Sm2Timeline_id TEXT, Name TEXT);
                CREATE TABLE Sm2Sequence(Sm2Sequence_id TEXT, Sm2Timeline_id TEXT);
                CREATE TABLE Sm2TiTrack(Sm2TiTrack_id TEXT, Type INT, Sequence TEXT, FieldsBlob BLOB);
                INSERT INTO Sm2Timeline VALUES('T1','one'),('T2','two');
                INSERT INTO Sm2Sequence VALUES('S1','T1'),('S2','T2');
            """)
            other = lsp.set_bytearray(STUB_WITH_BOOL, lsp.STYLE_KEY, STYLE_B)
            con.executemany("INSERT INTO Sm2TiTrack VALUES(?,?,?,?)", [
                ("sub1", 2, "S1", STUB_WITH_BOOL), ("vid1", 0, "S1", STUB_WITH_BOOL),
                ("sub2", 2, "S2", other)])
            con.commit()
            rows = lsp.subtitle_tracks(con, ["T1"])
            con.close()
            plan = lsp.plan_updates(rows, STYLE_A)
            self.assertEqual([p["track_id"] for p in plan], ["sub1"])
            lsp.write_plan(db, plan, STYLE_A)
            self.assertEqual(lsp.verify_db(db, ["T1"], STYLE_A, 1), 1)
            con = sqlite3.connect(db)
            blobs = dict(con.execute("SELECT Sm2TiTrack_id, FieldsBlob FROM Sm2TiTrack"))
            con.close()
        self.assertEqual(blobs["vid1"], STUB_WITH_BOOL)
        self.assertEqual(blobs["sub2"], other)
        self.assertEqual(lsp.get_bytearray(blobs["sub1"], lsp.STYLE_KEY), STYLE_A)


if __name__ == "__main__":
    unittest.main()
