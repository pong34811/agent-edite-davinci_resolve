from __future__ import annotations

"""Compatibility wrapper for the repository-owned subtitle preset helper.

The skill copy intentionally contains no independent Resolve connection or
SQLite writer. The canonical helper lives at the repository root and must be
run under the project's MCP-first and offline-database safeguards.
"""

import importlib.util
from pathlib import Path
import sys


def main() -> int:
    repository = Path(__file__).resolve().parents[4]
    helper = repository / "scripts" / "load_subtitle_preset.py"
    if not helper.is_file():
        raise SystemExit(
            "The repository-owned scripts/load_subtitle_preset.py is unavailable. "
            "Do not run a copied database-writer; use the project's approved workflow."
        )
    spec = importlib.util.spec_from_file_location("project_load_subtitle_preset", helper)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Cannot load the repository helper: {helper}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main()


if __name__ == "__main__":
    raise SystemExit(main())
