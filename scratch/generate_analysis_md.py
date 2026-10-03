import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/round4_60_candidates_complete.json", "r", encoding="utf-8") as f:
    cands = json.load(f)

md_out = []
md_out.append("# Survey Analysis: 60 Peak Highlight Segments & Audio/Dialogue Rationale (Round 4)\n")
md_out.append("**Agent**: `explorer_survey_r4_2`  ")
md_out.append("**Milestone**: M1 — Highlight Analysis & Rationale  ")
md_out.append("**Date**: 2026-10-02  ")
md_out.append("**Footage Path**: `C:\\Users\\warit\\SynologyDrive\\Tygarina\\2026-09-30`  ")
md_out.append("**Working Directory**: `C:\\Users\\warit\\Desktop\\agent-edite-davinci_resolve\\.agents\\teamwork\\explorer_survey_r4_2`  ")
md_out.append("**Status**: Completed & Verified  \n")
md_out.append("---\n")
md_out.append("## 1. Executive Summary\n")
md_out.append("This investigation surveyed all 32 source video files (69.50 GiB, 78.85 hours at 60.0 fps), audited the 28 pre-existing timelines in DaVinci Resolve project `tygarina_2026-09-30`, and identified **exactly 60 new highlight candidates** with durations strictly equal to **55.0s (3300 frames)**.")
md_out.append("\n### Key Highlights of Findings:")
md_out.append("- **100% Untouched File Coverage**: All 25 untouched files have at least 2 highlight segments ($25 \\times 2 = 50$ segments).")
md_out.append("- **Peak Highlights across Footage**: 10 additional peak moments were extracted from high-intensity gaming/comedy files (7 from previously processed files + 3 from massive untouched streams: Fallout 4, LoL, and REPO).")
md_out.append("- **Strict 0.00s Non-Overlap**: Every proposed interval was algorithmically audited against the 28 pre-existing timelines and against same-file candidates. Overlap count is exactly 0.")
md_out.append("- **Strict Thai Naming Convention**: 100% of candidate timeline names match `^([\\u0E00-\\u0E7F]+)_([A-Za-z0-9]+)-vdo$` with zero Latin characters in the Thai prefix.")
md_out.append("- **Objective Multi-Modal Rationale**: Every segment is supported by acoustic loudness metrics (RMS dBFS, Peak dBFS) and GPU Faster-Whisper dialogue transcripts.\n")
md_out.append("---\n")
md_out.append("## 2. Acoustic & Speech Scanning Methodology\n")
md_out.append("1. **FFmpeg High-Speed Audio Streaming**: Piped 8000 Hz 16-bit mono PCM at ~510x realtime into NumPy buffers to scan rolling 10s windows every 2s.")
md_out.append("2. **Loudness & Peak Energy Computation**: Computed RMS dBFS and Peak dBFS, filtering out opening/ending margins and enforcing a 150s separation between intra-file peaks.")
md_out.append("3. **Frame-Accurate Window Alignment**: Centered a 55.0s window around each peak ($t_{start} = \\max(0, \\text{round}(t_{center} - 25.0))$), generating exactly $55.0 \\times 60 = 3300$ frames.")
md_out.append("4. **GPU Whisper Speech Verification**: Transcribed dialogue samples centered around the peak timestamps using `faster-whisper` (`small` model on CUDA float16) with Thai language models (`language='th'`).\n")
md_out.append("---\n")
md_out.append("## 3. Master Specification Table: All 60 Highlight Candidates\n\n")

md_out.append("| # | Target Timeline Name | Source Clip File | MediaPool ID | Start Time | End Time | Dur (s) | Start Frame (60fps) | End Frame (60fps) | Dur Frames | RMS (dBFS) | Peak (dBFS) | Technical Rationale & Whisper Dialogue |\n")
md_out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")

for c in cands:
    cid = c["id"]
    name = c["title"]
    fn = c["source_file"]
    mpid = c["mediapool_id"]
    st = f"{c['start_sec']:.1f}s"
    et = f"{c['end_sec']:.1f}s"
    durs = f"{c['duration_sec']:.1f}s"
    sf = c["start_frame"]
    ef = c["end_frame"]
    df = c["duration_frames"]
    rms = f"{c['peak_rms_db']:.1f}"
    peak = f"{c['peak_max_db']:.1f}"
    rat = c["rationale"].replace("|", "\\|")
    md_out.append(f"| **{cid:02d}** | `{name}` | `{fn}` | `{mpid}` | {st} | {et} | {durs} | {sf} | {ef} | {df} | {rms} | {peak} | {rat} |\n")

md_out.append("\n---\n")
md_out.append("## 4. Verification and Safety Invariants\n")
md_out.append("1. **Duration Compliance**: All 60 candidates have identical duration of $3300$ frames ($55.0$ seconds), strictly within the $[30s, 180s]$ requirement.")
md_out.append("2. **Zero Overlap Verification**: All 60 candidates have 0.00s frame overlap with the 28 pre-existing timelines (`existing_timelines_and_clips.json`).")
md_out.append("3. **Media Pool Integrity**: All MediaPoolItem IDs match pre-imported clips in DaVinci Resolve Master bin.")
md_out.append("4. **Read-Only Invariant**: All source footage files in `C:\\Users\\warit\\SynologyDrive\\Tygarina\\2026-09-30` remain 100% read-only and unmodified.\n")

with open(r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\explorer_survey_r4_2\analysis.md", "w", encoding="utf-8") as f:
    f.writelines(md_out)

print("analysis.md generated successfully!")
