---
name: thai-proofread
description: ตรวจสอบและแก้คำผิดภาษาไทย เรียงคำ ตัวสะกด น้ำเสียง
version: 0.3.0
author: Warit (pong34811), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Thai, Proofread, Spellcheck, Grammar]
---







# Thai Proofread







Segment Thai text, check against dictionary, verify tone markers, flag duplicates/invalid characters, and suggest corrections. For Thai VTuber captions — load together with thai-subtitles-resolve or resolve-video-enrichment when caption text needs cleanup.







## When to Use



- "ตรวจสอบ ความถูกต้อง ภาษาไทย เเก้ไขคำผิด"



- Before importing SRT captions into Resolve



- After Whisper transcription output needs cleanup



- House-style caption QA (max 3 words / ~14 Thai chars, no spaces between Thai words)







## Procedure



1. Segment text into words (newlines / pipes / periods as delimiters)



2. Check each word against Thai dictionary; flag unknown / mixed-Latin tokens



3. Verify tone markers (่ ้ ๊ ๋) and vowel completeness



4. Flag duplicates, invalid characters, stray spaces inside Thai runs



5. Output corrected text with a diff; never silently drop speech







## Pitfalls



- Don't auto-fix names without confirmation (Latin names get spaces around them only)



- Don't merge captions past 1.5s on-screen or 3 short words



- Stray `แ็` / `เ` / `า` ligature errors are common — watch for them







## Verification



- Run on a sample caption file; diff shows only real corrections, no dropped cues



- Re-read corrected text end-to-end before import



