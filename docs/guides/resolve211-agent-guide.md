# Resolve 21.1 agent guide

Use this when an older skill says a Resolve capability is unavailable, or when
choosing native 21.1 actions. This repository packages editing guidance, not the
MCP implementation. Follow `AGENTS.md` for authorized scope, backup, variants,
MCP-first execution and state restoration.

## Choose evidence for the installed build

1. Read community `resolve_control get_version` and `check_version_support`, and
   Studio `get_resolve_status`. Record the full build and MCP version. An empty
   unavailable list only clears recorded gates; `unknown` requires investigation.
2. Use Studio `get_whats_new`, `search_scripting_api`, `get_scripting_api` and
   `get_scripting_docs` for vendor declarations and option types. A changelog
   query with no entries does not prove there were no API changes; also consult
   the installed scripting changelog and typed stub.
3. Inspect the attached community action schema. A native method in the stub is
   not automatically a community action. Prefer an existing matching action;
   if absent or demonstrably broken, document `MCP-GAP:` and follow the Studio
   MCP / repository-script fallback in `AGENTS.md`.
4. Interpret measured limitations with their build, platform, item type and
   test coverage. Older negative findings are evidence about those builds.
   Before a required mutation, use an authorized recoverable pilot and readback;
   do not turn documentation research into an unrequested live edit.

The [X-Raym Gist](https://gist.github.com/X-Raym/2f2bf453fc481b9cca624d7ca0e19de8)
was labeled 21.0.4 when reviewed on 2026-10-15, with document date 24 Jul 2026.
Use it for historical reference and revisions. Prefer installed 21.1 vendor
documentation for current signatures; comments from older releases are not
current capability tests. Do not replace the typed reference with the Gist.

## Native routes to inspect on 21.1+

Action names below were present in the attached community MCP 4.13.1 catalog.
Inspect the live schema for parameters; this table is not permission to execute.

| Task | Native API / community action | Read before use |
|---|---|---|
| Constant clip speed and fades | `TimelineItem.SetSpeed`, `SetFades` / `timeline_item set_speed`, `set_fades` | [Speed/fades](../reference/resolve211-speed-fades.md); `set_retime` controls quality, not percentage speed. Arbitrary speed ramps are not established. |
| Create a transition | `TimelineItem.AddTransition` / `timeline_item add_transition` | [Transitions](../reference/resolve211-native-transitions.md); check handles and actual span, then re-query item indexes. Creation is separate from cloning. |
| Create/flatten multicam | `MediaPool.CreateMulticamClip`, `TimelineItem.FlattenMulticam` / `media_pool create_multicam_clip`, `timeline_item flatten_multicam` | [Multicam](../reference/resolve211-multicam.md); creation defaults can reorganize source pool clips, flattening replaces the item with its active angle. SmartSwitch is separately documented in the stub. |
| Normalize audio | `Timeline.NormalizeAudioLevel` / `timeline normalize_audio_level` | [Normalization](../reference/resolve211-normalization.md); discover modes with `get_normalize_audio_modes`, measure output loudness. This is not bus routing or a complete auto-mix. |
| Align clips | `Timeline.AutoAlignClips` / `timeline auto_align_clips` | [Alignment](../reference/resolve211-alignment.md); include the intended video and audio IDs when moving linked pairs. |
| Validate/encrypt DCTL | `Resolve.ValidateDCTL`, `EncryptDCTL` / `dctl validate_native`, `encrypt_native` | [Validation](../reference/resolve211-dctl-validation.md), [encryption](../reference/resolve211-encryption.md); `None` means native validation success, a string is a diagnostic. Validation does not verify rendered pixels. |

For transcription, inspect `MediaPoolItem.GetTranscription` and the current
`timeline_ai` schema rather than treating a transcription-start boolean as text.
For source channel routing, inspect `MediaPoolItem.SetAudioMapping` and
`TimelineItem.SetSourceAudioChannelMapping`; read the vendor Audio Mapping
section for the JSON string format and channel counts. These do not establish
Fairlight bus-routing or mix-automation support.

## Runtime and settings

- Vendor 21.1 documentation describes a built-in Python 3.14 interpreter at
  `C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\ResolvePython.exe`.
  `import DaVinciResolveScript` works without environment setup in that runtime;
  `pip`, Tk and IDLE are unavailable. External Python has separate module/library
  setup requirements. Python 2 is no longer supported. Reusable repository
  scripts still use `resolve_common`; do not replace their connection plumbing.
- Use typed `ProjectSettings`, `TimelineSettings` and `TimelineItemProperties`
  to discover valid keys and types. The vendor deprecates singular settings and
  timeline-item property forms in favor of `GetSettings`/`SetSettings` and
  `GetProperties`/`SetProperties`; retain documented exceptions such as the
  four-argument Super Scale setter. This is not a reason to rename working MCP
  actions or `MediaPoolItem.GetClipProperty`.
- A multi-setting write is not atomic: successful keys can remain applied when
  another key fails. Snapshot first and read back every requested key on either
  success or failure. Timeline settings inherit project values when
  `useCustomSettings` is `'0'`; custom settings require `'1'`. Preserve the
  approved aspect ratio, timeline FPS and separately measured playback FPS.
- Check frame/sample units and index conventions in the exact method/action.
  A wrapper's zero-based item index is not a universal native API convention.
  Subtitle-generation options are not a saved Subtitle-track font preset loader.
- Use explicit render job IDs and distinguish `BurnIn`, `EmbeddedCaptions` and
  `SeparateFile` subtitle outputs. Delivery verification still requires Complete
  status, a nonempty file, ffprobe checks and visual QC. A native still can omit
  subtitles. API return values alone do not satisfy delivery QC.

## Report evidence separately

For a capability, state: vendor declaration and build; attached MCP action;
runtime probe or mutation result, if performed; and audiovisual QC, if performed.
Reference presence, native success, readback and rendered behavior are distinct.

On 2026-10-15 community MCP reported Studio **21.1.0.17** and MCP **4.13.1**;
Studio MCP reported running **21.1**. The version gate list was empty. The local
vendor stub matched the Studio-returned stub byte-for-byte; see
[snapshot provenance](../reference/resolve-211-typed-api.md) for raw and normalized hashes.
This documentation review did not mutate timelines, test these setters, or
render media. Existing contributor fixtures measured on macOS 21.1.0.14 remain
historical evidence with their stated limits, not new Windows Build 17 tests.
