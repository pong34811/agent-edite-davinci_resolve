---
name: vtuber-content-curriculum
description: Thai VTuber content creation curriculum.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [VTuber, Thai, YouTube, Content, Curriculum]
---

# VTuber Content Creation Curriculum

A 24-topic learning curriculum for agents editing Thai VTuber content. Covers content strategy, video production, audio, visual elements, platform-specific editing, AI automation, quality control, and Thai internet culture. Each topic is a reference file loaded on demand.

## When to Use

- "เรียนรู้การทำคอนเทนต์ VTuber ไทย" or "ศึกษาหัวข้อทั้งหมด"
- Agent needs domain knowledge before planning, editing, or reviewing VTuber content
- User asks about any of the 24 curriculum topics
- Before creating a content strategy, script, or editing plan for Thai VTuber channels

## How to Run

1. Load with `skill_view(name="vtuber-content-curriculum")`.
2. Load the relevant topic reference with `skill_view(name="vtuber-content-curriculum", file_path="references/<file>.md")`.
3. Apply the guidance to the current task; do not treat reading as authorization to edit.

## Quick Reference

- `references/content-strategy.md` — Topics 1-3, 23-24: VTuber Thai style, YouTube strategy, scriptwriting, performance analysis, continuous learning
- `references/video-production.md` — Topics 4-6, 12-13: AI editing, pacing, hooks, zoom/cut/transition, character reactions
- `references/audio-and-subtitles.md` — Topics 7-9, 19: Thai subtitles, SFX, BGM, audio mixing
- `references/visual-elements.md` — Topics 10-11, 18: Meme/GIF, motion graphics, thumbnails
- `references/platform-editing.md` — Topics 15-16: Shorts 9:16, long-form 16:9
- `references/intelligence-automation.md` — Topics 17, 22: AI highlight detection, agent workflow
- `references/quality-safety.md` — Topics 20-21: QC, copyright
- `references/thai-culture.md` — Topic 14: Thai humor and internet culture

## Procedure

1. Identify which curriculum topics apply to the current task.
2. Load the relevant reference file(s) with `skill_view`.
3. Apply the principles to the specific content, channel, and audience.
4. For editing tasks, also load `resolve-video-enrichment` and `house-style`.
5. Report what was applied and what remains unverified.

## Pitfalls

- Curriculum principles are starting points, not universal rules — each VTuber has a distinct personality and audience.
- Thai internet culture evolves rapidly; verify current trends before applying.
- Content strategy is not a guarantee of performance; measure and iterate.
- Do not treat learning as authorization to edit, publish, or change Resolve projects.

## Verification

For a learning-only deliverable: every loaded reference file is present and the agent can summarize the key principles of the requested topics. For an edit task: follow `resolve-video-enrichment` verification.