import os
import sys
import subprocess
import json

sys.stdout.reconfigure(encoding='utf-8')

folder = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
files = [f for f in os.listdir(folder) if f.endswith('.mp4')]

print(f"Analyzing {len(files)} files in {folder}...")

results = []
for f in sorted(files):
    path = os.path.join(folder, f)
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,avg_frame_rate,duration,codec_name",
        "-show_entries", "format=duration,size",
        "-of", "json",
        path
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        probe_data = json.loads(proc.stdout)
        v_stream = probe_data.get('streams', [{}])[0]
        fmt = probe_data.get('format', {})
        
        duration_sec = float(fmt.get('duration', v_stream.get('duration', 0)))
        fps_str = v_stream.get('r_frame_rate', '0/1')
        num, den = map(int, fps_str.split('/')) if '/' in fps_str else (0, 1)
        fps = num / den if den != 0 else 0
        
        results.append({
            "name": f,
            "codec": v_stream.get('codec_name'),
            "width": v_stream.get('width'),
            "height": v_stream.get('height'),
            "fps": fps,
            "fps_str": fps_str,
            "duration_sec": duration_sec,
            "size_mb": os.path.getsize(path) / (1024 * 1024)
        })
    except Exception as e:
        print(f"Error probing {f}: {e}")

# Summary statistics
resolutions = set((r['width'], r['height']) for r in results)
fps_set = set(r['fps'] for r in results)
codecs = set(r['codec'] for r in results)
total_dur_hours = sum(r['duration_sec'] for r in results) / 3600
total_size_gb = sum(r['size_mb'] for r in results) / 1024

print(f"\n--- Footage Summary ---")
print(f"Total video count: {len(results)}")
print(f"Resolutions: {resolutions}")
print(f"Frame rates: {fps_set}")
print(f"Codecs: {codecs}")
print(f"Total duration: {total_dur_hours:.2f} hours")
print(f"Total size: {total_size_gb:.2f} GB")

print("\n--- Detail List (first 10) ---")
for r in results[:10]:
    mins = r['duration_sec'] / 60
    print(f"- {r['name']}: {r['width']}x{r['height']}, {r['fps']:.2f} fps, {mins:.1f} min, {r['size_mb']:.1f} MB")
if len(results) > 10:
    print(f"... and {len(results) - 10} more files.")

# Save full results to json in working directory
out_path = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\explorer_survey_2\footage_specs.json"
with open(out_path, "w", encoding="utf-8") as out_f:
    json.dump(results, out_f, indent=2, ensure_ascii=False)
print(f"Saved full specs to {out_path}")
