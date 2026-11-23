# Reader assignments — Katy404/2026-11 (owner: claude)

Each pack has a brief: `review/<pack>.brief.md`. Follow it exactly and write ONLY
`review/<pack>.json`. Do not run pipeline.py stages, do not touch Resolve, do not
run git. Before starting a pack, check that `<pack>.json` does not exist yet.
When you finish, write your result in the channel.

Full ASR is still running (v04-v14). New packs will be added here as they appear.

| Pack | Reader |
|---|---|
| v01-read-01 | chatgpt |
| v01-read-02 | chatgpt |
| v01-read-03 | chatgpt |
| v01-read-04 | opencode |
| v01-read-05 | opencode |
| v01-read-06 | opencode |
| v01-read-07 | antigravity |
| v02-read-01 | claude |
| v02-read-02 | claude |
| v03-read-01 | antigravity |
| v03-read-02 | hermes |
| v03-read-03 | hermes |

opencode: the job already does loudness + full ASR for all 14 videos; please stop
any separate loudness/candidate-transcription scripts so the GPU is free.
