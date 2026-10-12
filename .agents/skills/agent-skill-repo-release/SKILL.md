---
name: agent-skill-repo-release
description: Version, tag, push, and publish skill-repo releases.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Git, GitHub, Release, Skills, Versioning]
---

# Agent Skill Repo Release

Cuts a versioned release of the user's agent/skill repositories. These are repos
that package `.agents/skills/` plus scripts and tests. The flow is: sync skills,
bump VERSION and CHANGELOG, commit, tag, push, then publish a GitHub Release with
Thai notes. It does not decide what work is in scope beyond the files of the
current task. Uses `git` and an authenticated `gh` CLI.

## When to Use

- "git push and git add release", "เพิ่ม Releases ด้วย", "release new version"
- "update skill and push" in a repo that ships `.agents/skills/`
- "git push ทั้งหมด" (push everything) with many untracked files — see the bulk-push step below

## Prerequisites

- `gh auth status` logged in. Remotes are `git@github.com:<owner>/<repo>.git`.
- An explicit user request to push or release. That request is the authorization;
  rewriting a pushed tag still needs its own confirmation.

## Procedure

1. Inspect state through the `terminal` tool:
   `git fetch -q && git status -sb`, `git tag`, `git log --oneline -5`,
   `gh release list`, and read `VERSION` / `CHANGELOG.md` with `read_file`.
   Read the latest release body (`gh release view <tag> --json body -q .body`)
   and copy its format.
2. "Update skill" in a repo that has no skills yet means copying the current
   Hermes copies of the relevant skills into `.agents/skills/<name>/`, including
   `references/` and `scripts/` and excluding `__pycache__`. Mirror the sister
   repo's layout. Before publishing, search the copies for usernames, tokens and
   passwords. Say how you interpreted the request in the reply.
3. Choose the version. Use the next minor after the highest tag (tags win over
   a stale `VERSION` file). A repo with no tags starts at `v0.1.0`.
4. Edit `VERSION` with `patch`, not `write_file`. Add a `## vX.Y.Z` section at
   the top of `CHANGELOG.md` with `### Added` / `### Verified` (or `### Scope`).
   Only claim live verification that actually happened. Name dry-run-only paths
   as such.
5. Stage only this task's files: new scripts and tests, `.agents/skills/`,
   `VERSION`, `CHANGELOG.md`, plus clearly related work data. Leave unrelated
   untracked plans, scratch and pilot files alone.
5b. Bulk push ("push everything", no release): before `git add -A`, measure the
   untracked set by extension and size (list with `git status --short -uall`).
   Stage code, docs and JSON, but hold back raster stills and media (PNG/JPG
   frames, often ~6 MB each, hundreds of MB total): they bloat `.git`
   irreversibly and a repo whose AGENTS.md says it holds no footage should not
   carry footage frames. Use `git add -A -- . ':!*.png' ':!*.jpg'`, confirm 0
   staged images and nothing over 1 MB with `git diff --cached --name-only`,
   scan for tokens/keys, commit without a tag, push, and tell the user what was
   held back and why; offer Git LFS or a `.gitignore` entry rather than
   deciding either alone.
5c. Stage release-evidence artifacts only when they are part of the requested
   release and contain reviewable, non-sensitive files. A broad `.gitignore`
   pattern such as `*.drp` also matches files inside subdirectories. To keep
   `.drp` files ignored while allowing selected evidence directories, add
   `!backups/` and explicit file exceptions such as `!backups/*.drp` (plus
   `!backups/**/*.drp` only when deeper levels are intended). Add `!patches/`
   and matching file exceptions only when that directory is explicitly part
   of the release. Verify each exact file with `git check-ignore -v` and
   `git add -n <path>`; unignoring a directory alone does not unignore its
   contents. Never stage database snapshots, media,
   credentials, or private project data by default; confirm the exact file list
   and size before adding evidence.
6. **Before tagging, run `git diff --cached --stat` and confirm `VERSION` is
   staged with the new number.** If an edit was refused, the release commit
   ships the old version, and fixing it later means rewriting a pushed tag.
7. `git commit -m "chore(release): vX.Y.Z — <summary>"`, `git tag vX.Y.Z`,
   `git push origin main && git push origin vX.Y.Z`.
8. Publish the release. Write the notes to a scratch file with `write_file`, then
   `gh release create vX.Y.Z -R <owner>/<repo> --verify-tag --latest
   --title "vX.Y.Z — <สรุปภาษาไทย>" --notes-file <file>`.
   Notes style, which is the user's house format: Thai prose with English for
   code/paths, a `## 🚀 Release vX.Y.Z — …` heading, then `### 🛠️ สิ่งที่เปลี่ยนแปลง`
   (numbered `####` subsections), `### ✅ ผลการตรวจสอบ`, and
   `### 📋 รายละเอียดทางเทคนิค` (commit hashes and limits).
   Include usage commands and a decision table when they exist.

## Pitfalls

- A working tree can carry staged deletions that arrived with an earlier checkout, and `git commit` of a path-scoped `git add` still picks them up. Run `git diff --cached --name-only --diff-filter=D | wc -l` and group the paths by top directory BEFORE committing; if they are work artifacts already covered by `.gitignore` (audit/teamwork records, scratch, reference stills), say so in the release notes rather than pretending the commit was only this task's files.
- Never stage raster stills or media. Verify with a count of staged `png/jpg/mp4/mov/drp` files and a >1 MB sweep over staged additions; report 0/0 in the notes.
- A `.gitignore` pattern like `*.drp` matches at any depth, not just the repo root. A root-only pattern (`/*.drp`) ignores only root files but does not express that nested evidence is intentionally allowed. To allow selected files in a nested evidence directory, use `*.drp`, `!backups/`, and `!backups/*.drp` (add `!backups/**/*.drp` only when deeper files are intended), then verify the exact file with `git check-ignore -v` and `git add -n <path>`.
- Scan the staged additions for tokens/keys before committing, not the whole repo — `gho_`, `ghp_`, `sk-`, `AKIA`, private-key headers.
- A local skill file may legitimately differ from its manifest `source` copy. Compare them with line endings normalised before claiming drift; if the local file only gains frontmatter and reformatted prose, name it as a local amendment, not as "synced with the live copy".
- `gh release view --json` rejects unknown fields and exits non-zero; `isLatest` is not a field — use `gh release list` to confirm the Latest marker.
- When a release adds a `VERSION` or `CHANGELOG.md` change, re-run the repo's manifest/validator step and stage the regenerated manifest plus report in the SAME commit, or the release commit ships stale checksums.

- Moving a pushed tag: get the user's OK first. Then run
  `git tag -f vX.Y.Z <sha>`, `git push origin :refs/tags/vX.Y.Z`,
  `git push origin vX.Y.Z`. Do it before creating the GitHub Release, which
  binds to the tag.
- Never amend or force-push `main` to fix a missed file. Add a follow-up
  `chore(release): …` commit.
- A repo's own bundle validator may already fail before your change. Run the
  task's tests and report the earlier failures as pre-existing. Don't block the
  release on them. Record the failure in the CHANGELOG `### Scope` and release
  notes, and do not hand-refresh the manifest to hide it.
- The system Python has no `pytest`/`yaml`: run tests with
  `uv run --with pytest --with pyyaml python -m pytest <file>` (invoke through
  `terminal`). An exported `PYTHONHOME` left over from a Resolve interpreter
  breaks other Pythons (`SRE module mismatch`); `unset PYTHONHOME` first.
- When the live skill copy is synced into `.agents/skills/`, it also carries
  every earlier unsynced edit (new references, assets, a rewritten SKILL.md).
  Name those in the CHANGELOG `### Updated` entry instead of claiming only this
  task's change.

## Verification

`git ls-remote --tags origin vX.Y.Z` shows the intended sha,
`git show vX.Y.Z:VERSION` prints the new number, and
`gh release view vX.Y.Z --json isDraft,url` reports `isDraft:false`.
