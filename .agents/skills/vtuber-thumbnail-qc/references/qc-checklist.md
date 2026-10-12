# Thumbnail QC Checklist (23 steps)

Use every step; mark N/A only when the input truly lacks the data (say which data is missing).

## A. Content
1. **Content match** — character relevant to clip event? emotion matches clip mood? text describes something that really happens? exaggeration that misleads? background/props/side characters related? is this the most interesting moment? a better moment elsewhere?
   - With timeline/transcript: list `HH:MM:SS – moment` candidates (shock, boss reveal, funny loss, strongest reaction), choose 1–3 top-potential moments.

## B. VTuber character
2.1 **Prominence** — big enough, face clear, expression clear, eyes readable, nothing covering face, not blending into BG, silhouette separated, still recognisable at phone size. VTuber should be one of the main visual foci.
2.2 **Expression** — palette: ตกใจ งง ดีใจ โกรธ เขิน กลัว ช็อก ขำ จริงจัง หัวร้อน สิ้นหวัง ภูมิใจ. Readable instantly? matches clip? strong enough? too stiff/neutral? → name the expression to switch to.
2.3 **Pose/gesture** — stiff? supports story? hands/arms/body language amplify emotion? readable small?
2.4 **Accuracy** — hair colour, eye colour, outfit, key accessories, no design drift, no anatomical errors (hands, fingers, arms, face), no AI artifacts, no unintentional crops.

## C. Structure
3. **Composition** — main focus, secondary focus, eye path A→B, focal point, hierarchy, over-crowded?, useless empty space?, competing objects? Rule: 1 Thumbnail = 1 Main Idea (not 4–5 stories).
4. **Space allocation** — Character / Text / Supporting object / Background / Logo balance. If character is the selling point it needs the visual weight. Multi-character: main vs supporting, focus fight?

## D. Thai text & type
5.1 **Spelling** — consonants, vowels, tone marks, spacing, transliterations, English words, character names, game names. Report `wrong → correct`.
5.2 **Readability (~1 s)** — size, weight, upper/lower vowels and tone marks colliding, stroke too thin, text colour vs BG, outline/shadow helping, too long. Thai-specific: สระบน, สระล่าง, วรรณยุกต์, odd Thai font spacing, outline so thick vowels vanish, effects making words unreadable.
5.3 **Word count** — short, punchy, easy. Bad: a full narrative sentence. Better: "มันเกิดอะไรขึ้น!?", "เกมนี้หลอนเกิน!", "โดนเต็ม ๆ!" — only if true to the clip.
6. **Typography** — font fits mood, Thai/Latin pairing, weight, outline not too thick, shadow not excessive, gradient not hurting legibility, not too many fonts without reason.

## E. Visual values
7. **Contrast** — character vs BG, text vs BG, object vs BG, main vs secondary focus. Busy BG remedies: blur, darken, desaturate, depth of field, glow around character, rim light, stroke, reduce detail. (Repo convention: gameplay stays 0px blur — prefer darken/gradient mask/rim light there.)
8. **Color** — primary, secondary, accent; too many colours? character colour blending? matches VTuber brand? mood fits? Hints (not rules): Horror = black/red/purple/dark green; Funny = yellow/orange/pink/cyan; Gaming = game + character brand colours.
9. **Background** — tells story or steals attention? too bright? too detailed? character separated? relevant to game/moment? Unimportant BG → reduce detail to push character forward.
10. **Supporting elements** — arrows, circles, glow, emoji, icons, game items, other characters, effects, explosions, speed lines, ?/!. Each must have a function; else recommend removal. Never add them just to "look like a YouTube thumbnail".

## F. Tests (use real previews from scripts/qc_previews.py)
11. **Safe area** — 16:9, recommend 1280×720 or larger. Text/face/key objects too close to edges or corners? Bottom-right = duration badge: no important text, logo, face, or item there.
12. **Mobile test (10–20 % size)** — can you still see: (1) what the character feels, (2) what the clip is about, (3) what the text says, (4) the focal point? Any "no" → needs fixing.
13. **Grayscale test** — character still dominant? text separated from BG? focal point clear? Loss of contrast = weak value structure.
14. **Squint test** — should resolve into 2–4 big blobs (e.g. Character, Text, Game object, BG). Scattered small details with no focus → too complex.
15. **First 1-second test** — answer "what is this clip about?" in 1 s; needing 1–2 s+ of reading = unclear communication.

## G. Audience & marketing
16. **Curiosity gap** — raises a question (เกิดอะไรขึ้น? ทำไมตกใจ? ใครชนะ? ของนี้คืออะไร? ทำไมเกมเป็นแบบนี้?) without total confusion. Goal: Understandable + Curious.
17. **Repetition vs channel** — pose, expression, layout, colours, text placement repeated so the feed looks identical? Consistency good; each clip must still be distinguishable.
18. **Brand identity** — recognisable as this VTuber via character, signature colours, graphic style, font, logo, editing style, expression style, composition. Branding must not overpower content.
19. **Thai audience** — natural wording? stiff? instantly understood? memes/game slang fit target audience? English necessary and understood? Avoid Thai that reads like a literal English translation.
20. **Title + thumbnail pair** — shouldn't say the same thing. Bad pair: thumb "บอสโกงมาก" + title "บอสโกงมากในเกม XXX". Good: thumb "มันโกง!!" + title giving the situation. Thumbnail = Emotion/Question, Title = Context. Classify: complementary / redundant / contradictory / no curiosity.
21. **Clickworthiness** — among 10–20 feed neighbours, why would the eye stop here? Face, emotion, contrast, colour, unexpected element, text, scale, composition, curiosity — not beauty alone.
22. **Clickbait class** — GOOD CURIOSITY (real in clip) / BORDERLINE (mild emotional amplification, still related) / MISLEADING (promises event/character/text not in clip → state exactly what to change).

## H. Technical
23. Resolution, aspect ratio, compression, pixelation, blur, JPG artifacts, jagged edges, cutout edges, white halo, colour banding, oversharpening, noise, AI artifacts. On the VTuber zoom into: hair, hair tips, ears, horns, accessories, hands, fingers, eyes, mouth, clothing.

## Severity examples
- 🔴 CRITICAL: Thai misspelling; unreadable text; wrong character design; thumbnail doesn't match clip; obvious AI artifact; key element under duration badge.
- 🟠 IMPORTANT: character too small; low contrast; weak expression; unclear composition.
- 🟡 OPTIONAL: glow tweak, spacing, fewer effects, small hue shift.

## QC rules
1 no flattery · 2 no personal-taste critique · 3 every point has a reason · 4 mobile first · 5 VTuber face & emotion first · 6 always check Thai · 7 always check thumbnail↔content · 8 no unnecessary detail · 9 no clutter for CTR · 10 preserve character identity · 11 no misleading clickbait · 12 unsure → "ไม่สามารถยืนยันจากข้อมูลที่มี" · 13 use timeline/transcript when given · 14 fixes must be actionable.
