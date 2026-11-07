"""Give a timeline's subtitles a plain subtitle-track style (e.g. `Mitr Font`) with Resolve kept open and no Project.db write.

The style of a classic (non-animated) subtitle preset lives on the Subtitle track element of a DRT. This tool clones that
track element from a reference DRT whose subtitles already carry the style, rebuilds the target timeline's own cues inside
it, and imports the result as a NEW timeline; the source timeline is never edited. Proven on 48 KT404 highlight
timelines (2026-11-05) and Bunny Girl ep5 (2026-11-07).

MCP-GAP: timeline_ai set_subtitle_preset copies only an animated preset (the track's FusionCompHolderItems, e.g. Word
Highlight); for a plain track style it refuses with "No animation preset" (MCP 4.18.5, Resolve 21.1.0.17, 2026-11-07).

    py -3.13 -m scripts.drt_clone_subtitle_style --timeline "Timeline 1_pop" --new "Timeline 1_pop_mitr" \
        --styled .hermes/kt404-hl/batch/pilot_edit.drt --workdir .hermes/projects/<job>/substyle
"""
import argparse
import copy
import time
from pathlib import Path

from scripts import drt_focus_track as d
from scripts.drt_shift_subtitles import _patch_fields_blob


def clone_styled_subtitle_track(src_drt, styled_drt, out, cues, styled_track=1):
    """Write `out` = `src_drt` whose single Subtitle track is replaced by a copy of `styled_drt`'s track
    `styled_track` (1-based) holding `cues` [(start, end, text)] in timeline frames. Returns the cue count."""
    src_drt, styled_drt, out = Path(src_drt), Path(styled_drt), Path(out)
    pay, infos, com = d._read_archive(src_drt)
    mem = d._sequence_member(pay, src_drt)
    root = d._parse_xml(pay[mem], 'source')
    spay = d._read_archive(styled_drt)[0]
    sroot = d._parse_xml(spay[d._sequence_member(spay, styled_drt)], 'styled')
    used = d._all_archive_dbids(pay, src_drt) | d._all_archive_dbids(spay, styled_drt)
    seq = root.find('VideoTrackVec').findall('Element')[0].find('Sm2TiTrack').findtext('Sequence')
    stracks = sroot.find('SubtitleTrackVec').findall('Element')
    if len(stracks) < styled_track:
        raise ValueError(f'styled DRT has {len(stracks)} subtitle tracks')
    sw = copy.deepcopy(stracks[styled_track - 1])
    st = sw.find('Sm2TiTrack')
    st.find('Sequence').text = seq
    sitems = st.find('Items')
    templates = sitems.findall('Element')
    if not templates:
        raise ValueError('styled subtitle track has no cue to use as a template')
    tmpl = templates[0]
    tstart, stail = int(tmpl[0].findtext('Start')), tmpl.tail
    for e in templates:
        sitems.remove(e)
    for s, e, txt in cues:
        if not 0 <= s < e:
            raise ValueError(f'bad cue {s}-{e} {txt!r}')
        el = copy.deepcopy(tmpl)
        g = el[0]
        g.find('Name').text = txt
        g.find('Start').text = str(s)
        g.find('Duration').text = str(e - s)
        g.find('FieldsBlob').text = _patch_fields_blob(g.findtext('FieldsBlob'), tstart, s)
        el.tail = stail
        sitems.append(el)
    for x in sw.iter():
        if x.get('DbId'):
            x.set('DbId', d._fresh_dbid(used))
    svec = root.find('SubtitleTrackVec')
    old = svec.findall('Element')
    if len(old) != 1:
        raise ValueError(f'source DRT must have exactly one subtitle track, has {len(old)}')
    sw.tail = old[0].tail
    svec.remove(old[0])
    svec.append(sw)
    if out.exists():
        raise FileExistsError(out)
    out.write_bytes(d._build_archive(pay, infos, com, mem, d._serialize_xml(root)))
    return len(cues)


def _snapshot(tl):
    """Every item on every track (+ audio gain/fades) for an exact before/after comparison."""
    snap = {}
    for k in ('video', 'audio', 'subtitle'):
        for i in range(1, tl.GetTrackCount(k) + 1):
            rows = []
            for x in tl.GetItemListInTrack(k, i) or []:
                row = [x.GetName(), int(x.GetStart()), int(x.GetEnd())] + ([] if k == 'subtitle' else [x.GetLeftOffset()])
                if k == 'audio':
                    row += [round(float(x.GetProperty('AudioVolume')), 2), {a: int(b) for a, b in (x.GetFades() or {}).items()}]
                rows.append(row)
            snap[f'{k}{i}:{tl.GetTrackName(k, i)}'] = rows
    return snap


def main(argv=None):
    from scripts.resolve_common import connect_resolve
    from scripts.backup_drp import export_verified
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--timeline', required=True)
    ap.add_argument('--new', required=True)
    ap.add_argument('--styled', required=True, help='DRT whose Subtitle track already carries the style')
    ap.add_argument('--styled-track', type=int, default=1)
    ap.add_argument('--workdir', required=True)
    a = ap.parse_args(argv)
    work = Path(a.workdir)
    work.mkdir(parents=True, exist_ok=True)
    r = connect_resolve()
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    mp = p.GetMediaPool()
    T = {p.GetTimelineByIndex(i).GetName(): p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)}
    if a.new in T:
        raise SystemExit(f'STOP: {a.new} already exists')
    src, entry = T[a.timeline], p.GetCurrentTimeline()
    print('backup', export_verified(pm, p, work / 'pre_substyle.drp'), 'bytes')
    p.SetCurrentTimeline(src)
    time.sleep(1.2)
    before = _snapshot(src)
    cues = [(int(x.GetStart()), int(x.GetEnd()), x.GetName()) for x in src.GetItemListInTrack('subtitle', 1) or []]
    if not cues:
        raise SystemExit('STOP: no cues on Subtitle 1')
    sd, out = work / 'source.drt', work / 'styled_subs.drt'
    sd.unlink(missing_ok=True)
    out.unlink(missing_ok=True)
    if not src.Export(str(sd), r.EXPORT_DRT, r.EXPORT_NONE):
        raise SystemExit('STOP: export failed')
    clone_styled_subtitle_track(sd, a.styled, out, cues, a.styled_track)
    mp.SetCurrentFolder(mp.GetRootFolder())
    tl = mp.ImportTimelineFromFile(str(out), {'timelineName': a.new, 'importSourceClips': False})
    if not tl:
        raise SystemExit('STOP: import failed')
    time.sleep(2)
    if tl.GetName() != a.new and not tl.SetName(a.new):
        raise SystemExit('STOP: rename failed')
    p.SetCurrentTimeline(tl)
    time.sleep(1.5)
    after = _snapshot(tl)
    diff = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    p.SetCurrentTimeline(src)
    time.sleep(1.2)
    if _snapshot(src) != before:
        raise SystemExit('STOP: source timeline changed')
    p.SetCurrentTimeline(entry)
    if diff:
        raise SystemExit(f'STOP: {a.new} differs from {a.timeline} on {diff} (not saved; delete it and check)')
    if not pm.SaveProject():
        raise SystemExit('STOP: save failed')
    # Fusion transforms on adjustment clips round-trip to 15 significant digits; check them with focus tools if present.
    print('ok', a.new, tl.GetUniqueId(), len(cues), 'cues; all tracks, gains and fades equal to', a.timeline)


if __name__ == '__main__':
    main()
