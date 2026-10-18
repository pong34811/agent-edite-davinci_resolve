# Superpowers methodology skills (15 skills)

Vendored from the upstream superpowers plugin. **Directory prefix ≠ frontmatter
name**: the directory is `.agents/skills/superpowers-<name>/` while the
frontmatter declares `name: <name>`. `skill_view` needs the frontmatter name
(the directory form only works in hosts that key on the folder).

| Directory | frontmatter `name` | Trigger / what it enforces |
|---|---|---|
| `superpowers-using-superpowers` | `using-superpowers` | Start of any conversation — how to find and use skills; skill invocation before ANY response, including clarifying questions. Ships per-platform tool references (`references/hermes-tools.md`, `claude-code-tools.md`, `codex-tools.md`, `gemini-tools.md`, `muse-tools.md`, `pi-tools.md`, `antigravity-tools.md`) |
| `superpowers-brainstorming` | `brainstorming` | Before any creative work — features, components, functionality, behavior changes. Explores intent, requirements and design before implementation |
| `superpowers-writing-plans` | `writing-plans` | You have a spec/requirements for a multi-step task, before touching code |
| `superpowers-executing-plans` | `executing-plans` | Executing a plan inline as the implementer (no subagent tool, or the human chose inline). Ships `scripts/task-start`, `scripts/task-done` |
| `superpowers-subagent-driven-development` | `subagent-driven-development` | Executing a plan with independent tasks in the current session via fresh subagents; ships `implementer-prompt.md`, `task-reviewer-prompt.md`, `re-review-prompt.md`, `scripts/task-brief`, `scripts/sdd-workspace`, `scripts/review-package` |
| `superpowers-dispatching-parallel-agents` | `dispatching-parallel-agents` | 2+ independent tasks with no shared state or sequential dependency |
| `superpowers-test-driven-development` | `test-driven-development` | Any feature or bugfix, before writing implementation code. Iron law: RED-GREEN-REFACTOR |
| `superpowers-systematic-debugging` | `systematic-debugging` | Any bug, test failure, or unexpected behavior, before proposing fixes. Iron law + four phases; ships `root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md` |
| `superpowers-verification-before-completion` | `verification-before-completion` | About to claim work is complete/fixed/passing, before committing or PRs. Evidence before assertions |
| `superpowers-requesting-code-review` | `requesting-code-review` | Completing tasks, major features, or before merging. Ships `code-reviewer.md` |
| `superpowers-receiving-code-review` | `receiving-code-review` | Receiving review feedback, before implementing suggestions — technical rigor, not performative agreement |
| `superpowers-finishing-a-development-branch` | `finishing-a-development-branch` | Implementation complete, tests pass, deciding how to integrate |
| `superpowers-using-git-worktrees` | `using-git-worktrees` | Feature work needing isolation from the current workspace, or before executing plans |
| `superpowers-writing-skills` | `writing-skills` | Creating/editing skills or verifying they work before deployment. Largest skill (681 lines); ships `anthropic-best-practices.md`, `persuasion-principles.md`, `testing-skills-with-subagents.md`, `render-graphs.js` |
| `superpowers-diagnosing-superpowers` | `diagnosing-superpowers` | A superpowers session went wrong and the human wants to know why, or wants a bug report for the maintainers. Ships 19 prompt files under `prompts/` |

## Notes that matter when routing

- These 15 declare **no `version:`** — the inventory script flags them; that is
  expected for vendored skills, not drift to fix silently.
- Their descriptions are long-form (upstream style) and run from ~80 to ~375
  characters; they are not written to the Hermes 60-character index bar. Most
  also omit the closing period, which the inventory script flags.
- `superpowers-writing-skills` is the authority for authoring a new project
  skill here: check it before inventing frontmatter or section order.
- `superpowers-verification-before-completion` is the rule behind this repo's
  "only report what was actually verified" handoff requirement.
- For this repo, `superpowers-executing-plans` / `subagent-driven-development`
  are the two sanctioned ways to run a written plan; `dispatching-parallel-agents`
  is what the thumbnail and cover batches use.
