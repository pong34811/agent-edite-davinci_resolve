---
name: resolve-session
description: Start a Resolve working session — connect, confirm the bridge and edition, open the project, and report timeline and media-pool state before any editing begins.
version: 0.3.1
author: Warit (pong34811), Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Session, Resolve, MCP]
disable-model-invocation: true
---

# Start a Resolve Session

Run this at the top of an editing conversation so the session begins with known

state instead of four rounds of discovery. Report findings compactly; this is

orientation, not an audit.

## Steps

1. **Connect and identify the host.**

   `resolve_control(action="get_version")` — or the nearest capability action.

   Capture: Resolve version, Studio vs free edition, and whether this connected

   over external scripting or the in-app bridge. If the connection fails, read

   the error's own `remediation` field and follow it — it names the applicable

   fix. A connection error does **not** mean the free edition is unsupported;

   the bridge path (Workspace > Scripts > resolve_bridge) covers it, and is used

   automatically once running — `DAVINCI_RESOLVE_BRIDGE=1` only forces it.

   Report **both** versions: `version_string` is the Resolve build,

   `mcp.version` is this server. They fail differently, and one of them is

   easy to forget — a running MCP keeps executing the version it started with,

   so a `git pull` does not refresh its ledger until restart.

2. **Ask what this build cannot do.**

   `get_version` already answers this in its `build.unavailable_on_this_build`

   block, so read that first; `resolve_control(action="check_version_support")`

   is for asking about one named symbol, or for re-checking after a reconnect.

   The scripting API changes per **patch** release, so "Resolve 21" is not a

   usable label: `GetFairlightPresets` needs 20.2.2, and three surfaces exist in

   21.0.4 but not 21.0.2. Knowing this at the top of the session is the

   difference between "that needs 21.0.4, here is the alternative" and

   discovering it halfway through a task.

   Two things to hold on to:

   - An empty list means **nothing recorded is missing**, not that everything

     exists. Most of the API has never been version-bisected, so a symbol with

     no gate returns `unknown` — which means probe it, not yes.

   - Probe with `name in dir(obj)`. Never bare `hasattr`: on a Resolve object it

     returns `True` for every name, real or invented, so it can only say yes.

3. **Report the current project.**

   `project_manager(action="get_current_project")`. If none is open, list

   available projects and stop — ask which to open rather than guessing.

4. **Report timelines.**

   `timeline(action="list")` plus the current timeline's frame rate,

   resolution, duration, and track layout. Frame rate and resolution matter

   before any edit decision; note them explicitly.

5. **Report media pool shape.**

   Bin structure and clip count. Enough to know what is available — not a full

   inventory.

6. **Flag anything that will bite later.**

   Offline or unlinked media, mixed frame rates in the pool, a timeline

   resolution that disagrees with the project, or missing render presets.

## Output

A short block: version and edition, project, current timeline with its format,

pool summary, then warnings — and list anything `check_version_support` reported

missing, since a capability gap changes what is worth proposing. Say what you are

ready to do and wait — do not

start editing off the back of this.

## Notes

- If Resolve is not running, the MCP tools will launch it; the first call can

  take up to 60 seconds. Say so rather than appearing to hang.

- Do not open, create, or switch projects without being asked. Reporting state

  is the whole job here.

- Exception, user-authorised: if Resolve crashes or hangs during a task, run
  `python scripts/resolve_recover.py --project "<project>"` (restarts Google Drive
  when the project library's drive is gone, relaunches via Explorer, reopens the
  project), re-verify the item in flight, and continue. A library on `G:` that
  vanished is the usual cause of `SaveProject` returning False and the crash.

- **Library on `G:` shows empty (only "New Project") but the folder is there**
  (seen 2026-11-07): Google Drive for desktop can list files while every content
  read returns 0 bytes or "Could not find file". `ResolveDebug.txt` then shows
  `Initializing fresh project library ...User.db` and `file is not a database`
  for every `G:` library. `resolve_recover.py` does not catch this (the path
  exists). Two stages were seen:
  1. Every read empty: stop every `GoogleDriveFS.exe`, run
     `C:\Program Files\Google\Drive File Stream\launch.bat`, wait for
     `G:\My Drive` (it can drop once more while the second process restarts).
  2. Files read but stop early, the same byte count every time (`User.db`
     164,514 of 2,912,256; 53 of 128 `.db` files), error `database disk image is
     malformed`. Drive's cached copy was truncated
     (`%LOCALAPPDATA%\Google\DriveFS\<account>\content_cache\...` had a file of
     exactly that size), and "Available offline", a restart or launching the old
     132 exe (it hands off to 133) did not refresh it. The cloud copy was fine:
     the MD5 in Drive's `metadata_sqlite_db` (`items.proto`) did not match the
     read, also not with zero padding. Fix that worked: copy the metadata DB to
     scratch and confirm `select count(*) from operations` is 0 (no pending
     uploads), stop Drive, rename that account's `content_cache` to
     `content_cache.bak_<date>`, run `launch.bat`; every file then read in full
     and passed SQLite `pragma quick_check` (128/128).
  Check each `.db` by reading it to the end and comparing with its size (the
  header alone can look healthy), then reselect the library in Resolve. Do not
  let Resolve "initialize" the library meanwhile. Library paths live in
  `Preferences\dblist.conf`; several names may point at one Drive folder
  (`My Drive\...` and `.shortcut-targets-by-id\...`). Never touch the user's
  `Drive Z` library as a workaround.
