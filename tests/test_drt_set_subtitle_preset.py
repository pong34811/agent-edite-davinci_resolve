"""Offline tests for scripts/drt_set_subtitle_preset.py (no Resolve calls)."""
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import drt_set_subtitle_preset as d  # noqa: E402
from scripts import load_subtitle_preset as lsp  # noqa: E402

# Subtitle-track FieldsBlob as exported in a DRT on Resolve 21.1.0.17 (Bunny Girl ep9, 2026-11-14).
BLOB = ("000000010000000200000012004e0075006d004c00610079006500720073000000020000000000000000"
        "3e004500780063006c0075006400650054007200610063006b00460072006f006d0053006500710075"
        "0065006e0063006500430061006300680069006e0067000000010001")
STYLE = bytes.fromhex("000000020000000481") + b"\x28\xb5\x2f\xfdAAAA"


def track(dbid, blob, typ):
    return (f'<Sm2TiTrack DbId="{dbid}">\n    <FieldsBlob>{blob}</FieldsBlob>\n    <Type>{typ}</Type>\n'
            f'    <SubType>0</SubType>\n</Sm2TiTrack>\n')


XML = "<Seq>\n" + track("v1", BLOB, 0) + track("s1", BLOB, 2) + track("s2", BLOB, 2) + "</Seq>\n"


class PatchXmlTests(unittest.TestCase):
    def test_sets_style_on_subtitle_tracks_only(self):
        out, rep = d.patch_xml(XML, STYLE)
        self.assertEqual([r["track"] for r in rep], [1, 2])
        self.assertIn(track("v1", BLOB, 0), out)  # video track untouched
        blobs = d.TRACK_RE.findall(out)
        for _, hexblob, _, typ in blobs:
            got = lsp.get_bytearray(bytes.fromhex(hexblob), lsp.STYLE_KEY)
            self.assertEqual(got, STYLE if typ == "2" else None)

    def test_track_filter_and_idempotent(self):
        out, rep = d.patch_xml(XML, STYLE, [2])
        self.assertEqual([r["track"] for r in rep], [2])
        again, rep2 = d.patch_xml(out, STYLE, [2])
        self.assertEqual(again, out)
        self.assertTrue(rep2[0]["already_matches"])

    def test_drt_roundtrip_keeps_other_members(self):
        with tempfile.TemporaryDirectory() as t:
            src, dst = Path(t) / "a.drt", Path(t) / "b.drt"
            with zipfile.ZipFile(src, "w") as z:
                z.writestr("project.xml", "<p/>")
                z.writestr("SeqContainer/x.xml", XML)
            rep = d.patch_drt(src, dst, STYLE)
            self.assertEqual(len(rep), 2)
            with zipfile.ZipFile(dst) as z:
                self.assertEqual(z.read("project.xml"), b"<p/>")
                self.assertIn(STYLE.hex(), z.read("SeqContainer/x.xml").decode())

    def test_no_subtitle_track_refused(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "a.drt"
            with zipfile.ZipFile(src, "w") as z:
                z.writestr("SeqContainer/x.xml", "<Seq>" + track("v1", BLOB, 0) + "</Seq>")
            with self.assertRaises(RuntimeError):
                d.patch_drt(src, Path(t) / "b.drt", STYLE)


if __name__ == "__main__":
    unittest.main()
