# Changelog

## v0.1.0

First versioned release of the DaVinci Resolve editing skill bundle. The bundle version is independent of Resolve, the upstream MCP server, and individual archived skill versions.

### Added
- Thai VTuber editorial guidance: selecting self-contained highlights, truthful hooks, comic timing, and preserving the creator's personality.
- On-demand chapters for Resolve editing, Thai captions/audio/framing, YouTube packaging/feedback, and delivery/rights, with primary-source references.
- A reusable edit brief, cutlist, experiment plan, and acceptance-record template.

### Updated
- Expanded `resolve-video-enrichment` into a lean core with 11 reference chapters and one template, retaining the existing enrichment/recovery workflows.
- Clarified native subtitles versus burned-in pixels, evidence-led cue placement, measured audio versus scripting capability, source-frame timebases, and approval-gated repair/cleanup.
- Preserved the project's native Subtitle-track workflow and Thai short-form limits: three short words/about 14 Thai characters, at most 1.5 seconds, and no spaces between Thai words except appropriate Latin boundaries.
- Refreshed bundle provenance/checksums and validation evidence for the release contents.

### Fixed
- Bundle validation now accepts Git's LF/CRLF conversion for UTF-8 text while still rejecting content changes and preserving exact binary checksums; regression tests cover both newline directions and binary changes.

### Scope
- Skills, documentation, and bundle-validation release only: no MCP implementation, Resolve project, source media, or live editing behavior was changed.
- No claim of proven audience growth, channel-specific analytics, or live Resolve verification.
- Unrelated local editing plans, worklogs, scratch reports, media, and project backups are not part of this release change.
