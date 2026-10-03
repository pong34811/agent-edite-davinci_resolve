# Task: Footage Review and 60 Highlight Candidate Extraction

- [x] 1. Inventory 32 video files in `C:\Users\warit\SynologyDrive\Tygarina\2026-09-30` and identify 25 untouched files vs 7 processed files
- [x] 2. Inventory the 28 existing timelines (H1-H7 and R3 clips 1-21) to map forbidden [start_frame, end_frame] intervals
- [x] 3. Check existing scan data / transcripts / audio energy peaks across the 25 untouched files
- [x] 4. Run audio energy scanning / transcript sampling for the untouched files if not already cached
- [x] 5. Select 60 peak highlight candidate segments (50s-70s, target 55.0s / 3300 frames):
  - 2 clips per untouched file (2 * 25 = 50 clips)
  - 10 peak clips across other high-interest moments
- [x] 6. Ensure strict 0.00s overlap with all 28 existing timelines and ensure proper Thai naming `{ชื่อคลิปภาษาไทย}_{ชื่อเกม}-vdo`
- [x] 7. Compile `analysis.md` and `handoff.md` with complete metadata, frames, timestamps, and rationales
- [x] 8. Send message back to parent orchestrator with complete findings
