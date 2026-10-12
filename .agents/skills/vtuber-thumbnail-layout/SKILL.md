---
name: vtuber-thumbnail-layout
description: "VTuber thumbnail layout rules for landscape and Shorts."
version: 0.1.0
author: Hermes
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [VTuber, YouTube, Thumbnail, Layout, Model-Placement, Thai]
---

# VTuber Thumbnail Layout

Canonical rules for VTuber YouTube thumbnail composition in 16:9 landscape and 9:16 Shorts: safe zones, avatar placement, model expression, text hierarchy, and storytelling elements. Source: Davinci Thumbnails knowledge base plus engine specs (src/engine/layout.py, graphics.py, compositor.py).

## When to Use

- "จัดวางโมเดล", "ปกแนวนอน/แนวตั้ง", "วาง avatar ปก", "safe zone thumbnail"
- ทำปกใหม่หรือตรวจเลย์เอาต์ปกที่มีอยู่แล้ว
- แปลแบบจากแนวนอนเป็นแนวตั้ง (ห้าม crop ตรง)

## Prerequisites

- ภาพต้นแบบ Canva หรือ JPG/PNG ของปกที่ต้องตรวจ
- โหลด `skill_view(name="vtuber-thumbnail-qc")` เพื่อ QC หลังจัดวาง
- สำหรับตรวจข้อความไทย โหลด `skill_view(name="thai-proofread")`

## How to Run

เรียก `skill_view(name="vtuber-thumbnail-layout")` แล้วอ่านอ้างอิงที่ต้องการ:
- `references/landscape-layout.md` — ปกแนวนอน 16:9
- `references/portrait-layout.md` — Shorts 9:16
- `references/avatar-placement.md` — อวาตาร์ 5 เลเยอร์, สีหน้า, Gaze
- `references/typography-thai.md` — ฟอนต์, สระ, วรรณยุกต์, stroke
- `references/color-and-storytelling.md` — สี, Hook, Drama elements
- `references/delegation-pattern.md` — 4 บทบาท subagent สำหรับระดมคอนเซ็ปต์

## Quick Reference

- Landscape: 1920×1080, ข้อความซ้ายกลาง `y ≈ 380–520`, โมเดลขวา 35–50%, หลบ Timestamp มุมขวาล่าง
- Shorts: 1080×1920, ข้อความบนกลาง `y ≈ 280–650`, โมเดลล่างกลาง, หลบ 25% ล่าง + 20% ขวา
- Hook หลัก: 1–4 คำ, แดง `#EC1C24`, ขอบดำ ~8%, Mitr Bold
- ข้อความรอง: ขาว `#FFFFFF`, ขอบดำ
- เกม: 0px blur + Gradient Mask ซ้าย; คุย: เบลอ 46–60 px
- Model separation: White stroke 8–18 px + Drop Shadow + Rim Light

## Procedure

1. ล็อกสัดส่วนและจุดประสงค์ (คลิปเกม/คุย/เดบิวต์/Shorts)
2. เลือก reference: landscape หรือ portrait แล้วอ่านไฟล์ที่เกี่ยวข้อง
3. เลือกโมเดล/สีหน้าจาก Avatar Expression Matrix ให้ตรงคลิมักซ์คลิป
4. วาง Avatar Zone + Text Zone ตามพิกัด safe zone ในเลเยอร์นั้น
5. ใส่องค์ประกอบเล่าเรื่อง (วงกลมแดง, !, ?) เฉพาะที่มีหลักฐานในคลิป
6. ตรวจซ้ำด้วย vtuber-thumbnail-qc หลังทำปกเสร็จ

## Pitfalls

- ห้าม crop ปกแนวนอนมาใช้กับ Shorts โดยตรง — จัดองค์ประกอบใหม่
- อย่าวางข้อความใน Timestamp Badge (1580–1900, 980–1060) หรือ Scrubber ล่าง
- อย่าใช้สีแดงมากกว่า 1 จุดบนปก (สงวนเฉพาะ hook หลัก)
- อย่าอ้าง CTR จากความสวยงามโดยไม่มีหลักฐาน

## Verification

- อ่าน `references/landscape-layout.md` และ `references/portrait-layout.md` แล้วพิกัดตรงกับ `src/engine/layout.py`
- โหลด `skill_view(name="vtuber-thumbnail-qc")` แล้ว QC ปกทุกใบหลังจัดวาง