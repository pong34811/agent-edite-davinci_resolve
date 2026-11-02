"""Job-local Whisper fallback: transcribe shortlisted spans with cached PyTorch CUDA model."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import torch
import whisper

import config
import features
from transcribe import boost, read_span, spans

PAD_S = 90
MODEL_NAME = "large-v3-turbo"


def main() -> None:
    inventory = json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))
    model = whisper.load_model(MODEL_NAME, device="cuda")
    out_dir = config.WORK_DIR / "transcripts"
    out_dir.mkdir(parents=True, exist_ok=True)
    for row in inventory:
        source_id = row["source_id"]
        out = out_dir / f"{source_id}.json"
        partial = out_dir / f"{source_id}.partial.json"
        if out.exists():
            print(source_id, "cached", flush=True)
            continue
        top_path = config.WORK_DIR / "scores" / f"{source_id}.top.json"
        windows = [tuple(w) for w in json.loads(top_path.read_text(encoding="utf-8"))]
        work_spans = spans(windows, row["duration_s"], pad=PAD_S)
        state = json.loads(partial.read_text(encoding="utf-8")) if partial.exists() else {"done": [], "segments": []}
        done = {tuple(x) for x in state["done"]}
        for start, end in work_spans:
            key = (float(start), float(end))
            if key in done:
                continue
            audio = boost(read_span(features.wav_path(source_id), start, end))
            result = model.transcribe(
                audio,
                language=config.LANGUAGE,
                fp16=torch.cuda.is_available(),
                condition_on_previous_text=False,
                verbose=False,
            )
            state["segments"].extend(
                {"start": round(seg["start"] + start, 2), "end": round(seg["end"] + start, 2), "text": seg["text"].strip()}
                for seg in result["segments"]
            )
            state["done"].append([start, end])
            partial.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            print(source_id, f"span {start:.0f}-{end:.0f}", f"({len(state['done'])}/{len(work_spans)})", flush=True)
        state["segments"].sort(key=lambda segment: segment["start"])
        out.write_text(json.dumps(state["segments"], ensure_ascii=False), encoding="utf-8")
        partial.unlink(missing_ok=True)
        print(source_id, "transcript complete", flush=True)
    print("done", MODEL_NAME, torch.cuda.get_device_name(0), flush=True)


if __name__ == "__main__":
    main()
