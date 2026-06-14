# 📓 Log — Activity Record

Append-only, reverse-chronological (newest on top). Every Ingest / Query-of-note / Lint
gets a dated entry. Date prefixes are ISO `YYYY-MM-DD` so the log stays greppable.

## 2026-06-13 — Ingest

- Ingested **Tradewinds** from `raw/inbox/Untitled.md` and **Bijou (Layered)** from `raw/inbox/Untitled 1.md`.
- Completed Background and flavor profile from the web for both.
- **Tradewinds**: Assigned 7 tags: `#Rum`, `#Lemon`, `#Coconut`, `#Refreshing`, `#Creamy`, `#Blended`, `#Tiki`. Linked **Other Similar Cocktails**: **Bermuda Rum Swizzle** and **Queen's Park Swizzle** (passing legacy §7).
- **Bijou (Layered)**: Assigned 7 tags: `#Gin`, `#Vermouth`, `#Boozy`, `#Complex`, `#Herbal`, `#Layered`, `#Shot`. Linked **Other Similar Cocktails**: **Martini** and **Shamrock Cocktail**.
- **Similarity engine**: Extended `ALIASES` in `scripts/similarity.py` to include **apricot** (as `fruit-liqueur`), **chartreuse**, and **crème de menthe** (as `menthe-liqueur`). Expanded `SWEET_RE` to include `sweet` and `chartreuse` to improve flavor detection.
- Archived originals as `raw/archive/tradewinds.md` and `raw/archive/bijou-layered.md`.
- Updated `index.md`, `tags.md`, and VitePress sidebar via `wiki.py compile`.

## 2026-06-13 — Ingest

- Ingested **Shamrock Cocktail** from `raw/inbox/Untitled.md`.
- Completed Background and flavor profile from the web (Source: Difford's Guide).
- Assigned 6 tags including the new Theme / Era dimension: `#Whiskey`, `#Herbal`, `#Stirred`, `#Martini`, `#Classic`, `#StPatricksDay`.
- Linked **Other Similar Cocktails**: **TBD** (no existing cocktails met the 0.38 fused threshold; closest was **Martini** at 0.22).
- Archived original as `raw/archive/shamrock-cocktail.md`.
- Updated `index.md`, `tags.md`, and VitePress sidebar via `wiki.py compile`.

## 2026-06-13 — Ingest

- Ingested **French 75** and **Margarita (Classic)** from `raw/inbox/`.
- Completed Background and historical context from the web for both.
- **French 75**: Assigned 7 tags: `#Gin`, `#Lemon`, `#Refreshing`, `#Shaken`, `#Fizz`, `#Flute`, `#Wine`. Linked **Other Similar Cocktails**: **TBD** (no existing cocktails met the 0.38 fused threshold; closest was **Sangria** at 0.30).
- **Margarita (Classic)**: Assigned 7 tags: `#Tequila`, `#Lime`, `#Orange`, `#Tart`, `#Shaken`, `#Rocks`, `#Sour`. Linked **Other Similar Cocktails**: **TBD** (no existing cocktails met the 0.38 fused threshold; closest was **The Salty Shaker** at 0.28).
- **Similarity engine**: Extended `ALIASES` in `scripts/similarity.py` to include **Grand Marnier** (as `orange-liqueur`) and **Sherry** (as `wine`) to improve material overlap detection.
- Updated `index.md`, `tags.md`, and VitePress sidebar via `wiki.py compile`.

## 2026-06-12 — Ingest

- Ingested **Whiskey Sour** and **Martini** from `raw/inbox/`.
- Completed Background and historical context from the web for both.
- **Whiskey Sour**: Assigned 6 tags: `#Whiskey`, `#Lemon`, `#Sugar`, `#Egg`, `#Shaken`, `#Sour`. Linked **Other Similar Cocktails**: **TBD** (fused scores < 0.38).
- **Martini**: Assigned 6 tags: `#Gin`, `#Vermouth`, `#Dry`, `#Stirred`, `#Martini`, `#NickAndNora`. Linked **Other Similar Cocktails**: **TBD** (no strong candidates).
- Updated `index.md`, `tags.md`, and VitePress sidebar via `wiki.py compile`.

## 2026-06-12 — Similarity engine

Replaced the hand-scored §7 rubric with a deterministic engine (OpenSpec change
`add-content-aware-similarity`).

- **New tool `scripts/similarity.py`** (stdlib-only): fuses three signals —
  `0.45·rubric + 0.35·ingredient_jaccard + 0.20·text_cosine` — into one `fused` score.
  Imports `VOCABULARY` from `wiki.py` (one-way) so a new tag is auto-visible to scoring.
  Modes: `report` / `pairs` / `matrix` / `json` / `gaps` / `test` (47 self-tests pass).
- **`gaps` command** (folded into the Lint workflow): flags un-canonicalised ingredient
  variant clusters, sour/sweet double-misses, and link drift (stale / missing / one-way),
  exiting non-zero on any warning.
- **Thresholds (owner-tunable):** link/removal set to **0.38 / 0.33** (down from the
  reference 0.45 / 0.40), validated against the live 8-card distribution. Lowered per owner
  direction so **Espresso Martini ↔ Long Island Ice Tea** (fused 0.40) is classified similar.
- **Corrected the audited link errors:** removed the wrong "shared Rum base" link between
  **Daiquiri** and **Long Island Ice Tea** (LIIT's base is Vodka; fused 0.18); added the
  mutual **Espresso Martini ↔ LIIT** link.
- **Re-linked all 8 cards** to the new `(fused 0.NN — reason)` format (legacy `(Score N:)`
  retired). Connected rum trio (Daiquiri–Mojito–QPS) + swizzle pair (QPS–Bermuda) + vodka
  pair (EM–LIIT); **Sangria** and **The Salty Shaker** are TBD (nothing clears 0.38).
- **Docs:** rewrote `CLAUDE.md` §7 (script computes / LLM selects + explains), added the §1
  Similarity row, the §8 dual-lint flow, and the tiered extension-paths table; updated
  `README.md`. Ratings / Modified Variation / `raw/archive/` untouched.
- **Trial run:** report → judge → gaps → lint all green; gap-extension loop exercised on a
  scratch card (variant cluster flagged, then discarded). `wiki.py compile` regenerated
  `index.md` / `tags.md` / sidebar JSON.

## 2026-06-11 — Website Rendering Update

- Updated `site/.vitepress/theme/enhance.js` to change the half-star base character from a solid star (★) to an outline star (☆).
- This ensures that half-stars render with a transparent background for the unfilled portion (keeping the shape outline), rather than a solid/translucent block.
- Verified consistency via `python scripts/wiki.py lint`.

---

## 2026-06-11 — Ingest

- Ingested **Long Island Ice Tea** from `raw/inbox/Untitled.md`.
- Completed Background and historical context from the web (Source: spiritsanddistilling.com).
- Assigned 7 tags: `#Vodka`, `#Rum`, `#Gin`, `#Tequila`, `#Highball`, `#Boozy`, `#Refreshing`.
- Linked **Other Similar Cocktails**: mutual links with **Mojito**, **Daiquiri**, and **The Salty Shaker** based on scoring rubric (§7).
- Updated `index.md`, `tags.md`, and VitePress sidebar.

---

## 2026-06-10 — Documentation Update

- Updated `README.md` §6 and the prompt cheat-sheet to reflect the new Similar-cocktail linking algorithm (§7 in `CLAUDE.md`).
- Refined the explicit Ingest prompt to include the scoring system and threshold requirement.

## 2026-06-10 — Similarity Re-evaluation

- Re-calculated all 'Other Similar Cocktails' links across 7 cards using the strict scoring rubric (§7).
- Updated links to include scores and mutual back-links.
- Removed links failing the threshold (Score < 5), such as Sangria and Bermuda Rum Swizzle's previous cross-links.
- Verified consistency via compile and lint.

## 2026-06-10 — Ingest

- Ingested **Espresso Martini** from `raw/inbox/Espresso Martini.md`.
- Completed Background and historical context from the web (Source: mclarenvalecellars.com).
- Assigned 7 tags: `#Vodka`, `#Coffee`, `#Sugar`, `#Boozy`, `#Complex`, `#Shaken`, `#Coupe`.
- Linked **Other Similar Cocktails**: **TBD** (no existing cocktails met the similarity threshold).
- Updated `index.md`, `tags.md`, and VitePress sidebar.

## 2026-06-10 — Ingest

- Ingested **The Salty Shaker** from `raw/inbox/The salty shaker.md`.
- Completed Background, Glassware, and enriched recipe context from the web (Source: murlarkey.com).
- Added `Mango` to the **Ingredient** tag vocabulary in `scripts/wiki.py`.
- Assigned 7 tags: `#Whiskey`, `#Lime`, `#Mango`, `#Spiced`, `#Refreshing`, `#Shaken`, `#Sour`.
- Linked **Other Similar Cocktails**: mutual link with **Daiquiri** (Shaken Sour family).
- Updated `index.md`, `tags.md`, and VitePress sidebar.

## 2026-06-09 — Ingest

- Ingested **Sangria** from `raw/inbox/Sangria.md`.
- Completed Background, Glassware (partially), Ingredients normalization, Instruction, Garnish, Profile, and Tags from the web (Source: thisdayinwinehistory.com).
- Added `Wine` to Base Spirit and renamed `Wine` Glassware to `WineGlass` in `scripts/wiki.py` to avoid tag collision.
- Linked **Other Similar Cocktails**: mutual link with **Bermuda Rum Swizzle**.
- Updated `index.md`, `tags.md`, and VitePress sidebar.

## 2026-06-08 — VitePress site

Added a static **VitePress** site over the existing wiki markdown, published to GitHub Pages,
plus an `llms.txt` export so any external LLM can query the collection over HTTP.

- **Site (view, not a fork):** reads content in-place from the repo root (`srcDir: '.'`),
  `base: '/CocktailDex/'`, with `srcExclude` hiding operational files (`raw/`, `scripts/`,
  `openspec/`, `.claude/`, `node_modules/`, `CLAUDE.md`, `GEMINI.md`, `README.md`, `log.md`).
  Built-in local search; photos and card↔card links resolve in the build.
- **Deterministic nav:** `scripts/wiki.py compile` now also emits the committed
  `.vitepress/sidebar.generated.json` (alongside `index.md` / `tags.md`); the VitePress config
  imports it, so the sidebar stays in lockstep with the cards. CLAUDE.md §5/§10 updated.
- **llms.txt:** `vitepress-plugin-llms` emits `llms.txt` (index map) + `llms-full.txt` (full
  text) at the site root with absolute `https://c892836a.github.io/CocktailDex/` URLs. Note:
  the plugin's `domain` is set to the **origin only** (`https://c892836a.github.io`) because it
  appends the already-base-prefixed page paths — using `.../CocktailDex` would double the base.
- **Deploy:** `.github/workflows/deploy.yml` builds (Node-only, Yarn via Corepack) and deploys
  to Pages on push to `main` + manual dispatch. Build consumes the committed artifacts — no
  Python in CI.
- **Card heading → H1:** changed each card's title heading from `## {Name}` to `# {Name}`
  (and CLAUDE.md §3b template) so VitePress and `llms.txt` pick up the cocktail name as the
  page title — previously they showed "Untitled". This is a presentation tweak only; the card
  **schema** (frontmatter fields, ingest/lint/query, human-only ratings) is unchanged, and
  `wiki.py` parses the name from frontmatter, so compile/lint are unaffected.
- **Manual one-time step (pending):** set GitHub repo Settings → Pages → Source = **GitHub
  Actions** before the first deploy will publish.

## 2026-06-08 — Rename

Project renamed from "Cocktail LLM Wiki" to **CocktailDex**. Updated titles/headers in
`CLAUDE.md`, `GEMINI.md`, `README.md`, and `scripts/wiki.py` (index + tags page headers),
then recompiled `index.md` / `tags.md`. The folder on disk is still `調酒LLM wiki/` — rename
it manually if desired (the docs don't depend on the folder name).

---

## 2026-06-08 — Ingest (seed)

Ingested 4 connected seed-demo cocktails from `raw/inbox/` → `wiki/`, then archived the
originals to `raw/archive/`:

- **Bermuda Rum Swizzle**, **Daiquiri**, **Mojito**, **Queen's Park Swizzle**.
- Completed from the web: Background (all four, with source links), plus Glassware /
  Profile / Garnish / full measured Ingredients where the raw drop was sparse (esp. Mojito
  and Bermuda Rum Swizzle, which arrived as little more than a name).
- Tagged each with 6-dimension tags (3–7 each) and registered them in `tags.md`.
- Cross-linked **Other Similar Cocktails** by structure / flavour / technique: the rum +
  lime + mint trio (QPS ↔ Mojito ↔ Daiquiri) and the Swizzle pair (QPS ↔ Bermuda).
- Left all Eric / Charlene ratings and Modified Variations blank (human-only fields).
- Updated `index.md`.

## 2026-06-08 — Wiki created

Initialised the wiki scaffolding per `CLAUDE.md`: `raw/inbox`, `raw/archive`, `wiki`,
`photos` folders; `index.md`, `tags.md` (Standard 6-dimension scheme), and this log.
Architecture: two-layer (immutable `raw/` + maintained `wiki/`); links: standard Markdown.

---

<!-- New entries go ABOVE this line, newest first. Template:

## YYYY-MM-DD — Ingest | Query | Lint
- what happened, what changed, anything left as TBD
-->
