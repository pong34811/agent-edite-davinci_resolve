#!/usr/bin/env python3
"""Inventory a repo's portable skills: frontmatter, support files, defects.

Read-only, stdlib only. Default root is the current working directory.

Invoke through the `terminal` tool:
    python scripts/inventory_skills.py --root <repo>
    python scripts/inventory_skills.py --root <repo> --json
    python scripts/inventory_skills.py --root <repo> --problems

Scans .agents/skills and .claude/skills for <dir>/SKILL.md, reads the YAML
frontmatter (top-level scalar keys only), counts support files per skill, and
flags directory-name/frontmatter-name drift, over-long descriptions, and
missing required keys.
"""

import argparse
import json
import os
import re
import sys

SKILL_DIRS = (".agents/skills", ".claude/skills")
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
TOP_KEY_RE = re.compile(r"^([a-z_][a-z0-9_]*):[ \t]*(.*)$")
DESC_LIMIT = 60

# Directory prefixes that legitimately differ from the frontmatter name.
NAME_PREFIXES = ("superpowers-",)


def parse_frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        km = TOP_KEY_RE.match(line)
        if km:
            fm[km.group(1)] = km.group(2).strip().strip('"').strip("'")
    return fm


def inventory(root):
    rows = []
    for sub in SKILL_DIRS:
        base = os.path.join(root, sub)
        if not os.path.isdir(base):
            continue
        for entry in sorted(os.listdir(base)):
            path = os.path.join(base, entry, "SKILL.md")
            if not os.path.isfile(path):
                continue
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            fm = parse_frontmatter(text)
            support = []
            for dirpath, dirnames, filenames in os.walk(os.path.join(base, entry)):
                dirnames[:] = [d for d in dirnames if d != "__pycache__"]
                for name in filenames:
                    if name == "SKILL.md":
                        continue
                    support.append(
                        os.path.relpath(os.path.join(dirpath, name),
                                        os.path.join(base, entry)).replace("\\", "/")
                    )
            desc = fm.get("description", "")
            problems = []
            declared = fm.get("name", "")
            if not declared:
                problems.append("missing name")
            elif declared != entry and not entry.startswith(NAME_PREFIXES):
                problems.append("name != dir (%s)" % declared)
            elif declared != entry:
                problems.append("known prefix alias -> %s" % declared)
            if not desc:
                problems.append("missing description")
            elif len(desc) > DESC_LIMIT:
                problems.append("description %d chars > %d" % (len(desc), DESC_LIMIT))
            if not fm.get("version"):
                problems.append("no version")
            if desc and not desc.endswith((".", "?", "!")):
                problems.append("description not sentence-final")
            rows.append({
                "dir": entry,
                "source": sub,
                "name": declared,
                "version": fm.get("version", ""),
                "platforms": fm.get("platforms", ""),
                "desc_chars": len(desc),
                "lines": len(text.splitlines()),
                "support_files": len(support),
                "problems": problems,
            })
    return rows


def main():
    ap = argparse.ArgumentParser(description="Inventory a repo's portable skills.")
    ap.add_argument("--root", default=os.getcwd(),
                    help="repo root (default: cwd)")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--problems", action="store_true",
                    help="print only rows with frontmatter defects")
    args = ap.parse_args()

    rows = inventory(args.root)
    if not rows:
        print("no SKILL.md found under %s (looked in: %s)"
              % (args.root, ", ".join(SKILL_DIRS)), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0

    if args.problems:
        flagged = [r for r in rows if r["problems"]]
        for r in flagged:
            print("%-34s %s" % (r["dir"], "; ".join(r["problems"])))
        print("\n%d of %d skills flagged" % (len(flagged), len(rows)))
        return 0

    print("%-34s %-28s %-7s %5s %5s %s"
          % ("DIR", "NAME", "VER", "DESC", "FILES", "PLATFORMS"))
    for r in rows:
        print("%-34s %-28s %-7s %5d %5d %s"
              % (r["dir"], r["name"] or "-", r["version"] or "-",
                 r["desc_chars"], r["support_files"], r["platforms"] or "-"))
    print("\n%d skills" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
