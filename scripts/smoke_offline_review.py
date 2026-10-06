"""Offline ASR smoke test from existing preview; no API or Resolve connection."""
import json
from pathlib import Path
from faster_whisper import WhisperModel

ART = Path(__file__).resolve().parents[1] / '.hermes/artifacts/enrichment-review-2026-10-06-live2'
root = Path.home() / '.cache/huggingface/hub/models--mobiuslabsgmbh--faster-whisper-large-v3-turbo/snapshots'
models = [p for p in root.iterdir() if (p / 'model.bin').is_file()]
if not models:
    raise RuntimeError('No complete offline model')
model = WhisperModel(str(models[0]), device='cpu', compute_type='int8', cpu_threads=4,
                     local_files_only=True)
source = ART / 'alternative-smoke-13-first20s.mp4'
segments, info = model.transcribe(str(source), language='th', beam_size=5,
                                 vad_filter=True, word_timestamps=True)
rows = []
for segment in segments:
    row = {'start': segment.start, 'end': segment.end, 'text': segment.text,
           'avg_logprob': segment.avg_logprob,
           'words': [{'start': w.start, 'end': w.end, 'word': w.word,
                      'probability': w.probability} for w in (segment.words or [])]}
    rows.append(row)
    print(json.dumps(row, ensure_ascii=False), flush=True)
result = {'route': 'offline faster-whisper CPU int8; local_files_only',
          'model_path': str(models[0]), 'preview': str(source),
          'language': info.language, 'duration': info.duration,
          'segments': rows, 'status': 'ASR_only_not_audiovisual_or_humor_QC'}
(ART / 'offline-asr-smoke-13.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print('OFFLINE ASR SAVED', flush=True)
