#!/usr/bin/env python3
"""Lint a markdown-link LLM-wiki vault (stdlib only).

Usage: python lint_vault.py <vault_dir> [--max-lines 200]

Checks: frontmatter fields, `sources:` paths exist, index coverage, broken
relative .md links, orphan pages, oversize pages, tag counts, log entry count,
and raw/ sha256 drift (only for raw files that carry a `sha256:` field).
Exit code 1 if any hard problem is found. Read-only: never edits the vault.
"""
import collections, hashlib, pathlib, re, sys

REQUIRED = ("title", "type", "created", "updated", "tags", "sources")
KNOWLEDGE_DIRS = ("concepts", "entities", "analyses", "sources", "comparisons", "queries")
LINK = re.compile(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)")
FENCE = re.compile(r"```.*?```", re.S)


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---", text.replace("\r\n", "\n"), re.S)
    return m.group(1) if m else None


def listfield(fm, key):
    m = re.search(rf"^{key}:\s*\[(.*?)\]", fm, re.M)
    return [x.strip().strip('"') for x in m.group(1).split(",") if x.strip()] if m else []


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    root = pathlib.Path(argv[1])
    max_lines = int(argv[argv.index("--max-lines") + 1]) if "--max-lines" in argv else 200
    wiki = root / "wiki"
    pages = [p for d in KNOWLEDGE_DIRS for p in sorted((wiki / d).glob("*.md"))]
    if (wiki / "overview.md").exists():
        pages.append(wiki / "overview.md")
    index = (wiki / "index.md").read_text(encoding="utf-8") if (wiki / "index.md").exists() else ""
    hard, soft = [], []
    inbound = collections.defaultdict(set)
    for f in root.rglob("*.md"):
        if ".obsidian" in f.parts:
            continue
        for link in LINK.findall(FENCE.sub("", f.read_text(encoding="utf-8"))):
            if link.startswith("http"):
                continue
            target = (f.parent / link).resolve()
            if not target.exists():
                hard.append(f"broken link {f.relative_to(root)} -> {link}")
            inbound[target].add(f.resolve())
    tags = collections.Counter()
    for p in pages:
        text = p.read_text(encoding="utf-8"); rel = p.relative_to(root)
        fm = frontmatter(text)
        if fm is None:
            hard.append(f"no frontmatter {rel}"); continue
        for k in REQUIRED:
            if not re.search(rf"^{k}:", fm, re.M):
                hard.append(f"missing field '{k}' {rel}")
        for s in listfield(fm, "sources"):
            if not (root / s).exists():
                hard.append(f"sources path missing {rel} -> {s}")
        tags.update(listfield(fm, "tags"))
        if p.name != "overview.md" and p.name not in index:
            hard.append(f"not in index {rel}")
        if not (inbound[p.resolve()] - {p.resolve(), (wiki / "index.md").resolve()}):
            soft.append(f"orphan (no inbound from other pages) {rel}")
        n = len(text.splitlines())
        if n > max_lines:
            soft.append(f"{n} lines (> {max_lines}) {rel}")
    for r in sorted((root / "raw").glob("*.md")):
        text = r.read_text(encoding="utf-8").replace("\r\n", "\n")
        m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
        h = re.search(r"^sha256:\s*([0-9a-f]{64})", m.group(1), re.M) if m else None
        if h and hashlib.sha256(m.group(2).encode("utf-8")).hexdigest() != h.group(1):
            soft.append(f"raw drift (sha256 mismatch) {r.relative_to(root)}")
    log = wiki / "log.md"
    entries = len(re.findall(r"^## \[", log.read_text(encoding="utf-8"), re.M)) if log.exists() else 0
    print(f"pages={len(pages)} log_entries={entries} tags={dict(tags)}")
    for line in hard:
        print("HARD", line)
    for line in soft:
        print("SOFT", line)
    print(f"hard={len(hard)} soft={len(soft)}")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
