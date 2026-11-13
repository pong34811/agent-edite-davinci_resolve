"""Put a saved Subtitle-track preset into an exported .drt, so Resolve loads it on import (no DB write, no restart).

Resolve keeps a subtitle track's style as ``EffectFiltersBA`` inside ``Sm2TiTrack.FieldsBlob`` (``Type`` 2), and a
DRT export carries that blob as hex. This tool reads the named preset from ``User.db`` (read-only), sets
``EffectFiltersBA`` on the chosen subtitle track(s) of the DRT, checks every other blob entry and every other byte
of the DRT is unchanged, and writes a new .drt. Import it with ``MediaPool.ImportTimelineFromFile`` and rename the
new timeline by ID. It is the close-free alternative to ``load_subtitle_preset_auto`` (which patches Project.db and
restarts Resolve).

Example::

    python -m scripts.drt_set_subtitle_preset in.drt out.drt --user-db "<library>/Resolve Projects/Users/guest/User.db" \
        --preset "Mitr Font"

This utility edits DRT files offline and does not connect to Resolve.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.load_subtitle_preset import (STYLE_KEY, SUBTITLE_TRACK_TYPE, get_bytearray,  # noqa: E402
                                          parse_fields_blob, read_presets, set_bytearray)

TRACK_RE = re.compile(r"(<Sm2TiTrack DbId=\"[^\"]+\">\s*<FieldsBlob>)([0-9a-fA-F]*)(</FieldsBlob>\s*<Type>(\d+)</Type>)")


def patch_xml(text: str, style: bytes, track_numbers: list[int] | None = None) -> tuple[str, list[dict]]:
    """Return (new_text, report). Subtitle tracks are numbered 1.. in document order."""
    report, n = [], 0

    def sub(m: re.Match) -> str:
        nonlocal n
        if int(m.group(4)) != SUBTITLE_TRACK_TYPE:
            return m.group(0)
        n += 1
        if track_numbers and n not in track_numbers:
            return m.group(0)
        blob = bytes.fromhex(m.group(2))
        new = set_bytearray(blob, STYLE_KEY, style)
        rest_old = [e for e in parse_fields_blob(blob)[1] if e[0] != STYLE_KEY]
        rest_new = [e for e in parse_fields_blob(new)[1] if e[0] != STYLE_KEY]
        if rest_old != rest_new or get_bytearray(new, STYLE_KEY) != style:
            raise RuntimeError(f"subtitle track {n}: blob entries other than {STYLE_KEY} changed")
        report.append({"track": n, "already_matches": get_bytearray(blob, STYLE_KEY) == style})
        return m.group(1) + new.hex() + m.group(3)

    return TRACK_RE.sub(sub, text), report


def patch_drt(src: Path, dst: Path, style: bytes, track_numbers: list[int] | None = None) -> list[dict]:
    report: list[dict] = []
    buf = io.BytesIO()
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.startswith("SeqContainer/") and info.filename.endswith(".xml"):
                text = data.decode("utf-8")
                new_text, rep = patch_xml(text, style, track_numbers)
                report += rep
                data = new_text.encode("utf-8")
            zout.writestr(info, data)
    if not report:
        raise RuntimeError("no subtitle track found in the DRT")
    dst.write_bytes(buf.getvalue())
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path)
    ap.add_argument("--user-db", type=Path, required=True)
    ap.add_argument("--preset", required=True)
    ap.add_argument("--track", type=int, action="append", help="subtitle track number (1-based); default all")
    a = ap.parse_args(argv)
    presets = read_presets(a.user_db)
    if a.preset not in presets:
        raise SystemExit(f"preset {a.preset!r} not found; have {list(presets)}")
    rep = patch_drt(a.src, a.dst, presets[a.preset], a.track)
    for r in rep:
        print(f"subtitle track {r['track']}: set {a.preset!r} (already_matches={r['already_matches']})")
    print("wrote", a.dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
