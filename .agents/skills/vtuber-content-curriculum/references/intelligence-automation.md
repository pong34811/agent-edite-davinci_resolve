# Intelligence & Automation (Topics 17, 22)

## 17. AI Highlight Detection

**Core principle:** AI can surface potential moments, but human judgment selects the story.

**AI highlight detection workflow:**
1. **Transcribe:** AI transcribes dialogue with timestamps
2. **Detect:** AI flags potential highlights (laughter, reactions, game events, emotional peaks)
3. **Score:** AI ranks moments by predicted engagement value
4. **Review:** Editor watches flagged moments and selects final highlights
5. **Verify:** Confirm selected moments work in context

**Detection signals:**
| Signal | Detection method | Reliability |
|---|---|---|
| Laughter | Audio analysis + transcription | Medium — verify context |
| Game events | Game audio + visual | Medium — game-specific |
| Emotional peaks | Audio intensity + transcription | Low — needs human review |
| Chat spikes | Chat log analysis | Medium — correlation not causation |
| Story moments | Transcription keyword matching | Low — context dependent |

**Limitations:**
- AI cannot judge comedic timing or cultural context
- AI misses quiet moments that resonate emotionally
- AI over-values loud moments over subtle ones
- Thai speech recognition over game audio is unreliable

**For agents:**
- Use AI suggestions as candidates, not final selections
- Always review AI-highlighted moments in context
- Combine multiple signals for better accuracy
- Track which AI suggestions were selected vs. rejected for calibration

## 22. AI Agent Workflow & Automation

**Core principle:** Automate repetitive tasks, preserve human judgment for creative decisions.

**Agent workflow for Resolve editing:**
```
Task → resolve_preflight.py → MCP (davinci-resolve v4.10.3)
  ↓ MCP-GAP: (logged reason)
  ↓ Python script via scripts/resolve_common.py
  ↓ Must use: preserved_state(), read-back verify, backup_drp.py
```

**Automation principles:**
- **MCP first, script second:** Check MCP catalog before writing scripts
- **Dry-run first:** Test on copies before originals
- **Pilot then batch:** Verify one item end-to-end before scaling
- **Idempotent:** Re-runs must not duplicate work
- **Read-back verify:** Confirm every modification
- **Preserve state:** Restore project, timeline, playhead, page, folder

**Safety rules:**
- Source media is sacred — never modify/transcode/relink
- Mutation rate: ~1.2s between structural edits
- Backup before batch operations (`backup_drp.py`)
- Work in recoverable variants (`_focus_variant`, `_bak`)
- Never overwrite source footage

**Subagent delegation:**
- Use `delegate_task` for parallel evidence gathering
- One controller for live Resolve, subagents for offline analysis
- Immutable ID-keyed packets for disjoint batches
- Controller reconciles results and restores state

**Continuous improvement:**
- Log MCP-GAP reasons for script fallbacks
- Update preflight checks when new limitations found
- Share reusable patterns across editing tasks