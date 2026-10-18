# Skill authoring rules (from `superpowers-writing-skills`)

Source: `.agents/skills/superpowers-writing-skills/SKILL.md` (681 lines — the
largest skill in the bundle) plus its supporting files
(`anthropic-best-practices.md`, `persuasion-principles.md`,
`testing-skills-with-subagents.md`, `graphviz-conventions.dot`,
`render-graphs.js`). Load that skill itself before authoring; this file is the
distilled decision structure.

## The Iron Law

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

It applies to NEW skills AND EDITS to existing skills. Wrote the skill before
testing it? Delete it and start over. **No exceptions** — not for "simple
additions", not for "just adding a section", not for "documentation updates", not
for keeping untested changes as "reference", not for "adapting" while running
tests. Delete means delete.

## When to create a skill (and when not to)

**Create when:** the technique was not intuitively obvious; you would reference it
again across projects; the pattern applies broadly; others would benefit.

**Don't create for:** one-off solutions; standard practices documented elsewhere;
project-specific conventions (those go in the instructions file); mechanical
constraints (if it is enforceable with regex/validation, automate it — save
documentation for judgment calls).

## Skill types

- **Technique** — a concrete method with steps (condition-based-waiting,
  root-cause-tracing).
- **Pattern** — a way of thinking about problems (flatten-with-flags,
  test-invariants).
- **Reference** — API docs, syntax guides, tool documentation.

## Layout

```
skills/
  skill-name/
    SKILL.md              # required
    supporting-file.*     # only if needed
```

Flat namespace. Separate files for heavy reference (100+ lines) and reusable tools
(scripts, utilities, templates); keep principles, concepts and code patterns under
50 lines inline. Invoke bundled scripts **through their interpreter in the prose**
(`bash scripts/tool.sh`, `node scripts/tool.js`), never by bare path — some
harness plugin packagers strip executable bits and a bare `scripts/tool.sh` fails
there with `Permission denied`.

## Frontmatter

Two required fields: `name` and `description` (max 1024 characters total). `name`
uses letters, numbers and hyphens only — no parentheses or special characters.

**`description` describes ONLY when to use, never what the skill does.** Start
with "Use when...", include specific symptoms/situations/contexts, third person,
under 500 characters if possible, and **never summarize the process or workflow**.

Why this is load-bearing, not stylistic: testing showed that when a description
summarized the workflow, an agent followed the description instead of reading the
skill. A description saying "code review between tasks" caused an agent to do ONE
review even though the skill's flowchart clearly showed TWO (spec compliance, then
code quality). Changing it to "Use when executing implementation plans with
independent tasks" (no workflow summary) made the agent read the flowchart and
follow the two-stage process. **Descriptions that summarize workflow create a
shortcut agents will take; the skill body becomes documentation they skip.**

```yaml
# BAD: summarizes workflow - agents may follow this instead of reading the skill
description: Use when executing plans - dispatches subagent per task with code review between tasks
# BAD: too much process detail
description: Use for TDD - write test first, watch it fail, write minimal code, refactor
# GOOD: just triggering conditions, no workflow summary
description: Use when executing implementation plans with independent tasks in the current session
# GOOD: triggering conditions only
description: Use when implementing any feature or bugfix, before writing implementation code
```

## Match the form to the failure (the highest-value table here)

Classify the baseline failure before writing guidance — the form that bulletproofs
one failure type measurably backfires on another.

| Baseline failure | Right form | Wrong form |
|---|---|---|
| Skips/violates a rule under pressure (knows better, does it anyway) | Prohibition + rationalization table + red flags | Soft guidance ("prefer...", "consider...") |
| Complies, but output has the wrong shape (bloated prompt, buried verdict, restated spec) | Positive recipe or contract: state what the output IS — its parts, in order | Prohibition list ("don't restate", "never narrate") |
| Omits a required element from something they already produce | Structural: a REQUIRED field or slot in the template they fill in | Prose reminders near the template |
| Behavior should depend on a condition | Conditional keyed to an observable predicate ("if the brief exists, reference it") | Unconditional rule + exemption clauses |

**Why prohibitions backfire on shaping problems:** under a competing incentive
("make the prompt self-contained"), agents negotiate with "don't X". In
head-to-head wording tests on dispatch-prompt guidance, the prohibition arm
produced clearly more of the unwanted content than the recipe arm (fully separated
distributions) and trended worse than even the no-guidance control. Micro-test
your own case rather than assuming — but never reach for the prohibition by
default. A recipe leaves nothing to negotiate.

**Rules for whichever form you pick:**

- **No nuance clauses.** "Don't X unless it matters" reopens the negotiation —
  appending a single nuance clause to a winning recipe degraded it from consistent
  to noisy in the same tests. Express a real exception as its own conditional on an
  observable predicate.
- **Exemption clauses don't scope.** "This limit doesn't apply to code blocks"
  still suppresses code blocks. If part of the output must be exempt, restructure
  so the rule cannot reach it.

## Bulletproofing discipline skills against rationalization

Scope: this toolkit is for **discipline failures** (knows the rule, skips it under
pressure). For wrong-shaped output or omitted elements, prohibition-based
bulletproofing backfires — use the form table above.

- **Close every loophole explicitly.** Not "Write code before test? Delete it." but
  the version that also forbids the workarounds: don't keep it as "reference",
  don't "adapt" it while writing tests, don't look at it, delete means delete.
- **Address "spirit vs letter" arguments** — state that the letter is the spirit.
- Psychology foundation (Cialdini 2021; Meincke et al. 2025 — authority, commitment,
  scarcity, social proof, unity) is in `persuasion-principles.md`.

## RED-GREEN-REFACTOR for skills

- **RED — write the failing test.** Run the pressure scenario with a subagent
  WITHOUT the skill and document exact behaviour: what choices, which
  rationalizations (verbatim), which pressures triggered violations. You must see
  what agents naturally do before writing the skill.
- **GREEN — write the minimal skill** that addresses those specific
  rationalizations. Do not add content for hypothetical cases. Re-run WITH the
  skill; the agent should comply.
- **REFACTOR — close loopholes.** New rationalization found? Add an explicit
  counter and re-test until bulletproof.

**Micro-test the wording before full scenarios** (full runs are the final gate but
slow and expensive per iteration): one fresh-context sample per call with the
system prompt set to the realistic context the guidance will live in; **always
include a no-guidance control** (if the control doesn't exhibit the failure there
is nothing to fix — stop and don't author the guidance); 5+ reps per variant;
**manually read every flagged match**, because template echoes and quoted
counter-examples masquerade as hits; and treat variance as a metric — when
wording lands, reps converge on the same shape.

## Testing all skill types

- **Discipline-enforcing** (TDD, verification-before-completion,
  designing-before-coding): academic questions, pressure scenarios, multiple
  pressures combined (time + sunk cost + exhaustion); identify rationalizations and
  add explicit counters. Success = follows the rule under maximum pressure.
- **Technique** (condition-based-waiting, root-cause-tracing,
  defensive-programming): application scenarios, variation scenarios, missing-
  information tests. Success = applies the technique to a new scenario.
- **Pattern** (mental models): test whether the model transfers.

## STOP before moving to the next skill

After writing ANY skill you must stop and complete the deployment process. Do not
create multiple skills in batch without testing each, do not move on before the
current one is verified, and do not skip testing because "batching is more
efficient". Deploying untested skills = deploying untested code.

## Anti-patterns

- **Narrative example** — "In session 2025-10-03, we found empty projectDir
  caused...": too specific, not reusable.
- **Multi-language dilution** — `example-js.js`, `example-py.py`, `example-go.go`:
  mediocre quality, maintenance burden. One excellent example.
- **Code in flowcharts** — cannot be copy-pasted and is hard to read.
- **Generic labels** — `helper1`, `step3`, `pattern4`: labels should carry
  semantic meaning.

## Flowcharts — use only for non-obvious decisions

Use a small inline flowchart ONLY for non-obvious decision points, process loops
where you might stop too early, and "when to use A vs B" decisions. **Never for**
reference material (tables/lists), code examples (markdown blocks), linear
instructions (numbered lists), or labels without semantic meaning. Style rules are
in `graphviz-conventions.dot`; `render-graphs.js` renders a skill's flowcharts to
SVG (`node ./render-graphs.js ../some-skill`, add `--combine` for one SVG).

## Creation checklist (TDD-adapted, condensed)

RED: pressure scenarios (3+ combined pressures for discipline skills) → run
WITHOUT the skill, document baseline verbatim → identify rationalization patterns.

GREEN: name is letters/numbers/hyphens only → frontmatter `name` + `description`
→ description starts "Use when", third person, specific triggers → keywords
throughout for search (errors, symptoms, tools) → clear overview with the core
principle → addresses the baseline failures from RED → guidance form matches the
failure type → behavior-shaping guidance micro-tested against a no-guidance
control (N/A for pure reference skills) → code inline or linked → one excellent
example → run scenarios WITH the skill and verify compliance.

REFACTOR: identify new rationalizations → add explicit counters → build the
rationalization table from all iterations → create a red-flags list → re-test.
