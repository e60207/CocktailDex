# 📓 Log — Activity Record

Append-only, reverse-chronological (newest on top). Every Ingest / Query-of-note / Lint
gets a dated entry. Date prefixes are ISO `YYYY-MM-DD` so the log stays greppable.

## 2026-06-24 — Ingest

**Added:**
- Chicago Fizz ([wiki/chicago-fizz.md](./wiki/chicago-fizz.md))
- Chicago Cocktail ([wiki/chicago-cocktail.md](./wiki/chicago-cocktail.md))
- The Lower Wacker ([wiki/the-lower-wacker.md](./wiki/the-lower-wacker.md))

**Completed from the web:**
- **Chicago Fizz** — Background (late 19th/early 20th century, Waldorf-Astoria Bar Book 1935), Glassware (Collins), Profile. Source: https://www.diffordsguide.com/cocktails/recipe/5860/chicago-fizz
- **Chicago Cocktail** — Background (first published Vermeire 1922, Savoy 1930), Glassware (Coupe), Profile. Source: https://www.diffordsguide.com/cocktails/recipe/16019/chicago
- **The Lower Wacker** — Background (contemporary Chicago cocktail; Lower Wacker Drive + Malört context from general knowledge; no known prior source found online).

**Similar links added:**
- Chicago Fizz ↔ Rum Flip (fused 0.45)
- The Lower Wacker ↔ Manhattan (fused 0.40), ↔ Tipperary (fused 0.38)
- Chicago Cocktail: no ✅ candidates (TBD)

---

## 2026-06-22 — Ingest

**Added:** Rabo de Galo ([wiki/rabo-de-galo.md](./wiki/rabo-de-galo.md))

**Completed from the web:**
- Background: classic Brazilian stirred drink built on cachaça, sweet vermouth, and Cynar; name means "rooster's tail" (a play on "cocktail"); staple of São Paulo bar culture. (source: https://www.diffordsguide.com/cocktails/recipe/1740/rabo-de-galo)
- Glassware: Rocks
- Profile: bittersweet and spirit-forward; earthy/vegetal from Cynar, herbaceous from vermouth, grassy brightness from cachaça.

**New tags added to VOCABULARY:**
- `Cachaca` (Base Spirit dimension) — first used by Rabo de Galo
- `Cynar` (Ingredient dimension) — first used by Rabo de Galo

**New ALIASES added to `similarity.py`:**
- `crème de menthe` accent-tolerant fix (resolves existing menthe-liqueur mapping)
- `crème de cacao` → `cacao-liqueur` (cleared cluster: green-crme-de-menthe / white-crme-de-cacao)
- `cynar` → `cynar`

**Similarity:** No candidates reached the ✅ link threshold (0.38); Manhattan was closest at fused 0.266. "Other Similar Cocktails" left as TBD.

**Lint:** 0 errors, 0 warnings.

## 2026-06-21 — Ingest

**Added:** Pago Pago ([wiki/pago-pago.md](./wiki/pago-pago.md))

**Completed from the web:**
- Background: classic Daiquiri variant circa 1940, credited to Ronrico rum brand; first appeared in *The How and When* (Gale & Marco, 2nd ed., 1940); named after Pago Pago, capital of American Samoa. (source: https://punchdrink.com/articles/pago-pago-echo-lake-chartreuse-daiquiri-cocktail-recipe/)
- Glassware: Coupe (cocktail glass per original recipe)
- Profile: tropical and complex — pineapple, herbal Chartreuse, whisper of chocolate, bright lime backbone

**New tag added to VOCABULARY:** `Chartreuse` (Ingredient dimension) — first used by Pago Pago.

**Similarity:** No candidates reached the ✅ link threshold (0.38); Daiquiri was closest at fused 0.363. "Other Similar Cocktails" left as TBD.

**Lint:** 0 errors, 0 warnings.

## 2026-06-21 — Ingest

- Completed **Caipirinha** from `raw/inbox/Untitled.md` (the card already existed in `wiki/` with
  Background/Profile/tags filled in from a prior session, but had never been archived or linked —
  treated as still-pending per the inbox/archive state machine).
- Verified Background/era against [Wikipedia](https://en.wikipedia.org/wiki/Caipirinha): early-20th-century
  Brazilian origin, official cultural-heritage status (2003) — confirms the existing `#Classic` tag.
  No other fields needed completion; carried Eric's rating (4.5/5) and !!Tips verbatim (human-only).
- **Similarity engine**: ran `similarity.py report` — linked **Caipirinha** to its 4 ✅ candidates:
  **Daiquiri** (fused 0.660), **Daiquiri (Frozen strawberry)** (fused 0.559), **Mojito** (fused 0.492),
  **Queen's Park Swizzle** (fused 0.383).
- **Mutual back-links**: added **Caipirinha** to the "Other Similar Cocktails" line on **Daiquiri**,
  **Daiquiri (Frozen strawberry)**, **Mojito**, and **Queen's Park Swizzle**; refreshed the other
  drifted fused scores on those 4 cards to match the current corpus (left **Queen's Park Swizzle**'s
  existing **Bermuda Rum Swizzle** link at 0.38 untouched — within the hysteresis band).
- Archived original as `raw/archive/caipirinha.md`.
- `wiki.py compile` / `wiki.py lint` / `similarity.py gaps` all clean after the change.
- **Note:** a second, blank `raw/inbox/Untitled.md` (empty template) appeared mid-session — left
  as-is in the inbox since it has no content yet to ingest.

## 2026-06-20 — Ingest

- Ingested **Tipperary** from `raw/inbox/Untitled.md` and **The Belmont Jewel** from `raw/inbox/Untitled 1.md`.
- Completed details from the web (Background, Glassware, Profile, and Tags).
- Both new cocktails defaulted to using `![](../photos/_TBD/pending-cocktails.jpg)` as their photo links.
- **Similarity engine**: Linked **Other Similar Cocktails**:
  - **Tipperary**: Linked to **Manhattan** (fused 0.58) and **Shamrock Cocktail** (fused 0.57).
  - **The Belmont Jewel**: Linked to **Scofflaw** (fused 0.41) and **Whiskey Sour** (fused 0.40).
- **Mutual back-links**: Added **Tipperary** to **Manhattan** and **Shamrock Cocktail**, and **The Belmont Jewel** to **Scofflaw** and **Whiskey Sour**.
- Archived originals as `raw/archive/tipperary.md` and `raw/archive/the-belmont-jewel.md`.
- Updated `index.md`, `tags.md`, and VitePress sidebar via `wiki.py compile`.

## 2026-06-20 — Configuration Update

- Updated `CLAUDE.md` §3b to use `![](../photos/_TBD/pending-cocktails.jpg)` as the default photo link for future cocktail card generation.
- Configured stdout of `scripts/wiki.py` to use UTF-8 on Windows to resolve console encoding crashes.
- Updated last-updated dates in `CLAUDE.md` and `GEMINI.md`.

## 2026-06-14 — Ingest

- Ingested **Scofflaw** from `raw/inbox/Untitled.md`.
- Completed Background and historical context from the web (Source: thekitchn.com).
- Assigned 7 tags: `#Whiskey`, `#Vermouth`, `#Lemon`, `#Citrusy`, `#Tart`, `#Shaken`, `#Classic`.
- **Similarity engine**: Linked **Other Similar Cocktails**: **Whiskey Sour** (fused 0.41).
- **Mutual back-links**: Added **Scofflaw** to the similarity list of **Whiskey Sour**.
- Archived original as `raw/archive/scofflaw.md`.
- Updated `index.md`, `tags.md`, and VitePress sidebar via `wiki.py compile`.

## 2026-06-14 — Ingest

- Ingested **Manhattan** from `raw/inbox/Untitled.md`.
- Completed Background and Profile from the web (Source: Difford's Guide).
- Assigned 7 tags: `#Whiskey`, `#Vermouth`, `#Angostura`, `#Boozy`, `#Complex`, `#Stirred`, `#Classic`.
- **Similarity engine**: Linked **Other Similar Cocktails**: **Shamrock Cocktail** (fused 0.37).
- **Mutual back-links**: Added **Manhattan** to the similarity list of **Shamrock Cocktail**.
- Archived original as `raw/archive/manhattan.md`.
- Updated `index.md`, `tags.md`, and VitePress sidebar via `wiki.py compile`.

## 2026-06-14 — Ingest

- Ingested **Daiquiri (Frozen strawberry)** from `raw/inbox/Untitled.md`.
- Completed Background and Profile from the web (Source: copenhagendistillery.com).
- Assigned 7 tags: `#Rum`, `#Lime`, `#Strawberry`, `#Refreshing`, `#Fruity`, `#Blended`, `#Sour`.
- **Vocabulary update**: Added `Strawberry` to **Ingredient** in `scripts/wiki.py`.
- **Similarity engine**: Extended `ALIASES` in `scripts/similarity.py` to include **strawberry**.
- **Mutual back-links**: Added **Daiquiri (Frozen strawberry)** to the similarity lists of **Daiquiri**, **Mojito**, and **Queen's Park Swizzle**.
- Archived original as `raw/archive/daiquiri-frozen-strawberry.md`.
- Updated `index.md`, `tags.md`, and VitePress sidebar via `wiki.py compile`.

## 2026-06-13 — Ingest

- Ingested **Penicillin**, **B-52**, and **Rum Flip** from `raw/inbox/`.
- Completed Background and flavor profile from the web for all three.
- **Penicillin**: Created by Sam Ross in 2005. Assigned 7 tags: `#Whiskey`, `#Lemon`, `#Ginger`, `#Honey`, `#Smoky`, `#Spicy`, `#ModernClassic`. Linked **Other Similar Cocktails**: **Whiskey Sour** (fused 0.436).
- **B-52**: Invented by Peter Fich in 1977. Assigned 7 tags: `#Liqueur`, `#Coffee`, `#Orange`, `#Creamy`, `#Layered`, `#Shot`, `#Classic`. Linked **Other Similar Cocktails**: **TBD** (no strong matches).
- **Rum Flip**: Historic cocktail from the late 1600s. Assigned 7 tags: `#Rum`, `#Egg`, `#Nutmeg`, `#DryShake`, `#Flip`, `#Coupe`, `#Classic`. Linked **Other Similar Cocktails**: **TBD** (no existing cocktails met the 0.38 fused threshold; closest was **Daiquiri** at 0.35).
- **Vocabulary update**: Added `Honey` and `Nutmeg` to **Ingredient**, and `Spicy` to **Flavor / Profile** in `scripts/wiki.py`.
- Archived originals as `raw/archive/penicillin.md`, `raw/archive/b-52.md`, and `raw/archive/rum-flip.md`.
- Updated `index.md`, `tags.md`, and VitePress sidebar via `wiki.py compile`.
- **Mutual back-links**: Added **Penicillin** to the **Whiskey Sour** similarity list.

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
