"""One-preview alternative video model smoke test; no Resolve/config changes."""
import base64
import json
import subprocess
from pathlib import Path
from agent.auxiliary_client import get_text_auxiliary_client

ART = Path(__file__).resolve().parents[1] / '.hermes/artifacts/enrichment-review-2026-10-06-live2'
preview = json.loads((ART / 'preview-13.json').read_text(encoding='utf-8'))
source = Path(preview['path']).parent / 'analysis-960x540-15fps.mp4'
path = ART / 'alternative-smoke-13-first20s.mp4'
if not path.exists():
    subprocess.run(['ffmpeg', '-n', '-i', str(source), '-t', '20', '-c:v', 'libx264',
                    '-preset', 'veryfast', '-crf', '30', '-c:a', 'aac', '-b:a', '64k',
                    str(path), '-hide_banner', '-loglevel', 'error'], check=True)
meta = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)], capture_output=True, text=True, check=True).stdout)
client, _ = get_text_auxiliary_client('vision')
if client is None:
    raise RuntimeError('No authorized native video client available')
response = client.chat.completions.create(
    model='gemini-3.5-flash-lite',
    messages=[{'role':'user','content':[
        {'type':'text','text':'Inspect this actual MP4. Return JSON with observed_duration_seconds, audio_received (boolean), seen_scene (Thai), heard_speech_examples (Thai, only words actually audible), existing_sound, coverage_limitations. Describe visible avatar/background and one action with approximate total-seconds timestamp. If unable to hear or view, explicitly say so. Never infer speech solely from subtitles.'},
        {'type':'image_url','image_url':{'url':'data:video/mp4;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')}}]}],
    max_tokens=4096, response_format={'type':'json_object'}, temperature=0.1, timeout=180)
text = response.choices[0].message.content
out = {'model':'gemini-3.5-flash-lite','timeline_id':preview['timeline_id'], 'path':str(path),
       'ffprobe':meta, 'raw_response':text, 'finish_reason':response.choices[0].finish_reason,
       'status':'smoke_pending_source_matching_not_batch_approved'}
(ART / 'alternative-flash-lite-smoke.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'duration':meta['format']['duration'], 'raw_response':text}, ensure_ascii=False), flush=True)
