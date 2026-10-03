"""Split the 88 timelines of tygarina_2026-09-30 into per-game projects.

Source of truth: scratch/split_timelines.json (read from the live project, read-only).
The original project is never modified. Usage:
    python scripts/split_projects.py plan            # print groups
    python scripts/split_projects.py build <group>   # create one project, verify, save
"""
import os, sys, json, re, time, collections

sys.stdout.reconfigure(encoding='utf-8')
os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'scratch', 'split_timelines.json')
BASE = 'tygarina_2026-09-30'
MAX_PER_PROJECT = 12
DELAY = 1.2

GAME_ALIASES = {'Gaming_REPO': 'REPO', 'Gaming_Climbing': 'Climbing', 'Gaming_Ib': 'Ib',
                'Fun_DnD': 'DnD', 'Meme_GarticPhone': 'GarticPhone', 'Meme_FreeTalk': 'FreeTalk',
                'Fun_Overcooked': 'Overcooked'}


def game_of(name):
    m = re.search(r'_([A-Za-z0-9]+)-vdo$', name)
    if m:
        return m.group(1)
    m = re.match(r'Highlight_(.+?)(?:_[A-Za-z]+)?$', name)
    for k, v in GAME_ALIASES.items():
        if name.startswith('Highlight_' + k):
            return v
    raise ValueError(name)


def groups():
    rows = json.load(open(DATA, encoding='utf-8'))
    by = collections.defaultdict(list)
    for r in rows:
        by[game_of(r['name'])].append(r)
    out = {}
    for g in sorted(by):
        items = sorted(by[g], key=lambda r: (r['src'], r['ss']))
        chunks = [items[i:i + MAX_PER_PROJECT] for i in range(0, len(items), MAX_PER_PROJECT)]
        # balance so the last chunk is not tiny
        if len(chunks) > 1:
            n = -(-len(items) // len(chunks))
            chunks = [items[i:i + n] for i in range(0, len(items), n)]
        for k, c in enumerate(chunks, 1):
            out[f'{g}' if len(chunks) == 1 else f'{g}_{k}'] = c
    return out


def build(key):
    import DaVinciResolveScript as dvr
    G = groups()
    items = G[key]
    pname = f'{BASE}_{key}'
    resolve = dvr.scriptapp('Resolve')
    pm = resolve.GetProjectManager()
    resume = pname in (pm.GetProjectListInCurrentFolder() or [])
    if resume:
        proj = pm.LoadProject(pname)
        if not proj:
            sys.exit(f'[FATAL] cannot load {pname}')
        print('[INFO] resuming existing project', pname, 'timelines:', proj.GetTimelineCount())
    else:
        proj = pm.CreateProject(pname)
    if not proj:
        sys.exit(f'[FATAL] CreateProject failed: {pname}')
    for k, v in (('timelineFrameRate', '60'), ('timelinePlaybackFrameRate', '24'),
                 ('timelineResolutionWidth', '1920'), ('timelineResolutionHeight', '1080')):
        if not proj.SetSetting(k, v):
            print('[WARN] SetSetting', k, v, 'returned False')
    for k in ('timelineFrameRate', 'timelinePlaybackFrameRate', 'timelineResolutionWidth', 'timelineResolutionHeight'):
        print(k, proj.GetSetting(k))
    mp = proj.GetMediaPool()
    paths = sorted({r['path'] for r in items})
    if resume:
        clips = [c for c in mp.GetRootFolder().GetClipList() or [] if c.GetClipProperty('File Path') in paths]
    else:
        clips = mp.ImportMedia(paths) or []
    by_path = {c.GetClipProperty('File Path'): c for c in clips}
    print(f'[OK] imported {len(clips)}/{len(paths)} source clips')
    if len(clips) != len(paths):
        sys.exit('[FATAL] import count mismatch')
    have = {proj.GetTimelineByIndex(i).GetName() for i in range(1, proj.GetTimelineCount() + 1)}
    for r in items:
        if r['name'] in have:
            print('  exists', r['name']); continue
        c = by_path[r['path']]
        if float(c.GetClipProperty('FPS')) != 60.0:
            # original project forced these 59.94 clips to 60 (metadata only); mirror that
            c.SetClipProperty('FPS', '60')
        if float(c.GetClipProperty('FPS')) != 60.0:
            sys.exit(f"[FATAL] clip fps {c.GetClipProperty('FPS')} {r['src']}")
        tl = mp.CreateEmptyTimeline(r['name'])
        if not tl:
            sys.exit(f"[FATAL] CreateEmptyTimeline {r['name']}")
        proj.SetCurrentTimeline(tl)
        ok = mp.AppendToTimeline([{'mediaPoolItem': c, 'startFrame': r['ss'], 'endFrame': r['se'],
                                   'recordFrame': 0, 'trackIndex': 1}])
        if not ok:
            sys.exit(f"[FATAL] Append {r['name']}")
        time.sleep(DELAY)
        print('  built', r['name'])
    pm.SaveProject()
    # verify
    bad = []
    if proj.GetTimelineCount() != len(items):
        bad.append(f'count {proj.GetTimelineCount()} != {len(items)}')
    tls = {proj.GetTimelineByIndex(i).GetName(): proj.GetTimelineByIndex(i) for i in range(1, proj.GetTimelineCount() + 1)}
    for r in items:
        t = tls.get(r['name'])
        if not t:
            bad.append('missing ' + r['name']); continue
        v = t.GetItemListInTrack('video', 1) or []
        a = t.GetItemListInTrack('audio', 1) or []
        if len(v) != 1 or len(a) != 1:
            bad.append(f"{r['name']} items v{len(v)} a{len(a)}"); continue
        for lbl, it in (('v', v[0]), ('a', a[0])):
            if (it.GetSourceStartFrame(), it.GetSourceEndFrame(), it.GetDuration()) != (r['ss'], r['se'], r['dur']):
                bad.append(f"{r['name']} {lbl} {it.GetSourceStartFrame()},{it.GetSourceEndFrame()},{it.GetDuration()} != {r['ss']},{r['se']},{r['dur']}")
        if t.GetStartFrame() != r['tl_start']:
            bad.append(f"{r['name']} tl_start {t.GetStartFrame()} != {r['tl_start']}")
    if bad:
        print('[FAIL]'); [print(' -', b) for b in bad]; sys.exit(1)
    print(f'[PASS] {pname}: {len(items)} timelines verified, saved')


if __name__ == '__main__':
    if sys.argv[1] == 'plan':
        G = groups(); tot = 0
        for k, v in G.items():
            tot += len(v); print(f'{BASE}_{k}: {len(v)} timelines, {len({r["src"] for r in v})} sources')
        print('total', tot, 'projects', len(G))
    else:
        build(sys.argv[2])
