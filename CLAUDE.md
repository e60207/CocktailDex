# CLAUDE.md — CocktailDex (Schema & Operating Manual)

**CocktailDex** is a **persistent, compounding cocktail knowledge base**, built on Andrej
Karpathy's *LLM Wiki* pattern (raw sources → LLM-maintained wiki → schema doc) and
adapted for a personal cocktail collection.

**You (the LLM) are the maintainer.** A human (the owner) curates and directs; you
ingest new cocktails, complete missing data, assign tags, link similar drinks, and keep
the navigation files (`index.md`, `tags.md`, `log.md`) consistent. This file is the
single source of truth for *how* to do that. Read it fully before any operation.

> Core principle (Karpathy): *"The wiki is a persistent, compounding artifact."*
> Knowledge accumulates here. We do **not** re-derive everything per question.

---

## 1. Quick start — the three operations

| Op | Trigger phrase (examples) | What you do |
|----|---------------------------|-------------|
| **Ingest** | "ingest", "process my new cocktails", "I dropped some drinks in" | Process every file in `raw/inbox/` → enriched cards in `wiki/`, update indexes (hiding rating denominators), archive originals |
| **Query** | "what should I make with…", "show me all Tiki drinks", "which did Eric rate 5?" | Read `index.md` (check ratings as numbers) → narrow via `tags.md` + grep → open relevant `wiki/` cards → answer with citations |
| **Lint** | "lint", "health check", "is the wiki consistent?" | Run `python scripts/wiki.py lint` **and** `python scripts/similarity.py gaps` (§8), fix what they flag, report content issues |
| **Compile** | "compile", "rebuild the index", "resync tags" | Run `python scripts/wiki.py compile` — regenerate `index.md` + `tags.md` from the `wiki/` cards |
| **Similarity** | "相似度", "similar", "重算連結", "re-link", "recompute similar cocktails" | Run `python scripts/similarity.py report` → link the `✅` candidates per card (§7), keep links mutual |

If the owner just drops files and says nothing, assume **Ingest**.

> **Deterministic vs judgment.** `index.md` and `tags.md` are *generated* by
> `scripts/wiki.py compile`; lint is `scripts/wiki.py lint`; **similarity scores are computed
> by `scripts/similarity.py`** (never hand-derived — §7). Let the scripts do the deterministic
> work. You (the LLM) own the judgment: completing fields from the web, assigning tags, and
> *selecting + explaining* which of the script's recommended candidates to link.

---

## 2. Directory structure

```
CocktailDex/
├── CLAUDE.md            ← you are here (schema + workflows). Single source of truth for both agents.
├── GEMINI.md            ← Gemini CLI entry point. Thin shim that imports CLAUDE.md (don't duplicate rules here).
├── index.md             ← MASTER INDEX (GENERATED). Entry point. Read this first for any query.
├── tags.md              ← 7-dimension tag reverse index (GENERATED).
├── log.md               ← append-only, date-prefixed activity log
├── scripts/
│   ├── wiki.py          ← deterministic tooling: `compile` (rebuild index+tags) & `lint`.
│   │                       Holds the canonical tag VOCABULARY. (compile.py / lint.py = aliases.)
│   └── similarity.py    ← deterministic similarity engine: `report`/`pairs`/`matrix`/`json`/
│                           `gaps`/`test`. Imports VOCABULARY from wiki.py (one-way); holds the
│                           ALIASES / SOUR_RE / SWEET_RE / weight + threshold constants.
├── raw/
│   ├── inbox/           ← DROP ZONE. New cocktail docs land here = "pending / not yet processed"
│   └── archive/         ← FROZEN originals, moved here after ingest = "done". NEVER edit these.
├── wiki/                ← enriched, living cocktail cards (one per cocktail). You maintain these.
├── photos/             ← images referenced by cards as ../photos/<slug>.jpg
└── site/                ← VitePress + Node/Yarn toolchain (NOT content). Build runs from here.
    ├── package.json     ← Yarn project (vitepress deps + docs:build/dev/preview scripts).
    ├── yarn.lock  .yarnrc.yml  .yarn/  node_modules/
    └── .vitepress/      ← VitePress project root: config.mjs (srcDir:'..'), theme/,
                            sidebar.generated.json (GENERATED), dist/, cache/.
```

> **Why `site/`?** VitePress needs its `.vitepress/` config and `node_modules` co-located,
> but the wiki content stays at the repo root (D1). So the whole toolchain lives in `site/`
> with `srcDir: '..'` pointing back at the root content; a git-ignored `node_modules` symlink
> at the repo root lets the root content resolve its imports. Run builds with `cd site && yarn …`.

**The inbox/archive split is the state machine.** You never need a separate "processed"
list: anything in `raw/inbox/` is pending; anything in `raw/archive/` is done. After you
finish ingesting a file, *move* it (don't copy, don't edit) from `inbox/` to `archive/`.

---

## 3. The cocktail card schema

Every card in `wiki/` follows this exact structure. Raw drops in `inbox/` may be sparse
or messy — your job is to normalise them into this shape.

### 3a. Frontmatter (wiki cards only — machine-readable header)

```yaml
---
name: Queen's Park Swizzle
slug: queens-park-swizzle
base: Rum
tags: [Rum, Mint, Lime, Swizzle, Tiki, Refreshing, Spiced]
glassware: Collins
ingested: 2026-06-08
updated: 2026-06-08
source: raw/archive/queens-park-swizzle.md
---
```

Frontmatter exists so index/tag/lint operations are deterministic (parse, don't guess).
Raw cards in `archive/` do **not** get frontmatter — they mirror what the owner dropped.

### 3b. Body (human-readable — mirrors the owner's template)

```markdown
# {Name}

**Background:** {2–4 sentences of history/origin. If completed from the web, end with a
source link: (source: https://…). Never invent history.}

![{Name}](../photos/{slug}.jpg)

- **Glassware:** {glass type}
- **Ingredients:**
  - {qty} {ingredient}
  - {qty} {ingredient}
- **Instruction:** {method}
- **Garnish:** {garnish}
- **Profile:** {flavour summary}
- **Tags:** #{Tag1} #{Tag2} #{Tag3}   ← 3–7 tags, drawn from the 6 dimensions (§4)

**Eric — Rating:** _ / 5  (increments of 0.5)
> N/A

**Charlene — Rating:** _ / 5  (increments of 0.5)
> N/A

**Modified Variation:** N/A

**!!Tips:** N/A

**Other Similar Cocktails:** [Name](./other-slug.md), [Name](./other-slug.md)
```

**Field completion authority** (who may fill each field):

| Field                   | You may complete? | Notes                                                   |
| ----------------------- | :---------------: | ------------------------------------------------------- |
| Name                    |         —         | from the source                                         |
| Theme/era               |         —         | ingest-only hint (raw/inbox only); used for tags        |
| Background              |       ✅ web       | cite a source; 2–4 sentences                            |
| Photo                   |         —         | owner adds the image file; you only write the link path |
| Glassware               |         ✅         |                                                         |
| Ingredients             |         ✅         | normalise to `qty + ingredient`, one per line           |
| Instruction             |         ✅         |                                                         |
| Garnish                 |         ✅         |                                                         |
| Profile                 |         ✅         |                                                         |
| Tags                    |         ✅         | assign 3–7 from controlled vocabulary (§4)              |
| **Eric — Rating**       | ❌ **HUMAN ONLY**  | carry over verbatim; never write/guess/change           |
| **Charlene — Rating**   | ❌ **HUMAN ONLY**  | carry over verbatim; never write/guess/change           |
| **Modified Variation**  | ❌ **HUMAN ONLY**  | carry over verbatim                                     |
| **!!Tips**              | ❌ **HUMAN ONLY**  | carry over verbatim                                     |
| Other Similar Cocktails |         ✅         | auto-linked via §7                                      |

> Note: this field was called **Theme** in the owner's original template. It is renamed
> **Tags** here because it now spans 7 dimensions, not just style/theme.

---

## 4. Tag system — 7 dimensions

The owner selected the **Standard 7** scheme. Every cocktail carries **3–7 tags total**,
chosen as the most *salient* across these seven dimensions (not one-per-dimension; pick what
actually defines the drink). The canonical vocabulary lives in `scripts/wiki.py` (the
`VOCABULARY` table); `tags.md` is its generated reverse index. If a genuinely new tag is
needed, **add it to `VOCABULARY` in `scripts/wiki.py`, then recompile** (§5). Tag tokens are
flat — a name belongs to exactly one dimension (the script enforces this).

| #   | Dimension            | What it captures                | Example tags                                                     |
| --- | -------------------- | ------------------------------- | ---------------------------------------------------------------- |
| 1   | **Base Spirit**      | the dominant spirit             | `#Gin` `#Vodka` `#Rum` `#Whiskey` `#Tequila` `#Brandy`           |
| 2   | **Ingredient**       | distinctive non-base components | `#Lime` `#Mint` `#Campari` `#Falernum` `#Angostura`              |
| 3   | **Flavor / Profile** | the taste experience            | `#Refreshing` `#Citrusy` `#Spiced` `#Bitter` `#Boozy` `#Complex` |
| 4   | **Technique**        | how it's made                   | `#Shaken` `#Stirred` `#Built` `#Muddled` `#Swizzle` `#Blended`   |
| 5   | **Family / Style**   | the cocktail family             | `#Sour` `#Highball` `#Tiki` `#OldFashioned` `#Fizz` `#Punch`     |
| 6   | **Glassware**        | serving vessel                  | `#Coupe` `#Collins` `#Rocks` `#NickAndNora` `#TikiMug`           |
| 7   | **Theme / Era**      | cocktail era or special theme   | `#Classic` `#ModernClassic` `#Contemporary` `#Original` `#Halloween` |

**Tag rules:**
- 3–7 per cocktail. Fewer than 3 = under-described; more than 7 = noise.
- Tags are `#PascalCase` hashtags in the card body (grep-friendly) **and** listed in
  frontmatter `tags: [...]` (without the `#`).
- One Base Spirit tag is mandatory. Beyond that, pick the most distinguishing tags.
- Keep names consistent with `tags.md`. `#WhiteRum` and `#white-rum` must not coexist.

---

## 5. Operation: INGEST

Trigger: files present in `raw/inbox/`, or the owner says "ingest".

1. **List** `raw/inbox/`. If empty, say so and stop. Each file may hold **one card** (`#`
   title) or **many cards** separated by `---` (`##` titles). Handle all.
2. For **each cocktail** in each file:
   1. **Parse** into the schema fields (§3b). Derive `slug` = kebab-case of Name
      (e.g. `Queen's Park Swizzle` → `queens-park-swizzle`). Note: raw files may
      include a `**Theme/era:**` line; this is an **ingest-only hint** to help you
      assign the 7th tag dimension (§4) and should **not** be carried over to the
      `wiki/` card body.
   2. **Complete missing fields** (Background, Glassware, Ingredients, Instruction,
      Garnish, Profile) from the web or reliable knowledge. For Background and any
      historical claim, cite a source URL in the card. Normalise Ingredients to
      `qty + ingredient`, one per line. **Never touch the three human-only fields** — copy
      Rating/Modified Variation across verbatim. If a rating or its comment blockquote
      is blank or contains a placeholder, use `_ / 5` and `> N/A` respectively.
   3. **Assign 3–7 tags** (§4). Use the `Theme/era` hint if provided; if the hint is
      missing, contains "TBD" (even if other text is present), or is otherwise
      inconclusive, search online to determine the correct era/theme tag.
      **Special rule for `#Original`:** only assign this if the user explicitly
      specified it in the hint, and you have verified online that it is not a known
      classic/existing cocktail. Add tags to the `**Tags:**` line and to frontmatter.
   4. **Link similar cocktails** (§7): run `python scripts/similarity.py report`, link the
      `✅` candidates (top 2–4, or TBD if none qualify), and add **mutual back-links** to
      those other cards. If `similarity.py gaps` flags an un-canonicalised ingredient, extend
      `ALIASES` (§7 tier table) and re-run before linking.
   5. **Write** the enriched card to `wiki/<slug>.md` with frontmatter (§3a).
   6. **Move** the original file from `raw/inbox/` to `raw/archive/` (unchanged). If a
      multi-cocktail file, move the whole file once after all its cards are processed.
3. **Register new tags (if any):** if you introduced a brand-new tag, add it to the
   `VOCABULARY` in `scripts/wiki.py` under the correct dimension.
4. **Compile:** run `python scripts/wiki.py compile` to regenerate `index.md`, `tags.md`, and
   `site/.vitepress/sidebar.generated.json` from the cards (deterministic — never hand-edit
   these generated files). The sidebar JSON is the committed nav artifact the VitePress site imports;
   it must be recompiled whenever cards are added/renamed so the published site stays in sync.
5. **Append to `log.md`** — `## YYYY-MM-DD — Ingest` with the cocktails added and which
   fields you completed from the web.
6. **Lint & report:** run `python scripts/wiki.py lint`; then tell the owner what you added,
   which fields you filled from the web (with sources), and anything left as `TBD`.

---

## 6. Operation: QUERY

The wiki is your knowledge base; answer **from it**, not from scratch.

1. **Read `index.md` first** — it's the entry point and gives the whole collection's
   first-layer data (Glassware / Ingredients / Instruction / Profile / both ratings) at a
   glance.
2. **Narrow** with `tags.md` and grep before opening cards:
   - by spirit: `grep -ri "#Rum" wiki/`
   - by family: `grep -ri "#Tiki" wiki/`
   - by rating: `grep -ri "Eric.*5 / 5" wiki/`
   - by ingredient: `grep -ri "Campari" wiki/`
3. **Open only the relevant `wiki/` cards** for full detail.
4. **Answer with citations** — name the cards you used (e.g. *Daiquiri (wiki/daiquiri.md)*).
5. If the query produced a reusable synthesis (e.g. "best summer rum drinks", "everything
   that uses Falernum"), offer to save it as a curated list page under `wiki/` and note it
   in `log.md`. This is how the wiki compounds.

---

### 7. Similar-cocktail linking algorithm

The owner's card has an **Other Similar Cocktails** field. Similarity is computed
**deterministically** by `python scripts/similarity.py report` — **run it; never re-derive
scores by hand.** The script fuses three signals into one `fused` score:

```
fused = 0.45·(rubric/11) + 0.35·ingredient_jaccard + 0.20·text_cosine
```

- **Rubric (0.45)** — the legacy discrete §7 rubric, made deterministic: base spirit from
  frontmatter, family/flavor/technique/era from tags, souring/sweetener re-derived from the
  **ingredient lines** via `SOUR_RE`/`SWEET_RE` (not LLM judgment).
- **Ingredient (0.35)** — Jaccard over canonicalised ingredient tokens (`ALIASES`), so
  material overlap that never made it into tags still counts (e.g. Mojito ↔ QPS share
  lime/mint/rum/sugar = 0.67 even though tags don't show it).
- **Text (0.20)** — TF-IDF cosine over Background + Profile + Instruction + Garnish +
  Glassware. Ratings, Modified Variation, and the existing `Other Similar Cocktails` line
  are **excluded** so prior links can't feed back into the score.

> **Script computes, you select & explain.** The numbers are the script's; the *judgment* is
> yours — which candidates to link, the short "why" note, and keeping links mutual.

#### Workflow (ingest or re-link)

1. After writing/updating a card, run `python scripts/similarity.py report`.
2. Link the candidates marked **`✅`** (fused ≥ the link threshold, currently **0.38**),
   **top 2–4** per card. If none qualify, write **TBD** — never force weak matches.
3. Write a brief "why" note grounded in the script's `rubric:` / `shared ingredients:`
   breakdown (don't invent reasons the script didn't surface).
4. **Mutual links:** when you link A → B, ensure B → A. Re-run the report after each ingest
   to refresh affected neighbors (dynamic re-evaluation).
5. If `python scripts/similarity.py gaps` flags an un-canonicalised ingredient or a
   sour/sweet miss, **extend the relevant knowledge table** (below) and re-run before linking.

The fused score is **authoritative**. The legacy discrete score (`☑️ §7`, threshold ≥ 5) is
still printed for reference/tie-breaking only.

#### Annotation format (D5 — one consistent format)

Every entry uses `[Name](./slug.md) (fused 0.NN — brief reason)`, e.g.:

`[Mojito](./mojito.md) (fused 0.51 — same Rum base; shared lime & sugar; both Refreshing)`

The legacy `(Score N: …)` hand-scored format is **retired** — never write it.

#### Thresholds (owner-tunable, named constants in `similarity.py`)

- **Link / recommend:** `LINK_THRESHOLD = 0.38` (the `✅` bar in `report`; also the bar at
  which `gaps` *requires* a mutual link to exist).
- **Stale (removal):** `REMOVE_THRESHOLD = 0.33`. Written links scoring below this are
  flagged stale by `gaps`; links in the **0.33–0.38 hysteresis band** are left alone (the
  TF-IDF idf shifts as the collection grows, so border-line links shouldn't flap every ingest).

These start from the live collection's score distribution (a natural gap separates the
meaningful cluster ≥ 0.38 from the weak tail) and are the **owner's to retune** as the
collection grows — change the constant + recompute, never hand-edit individual scores.

#### Tiered extension paths (when a future card carries a new similarity element)

"New similarity element" isn't one thing. Each tier has a detection signal and a single
deliberate extension point — the first three are data-only, so determinism is preserved
(same commit → same scores):

| Tier | Extension point | Detected by | Cost |
|------|-----------------|-------------|------|
| New ingredient spelling/variant | `ALIASES` in `similarity.py` | `gaps` — fallthrough clusters | one regex line |
| New souring / sweetening agent | `SOUR_RE` / `SWEET_RE` in `similarity.py` | `gaps` — sour/sweet double-miss | one token |
| New tag | `VOCABULARY` in `wiki.py` | `wiki.py lint` (already) | one word; **auto-visible** to scoring (similarity.py imports VOCABULARY) |
| New signal layer | new pure `(a, b, corpus) → [0,1]` function + weight | human decision | code, rare |
| Collection-scale shift | `W_*` weights / thresholds; TF-IDF → embeddings (swap layer 3 only) | human decision | code, rare |

Extend deliberately (like the tag VOCABULARY) — never invent a mapping at runtime.

---

## 8. Operation: LINT (consistency / health check)

**Run both `python scripts/wiki.py lint` and `python scripts/similarity.py gaps`** — together
they deterministically check the items below and each exits non-zero on a problem (keep
`wiki.py` free of similarity knowledge; the two stay decoupled). Then auto-fix mechanical
issues, but **ask before changing content** (recipes, backgrounds, tags you're unsure about).
After fixing tags or links, run `python scripts/wiki.py compile` to resync `index.md` /
`tags.md`.

`wiki.py lint` checks:

- **Tag count:** any card with <3 or >7 tags → flag.
- **Orphan tags:** a `#Tag` in a card that's missing from `tags.md`, or a tag in `tags.md`
  with no cocktails → reconcile.
- **Vocabulary drift:** near-duplicate tags (`#WhiteRum` vs `#white-rum`) → merge to canon.
- **Broken links:** `Other Similar Cocktails` or photo paths that don't resolve → fix or flag.
- **Non-mutual similar links:** A→B without B→A → add the back-link.
- **Index ↔ card mismatch:** a `wiki/` card with no `index.md` row, or index data that
  disagrees with the card → resync from the card (card is source of truth for recipe;
  ratings are owner-authoritative).
- **Pending inbox:** files still in `raw/inbox/` → remind the owner / offer to ingest.
- **Frontmatter ↔ body:** `tags:` in frontmatter must equal the `**Tags:**` line.
- **Human fields (info only, not errors):** cards with blank ratings — list them so the
  owner knows what still needs tasting notes. Never fill them yourself.

`similarity.py gaps` checks (machine-checkable coverage + drift; WARN sets exit 1):

- **Uncanonicalised ingredients:** tokens that fell through `ALIASES`, clustered by word
  overlap. A multi-member cluster (likely the same thing spelled two ways) → WARN: add an
  `ALIASES` entry (§7 tier table) and re-run. A lone fallthrough → INFO only (it still
  matches itself across cards).
- **Sour/sweet double-miss:** a card with ingredients but no `SOUR_RE`/`SWEET_RE` hit → INFO:
  review whether a new agent (verjus, orgeat…) needs adding to the detection patterns.
- **Link drift:** written `Other Similar Cocktails` entries vs current fused scores — stale
  links (fused < `REMOVE_THRESHOLD`) and missing strong links (fused ≥ `LINK_THRESHOLD`,
  neither side links the other) → WARN; links in the hysteresis band are left alone (§7).

End a lint with a short report + the `log.md` entry `## YYYY-MM-DD — Lint`.

---

## 9. Hard rules (never violate)

1. **Ratings, Modified Variation & !!Tips are HUMAN-ONLY.** Never write, estimate, infer, or alter
   `Eric — Rating`, `Charlene — Rating`, `Modified Variation`, or `!!Tips`. Carry them across
   raw→wiki exactly as written; if a rating or its comment is blank/placeholder, use `_ / 5`
   and `N/A`. Ratings use **0.5 increments**; the index page hides the denominator (e.g.,
   "4.5" instead of "4.5 / 5"). Rating comments (the blockquote following the rating) are
   hidden on the website if they contain `N/A` or are empty.
2. **`raw/archive/` is immutable.** Once a file is archived, never edit it. To revise, the
   owner drops a corrected file in `raw/inbox/` and you re-ingest (overwrite the `wiki/` card).
3. **No fabricated facts.** Background and any historical/sourcing claim must be grounded in
   a citable source; include the URL. If you can't verify, write `TBD` — don't guess.
4. **Tag from the controlled vocabulary** in `tags.md`; extend it deliberately, never ad hoc.
5. **Keep navigation in sync.** Every ingest updates `index.md`, `tags.md`, and `log.md`.

---

## 10. Conventions

- **Filenames:** kebab-case slug of the Name. `Queen's Park Swizzle` → `queens-park-swizzle.md`.
  Strip apostrophes/accents; spaces → hyphens.
- **Dates:** ISO `YYYY-MM-DD`, everywhere.
- **Links:** standard Markdown. Card→card (same `wiki/` dir): `[Mojito](./mojito.md)`.
  Index/tags (root)→card: `[Mojito](./wiki/mojito.md)`. Card→photo: `../photos/<slug>.jpg`.
- **Tags in cards:** `#PascalCase` hashtags, kept identical to `tags.md`.
- **Measurements:** keep the owner's units (oz / dashes / count). Don't silently convert.
- **Tone:** the body is for a human reader; keep it clean and faithful to the template.
- **Generated files:** `index.md`, `tags.md`, and `site/.vitepress/sidebar.generated.json` are
  produced by `python scripts/wiki.py compile` from the `wiki/` cards — never hand-edit them;
  edit the cards (and `VOCABULARY` in `scripts/wiki.py` for new canonical tags), then recompile.
  The `site/.vitepress/sidebar.generated.json` artifact is committed and imported by the VitePress
  site config so navigation stays deterministic; CI builds consume it without running Python.
- **VitePress toolchain lives in `site/`:** the Node/Yarn project (`package.json`, `yarn.lock`,
  `.yarnrc.yml`, `.yarn/`, `node_modules/`) and the `.vitepress/` root all live under `site/`.
  Build commands run from there (`cd site && yarn docs:build`); `srcDir: '..'` points VitePress
  at the repo-root content. A git-ignored `node_modules` symlink at the repo root lets the
  root-level content resolve its `vue`/`vitepress` imports — recreated by CI before the build.

---

## 11. Grep cookbook (fast retrieval without reading every card)

```bash
grep -ril "#Tiki"           wiki/    # all Tiki drinks
grep -ril "#Rum"            wiki/    # all rum-based
grep -ri  "Eric.*4.5 / 5"     wiki/    # Eric's high-rated
grep -ri  "Campari"         wiki/    # anything using Campari
grep -ril "#Swizzle"        wiki/    # by technique
grep -L   "Eric.*[\d.] / 5" wiki/*.md # cards still missing Eric's rating
```

*Last updated: 2026-06-13. This file is the schema; keep it current if the workflow changes.*
