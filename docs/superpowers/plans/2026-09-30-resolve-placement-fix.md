# Resolve Placement Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** แก้จุดวางคลิปไม่ดีและวางไม่เต็มจอใน variants ใหม่โดยไม่แตะต้นฉบับ

**Architecture:** duplicate timeline เป็น _FIX แล้วแก้ transform/crop/composite ด้วย scripting อ่านกลับทุกครั้งและยืนยันด้วย rendered frame

**Tech Stack:** DaVinci Resolve Studio 21.1.0.17, davinci-resolve MCP timeline/timeline_item/timeline_frame/project_manager

**Spec:** รีวิวก่อนหน้าใน session นี้ (17 timelines, 1920x1080 60fps + 1080x1920 60fps, source 1920x1080 AV1)

## Global Constraints

- ทำงานใน recoverable variants เท่านั้น ห้ามแก้ต้นฉบับจนกว่าจะมี verified .drp backup และอนุมัติชัดว่าลงต้นฉบับ
- เก็บ archive timelines ไว้ ห้ามลบถ้าไม่ได้รับอนุมัติแยก
- คง aspect ratio ที่อนุมัติ ห้ามเปลี่ยน 16:9 เป็น 9:16 อัตโนมัติ
- ค่า transform ต้องเป็นตัวเลข ไม่ใช่ string อ่านกลับหลัง setter False ก่อน retry
- โครงสร้างเปลี่ยนทีละขั้นห่าง ~1.2s save แล้ว read back
- ซับไทยสั้น: ไม่เกิน 3 คำสั้น / ~14 ตัวอักษรไทย / ไม่เกิน 1.5s ไม่เว้นวรรคระหว่างคำไทย batch ซับต้องผ่าน sample approval ก่อน (OPERATING-NOTES Task 3 gate)
- Subtitle import ใช้ empty subtitle track + bare {"mediaPoolItem": item} เท่านั้น
- ยืนยันด้วย rendered frame (timeline_frame quality frame/preview) ไม่ใช้ thumbnail/contact sheet ตัดสินภาพ
- Save ด้วย ProjectManager.SaveProject อ่านกลับทุก target และคืน active project/timeline/playhead/page/folder/track states เดิม
- รายงานเฉพาะสิ่งที่ verified จริง

## Review Focus

- ช็อตแนวตั้ง V1 เดี่ยวเหลือขอบดำบนทั้งที่ Zoom เกิน fill แล้ว
- overlay แมว/โลโก้บังหน้า VTuber กลางจอ
- Text+ ซ้ำกับ native subtitle และซับยาว/นานเกิน
- แทร็กเปล่า V2/V4/V5 0 ชิ้นรกแต่ลบไม่ได้ถ้าไม่มีอนุมัติ
- donation/chat bar ทับซับล่างในแนวตั้ง

---

### Task 1: Backup และ safety snapshot

**Files:**
- Create: `C:/Users/warit/AppData/Local/Temp/opencode/backup/AOMI_DEBUT_2026-09-30.drp`
- Modify: live Resolve project (save only)

**Interfaces:**
- Consumes: current project name
- Produces: verified .drp path + save state token

- [ ] **Step 1: Save project และจำ state เดิม**

```js
const cur = await tools["davinci-resolve"].timeline({action: "get_current"});
const saved = await tools["davinci-resolve"].project_manager({action: "save"});
```

- [ ] **Step 2: Export .drp backup**

Run: `project_manager export_project` ไปยัง Temp/opencode/backup
Expected: success true + ไฟล์ขนาด >0

- [ ] **Step 3: Verify backup อ่านกลับได้**

Run: check file exists + size + `project_manager list`
Expected: PASS

- [ ] **Step 4: Commit (repo plan only)**

```bash
git add docs/superpowers/plans/2026-09-30-resolve-placement-fix.md
git commit -m "plan: resolve placement fix variants"
```

### Task 2: Duplicate variants สำหรับ 4 timelines วิกฤต

**Files:**
- Modify: live timelines (duplicate only)

**Interfaces:**
- Consumes: ชื่อต้นฉบับ 4 ตัว
- Produces: ชื่อ _FIX 4 ตัวพร้อม unique id

Targets:
- `เคยเล่น Rov ไหม` -> `เคยเล่น Rov ไหม_FIX`
- `เคยเล่น Rov ไหม_9x16` -> `เคยเล่น Rov ไหม_9x16_FIX`
- `เกมเเรกที่เริ่มไลฟ์คือ_9x16` -> `เกมเเรกที่เริ่มไลฟ์คือ_9x16_FIX`
- `สาเหตุไม่ชอบหนอนเเมลง_9x16` -> `สาเหตุไม่ชอบหนอนเเมลง_9x16_FIX`

- [ ] **Step 1: Duplicate ทีละตัวห่าง ~1.2s**

```js
await tools["davinci-resolve"].timeline({action: "set_current", params: {name: "เคยเล่น Rov ไหม"}});
await tools["davinci-resolve"].timeline({action: "duplicate", params: {name: "เคยเล่น Rov ไหม_FIX"}});
```

- [ ] **Step 2: Read back ทุกตัว**

Run: `timeline list` + `get_current`
Expected: เจอ 4 ชื่อ _FIX ครบ id ใหม่

- [ ] **Step 3: SaveProject**

Run: `project_manager save`
Expected: success true

### Task 3: Fix vertical top black bar (V1 Tilt) ใน 2 FIX variants

**Files:**
- Modify: `เกมเเรกที่เริ่มไลฟ์คือ_9x16_FIX` V1, `สาเหตุไม่ชอบหนอนเเมลง_9x16_FIX` V1

**Interfaces:**
- Consumes: _FIX names + transform เดิม
- Produces: Tilt ใหม่ที่ไม่มีขอบดำ + rendered frames

Hypothesis: Tilt ติดลบมากไปดึงภาพลงจนเปิดขอบบน วิธีแก้คือขยับ Tilt ขึ้นครั้งละ +40-60 แล้ว capture จนขอบดำหายโดยหน้ายังอยู่กลาง

- [ ] **Step 1: เข้า FIX แรกอ่าน transform ปัจจุบัน**

```js
await tools["davinci-resolve"].timeline({action: "set_current", params: {name: "เกมเเรกที่เริ่มไลฟ์คือ_9x16_FIX"}});
const tr = await tools["davinci-resolve"].timeline_item({action: "get_transform", params: {track_type: "video", track_index: 1, item_index: 1}});
```

- [ ] **Step 2: ปรับ Tilt +60 ทีละคลิปกลุ่มเดียวกัน (numeric only)**

```js
await tools["davinci-resolve"].timeline_item({action: "set_transform", params: {track_type: "video", track_index: 1, item_index: 1, Tilt: -277}});
```

- [ ] **Step 3: Read back + capture preview frame 170**

Run: `get_transform` + `timeline_frame capture frame 170 quality preview`
Expected: FAIL ก่อนแก้มีแถบดำ / PASS หลังแก้ไม่มีแถบดำ หัวไม่ขาด

- [ ] **Step 4: ขยายผลเฉพาะกลุ่ม Zoom เดียวกัน save + read back**

Run: `project_manager save`
Expected: PASS

### Task 4: ย้าย overlay แมว/โลโก้ไม่ให้บังหน้า (FIX เคยเล่น Rov)

**Files:**
- Modify: `เคยเล่น Rov ไหม_FIX` V3 i0-i1, `เคยเล่น Rov ไหม_9x16_FIX` V4 455-603

**Interfaces:**
- Consumes: transform เดิม Zoom 1 center
- Produces: PiP มุมขวาล่าง Zoom 0.4-0.5 Pan/Tilt มุมปลอดภัย + rendered frames

- [ ] **Step 1: ย่อโลโก้ ROV เหลือ 0.5 ย้ายขวาล่าง**

```js
await tools["davinci-resolve"].timeline_item({action: "set_transform", params: {track_type: "video", track_index: 3, item_index: 0, ZoomX: 0.5, ZoomY: 0.5, Pan: 600, Tilt: -300}});
```

- [ ] **Step 2: ย่อแมวเหลือ 0.45 ย้ายซ้ายล่างพ้นหน้า**

```js
await tools["davinci-resolve"].timeline_item({action: "set_transform", params: {track_type: "video", track_index: 3, item_index: 1, ZoomX: 0.45, ZoomY: 0.45, Pan: -600, Tilt: -280}});
```

- [ ] **Step 3: Read back + capture frame 100 และ 500**

Run: `get_transform` ทั้ง 2 + `timeline_frame capture`
Expected: หน้าชัด ไม่ถูกบัง โลโก้/แมวอยู่มุม

- [ ] **Step 4: Save**

Run: `project_manager save`
Expected: PASS

### Task 5: Subtitle sample (ไม่ batch) + คืน state

**Files:**
- Modify: subtitle track ใน FIX เดียวเพื่อขออนุมัติเท่านั้น

**Interfaces:**
- Consumes: cue ที่เกิน 14 ตัวอักษร / เกิน 1.5s
- Produces: SRT sample 3 cues + รายงาน ไม่เขียนทั้ง timeline

- [ ] **Step 1: ดึง cue 3 ตัวอย่างที่เกิน**

Run: `timeline get_transcript with_timecodes`
Expected: ได้ 3 cues พร้อม start/end frames

- [ ] **Step 2: แยก cue ตาม house-style บนกระดาษ (ยังไม่ import)**

เช่น `ซึ่งเกมแรกที่หนูเริ่มไลฟ์ (25 ตัว, 2.48s)` -> `ซึ่งเกมแรก` + `ที่หนูเริ่มไลฟ์` อย่างละ ≤1.5s ไม่มีช่องไฟระหว่างคำไทย

- [ ] **Step 3: Restore active timeline/playhead เดิม + save**

Run: `set_current เคยเล่น Rov ไหม_9x16` + `project_manager save` + `get_current` ยืนยัน
Expected: PASS กลับที่เดิม
