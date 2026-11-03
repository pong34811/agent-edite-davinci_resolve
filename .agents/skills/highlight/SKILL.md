---
name: highlight
description: Entry point for finding the interesting moments in long livestream/VOD files (2-3 h mp4, Thai audio) and turning them into one Resolve timeline per clip. Use when the user runs /highlight, gives a footage folder and asks to find highlights, "หาช่วงน่าสนใจ", "ตัดไฮไลต์", or asks to resume a highlight job. Works the same in Claude Code, Codex and Hermes.
---

# /highlight

```
 footage folder (read-only)                         work/highlight/<channel>/<job>/
 ───────────────────────────                        ──────────────────────────────
 inventory ─► features ─► shortlist ──────────────────────────┐   cheap: loudness, every second
                 │                                            │
                 └► fulltext ─► readpacks ─► READERS ─► proposals   whole stream read by subagents
                                (30 min)    (1/pack)    (quote-checked, quiet tagged)
                                                              │
                    sheets ─► packets+briefs ─► REVIEWERS ◄───┘   one per video, picks final clips
                                                 │
                       schema gate ─► build_timelines ─► APPROVAL ─► Resolve MCP ─► verify_timelines
```

Every stage caches to files, so the job can stop and resume in any agent. `python pipeline.py status` says what is done and prints the ONE next command.

## First use
Also do the `AGENTS.md` start checklist: read `house-style` and `docs/OPERATING-NOTES.md`, read the channel profile in `docs/channels/`, and probe the MCP. The Resolve probe can wait until step 7.
`WORK_DIR` below means the folder that holds `job.json`, which is `work/highlight/<channel>/<job>/`.
```bash
cd scripts/highlight
export HIGHLIGHT_JOB="C:/Users/<you>/Desktop/agent-edite-davinci_resolve/work/highlight/<channel>/<job>/job.json"   # absolute, forward slashes; every command needs it
export PYTHONIOENCODING=utf-8                                                     # Thai file names on Windows
python pipeline.py status
```
No job.json yet: follow `.agents/skills/new-channel-job-setup/SKILL.md` (ask the user's open questions ONCE), copy the spec below, then `python pipeline.py inventory`.
GPU: run `python tools/gpu_smoke.py` once before `fulltext` (CUDA DLLs on Windows: `gpu_env.setup()`).

## Steps
1. **Status.** `python pipeline.py status [ids]`. Do what NEXT says, then run it again after each step. Never redo a stage whose files exist unless its inputs changed. `fulltext`, `readpacks`, `readbriefs`, `proposals`, `packets` and `status` accept video ids, so you can work on one video (`fulltext v01`).
   - **Redoing a video that already has an approved `review/<id>.json`** (status prints a NOTE): ask the user first. Archive the file as `review/<id>.v1.json` before the reviewer writes a new one. Its timelines already exist, so new clips need new names or the `_bak` replacement pattern from `long-video-highlight-clipping`.
   - **Long stages** (`features`, `fulltext`) run in the background:
     - Claude Code: Bash `run_in_background`.
     - Hermes: terminal background/`notify`.
     - Codex: `nohup <cmd> > <WORK_DIR>/<stage>.log 2>&1 &`, then read the log.
2. **Cheap signals.** `features`, then `shortlist` (loudness windows). Footage on `G:/My Drive`: set `DEMUX_WORKERS` 1-2 first.
3. **Whole transcript.** `fulltext` (background; about 34x realtime on the 8 GB RTX, so a 3 h stream takes about 5 min). It writes `transcripts/<id>.fulltext.txt`: `[H:MM:SS] text   [ends s]`.
4. **Readers.** `readpacks` then `readbriefs`. Spawn one subagent per pack with the prompt `Read <WORK_DIR>/review/<pack>.brief.md and follow it exactly.` Run up to 8 at a time. Then `proposals`; it prints rejected items (quote not in the pack, bad order/length) and missing packs.
5. **Final reviewers.** `sheets`, `packets`, `briefs <channel hint>` (rebuild packets after `fulltext`, so they show `[ends]`). Spawn one subagent per video: `Read <WORK_DIR>/review/<id>.brief.md and follow it exactly.` It reads `<id>.proposals.md` first and writes `review/<id>.json`.
6. **Gate.** `python -m pytest -q ../../tests/highlight -k review_files_match_schema`. Check the files, not the subagents' summaries.
7. **Plan.** Read the Resolve project read-only. Save the MCP `media_pool probe_media_pool` result to a file, then run `python resolve_clips.py <file>` to get `resolve_clips.json`. Then `python build_timelines.py` writes `candidates.json` and `timeline_plan.json`. Show the clip list to the user and stop if `APPROVAL` is `ask`.
8. **Resolve.** Follow the `long-video-highlight-clipping` section "Building the timelines": one `media_pool create_timeline_from_clips` per clip (`if_exists: "fail"`), `project_manager save`, then `python verify_timelines.py`.
9. **Hand over.** Report in Thai: timelines made, `quiet` picks, low-confidence clips, and what nobody has watched yet.

Subagents per agent:

| Agent | How to delegate |
|---|---|
| Claude Code | `Agent` with type `general-purpose` (sonnet is enough), prompt as above. |
| Codex | Use a sub-task or run the briefs one by one yourself. |
| Hermes | `delegate_task` with the brief text as context. |

When you do it yourself, write exactly the JSON file the brief names, and nothing else.

## Spec (`job.json`)
```json
{
  "INPUT_DIR": "G:/My Drive/Projects/<Channel>/<YYYY-MM>", "CHANNEL": "<Channel>", "JOB": "<YYYY-MM>",
  "CLIP_MIN_S": 30, "CLIP_MAX_S": 180, "CATEGORIES": ["gameplay", "fun", "meme"], "CLIPS_PER_VIDEO": "3-4",
  "ASPECT": "16:9", "LANGUAGE": "th", "APPROVAL": "ask",
  "GAME_OVERRIDES": {"<file-name substring>": "<game name>"},
  "DEMUX_WORKERS": 2, "SHORTLIST_PER_HOUR": 10,
  "READ_WHOLE_STREAM": true, "FULL_ASR_MODEL": "large-v3-turbo", "FULL_ASR_BEAM": 5
}
```
`READ_WHOLE_STREAM: false` skips steps 3-4 and uses the loudness shortlist only. That is cheaper, but it misses quiet moments.

## Taste
- A clip runs from setup to payoff to reaction. Start it at the first setup sentence and end it at the `[ends]` of the reaction, never on the payoff itself. Snap with `snap.py <id> in:<t> out:<t>`.
- A quiet clip (a story or a dry joke) is as good as a loud one. A loud minute with no words is often just game audio.
- Never put words in the streamer's mouth. Titles and quotes come from the transcript, and the Thai ASR is unverified, so flag low-confidence clips. Do not present the list as watched.
- Timelines only: no titles, captions or effects. Name them `{ชื่อคลิป}-{ชื่อเกม}-vdo`, with the game taken from the picture or from the user, never from the file name alone.
- Footage folders are read-only. Approved `review/<id>.json` files are the user's decisions, so do not overwrite them without asking.

Details and traps for each stage are in `long-video-highlight-clipping`. Load it before step 8, or when a stage fails.
