# YouTube packaging and evidence-led improvement

## What this chapter can and cannot claim
- YouTube describes recommendation goals in terms of relevant choices and long-term viewer satisfaction, using personalized and performance signals.[8]
- Therefore optimize for a real viewer promise and a satisfying payoff, not a mythical fixed recipe for the algorithm.
- This chapter combines official metric definitions with editorial diagnostic hypotheses; hypotheses require channel-specific evidence.
- No analytics, creator interviews, audience experiments, or success benchmarks were supplied for this learning task.
- Do not invent channel results, retention targets, best upload hours, or a guaranteed viral edit.
- Re-fetch official metric definitions through `web_extract` when reporting current performance; definitions and UI labels can change.

## Packaging: a truthful promise
- YouTube recommends accurate, concise titles with important words near the beginning; thumbnails should be clear and not overcomplicated.[7]
- Distinguish a searchable title from an intriguing title according to who should discover the clip.[7]
- Existing fans may recognize a name/running joke; newcomers need an understandable action or emotion.[7]
- Thai application: lead with the actual event or contradiction, then the creator/game context when useful.
- Treat example patterns such as `[ชื่อ] มั่นใจเต็มที่...ก่อนเจอสิ่งนี้` as drafts only; replace vague bait with the real event when it is clearer.
- Do not manufacture anger, romance, scandal, or an insult that the clip does not contain.
- Let thumbnail and title complement each other instead of repeating a full subtitle twice.
- Check the thumbnail at phone size: one readable focus, recognizable expression, and only necessary text.
- A Shorts feed hook needs the first frame and sound to work; a good thumbnail does not repair an unclear opening.
- Use the current format's actual thumbnail controls; do not assume long-form thumbnail upload/testing features apply to Shorts.
- Draft alternate titles/thumbnails locally; uploading or changing a published video needs explicit authorization.

## Read the right surface
1. In YouTube Studio, channel-level `Analytics > Content` provides format and traffic-source reports.[5]
2. For one video's retention, use `Content > [video] > Analytics > Overview` or `Engagement`.[3]
3. Record the actual metric label, format, traffic source, date range, upload age, and sample size with every comparison.
4. Use provided exports/screenshots or an authorized account session; missing access is not permission to guess credentials or results.
5. Prefer like-for-like videos by format, length, topic, audience, and exposure window.
6. Keep organic/paid, new/returning, and subscribed/non-subscribed cohorts separate when the data supports it.[3]

## Metrics by the question they answer
| Question | Metric / evidence | Interpretation boundary |
|---|---|---|
| Did the package attract a click? | Registered thumbnail impressions and CTR | Applies to counted thumbnail surfaces, not every feed exposure.[5] |
| Did a Short stop the swipe? | Stayed to watch | Percentage staying beyond initial seconds, not proof they finished.[5] |
| How many chose to continue? | Engaged views | Excludes loops in the official definition; not interchangeable with raw starts/views.[5] |
| How much was watched? | Average view duration and average percentage viewed | Among those who stayed, derived from engaged views/watch time under the retrieved definition.[5] |
| Where did attention change? | Retention curve / top moments / dips / spikes | Diagnose the actual frames and audio before assigning a cause.[3] |
| Did it create continuing interest? | Subscribers gained, returning/regular viewers where available, qualitative comments | Supporting evidence, not a universal ranking formula.[5] |
| Was the promised feeling delivered? | Specific viewer feedback plus watch behavior | A high click count alone cannot establish satisfaction. |

- Preserve the exported metric names and definitions rather than silently normalizing older datasets to a newer view definition.
- Do arithmetic and rate comparisons through `execute_code` or `terminal`; state denominators and never compare a count with a percentage.
- More impressions can bring a different audience mix; a CTR change alone does not identify an editing cause.
- Do not rank a long highlight against a very short loop by raw completion percentage alone.
- Do not treat repeated plays as proof that viewers understood or enjoyed the clip.

## Retention: read, then inspect
- Officially, flat sections indicate viewers staying through that part; dips identify skipping or leaving; spikes can indicate rewatches or shares.[3]
- Spikes can also mean the content was unclear and had to be rewatched.[3]
- The intro metric describes the first 30 seconds; it is not a command to build a 30-second introduction or a universal Shorts threshold.[3]
- Typical retention can compare the ten latest videos of similar length when available.[3]
- Retention data typically takes one to two days to process; do not treat an unavailable chart as zero interest.[3]
- Highlighted key-moment detection has eligibility conditions, including at least 60 seconds and 100 views in the retrieved help page; this is not a blanket statement that shorter videos have no analytics.[3]
- Review frames, captions, sound, and the preceding setup at each change point; graph timing is evidence to investigate, not a cut instruction.

## Diagnostic decision table
The causes and edits below are hypotheses, not conclusions supplied by the platform.

| Observed pattern | Inspect first | One controlled next edit |
|---|---|---|
| Weak stayed-to-watch, reasonable watch depth among stayers | Unclear first frame, delayed premise, wrong audience context | Open on the meaningful contradiction while preserving the cause |
| Strong CTR but a sharp early drop | Promise mismatch, long greeting, audio shock, missing context | Align the opening with the package and remove only unnecessary preamble |
| Drop during setup | Redundant explanation or essential context that is hard to parse | Shorten repetition or clarify one referent; do not delete all setup |
| Drop on a caption-heavy section | Reading speed, obstruction, wrong wording | Fix grouping/readability without omitting speech |
| Spike on a punchline | Genuine delight versus unclear audio/subtitle | Rewatch/listen and check comments before repeating the device |
| Exit after payoff | Whether the story is already complete | End cleanly rather than add an unearned second hook |
| Good watch depth, weak follow-up interest | Whether the clip reveals a recognizable creator/series | Improve truthful creator context or related-content linkage |
| Strong small-sample result | Cohort size and unusual traffic source | Gather comparable evidence instead of declaring a new rule |

## A practical experiment loop
1. Record a baseline from comparable existing clips, or state explicitly that none exists.
2. Form one question, e.g. whether showing the gameplay cause before the close-up improves clarity.
3. Specify one edit variable, the expected viewer effect, a primary metric, and a guardrail such as speech accuracy or satisfaction feedback.
4. Use the next approved comparable clips or an actually available authorized testing feature; do not claim randomization if there is none.
5. Choose the observation window before comparing; wait for the data being used to be available.
6. Preserve topic, format, traffic source, duration, and upload-age notes so confounders are visible.
7. Read results with the relevant audio/video segment, not just a dashboard screenshot.
8. Record `keep`, `revise`, or `inconclusive` with evidence and the next question.
9. Repeat across comparable cases before promoting a hypothesis to channel house style.
- Organic comparisons are observational; seasonality, game interest, creator events, and audience shifts can explain the difference.
- Do not change title, thumbnail, hook, duration, captions, and music simultaneously and then credit only one change.
- A low-performing experiment does not justify erasing source/context or escalating clickbait.

## Sustainable audience fit
- YouTube recommends learning audience interests, recognizable quality, and sustainable output rather than sheer upload frequency.[8]
- Its guidance does not identify publish time as a known driver of long-term viewership; live/premiere scheduling is a separate audience-availability issue.[8]
- Translate useful feedback into a specific testable edit rule, not a stereotype such as "Thai viewers only like memes".
- Record the creator's boundaries and the user's approved exemplar alongside performance notes.
- Keep current facts in the report and reusable decision rules in the skill; do not turn temporary analytics into permanent memory.

## Verification
- Each proposed improvement must name an observed issue or an explicit hypothesis, an exact edit variable, a suitable metric, and a scope-safe way to test it.
- All reported figures must resolve to actual authorized data; all publication changes must be read back at the exact target.

## Sources

[3] https://support.google.com/youtube/answer/9314415?hl=en-WS
[5] https://support.google.com/youtube/answer/12220281
[7] https://support.google.com/youtube/answer/12340300?hl=en
[8] https://support.google.com/youtube/answer/16533387?hl=en
