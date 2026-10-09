"""Read-only p2 inventory: reuses review_enrichment_readonly with a p2 output dir.
MCP-GAP: davinci-resolve MCP has no single-call all-timeline item/property dump
(timeline.list only returns names/ids); per-item reads across 44 timelines need the script.
Run from repo root: python -m scripts.p2_inventory_readonly
"""
from __future__ import annotations
from pathlib import Path
from scripts import review_enrichment_readonly as base

ROOT = Path(__file__).resolve().parents[1]
base.OUT = ROOT / '.hermes' / 'artifacts' / 'enrichment-p2-2026-10-09'

if __name__ == '__main__':
    base.main()
