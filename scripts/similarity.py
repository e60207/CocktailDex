#!/usr/bin/env python3
"""CocktailDex pairwise similarity — content-aware, deterministic, stdlib-only.

    python scripts/similarity.py report   [--top 4] [--threshold 0.45]
    python scripts/similarity.py pairs
    python scripts/similarity.py matrix
    python scripts/similarity.py json     [> similarity.json]
    python scripts/similarity.py gaps     # coverage + link-drift report (exit 1 on WARN)
    python scripts/similarity.py test     # self-test (exit 1 on failure)

Why this exists: CLAUDE.md §7 used to score similarity almost entirely from tags, but
tags are a lossy 3-7 token compression of each card. This script fuses THREE signals:

  1. RUBRIC  (weight 0.45) — the §7 discrete rubric, but made deterministic:
       base spirit from frontmatter, family/technique/flavor from tags, and the
       souring/sweetener checks re-derived from the *ingredient lines* (regex
       role detection) instead of LLM judgment.
  2. INGREDIENT (weight 0.35) — Jaccard over canonicalised ingredient tokens
       parsed from the body ("Gosling's Black Seal rum" -> rum, "simple syrup"
       -> sugar). Captures information that never made it into tags.
  3. TEXT (weight 0.20) — pure-python TF-IDF cosine over Background + Profile
       + Instruction + Garnish + Glassware. Ratings / Modified Variation / !!Tips
       (human-only) and the existing "Other Similar Cocktails" line are EXCLUDED
       so prior links can't feed back into the score.

The raw §7 discrete score is also reported so the CLAUDE.md linking rules
(score >= 5) keep working as a reference/tie-breaking input.

Single source of truth: the flavor/technique/family tag-dimension sets are imported
from `wiki.py` VOCABULARY (one-way dependency, similarity -> wiki), so adding a tag to
the vocabulary is automatically visible to scoring with no edit here. wiki.py stays
self-contained.
"""
from __future__ import annotations
import json, math, re, sys
from pathlib import Path

# Make emoji-bearing output safe on consoles whose default encoding isn't UTF-8
# (e.g. Windows cp1252). Pure presentation; does not change any computed value.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"

# D1 — tag-dimension knowledge is imported from wiki.py, never duplicated here.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wiki import VOCABULARY  # noqa: E402  (path set above)

FLAVOR_TAGS = set(VOCABULARY["Flavor / Profile"]["tags"])
TECHNIQUE_TAGS = set(VOCABULARY["Technique"]["tags"])
FAMILY_TAGS = set(VOCABULARY["Family / Style"]["tags"])
ERA_TAGS = set(VOCABULARY["Theme / Era"]["tags"])

# ---------------------------------------------------------------- weights ---
W_RUBRIC, W_INGREDIENT, W_TEXT = 0.45, 0.35, 0.20
RUBRIC_MAX = 11.0         # §7: base 3 + family 2 + sour 1 + sweet 1 + flavor cap 2 + technique 1 + era 1
# Owner-tunable link thresholds, validated against the live collection's score distribution
# (a natural gap separates the meaningful cluster ≥0.383 from the weak tail ≤0.306). The
# product owner adjusts these as the collection grows; see CLAUDE.md §7.
DEFAULT_THRESHOLD = 0.38  # fused-score threshold for the report
LINK_THRESHOLD = 0.38     # gaps: at/above this a pair SHOULD be linked (named constant, D3)
REMOVE_THRESHOLD = 0.33   # gaps: below this a written link is stale (0.05 hysteresis band 0.33-0.38)
DISCRETE_THRESHOLD = 5    # CLAUDE.md §7 legacy linking threshold (kept for reference)

# ------------------------------------------------------- parsing the cards ---
_UNIT = (r"(?:oz|ml|cl|l|tsp|tbsp|dash(?:es)?|part(?:s)?|cup(?:s)?|"
         r"barspoon(?:s)?|drop(?:s)?|splash(?:es)?|bsp|slice(?:s)?|wedge(?:s)?)")

# ingredient canonicalisation: first matching pattern wins (order matters)
ALIASES = [
    (r"\brum\b",                          "rum"),
    (r"\bcacha[cç]a\b",                   "rum"),
    (r"\bgin\b",                          "gin"),
    (r"\bvodka\b",                        "vodka"),
    (r"\b(bourbon|rye|scotch|whisk(?:e)?y)\b", "whiskey"),
    (r"\b(tequila|mezcal)\b",             "agave-spirit"),
    (r"\b(brandy|cognac)\b",              "brandy"),
    (r"\b(triple sec|cointreau|curacao|curaçao|orange liqueur|grand marnier)\b", "orange-liqueur"),
    (r"\b(coffee liqueur|kahl[uú]a)\b",   "coffee-liqueur"),
    (r"\bapricot\b",                      "fruit-liqueur"),
    (r"\bchartreuse\b",                   "chartreuse"),
    (r"\bcrme de menthe\b",               "menthe-liqueur"),
    (r"\bfalernum\b",                     "falernum"),
    (r"\bcampari\b",                      "campari"),
    (r"\bvermouth\b",                     "vermouth"),
    (r"\b(wine|sherry)\b",                "wine"),
    (r"\blime\b",                         "lime"),
    (r"\blemon\b",                        "lemon"),
    (r"\bgrapefruit\b",                   "grapefruit"),
    (r"\borange\b",                       "orange"),
    (r"\bpineapple\b",                    "pineapple"),
    (r"\bmango\b",                        "mango"),
    (r"\b(simple syrup|sugar syrup|demerara|sugar|honey|agave (?:nectar|syrup)|grenadine)\b", "sugar"),
    (r"\bmint\b",                         "mint"),
    (r"\b(angostura|bitters)\b",          "bitters"),
    (r"\b(soda|sparkling|seltzer|club soda)\b", "soda"),
    (r"\b(cola|coke)\b",                  "cola"),
    (r"\bginger\b",                       "ginger"),
    (r"\b(espresso|coffee)\b",            "coffee"),
    (r"\bstrawberr",                      "strawberry"),
    (r"\begg\b",                          "egg"),
    (r"\bcream\b",                        "cream"),
    (r"\bsalt\b",                         "salt"),
]
SOUR_RE  = re.compile(r"\b(lime|lemon|grapefruit|sour mix|citrus|verjus)\b", re.I)
SWEET_RE = re.compile(r"\b(sweet|sugar|syrup|honey|agave|grenadine|falernum|orgeat|demerara|liqueur|cola|chartreuse)\b", re.I)

STOPWORDS = set("""a an and are as at be but by for from has have in into is it its
of on or over that the their then this to until with your you all more most often
when which while also after before during each per onto""".split())


def strip_qty(line: str) -> str:
    s = line.strip().lstrip("-").strip()
    s = re.sub(r"^[\d./–—\-\s½¼¾⅓⅔]+", "", s)
    s = re.sub(rf"^{_UNIT}\b\.?\s*", "", s, flags=re.I)
    return s.strip()


def _alias_match(raw: str):
    """Return the (canon) an ingredient maps to via ALIASES, or None if it falls through."""
    s = re.sub(r"\(.*?\)", "", raw).lower().strip()
    for pat, canon in ALIASES:
        if re.search(pat, s):
            return canon
    return None


def canon_ingredient(raw: str) -> str:
    canon = _alias_match(raw)
    if canon is not None:
        return canon
    s = re.sub(r"\(.*?\)", "", raw).lower().strip()
    s = re.sub(r"[^a-z ]", "", s).strip()
    return re.sub(r"\s+", "-", s)


def parse_card(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")

    def fm(key, default=""):
        m = re.search(rf"^{key}:\s*(.+)$", text, re.M)
        return m.group(1).strip() if m else default

    def bodyline(label):
        m = re.search(rf"-\s*\*\*{label}:\*\*\s*(.+)", text)
        return m.group(1).strip() if m else ""

    m = re.search(r"tags:\s*\[(.*?)\]", text)
    tags = [t.strip() for t in m.group(1).split(",")] if (m and m.group(1).strip()) else []

    # ingredient bullet lines (the indented list under **Ingredients:**)
    ing_block = re.search(r"\*\*Ingredients:\*\*\s*\n((?:\s+-\s+.+\n?)+)", text)
    raw_ings = ([strip_qty(l) for l in ing_block.group(1).strip().splitlines()]
                if ing_block else [])
    raw_ings = [i for i in raw_ings if i]
    ing_text = " ; ".join(raw_ings).lower()

    background = re.search(r"\*\*Background:\*\*\s*(.+)", text)
    background = re.sub(r"\(sources?:.*?\)|\[([^\]]*)\]\([^)]*\)", r"\1",
                        background.group(1), flags=re.I | re.S) if background else ""

    free_text = " ".join([background, bodyline("Profile"), bodyline("Instruction"),
                          bodyline("Garnish"), bodyline("Glassware")])

    # written Other Similar Cocktails targets (slugs) — used by `gaps`, EXCLUDED from scoring
    sim = re.search(r"\*\*Other Similar Cocktails:\*\*\s*(.+)", text)
    similar = re.findall(r"\]\(\./([\w\-]+)\.md\)", sim.group(1)) if sim else []

    return {
        "slug": path.stem,
        "name": fm("name", path.stem),
        "base": fm("base"),
        "tags": tags,
        "flavor":    {t for t in tags if t in FLAVOR_TAGS},
        "technique": {t for t in tags if t in TECHNIQUE_TAGS},
        "family":    {t for t in tags if t in FAMILY_TAGS},
        "era":       {t for t in tags if t in ERA_TAGS},
        "raw_ingredients": raw_ings,
        "ingredients": {canon_ingredient(i) for i in raw_ings},
        "has_sour":  bool(SOUR_RE.search(ing_text)),
        "has_sweet": bool(SWEET_RE.search(ing_text)),
        "sour_agents":  set(SOUR_RE.findall(ing_text)),
        "sweet_agents": set(SWEET_RE.findall(ing_text)),
        "text": free_text,
        "similar": similar,
    }


# ------------------------------------------------------------ the 3 layers ---
def rubric_score(a: dict, b: dict) -> tuple[int, list[str]]:
    """CLAUDE.md §7 discrete rubric, sour/sweet derived from ingredient lines."""
    pts, why = 0, []
    if a["base"] and a["base"] == b["base"]:
        pts += 3; why.append(f"same base ({a['base']}, +3)")
    fam = a["family"] & b["family"]
    if fam:
        pts += 2; why.append(f"same family ({'/'.join(sorted(fam))}, +2)")
    sour = a["sour_agents"] & b["sour_agents"]
    if sour:
        pts += 1; why.append(f"shared sour ({'/'.join(sorted(sour))}, +1)")
    sweet = a["sweet_agents"] & b["sweet_agents"]
    if sweet:
        pts += 1; why.append(f"shared sweetener ({'/'.join(sorted(sweet))}, +1)")
    flav = a["flavor"] & b["flavor"]
    if flav:
        f = min(len(flav), 2)
        pts += f; why.append(f"shared flavor ({'/'.join(sorted(flav))}, +{f})")
    tech = a["technique"] & b["technique"]
    if tech:
        pts += 1; why.append(f"same technique ({'/'.join(sorted(tech))}, +1)")
    era = a["era"] & b["era"]
    if era:
        pts += 1; why.append(f"same theme/era ({'/'.join(sorted(era))}, +1)")
    return pts, why


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a or b) else 0.0


def tokenize(text: str) -> list[str]:
    text = re.sub(r"https?://\S+", " ", text.lower())
    return [t for t in re.findall(r"[a-z]{2,}", text) if t not in STOPWORDS]


def tfidf_vectors(docs: list[list[str]]) -> list[dict]:
    n = len(docs)
    df = {}
    for d in docs:
        for t in set(d):
            df[t] = df.get(t, 0) + 1
    vecs = []
    for d in docs:
        tf = {}
        for t in d:
            tf[t] = tf.get(t, 0) + 1
        v = {t: (1 + math.log(c)) * (math.log((1 + n) / (1 + df[t])) + 1)
             for t, c in tf.items()}   # smoothed idf (+1) so shared terms don't zero out
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vecs.append({t: x / norm for t, x in v.items()})
    return vecs


def cosine(u: dict, v: dict) -> float:
    if len(v) < len(u):
        u, v = v, u
    return sum(x * v.get(t, 0.0) for t, x in u.items())


# --------------------------------------------------------------- pipeline ---
def compute(cards: list[dict]) -> list[dict]:
    vecs = tfidf_vectors([tokenize(c["text"]) for c in cards])
    pairs = []
    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            a, b = cards[i], cards[j]
            disc, why = rubric_score(a, b)
            ing = jaccard(a["ingredients"], b["ingredients"])
            txt = cosine(vecs[i], vecs[j])
            shared_ing = sorted(a["ingredients"] & b["ingredients"])
            fused = (W_RUBRIC * (disc / RUBRIC_MAX) + W_INGREDIENT * ing + W_TEXT * txt)
            pairs.append({
                "a": a["slug"], "b": b["slug"],
                "score": round(fused, 4),
                "rubric_pts": disc, "rubric_why": why,
                "ingredient_jaccard": round(ing, 4),
                "shared_ingredients": shared_ing,
                "text_cosine": round(txt, 4),
                "eligible_§7": disc >= DISCRETE_THRESHOLD,
            })
    pairs.sort(key=lambda p: (-p["score"], -p["rubric_pts"]))
    return pairs


def neighbors(cards, pairs, top):
    out = {c["slug"]: [] for c in cards}
    for p in pairs:
        out[p["a"]].append((p["b"], p))
        out[p["b"]].append((p["a"], p))
    for s in out:
        out[s].sort(key=lambda x: (-x[1]["score"], -x[1]["rubric_pts"]))
        out[s] = out[s][:top]
    return out


# ---------------------------------------------------------------- outputs ---
def cmd_report(cards, pairs, top, threshold):
    names = {c["slug"]: c["name"] for c in cards}
    print(f"# Pairwise similarity report — {len(cards)} cards, "
          f"weights rubric {W_RUBRIC} / ingredients {W_INGREDIENT} / text {W_TEXT}\n")
    for slug, nbrs in neighbors(cards, pairs, top).items():
        print(f"## {names[slug]}")
        shown = 0
        for other, p in nbrs:
            mark = "✅" if p["score"] >= threshold else ("☑️ §7" if p["eligible_§7"] else "—")
            print(f"  {mark} {names[other]:<28} fused={p['score']:.3f}  "
                  f"(rubric {p['rubric_pts']}/10 · ing {p['ingredient_jaccard']:.2f} · "
                  f"text {p['text_cosine']:.2f})")
            if p["rubric_why"]:
                print(f"        rubric: {'; '.join(p['rubric_why'])}")
            if p["shared_ingredients"]:
                print(f"        shared ingredients: {', '.join(p['shared_ingredients'])}")
            shown += 1
        if not shown:
            print("  (no candidates)")
        print()
    print(f"Legend: ✅ fused ≥ {threshold} (recommend linking) · "
          f"☑️ §7 = passes the legacy discrete ≥{DISCRETE_THRESHOLD} threshold only · — below both.")


def cmd_matrix(cards, pairs):
    slugs = [c["slug"] for c in cards]
    names = {c["slug"]: c["name"] for c in cards}
    m = {s: {t: "" for t in slugs} for s in slugs}
    for p in pairs:
        m[p["a"]][p["b"]] = m[p["b"]][p["a"]] = f"{p['score']:.2f}"
    head = "| | " + " | ".join(names[s] for s in slugs) + " |"
    sep = "|" + "---|" * (len(slugs) + 1)
    print(head); print(sep)
    for s in slugs:
        cells = " | ".join(("—" if s == t else m[s][t]) for t in slugs)
        print(f"| **{names[s]}** | {cells} |")


def cmd_pairs(pairs, cards):
    names = {c["slug"]: c["name"] for c in cards}
    print(f"{'fused':>6}  {'rub':>3}  {'ing':>5}  {'txt':>5}  pair")
    for p in pairs:
        print(f"{p['score']:6.3f}  {p['rubric_pts']:3d}  {p['ingredient_jaccard']:5.2f}  "
              f"{p['text_cosine']:5.2f}  {names[p['a']]} ↔ {names[p['b']]}")


# ------------------------------------------------------------------- gaps ---
def _slug_words(slug: str) -> set:
    """Significant words of a fallthrough slug (>=4 chars) for variant clustering."""
    return {w for w in slug.split("-") if len(w) >= 4}


def _related_fallthrough(s1: str, s2: str) -> bool:
    """Two fallthrough slugs are likely the same ingredient if any significant word of
    one equals or is a substring of a significant word of the other."""
    for a in _slug_words(s1):
        for b in _slug_words(s2):
            if a == b or a in b or b in a:
                return True
    return False


def cluster_fallthroughs(slugs):
    """Union-find clustering of fallthrough slugs by word overlap.
    Returns a list of clusters (lists of slugs), each sorted, the list sorted by first slug."""
    uniq = sorted(set(slugs))
    parent = {s: s for s in uniq}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[max(rx, ry)] = min(rx, ry)

    for i in range(len(uniq)):
        for j in range(i + 1, len(uniq)):
            if _related_fallthrough(uniq[i], uniq[j]):
                union(uniq[i], uniq[j])

    groups = {}
    for s in uniq:
        groups.setdefault(find(s), []).append(s)
    return sorted((sorted(g) for g in groups.values()), key=lambda g: g[0])


def collect_fallthroughs(cards):
    """slug -> sorted list of card names that produced this uncanonicalised ingredient."""
    out = {}
    for c in cards:
        for raw in c["raw_ingredients"]:
            if _alias_match(raw) is None:
                slug = canon_ingredient(raw)
                if slug:
                    out.setdefault(slug, set()).add(c["name"])
    return {s: sorted(v) for s, v in out.items()}


def cmd_gaps(cards, pairs):
    """Deterministic coverage + link-drift report. WARN findings set exit code 1."""
    names = {c["slug"]: c["name"] for c in cards}
    warns, infos = [], []

    # 1. Uncanonicalised ingredient variants -----------------------------------
    fall = collect_fallthroughs(cards)
    clusters = cluster_fallthroughs(list(fall.keys()))
    print("## 1. Uncanonicalised ingredient tokens (fell through ALIASES)\n")
    if not fall:
        print("  (none — every ingredient canonicalises)\n")
    else:
        for cl in clusters:
            if len(cl) >= 2:
                where = "; ".join(f"{s} [{', '.join(fall[s])}]" for s in cl)
                msg = (f"likely same ingredient — extend ALIASES: {where}")
                warns.append(("variant-cluster", msg))
                print(f"  [WARN] cluster: {', '.join(cl)}")
                for s in cl:
                    print(f"         {s}  ←  {', '.join(fall[s])}")
            else:
                s = cl[0]
                infos.append(("fallthrough", f"{s} [{', '.join(fall[s])}]"))
                print(f"  [INFO] {s}  ←  {', '.join(fall[s])}")
        print()

    # 2. Sour/sweet double-misses ----------------------------------------------
    print("## 2. Sour/sweet double-misses (ingredients present, no SOUR_RE/SWEET_RE hit)\n")
    misses = [c for c in cards if c["raw_ingredients"] and not c["has_sour"] and not c["has_sweet"]]
    if not misses:
        print("  (none — every card with ingredients triggers a sour and/or sweet match)\n")
    else:
        for c in misses:
            infos.append(("double-miss", c["name"]))
            print(f"  [INFO] {c['name']}: no souring or sweetening agent detected — "
                  f"review SOUR_RE / SWEET_RE")
        print()

    # 3. Link drift ------------------------------------------------------------
    print("## 3. Link drift (written Other Similar Cocktails vs current fused scores)\n")
    by = {c["slug"]: c for c in cards}
    pmap = {}
    for p in pairs:
        pmap[(p["a"], p["b"])] = pmap[(p["b"], p["a"])] = p
    drift_found = False

    # 3a. stale + one-way written links
    for c in cards:
        for tgt in c["similar"]:
            if tgt not in by:
                continue  # nonexistent target is a wiki.py lint error, not a drift concern
            p = pmap.get((c["slug"], tgt))
            score = p["score"] if p else 0.0
            if score < REMOVE_THRESHOLD:
                drift_found = True
                warns.append(("stale-link", f"{c['name']} → {names[tgt]} (fused {score:.3f} < {REMOVE_THRESHOLD})"))
                print(f"  [WARN] stale: {c['name']} → {names[tgt]}  "
                      f"fused={score:.3f} (< {REMOVE_THRESHOLD})")
            elif c["slug"] not in by[tgt]["similar"]:
                drift_found = True
                warns.append(("one-way", f"{c['name']} → {names[tgt]} not mutual (fused {score:.3f})"))
                print(f"  [WARN] one-way: {c['name']} → {names[tgt]} (no back-link)  "
                      f"fused={score:.3f}")

    # 3b. missing strong links (fused >= LINK_THRESHOLD, neither side links the other)
    for p in pairs:
        if p["score"] >= LINK_THRESHOLD:
            a, b = p["a"], p["b"]
            if b not in by[a]["similar"] and a not in by[b]["similar"]:
                drift_found = True
                warns.append(("missing-link", f"{names[a]} ↔ {names[b]} (fused {p['score']:.3f})"))
                print(f"  [WARN] missing: {names[a]} ↔ {names[b]}  "
                      f"fused={p['score']:.3f} (≥ {LINK_THRESHOLD}, neither links the other)")
    if not drift_found:
        print("  (none — written links match current scores; no missing strong links)\n")
    else:
        print()

    print(f"{len(warns)} warning(s), {len(infos)} info.")
    print("✅ No gaps." if not warns else "❌ Gaps found (see WARN above).")
    return 1 if warns else 0


# --------------------------------------------------------------- self-test ---
def cmd_test():
    ok = True
    def check(cond, msg):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + msg)
        ok = ok and cond

    # --- ALIASES: one pinned mapping per canonical class ---------------------
    alias_cases = [
        ("Gosling's Black Seal rum", "rum"),
        ("Cachaça", "rum"),
        ("London Dry gin", "gin"),
        ("Vodka or Cognac", "vodka"),     # vodka pattern precedes brandy/cognac (order matters)
        ("Bourbon", "whiskey"),
        ("Blanco tequila", "agave-spirit"),
        ("Brandy", "brandy"),
        ("Triple sec", "orange-liqueur"),
        ("Mr. Black Cold Brew Coffee Liqueur", "coffee-liqueur"),
        ("Falernum", "falernum"),
        ("Campari", "campari"),
        ("Sweet vermouth", "vermouth"),
        ("Light red wine", "wine"),
        ("Fresh lime juice", "lime"),
        ("Lemon juice", "lemon"),
        ("Grapefruit juice", "grapefruit"),
        ("Orange juice", "orange"),
        ("Pineapple juice", "pineapple"),
        ("Mango juice", "mango"),
        ("Simple syrup", "sugar"),
        ("Mint leaves", "mint"),
        ("Angostura bitters", "bitters"),
        ("Club soda", "soda"),
        ("Splash of Coke", "cola"),
        ("Ginger beer", "ginger"),
        ("Freshly brewed espresso", "coffee"),
        ("Egg white", "egg"),
        ("Heavy cream", "cream"),
        ("Celery salt", "salt"),
    ]
    for raw, want in alias_cases:
        got = canon_ingredient(raw)
        check(got == want, f"alias: {raw!r} -> {want} (got {got!r})")

    check(canon_ingredient("Absinthe") == "absinthe", "fallthrough keeps raw slug")
    check(_alias_match("Absinthe") is None, "_alias_match None on fallthrough")
    check(strip_qty("- 1.5 oz Pineapple juice") == "Pineapple juice", "qty/unit stripping")
    check(jaccard({1, 2}, {2, 3}) == 1 / 3, "jaccard")

    # --- rubric full score ---------------------------------------------------
    a = {"base": "Rum", "family": {"Tiki"}, "flavor": {"Fruity", "Spiced", "Complex"},
         "technique": {"Swizzle"}, "era": {"Classic"}, "sour_agents": {"lemon"}, "sweet_agents": {"syrup"}}
    b = {"base": "Rum", "family": {"Tiki"}, "flavor": {"Fruity", "Spiced"},
         "technique": {"Swizzle"}, "era": {"Classic"}, "sour_agents": {"lemon", "lime"}, "sweet_agents": {"syrup"}}
    pts, _ = rubric_score(a, b)
    check(pts == 3 + 2 + 1 + 1 + 2 + 1 + 1, f"rubric full score (got {pts}, want 11)")

    # --- TF-IDF cosine -------------------------------------------------------
    v = tfidf_vectors([["mint", "lime", "rum"], ["mint", "lime", "gin"], ["coffee", "vodka"]])
    check(cosine(v[0], v[1]) > cosine(v[0], v[2]), "tfidf cosine ordering")
    check(abs(cosine(v[0], v[1]) - cosine(v[1], v[0])) < 1e-12, "cosine symmetric")

    # --- D1: VOCABULARY import is live (a tag added to wiki.py is seen here) --
    check(FLAVOR_TAGS == set(VOCABULARY["Flavor / Profile"]["tags"]),
          "FLAVOR_TAGS derived from wiki.VOCABULARY (no duplicate set)")
    check(TECHNIQUE_TAGS == set(VOCABULARY["Technique"]["tags"]),
          "TECHNIQUE_TAGS derived from wiki.VOCABULARY")
    check(FAMILY_TAGS == set(VOCABULARY["Family / Style"]["tags"]),
          "FAMILY_TAGS derived from wiki.VOCABULARY")
    check(ERA_TAGS == set(VOCABULARY["Theme / Era"]["tags"]),
          "ERA_TAGS derived from wiki.VOCABULARY")
    # functional: a flavor tag that lives ONLY in VOCABULARY is counted by the rubric layer.
    vtag = sorted(set(VOCABULARY["Flavor / Profile"]["tags"]))[0]
    ca = {"base": "", "family": set(), "flavor": {vtag}, "technique": set(), "era": set(),
          "sour_agents": set(), "sweet_agents": set()}
    cb = {"base": "", "family": set(), "flavor": {vtag}, "technique": set(), "era": set(),
          "sour_agents": set(), "sweet_agents": set()}
    pts2, why2 = rubric_score(ca, cb)
    check(pts2 == 1 and any("flavor" in w for w in why2),
          f"VOCABULARY flavor tag {vtag!r} scored by rubric layer")

    # --- gaps: variant clustering -------------------------------------------
    clusters = cluster_fallthroughs(["passion-fruit-syrup", "passionfruit-puree", "dry-sherry"])
    cl_with_passion = [c for c in clusters if any("passion" in s for s in c)][0]
    check(set(cl_with_passion) == {"passion-fruit-syrup", "passionfruit-puree"},
          "variant cluster groups passion-fruit-syrup + passionfruit-puree")
    check(["dry-sherry"] in clusters, "unrelated fallthrough stays a singleton")

    # --- gaps: link-drift thresholds & hysteresis ----------------------------
    def linkstate(score, a_links_b, b_links_a):
        """Mirror cmd_gaps decision for one pair, returns a label."""
        if a_links_b or b_links_a:
            if score < REMOVE_THRESHOLD:
                return "stale"
            if (a_links_b and not b_links_a) or (b_links_a and not a_links_b):
                return "one-way"
            return "ok"
        return "missing" if score >= LINK_THRESHOLD else "ok"
    band_mid = (REMOVE_THRESHOLD + LINK_THRESHOLD) / 2
    check(linkstate(REMOVE_THRESHOLD - 0.05, True, True) == "stale",
          f"stale link below REMOVE_THRESHOLD ({REMOVE_THRESHOLD}) flagged")
    check(linkstate(band_mid, True, True) == "ok",
          f"hysteresis band {band_mid:.3f} ({REMOVE_THRESHOLD}-{LINK_THRESHOLD}) not flagged")
    check(linkstate(LINK_THRESHOLD + 0.1, False, False) == "missing",
          f"missing strong link >= LINK_THRESHOLD ({LINK_THRESHOLD}) flagged")
    check(linkstate(LINK_THRESHOLD - 0.05, False, False) == "ok",
          "weak unlinked pair below LINK_THRESHOLD not flagged as missing")
    check(linkstate(LINK_THRESHOLD + 0.1, True, False) == "one-way", "one-way written link flagged")

    print("\nAll tests passed." if ok else "\nTESTS FAILED.")
    return 0 if ok else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "report"
    if cmd == "test":
        return cmd_test()
    top = 4
    threshold = DEFAULT_THRESHOLD
    if "--top" in argv:
        top = int(argv[argv.index("--top") + 1])
    if "--threshold" in argv:
        threshold = float(argv[argv.index("--threshold") + 1])
    cards = sorted((parse_card(p) for p in WIKI.glob("*.md")), key=lambda c: c["name"].lower())
    if not cards:
        print("no cards in wiki/"); return 1
    pairs = compute(cards)
    if cmd == "report":
        cmd_report(cards, pairs, top, threshold)
    elif cmd == "matrix":
        cmd_matrix(cards, pairs)
    elif cmd == "pairs":
        cmd_pairs(pairs, cards)
    elif cmd == "gaps":
        return cmd_gaps(cards, pairs)
    elif cmd == "json":
        print(json.dumps(pairs, ensure_ascii=False, indent=2))
    else:
        print(__doc__); return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
