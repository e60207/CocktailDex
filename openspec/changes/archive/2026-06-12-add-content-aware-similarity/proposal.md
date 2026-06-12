# Proposal: add-content-aware-similarity

## Why

CLAUDE.md §7 has the LLM hand-score pairwise similarity from tags at ingest time, which is
non-reproducible and lossy (tags are a 3–7 token compression of each card). An audit of the
8 current cards found concrete failures: a wrong link rationale on `daiquiri.md` ("shared Rum
base" with Long Island Ice Tea, whose base is Vodka), a missed link (Espresso Martini ↔ LIIT
scores 6/10 under §7's own rules but is TBD), and tag-invisible strong similarity (Mojito ↔
Queen's Park Swizzle share 4 canonical ingredients). Scoring must become deterministic —
same `wiki/` content, same scores — while staying flexible enough that future cards carrying
new similarity elements (new ingredient spellings, new sour/sweet agents, new tags) extend
the system deliberately instead of silently falling through.

## What Changes

- Add `scripts/similarity.py`: a stdlib-only, deterministic similarity engine that fuses
  three signals — the §7 discrete rubric (re-derived from frontmatter + ingredient lines),
  canonicalised-ingredient Jaccard, and TF-IDF cosine over card free text
  (`fused = 0.45·rubric + 0.35·ingredient + 0.20·text`).
- **Single source of truth for tag dimensions**: `similarity.py` imports `VOCABULARY` from
  `wiki.py` instead of duplicating flavor/technique/family tag sets, so adding a tag to the
  vocabulary is automatically visible to scoring (no silent drift between the two scripts).
- Add **gap detection** (`similarity.py gaps`): machine-checkable reports of ingredient
  tokens not covered by `ALIASES` (clustered to surface likely same-thing variants), cards
  whose ingredient lines trigger neither sour nor sweet detection, and **link drift** —
  written `Other Similar Cocktails` entries that no longer meet the current score threshold
  (with hysteresis to avoid churn as the corpus grows).
- Rewrite CLAUDE.md §7: the script computes scores (never re-derived by hand); the LLM keeps
  the judgment — selecting top 2–4 from eligible candidates, writing the "why" note from the
  script's breakdown, maintaining mutual links, and extending knowledge tables when gaps
  surface. Add a **Similarity** row to the §1 operations table, update the §8 Lint operation
  to include the gaps check, and document the tiered extension paths
  (ALIASES / SOUR_RE / SWEET_RE / VOCABULARY / new layer). **Update README.md** to document
  the new tool alongside `wiki.py` — both docs updates are required deliverables of this
  change, not follow-ups.
- Fix the audited card errors and rewrite all existing `(Score N: …)` link annotations to a
  single consistent format based on the new report output.
- **Post-implementation trial run**: after all code, docs, and card edits land, perform an
  end-to-end dry run of the new workflow exactly as the rewritten CLAUDE.md documents it
  (report → judge candidates → gaps → lint), confirming the docs match actual tool behavior
  on the real collection before the change is considered done.

**Non-goals**

- No embedding/ML similarity — the text layer stays pure-Python TF-IDF; the documented
  upgrade path (swap layer 3 only) is design guidance, not part of this change.
- No change to human-only fields (ratings, Modified Variation) — they remain excluded from
  scoring inputs and untouched on cards.
- No CI/site changes — `similarity.py` is a maintainer-side tool; the Node-only build and
  generated site artifacts are unaffected.
- No automatic link writing — the script recommends; the LLM/owner still writes card edits.

## Capabilities

### New Capabilities

- `similarity-scoring`: deterministic three-layer pairwise similarity computation with CLI
  modes (report / pairs / matrix / json / test), tag-dimension knowledge sourced from
  `wiki.py` VOCABULARY, and similarity-specific knowledge tables (ALIASES, SOUR_RE/SWEET_RE,
  weights, thresholds) as committed data.
- `similarity-gap-detection`: machine-checkable coverage gaps (uncanonicalised ingredient
  variants, sour/sweet double-misses) and link-drift detection between written card links
  and current scores, runnable as part of the lint workflow.
- `similar-links-maintenance`: the workflow contract for `Other Similar Cocktails` lines —
  script-computed eligibility, LLM-selected top 2–4 with why-notes, mutual links, TBD when
  nothing qualifies, and correction of the known-bad existing links.

### Modified Capabilities

_None — existing specs (site/deployment/index/llms-txt) have no requirement changes._

## Impact

- **New code**: `scripts/similarity.py` (engine + knowledge tables + gaps + self-test).
- **Modified docs**: `CLAUDE.md` (§1 operations table, §7 rewrite, §8 lint mention,
  §10/§11 as needed), `README.md` (tooling mention), `log.md` (change entry).
- **Modified content**: `wiki/daiquiri.md`, `wiki/long-island-ice-tea.md`,
  `wiki/espresso-martini.md` plus any card whose similar-links line is reformatted or
  re-linked per the new report (all 8 cards likely touched).
- **Untouched**: `scripts/wiki.py` (it remains self-contained; `similarity.py` depends on it
  one-way), generated files (`index.md`, `tags.md`, sidebar JSON — recompiled, not
  hand-edited), `raw/archive/` (immutable), CI workflow.
