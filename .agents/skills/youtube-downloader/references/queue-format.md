# .download_queue.json format

The queue file stores batch state for resume.

```json
{
  "created_at": "ISO-8601 timestamp",
  "output_dir": "string | null",
  "items": [
    {"url": "https://www.youtube.com/watch?v=ID", "status": "pending|completed|failed"}
  ]
}
```

## Fields
- `created_at`: when batch started, used in resume prompt.
- `output_dir`: destination folder stored at creation. On resume, output_dir is taken from queue, not CLI flag.
- `items[].status`:
  - `pending`: not started
  - `completed`: download succeeded
  - `failed`: yt-dlp error, e.g. Video unavailable, will stay failed on retry

## Workflow notes
- Queue is cleared automatically when all items become `completed`.
- Interrupting with Ctrl+C sets current item to `pending` for safe resume.
- Do not edit manually unless you intend to force status.
