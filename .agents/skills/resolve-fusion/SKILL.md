---
name: resolve-fusion
description: Fusion composition work in the DaVinci Resolve MCP. Apply when building or editing Fusion comps — titles, motion graphics, VFX, merges, masks, trackers — on a timeline item live in a running Resolve OR authoring a .comp declaratively offline. Routes to the live fusion_comp tools and the offline fusion authoring tool.
version: 0.3.1
author: Warit (pong34811), Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Fusion, VFX, Titles, Resolve]
---

# Resolve Fusion

Thin router; depth stays in the kernel.

- **Live tool mechanics** — `docs/kernels/fusion-composition-kernel.md` (the

  `fusion_comp` boundary).

- **Offline authoring** — `resolve-advanced/README.md` → the `fusion` tool.

## Two servers — author offline, apply live

| Job | Server | Tools |
|---|---|---|
| Build/edit a comp on a **running** timeline item | `davinci-resolve` (Python, live) | `fusion_comp` (`probe_fusion_comp`, `safe_add_tool`, `safe_set_inputs`, `safe_connect_tools`, `fusion_boundary_report`) |
| Author a `.comp` from a spec/template with **no Resolve open** | `davinci-resolve-advanced` (Node) | `fusion` (`generate`, `generate_from_template`, `list_templates`, `to_api_calls`) |

## Flow

1. Author/verify offline: `fusion(action="generate"|"generate_from_template")` →

   a `.comp`, or `fusion(action="to_api_calls")` → the ordered tool/input/

   connection calls.

2. Apply live: `fusion_comp` `safe_add_tool` → `safe_set_inputs` →

   `safe_connect_tools`. The `to_api_calls` output maps directly onto those.

3. Probe first (`probe_fusion_comp` / `probe_fusion_tool`) — tool availability

   and input readability vary by Resolve/Fusion build; some inputs coerce or are

   write-only. Bulk mutation needs timeline scope, not the active Fusion page.

## Native settings fragments and return-value traps

- Distinguish a settings fragment (`Tools = ordered() { ... }`) from a full
  exported composition. On Studio 21.1.0.17, importing a hand-authored tools-only
  fragment with `TimelineItem.ImportFusionComp` returned failure on newly
  injected Adjustment Clips. This does not establish a general import bug.
  After that measured refusal, `AddFusionComp` plus native `AddTool`, `SetInput`
  and `ConnectInput` built a graph that appeared in a Resolve pilot render.
  Preserve the comp's existing MediaIn/MediaOut context and verify every input
  and connection. Live readback alone was insufficient: after saving and a
  later render, exported DRTs still had empty `CompositionBA` entries for
  inactive clips, while their in-memory graphs were readable. Require a
  nonempty serialized comp for every target and fresh rendered evidence for
  every distinct scene. Do not claim a graph persisted merely because
  `SaveProject` and `GetFusionCompByIndex` succeeded.
- For this measured empty-serialization case, `Composition.Save(path)` produced
  native full `.comp` files. A recoverable DRT variant can embed those bytes in
  the existing `Sm2TiCompositionTable`: qCompress of a version-1 four-entry Qt
  QVariant map (`count`: int 1, `0_name`: QString, `0_mediaIdList`: empty
  QStringList, `0_data`: QByteArray of the native saved composition), with
  `ActiveCompositionIdx` 0. Use the repo's Qt field builders; preserve all
  unrelated tracks byte-for-byte. The ep11 imported variant rendered a pink
  chapter card in a fresh pilot after this operation. This is a DRT technique,
  not approval to patch a running project database. Importing the native full
  `.comp` directly onto the Adjustment Clip also returned failure on this build.
- Import `collections.OrderedDict` into the calling Python interpreter before
  `DaVinciResolveScript.readfile` parses `ordered()` settings. Without it the
  bridge raised `NameError: OrderedDict is not defined` and returned a partial
  mapping. Parsing a mapping is not proof that `Composition.Paste` accepted it.
- Read back `Input.GetExpression()` after `SetExpression`: the setter returned
  `None` even though the expression was stored and evaluated on this build.
  Do not interpret the void return as failure or keep retrying the write.
- Parenthesize substituted negative operands in expressions (`time-(-10)`),
  rather than emitting `time--10`, which introduces Lua comment syntax. Keep
  numeric readback separate from rendered typography, timing and framing QC.
- Keep cue-heavy comps small: reuse a TextPlus with time-driven `StyledText`
  and a shared keyword card instead of one masked-background/text/merge chain
  per word. The ep11 dense scene had 92 tools and its full render hung; the
  lighter scene used 31. This is an observed workload difference, not a proven
  cause of the hang. Re-test the lighter graph before treating it as a fix.
- Preserve real output port names when authoring settings: RectangleMask's
  output is `Mask`, not `Output`. Native `ConnectInput` selected it correctly,
  but a hand-authored `Source = "Output"` left the backgrounds unmasked and
  covered the footage. Verify on a rendered or native exported frame.
- Probe actual composition methods before use. `Composition.LoadSettings` was
  absent on this build; a tool-level settings method is not a comp method.

Never modify/transcode/derive source media (AGENTS.md).

## Tool selection (MCP first)

Before any script, check the davinci-resolve MCP catalog; write a Resolve Python scripting-API script only after a stated `MCP-GAP:` line shows the MCP lacks the tool/action. Follow `AGENTS.md` "Tool selection" and run `python scripts/resolve_preflight.py --need <tool[.action]>`.
