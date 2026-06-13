#!/usr/bin/env python3
"""CocktailDex tool — deterministic maintenance for the wiki.

    python scripts/wiki.py compile   # rebuild index.md + tags.md from the wiki/ cards
    python scripts/wiki.py lint      # health-check the wiki (exit 1 on errors)

Self-contained on purpose (no local imports) so it always reflects this file's current
contents. The controlled tag vocabulary lives in VOCABULARY below — add a tag there, then
recompile. compile NEVER edits cards; it only rebuilds the two derived navigation files.
"""
from __future__ import annotations
import re, sys, json, datetime
from pathlib import Path

ROOT        = Path(__file__).resolve().parent.parent
WIKI        = ROOT / "wiki"
RAW_INBOX   = ROOT / "raw" / "inbox"
RAW_ARCHIVE = ROOT / "raw" / "archive"
PHOTOS      = ROOT / "photos"
VITEPRESS   = ROOT / "site" / ".vitepress"

# --- Controlled vocabulary: dimension -> {blurb, ordered canonical tags} -----
VOCABULARY = {
    "Base Spirit": {
        "blurb": "The dominant spirit. Exactly one is mandatory per cocktail.",
        "tags": ["Rum", "Gin", "Vodka", "Whiskey", "Tequila", "Mezcal",
                 "Brandy", "Cognac", "Aquavit", "Liqueur", "FortifiedWine", "Wine"],
    },
    "Ingredient": {
        "blurb": "Distinctive non-base components (souring agent, sweetener, modifiers, aromatics).",
        "tags": ["Lime", "Mint", "Falernum", "Pineapple", "Mango", "Lemon", "Orange",
                 "Sugar", "Demerara", "Angostura", "Soda", "Campari",
                 "Vermouth", "Egg", "Cream", "Ginger", "Coffee"],
    },
    "Flavor / Profile": {
        "blurb": "The taste experience.",
        "tags": ["Refreshing", "Spiced", "Fruity", "Citrusy", "Tart", "Sweet",
                 "Bitter", "Herbal", "Boozy", "Complex", "Light", "Creamy",
                 "Smoky", "Dry"],
    },
    "Technique": {
        "blurb": "How the drink is built.",
        "tags": ["Shaken", "Muddled", "Swizzle", "Stirred", "Built",
                 "Blended", "Thrown", "Layered", "DryShake"],
    },
    "Family / Style": {
        "blurb": "The cocktail family it belongs to.",
        "tags": ["Tiki", "Highball", "Sour", "OldFashioned", "Martini",
                 "Fizz", "Punch", "Spritz", "Daisy", "Flip", "Julep"],
    },
    "Glassware": {
        "blurb": "Serving vessel.",
        "tags": ["Collins", "Coupe", "Rocks", "NickAndNora", "TikiMug", "Hurricane",
                 "WineGlass", "Flute", "Shot", "Margarita", "Pint", "MartiniGlass", "HighballGlass"],
    },
}

# Every tag token must belong to exactly ONE dimension (flat namespace).
_all = [t for d in VOCABULARY.values() for t in d["tags"]]
_dupes = sorted({t for t in _all if _all.count(t) > 1})
if _dupes:
    raise ValueError(f"Duplicate tag(s) across dimensions in VOCABULARY: {_dupes}")
TECHNIQUE_TAGS = VOCABULARY["Technique"]["tags"]

_UNIT = (r"(?:oz|ml|cl|l|tsp|tbsp|dash(?:es)?|part(?:s)?|cup(?:s)?|"
         r"barspoon(?:s)?|drop(?:s)?|splash(?:es)?|bsp)")


def tag_dimension(tag):
    for dim, d in VOCABULARY.items():
        if tag in d["tags"]:
            return dim
    return None


def strip_qty(line):
    s = line.strip().lstrip("-").strip()
    s = re.sub(r"^[\d./–—\-\s½¼¾⅓⅔]+", "", s)
    s = re.sub(rf"^{_UNIT}\b\.?\s*", "", s, flags=re.I)
    return s.strip()


def _bodyline(text, label):
    m = re.search(rf"-\s*\*\*{label}:\*\*\s*(.+)", text)
    return m.group(1).strip() if m else ""


def _rating(text, person):
    m = re.search(rf"\*\*{person}\s*[—–-]\s*Rating:\*\*\s*(.+)", text)
    if not m:
        return "—"
    v = m.group(1).strip()
    if "_" in v:
        return "—"
    # Extract the numeric part (allowing floats like 4.5)
    val_m = re.match(r"(\d+(?:\.\d+)?)", v)
    return val_m.group(1) if val_m else v


def parse_card(path):
    text = Path(path).read_text(encoding="utf-8")
    slug = Path(path).stem

    def fm(key, default=""):
        m = re.search(rf"^{key}:\s*(.+)$", text, re.M)
        return m.group(1).strip() if m else default

    name = fm("name", slug)
    base = fm("base")
    m = re.search(r"tags:\s*\[(.*?)\]", text)
    fm_tags = [t.strip() for t in m.group(1).split(",")] if (m and m.group(1).strip()) else []

    glass       = _bodyline(text, "Glassware") or fm("glassware")
    instruction = _bodyline(text, "Instruction")
    profile     = _bodyline(text, "Profile")
    body_tags   = re.findall(r"#(\w+)", _bodyline(text, "Tags"))

    ingredients = []
    m = re.search(r"-\s*\*\*Ingredients:\*\*\s*\n((?:\s{2,}-\s*.+\n?)+)", text)
    if m:
        for ln in m.group(1).splitlines():
            if ln.strip().startswith("-"):
                ingredients.append(strip_qty(ln))

    eric, charlene = _rating(text, "Eric"), _rating(text, "Charlene")
    m = re.search(r"\*\*Other Similar Cocktails:\*\*\s*(.+)", text)
    similar = re.findall(r"\]\(\./([\w\-]+)\.md\)", m.group(1)) if m else []

    techs = [t for t in body_tags if t in TECHNIQUE_TAGS]
    method = ", ".join(techs) if techs else (instruction.split(". ")[0][:60] +
                                             ("…" if len(instruction) > 60 else ""))
    return {"slug": slug, "name": name, "base": base, "glass": glass,
            "fm_tags": fm_tags, "body_tags": body_tags,
            "ingredients_summary": ", ".join(ingredients),
            "instruction": instruction, "method": method, "profile": profile,
            "eric": eric, "charlene": charlene, "similar": similar}


def load_cards():
    cards = [parse_card(p) for p in sorted(WIKI.glob("*.md"))]
    cards.sort(key=lambda c: c["name"].lower())
    return cards


def esc(s):
    return (s or "").replace("|", "\\|")


def build_index(cards):
    today = datetime.date.today().isoformat()
    bases = ", ".join(sorted({c["base"] for c in cards if c["base"]})) or "—"
    rows = "\n".join(
        f"| [{esc(c['name'])}](./wiki/{c['slug']}.md) | {esc(c['base'])} | {esc(c['glass'])} "
        f"| {esc(c['ingredients_summary'])} | {esc(c['method'])} | {esc(c['profile'])} "
        f"| {c['eric']} | {c['charlene']} |" for c in cards
    ) or "| _(no cocktails yet — drop files in raw/inbox/ and ingest)_ ||||||||"
    return f"""# 🍸 CocktailDex — Index

The at-a-glance index of the whole collection. **To find a drink:** use the search box (top
of the page), browse by [Tags](./tags) (spirit · flavour · technique · glass), or scan the
reference table below and click a name for the full card.

> **For LLMs:** the entire collection is available as a single machine-readable dump at
> [`llms-full.txt`](./llms-full.txt) — fetch that instead of crawling pages.

**Collection:** {len(cards)} cocktails · bases: {bases} · last updated {today}

> Auto-generated by `scripts/wiki.py compile` from the `wiki/` cards. **Don't hand-edit** —
> edit the cards, then recompile. The "Instruction" cell shows the technique; full steps
> are in each card.

---

## First-layer reference table

Each cocktail's core data at a glance. `—` in a rating column = not yet rated (owner-filled
only). Click a name for the full card.

| Cocktail | Base | Glassware | Ingredients | Instruction | Profile | Eric | Charlene |
|----------|------|-----------|-------------|-------------|---------|:----:|:--------:|
{rows}

---

*Regenerated by `scripts/wiki.py compile` on {today}.*
"""


def build_tags(cards):
    today = datetime.date.today().isoformat()
    used = {}
    for c in cards:
        for t in c["body_tags"]:
            used.setdefault(t, []).append(c)

    sections = []
    for i, (dim, d) in enumerate(VOCABULARY.items(), start=1):
        vocab_line = " · ".join((("● " if t in used else "○ ") + f"`#{t}`") for t in d["tags"])
        lines = [f"## {i}. {dim}", f"*{d['blurb']}*", "", f"**Vocabulary:** {vocab_line}", ""]
        rows = [f"- **#{t}** — " + ", ".join(
                    f"[{esc(x['name'])}](./wiki/{x['slug']}.md)"
                    for x in sorted(used[t], key=lambda c: c['name'].lower()))
                for t in d["tags"] if t in used]
        lines.extend(rows if rows else ["*(none yet)*"])
        sections.append("\n".join(lines))

    unknown = sorted({t for t in used if tag_dimension(t) is None})
    warn = ""
    if unknown:
        items = "\n".join(f"- **#{t}** — " + ", ".join(
            f"[{esc(x['name'])}](./wiki/{x['slug']}.md)" for x in used[t]) for t in unknown)
        warn = ("\n\n---\n\n## ⚠ Unrecognised tags (add to `scripts/wiki.py` VOCABULARY)\n\n" + items)

    header = """# 🏷️ CocktailDex Tags — Taxonomy (Reverse Index)

The controlled vocabulary for the wiki, organised into **6 dimensions**. Every cocktail
carries **3–7 tags** drawn from here (see `CLAUDE.md` §4). This page is the **reverse
index**: under each tag, every cocktail that carries it.

- **Entry point for browsing:** [index.md](./index.md)
- **Rules & workflow:** [CLAUDE.md](./CLAUDE.md)
- **How to use:** scan a tag below, or `grep -ril "#Tiki" wiki/`.

> Auto-generated by `scripts/wiki.py compile`. **Don't hand-edit** — to add a canonical tag,
> put it under the right dimension in `scripts/wiki.py` (VOCABULARY) and recompile.
> `●` = in use, `○` = available but unused so far.

---

"""
    footer = f"\n\n---\n\n*Regenerated by `scripts/wiki.py compile` on {today}.*\n"
    return header + "\n\n---\n\n".join(sections) + warn + footer


def build_sidebar(cards):
    """VitePress sidebar config, derived from the cards (committed artifact, consumed by
    .vitepress/config.mjs). Links are root-relative, extensionless, NO `base` prefix —
    VitePress prepends `base` itself. One 'Cocktails' group listing every card A→Z."""
    return [
        {
            "text": f"Cocktails ({len(cards)})",
            "collapsed": False,
            "items": [
                {"text": c["name"], "link": f"/wiki/{c['slug']}"} for c in cards
            ],
        }
    ]


def do_compile():
    cards = load_cards()
    (ROOT / "index.md").write_text(build_index(cards), encoding="utf-8")
    (ROOT / "tags.md").write_text(build_tags(cards), encoding="utf-8")
    VITEPRESS.mkdir(exist_ok=True)
    (VITEPRESS / "sidebar.generated.json").write_text(
        json.dumps(build_sidebar(cards), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"compiled {len(cards)} cards -> index.md, tags.md, site/.vitepress/sidebar.generated.json")
    return 0


def do_lint():
    cards = load_cards()
    slugs = {c["slug"] for c in cards}
    by = {c["slug"]: c for c in cards}
    index_txt = (ROOT / "index.md").read_text(encoding="utf-8") if (ROOT / "index.md").exists() else ""
    tags_txt  = (ROOT / "tags.md").read_text(encoding="utf-8")  if (ROOT / "tags.md").exists()  else ""
    errors, warns, infos = [], [], []
    for c in cards:
        s = c["slug"]; n = len(c["body_tags"])
        if not (3 <= n <= 7):
            errors.append(f"{s}: tag count {n} (must be 3–7)")
        if c["fm_tags"] != c["body_tags"]:
            errors.append(f"{s}: frontmatter tags {c['fm_tags']} != body Tags {c['body_tags']}")
        for t in c["body_tags"]:
            if tag_dimension(t) is None:
                errors.append(f"{s}: tag #{t} not in controlled vocabulary")
        if not c["base"]:
            errors.append(f"{s}: missing base spirit (frontmatter `base:`)")
        for tgt in c["similar"]:
            if tgt not in slugs:
                errors.append(f"{s}: similar link -> {tgt}.md does not exist")
            elif s not in by[tgt]["similar"]:
                errors.append(f"{s} -> {tgt}: not mutual ({tgt} doesn't link back)")
        if f"./wiki/{s}.md" not in index_txt:
            errors.append(f"{s}: missing from index.md (run compile)")
        if f"./wiki/{s}.md" not in tags_txt:
            warns.append(f"{s}: not referenced in tags.md (run compile)")
        if not (RAW_ARCHIVE / f"{s}.md").exists():
            warns.append(f"{s}: no frozen original in raw/archive/{s}.md")
        if c["eric"] == "—" or c["charlene"] == "—":
            infos.append(f"{s}: rating(s) still blank — needs tasting notes (human-only)")
        if not (PHOTOS / f"{s}.jpg").exists():
            infos.append(f"{s}: no photo at photos/{s}.jpg (optional)")
    pending = [p.name for p in RAW_INBOX.glob("*.md") if p.name.lower() != "readme.md"]
    if pending:
        warns.append(f"raw/inbox/ has unprocessed files: {pending} — run an ingest")

    print(f"Linted {len(cards)} cards.\n")
    for label, items in (("ERROR", errors), ("WARN", warns), ("INFO", infos)):
        for it in items:
            print(f"  [{label}] {it}")
    print(f"\n{len(errors)} error(s), {len(warns)} warning(s), {len(infos)} info.")
    print("✅ No errors." if not errors else "❌ Errors found.")
    return 1 if errors else 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "compile":
        return do_compile()
    if cmd in ("lint", "check"):
        return do_lint()
    print("usage: python scripts/wiki.py [compile|lint]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
