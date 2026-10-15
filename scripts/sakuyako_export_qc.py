"""Read-only ffmpeg/ffprobe analysis of Resolve exports and contact sheets."""
import json
import subprocess
import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scripts.sakuyako_export_preflight import OUT,VDO

def run(args):
    return subprocess.run(args,capture_output=True,text=True,encoding='utf-8',check=True)

def extract(path, seconds, dest):
    run(['ffmpeg','-v','error','-y','-ss',str(seconds),'-i',str(path),'-map','0:v:0','-frames:v','1',str(dest)])

def cover_ssim(frame,cover):
    r=run(['ffmpeg','-i',str(frame),'-i',str(cover),'-lavfi','[0:v]scale=1080:1920[a];[1:v]scale=1080:1920[b];[a][b]ssim','-f','null','-'])
    return float(re.search(r'All:([\d.]+)',r.stderr).group(1))

def main():
    jobs=json.loads((OUT/'jobs.json').read_text(encoding='utf-8'))
    baseline={t['name']:t for t in json.loads((OUT/'baseline.json').read_text(encoding='utf-8'))['timelines']}
    qc=OUT/'visual-qc'; qc.mkdir(exist_ok=True)
    rows=[]
    names=[s for s in sys.argv[1:] if not s.startswith('--')]
    for idx,j in enumerate(jobs):
        if names and j['out_name'] not in names: continue
        if '--completed' in sys.argv and j.get('status')!='Complete': continue
        f=next(p for p in VDO.glob(j['out_name']+'.*') if p.suffix.lower() in ('.mp4','.mov','.mkv'))
        b=baseline[j['timeline']]; cues=[x for track in b['tracks']['subtitle'] for x in track['items']]
        assert cues, 'no cues'
        duration=(b['end']-b['start'])/30
        offset=1 if j['vertical'] else 0
        samples=[]
        first=cues[0]
        times=[0.1,duration/2,max(0,duration-0.1),((first['start']+first['end'])/2-b['start'])/30]
        for n,content_stamp in enumerate(times):
            stamp=content_stamp+offset
            c=next((c for c in cues if c['start']<=content_stamp*30+b['start']<c['end']),None)
            dest=qc/f'{idx:02d}_{n}.png'; extract(f,stamp,dest)
            samples.append({'path':str(dest),'seconds':stamp,'cue':c['name'] if c else '(ไม่มีซับช่วงนี้)'})
        row={'name':j['out_name'],'vertical':j['vertical'],'samples':samples,'errors':[]}
        if j['vertical']:
            scores=[]
            for n,stamp in enumerate([0,29/30]):
                dest=qc/f'{idx:02d}_cover{n}.png'; extract(f,stamp,dest)
                scores.append(cover_ssim(dest,VDO/(j['out_name']+'.jpg')))
            row['cover_ssim']=scores
            if min(scores)<0.9: row['errors'].append('cover mismatch')
            r=run(['ffmpeg','-hide_banner','-i',str(f),'-vn','-af','atrim=end=1,volumedetect','-f','null','-'])
            level=float(re.search(r'max_volume: ([\-\w.]+) dB',r.stderr).group(1))
            row['cover_audio_max_db']=level
            if level>-70: row['errors'].append('sound during cover')
            boundary=qc/f'{idx:02d}_content0.png'; extract(f,1,boundary)
            row['content_first_ssim_to_cover']=cover_ssim(boundary,VDO/(j['out_name']+'.jpg'))
            if row['content_first_ssim_to_cover']>=0.9: row['errors'].append('cover persists into content')
            # Paired exports must contain the same audio after the one-second lead-in.
            import numpy as np
            horizontal=next(p for p in VDO.glob(j['out_name'][:-5]+'.*') if p.suffix.lower() in ('.mp4','.mov','.mkv'))
            def samples(path,ss):
                raw=subprocess.run(['ffmpeg','-v','error','-ss',str(ss),'-i',str(path),'-t','5','-vn','-ac','1','-ar','8000','-f','f32le','-'],capture_output=True,check=True).stdout
                return np.frombuffer(raw,dtype=np.float32)
            a,bb=samples(horizontal,2),samples(f,3)
            length=min(len(a),len(bb)); a,bb=a[:length],bb[:length]
            row['paired_audio_correlation']=float(np.corrcoef(a,bb)[0,1])
            if row['paired_audio_correlation']<0.99: row['errors'].append('paired audio differs')
        rows.append(row)
        print('QC',j['out_name'],row.get('cover_ssim'),row.get('cover_audio_max_db'),row['errors'],flush=True)
    font=ImageFont.truetype('C:/Windows/Fonts/tahoma.ttf',20)
    sheets=[]
    for vertical in [False,True]:
        group=[r for r in rows if r['vertical']==vertical]
        per_sheet=2 if vertical else 4
        w,h=540,(960 if vertical else 304)
        for begin in range(0,len(group),per_sheet):
            page=group[begin:begin+per_sheet]
            sheet=Image.new('RGB',(w*4,(h+85)*len(page)),(25,25,25)); draw=ImageDraw.Draw(sheet)
            for rn,row in enumerate(page):
                y=rn*(h+85); draw.text((8,y+2),row['name'],font=font,fill='white')
                for col,s in enumerate(row['samples']):
                    im=Image.open(s['path']).convert('RGB'); im.thumbnail((w,h))
                    sheet.paste(im,(col*w,y+32)); draw.text((col*w+5,y+h+35),f"{s['seconds']:.2f}s  {s['cue']}",font=font,fill='white')
            path=qc/f"{'vertical' if vertical else 'horizontal'}_{begin//per_sheet:02d}.jpg"
            sheet.save(path,quality=94); sheets.append(str(path))
    report={'rows':rows,'sheets':sheets}
    (qc/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=1),encoding='utf-8')
    print('SHEETS',sheets,flush=True)
    assert not any(r['errors'] for r in rows)

if __name__=='__main__': main()
