# Design: add-content-aware-similarity

## Context

CLAUDE.md §7's similarity rubric is executed by the LLM at ingest time. An audit of the
8 existing cards (see `reference/CocktailDex — Content-Aware Similarity.md`) showed the
results are non-reproducible and already wrong in places: a "shared Rum base" rationale on
a Vodka-based drink (`daiquiri.md` ↔ LIIT), a missed link that §7's own rules require
(Espresso Martini ↔ LIIT, 6/10), and strong ingredient-level similarity invisible to tags
(Mojito ↔ Queen's Park Swizzle, ingredient Jaccard 0.67). A reference implementation
(`reference/Similarity .py`) exists and works, but duplicates tag-dimension knowledge that
canonically lives in `wiki.py` VOCABULARY, and its "extend ALIASES when you notice long raw
slugs" guidance is a human-noticing pattern, not a machine check.

The repo already resolves the determinism↔flexibility tension once, in `wiki.py`: the
algorithm is stable, knowledge is data (`VOCABULARY`), and extension is a deliberate,
version-controlled act. This design applies the same pattern to similarity and adds the
missing detection loop.

## Goals / Non-Goals

**Goals:**

- Same `wiki/` content → same scores, always (CI-able, diff-able, regression-testable).
- Every foreseeable "new similarity element" in a future card has (a) a detection signal
  and (b) a documented extension point — no silent degradation.
- One source of truth per piece of knowledge: tag dimensions live in `wiki.py` only.
- The LLM keeps exactly the judgment §7 assigns it: candidate selection, why-notes,
  mutual-link upkeep, deliberate knowledge extension. It never re-derives scores by hand.

**Non-Goals:**

- Embeddings/ML for the text layer (documented as the upgrade path; not built now).
- Automatic editing of cards by the script (it reports; LLM/owner writes).
- Any change to CI, the VitePress build, or generated site artifacts beyond a recompile.
- Touching human-only fields or `raw/archive/`.

## Decisions

### D1 — Tag-dimension knowledge: import from `wiki.py`, never duplicate

`similarity.py` does `from wiki import VOCABULARY` (same directory) and derives its
flavor/technique/family sets from it. `wiki.py` stays self-contained (its "no local
imports" rule constrains what *it* imports, not who imports it); the dependency is one-way,
`similarity → wiki`.

- **Alternative — keep duplicated sets (reference implementation as-is):** rejected. The
  moment the owner adds a tag to VOCABULARY per CLAUDE.md §4, lint passes but the rubric
  layer silently ignores the new tag in scoring. This is precisely the silent-drift failure
  the change exists to eliminate.
- **Alternative — extract shared knowledge to a third file (knowledge.py / JSON):** rejected
  for now. It relocates VOCABULARY away from where CLAUDE.md, tags.md, and the owner's habits
  say it lives, for no benefit at this scale. Revisit only if a third consumer appears.
- **Alternative — duplicate + sync-check that parses wiki.py source:** rejected; a check
  guarding a duplication that need not exist.

### D2 — Gap detection is a script command, not an LLM habit

New `python scripts/similarity.py gaps` (also folded into the lint workflow in CLAUDE.md §8)
reports, deterministically:

1. **Uncanonicalised ingredient tokens** — tokens that fell through `ALIASES`. Nuance: a
   fallthrough is not inherently wrong (two cards both writing `passion fruit syrup` still
   match — same slug). The real failure is *variant splitting* (`passionfruit-puree` vs
   `passion-fruit-syrup` → different slugs → missed similarity). So the report clusters
   fallthrough tokens by word overlap and flags multi-member clusters as "likely same
   ingredient — extend ALIASES".
2. **Sour/sweet double-misses** — cards with a non-empty ingredient list where neither
   `SOUR_RE` nor `SWEET_RE` matched anything. Info-level prompt to review whether a new
   agent (verjus, orgeat-like) needs adding; some drinks legitimately have neither.
3. **Link drift** — see D3.

- **Alternative — wire gap checks directly into `wiki.py lint`:** rejected; it would break
  wiki.py's self-containment (it would need similarity knowledge). Instead CLAUDE.md's Lint
  operation runs both: `python scripts/wiki.py lint && python scripts/similarity.py gaps`.

### D3 — Link drift uses hysteresis, and checks written links against current scores

`gaps` compares each card's written `Other Similar Cocktails` entries against current
computed scores:

- **Link threshold:** fused ≥ `LINK_THRESHOLD` to *recommend*. Validated against the live
  8-card distribution at **0.38** (a natural gap separates the meaningful cluster ≥0.383
  from the weak tail ≤0.306) per owner direction; owner-tunable as the collection grows.
- **Removal warning threshold:** fused < `REMOVE_THRESHOLD` (**0.33**). Links in the
  0.33–0.38 band are left alone.

Rationale: the TF-IDF layer's idf shifts as the collection grows, so old pairs' fused
scores legitimately float (bounded by the 0.20 text weight). A single threshold would make
border-line links flap in and out on every ingest; the 0.05 hysteresis band absorbs the
drift while still catching genuinely stale links (e.g. the Daiquiri↔LIIT error at fused 0.18
sits far below any band). Also reported: *missing* links — pairs scoring ≥ `LINK_THRESHOLD`
where neither card links the other, and one-way links (already an error in wiki.py lint;
reported here with scores for context).

> **Threshold note (resolved during implementation):** the reference design started at
> 0.45/0.40, but the audited Espresso Martini↔LIIT pair the proposal cites as a "missed link"
> scores fused **0.399** — below 0.45. Per owner direction ("if the owner determines a Martini
> and a Long Island Iced Tea should be classified as similar, the threshold must be lowered"),
> the link/removal constants were set to **0.38 / 0.33** to capture that pair (and the
> structurally-strong swizzle pair Bermuda↔QPS at 0.383), validated against the actual score
> distribution. The constants remain owner-tunable.

- **Alternative — single threshold, no hysteresis:** rejected; churn on every ingest
  erodes trust in the report and invites needless card edits.
- **Alternative — corpus-independent eligibility (rubric+ingredient layers only):**
  rejected; it would let the authoritative fused score and the lint check disagree.

### D4 — Tiered extension paths, documented in CLAUDE.md

"New similarity element" is not one thing. Each tier gets a detection mechanism and an
extension point; the first three are data-only (determinism preserved — knowledge is
committed, same commit → same scores):

| Tier | Extension point | Detected by | Cost |
|---|---|---|---|
| New ingredient spelling/variant | `ALIASES` in similarity.py | `gaps` (fallthrough clusters) | one regex line |
| New sour/sweet agent | `SOUR_RE` / `SWEET_RE` | `gaps` (double-miss report) | one token |
| New tag | `VOCABULARY` in wiki.py | wiki.py lint (already) | one word; auto-visible via D1 |
| New signal layer | new pure function + weight | human decision | code, rare |
| Collection-scale shift | `W_*` / thresholds; TF-IDF → embeddings (layer 3 swap only) | human decision | code, rare |

Layer interface for the rare tiers: each layer is a pure function
`(cardA, cardB, corpus) → score in [0,1] + explanation`, fused by the weighted sum at the
top of the file. Adding a signal = one function + one weight; layers 1–2 never change when
layer 3 is upgraded.

### D5 — Card link-annotation format: one consistent fused-based format, migrated once

Existing cards carry `(Score N: free text)` annotations from hand-scoring. With drift
checking live, mixed formats would be perpetually flagged, so all similar-links lines are
rewritten once at integration to a single format derived from the report's breakdown, e.g.:

`[Mojito](./mojito.md) (fused 0.51 — same Rum base; shared lime, sugar)`

The "why" text remains LLM-written judgment, grounded in the script's `rubric:` /
`shared ingredients:` output. The legacy §7 discrete score stays available in the report
(`☑️ §7`) for reference/tie-breaking, but the fused score is authoritative.

- **Alternative — keep legacy `(Score N)` format:** rejected; it encodes the
  hand-derived numbers this change retires, and several are provably wrong.

## Risks / Trade-offs

- [Fused scores change as the corpus grows, so report output isn't stable across ingests]
  → By design (dynamic re-evaluation); hysteresis (D3) bounds the churn, and determinism is
  defined per-snapshot: same commit → same scores.
- [`from wiki import VOCABULARY` executes wiki.py module-level validation code on import]
  → That validation (duplicate-tag check) failing loudly at import is desirable; wiki.py has
  a `__main__` guard so no CLI side effects. Self-test covers the import.
- [ALIASES regex ordering is load-bearing (first match wins); a careless insertion can
  re-bucket existing ingredients] → Self-test pins canonical mappings for every alias class;
  `json` output diffs cleanly in review.
- [Hysteresis band (REMOVE_THRESHOLD–LINK_THRESHOLD, currently 0.33–0.38) could let a
  genuinely weakened link linger] → Acceptable at this scale; the band edges are named
  constants and the report still prints exact scores.
- [Two scripts must stay philosophically aligned (stdlib-only, deterministic)] → Stated in
  both docstrings; no third-party imports is checkable at review.
- [Rewriting 8 cards' similar-links lines touches owner-visible content] → Mechanical,
  reviewed in one commit; human-only fields untouched; `raw/archive/` untouched; rollback =
  revert the commit (no deploy coupling — site rebuilds from committed content either way).

## Migration Plan

1. Land `scripts/similarity.py` (modified from reference: D1 import, D2/D3 `gaps`); run
   `python scripts/similarity.py test` (self-test extended to cover import, clustering,
   drift hysteresis).
2. Rewrite CLAUDE.md §7 and §1 table; update §8 lint flow and README.
3. Re-link cards from the new report (fix Daiquiri↔LIIT, add Espresso Martini↔LIIT,
   reformat all annotations per D5), keeping mutual links.
4. `python scripts/wiki.py compile && python scripts/wiki.py lint && python scripts/similarity.py gaps`
   all green.
5. **End-to-end trial run** before calling the change done: execute the Similarity and Lint
   operations exactly as the rewritten CLAUDE.md documents them (report → judgment → gaps),
   plus one scratch-copy exercise of the gap-extension loop; cross-check that CLAUDE.md
   (§1 / §7 / §8 / extension tiers) and README.md actually carry the updates. Docs-vs-tool
   mismatch found here is a defect to fix, not a note to file. Log the change and trial-run
   result in `log.md`.
6. Rollback: revert the commit(s). No data migration, no deploy steps, archive untouched.

## Open Questions

- None blocking. Weights stay at the reference values (0.45/0.35/0.20). Link/removal
  thresholds were set during implementation to 0.38/0.33 (down from the reference 0.45/0.40)
  to match the live distribution and the owner's "EM↔LIIT should be similar" call; they are
  owner-tunable constants — revisit after the collection grows past ~20 cards.
