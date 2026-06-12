# Tasks: add-content-aware-similarity

## 1. Similarity engine (scripts/similarity.py)

- [x] 1.1 Copy `reference/Similarity .py` to `scripts/similarity.py`; replace the duplicated
      `FLAVOR_TAGS` / `TECHNIQUE_TAGS` / `FAMILY_TAGS` sets with sets derived from
      `from wiki import VOCABULARY` (one-way dependency; wiki.py untouched)
- [x] 1.2 Run `python scripts/similarity.py test` and `report` against the 8 current cards;
      verify output matches the reference doc's audit findings (Daiquiri↔LIIT rubric 2/10,
      Espresso Martini↔LIIT 6/10, Mojito↔QPS ingredient Jaccard 0.67)
- [x] 1.3 Add self-test items for the VOCABULARY import (a tag added to VOCABULARY is seen
      by the rubric layer) and pin canonical mappings for every ALIASES class

## 2. Gap detection (`gaps` command)

- [x] 2.1 Implement fallthrough-ingredient collection (tokens where `canon_ingredient`
      returned the raw slug) with word-overlap clustering; multi-member clusters = WARN,
      singletons = INFO
- [x] 2.2 Implement sour/sweet double-miss report (cards with ingredients but no SOUR_RE
      and no SWEET_RE hit) at INFO level
- [x] 2.3 Implement link-drift check: parse each card's `Other Similar Cocktails` targets;
      WARN on written links with fused < REMOVE_THRESHOLD (named constant), no flag
      in the REMOVE..LINK hysteresis band, WARN on unlinked pairs with fused ≥ LINK_THRESHOLD;
      exit non-zero iff any WARN
- [x] 2.4 Add self-test items: variant clustering, hysteresis band (band-midpoint not flagged),
      stale-link and missing-link detection
- [x] 2.5 Run `gaps` on the current wiki; confirm it flags the Daiquiri↔LIIT stale link
      (confirmed: fused 0.184 < 0.33, both directions). Note: per owner direction the link
      threshold was lowered to 0.38 so Espresso Martini↔LIIT (fused 0.399) is now a
      recommended `✅` candidate to add, rather than a sub-threshold "missing link"

## 3. Documentation (CLAUDE.md, README)

- [x] 3.1 Rewrite CLAUDE.md §7 per the proposal: script computes (report command), LLM
      selects top 2–4 from `✅` candidates / writes why-notes / maintains mutual links /
      writes TBD when none qualify; fused authoritative, legacy §7 score reference-only;
      document the D5 annotation format
- [x] 3.2 Add a **Similarity** row to the CLAUDE.md §1 operations table (trigger: "相似度 /
      similar / 重算連結" → `python scripts/similarity.py report`)
- [x] 3.3 Update CLAUDE.md §8 Lint operation to run both `python scripts/wiki.py lint` and
      `python scripts/similarity.py gaps`
- [x] 3.4 Document the tiered extension paths table (ALIASES / SOUR_RE+SWEET_RE /
      VOCABULARY / new layer / retuning) with their detection signals, in CLAUDE.md §7 or a
      new subsection
- [x] 3.5 Mention the similarity tool in README.md alongside wiki.py

## 4. Card re-linking (from the new report)

- [x] 4.1 Run `python scripts/similarity.py report` and record the recommended links per card
- [x] 4.2 Fix audited errors: remove/rewrite the Daiquiri↔LIIT "shared Rum base" rationale
      (link removed — fused 0.18); added the Espresso Martini↔LIIT mutual link (fused 0.40,
      recommended after the owner-directed threshold to 0.38)
- [x] 4.3 Rewrite all 8 cards' `Other Similar Cocktails` lines to the D5 format
      (`fused 0.NN — reason`), top 2–4 recommended candidates each, mutual links intact,
      TBD where nothing qualifies (Sangria, The Salty Shaker); ratings / Modified Variation /
      archive untouched
- [x] 4.4 Update each card's frontmatter `updated:` date

## 5. Script verification

- [x] 5.1 `python scripts/similarity.py test` — all self-tests pass
- [x] 5.2 `python scripts/wiki.py compile` — regenerate index.md / tags.md / sidebar JSON
- [x] 5.3 `python scripts/wiki.py lint && python scripts/similarity.py gaps` — both exit 0
      (no stale links, no missing strong links, mutual links intact)

## 6. End-to-end trial run (試run) & docs cross-check

- [x] 6.1 Trial run the **Similarity** operation as documented: follow the rewritten
      CLAUDE.md §7 steps verbatim (run `report` → read `✅` candidates and rubric/shared-
      ingredient breakdowns → confirm the written card links match what the docs say to
      select) — written links match the report's `✅` candidates exactly (mutual)
- [x] 6.2 Trial run the **Lint** operation as documented in updated §8 (`wiki.py lint` +
      `similarity.py gaps` together) — combined chain exits 0, output clean on final state
- [x] 6.3 Trial run the gap-extension loop once: temporarily introduce a fake uncovered
      ingredient variant in a scratch copy (not a committed card), confirm `gaps` clusters
      and flags it as the docs describe, then discard the scratch — confirmed: passion-fruit-
      syrup + passionfruit-puree clustered → WARN, exit 1; after discard back to clean exit 0
- [x] 6.4 Cross-check CLAUDE.md updates landed: §1 has the Similarity row, §7 references
      `scripts/similarity.py report` (no hand-scoring rubric remains), §8 includes the gaps
      step, extension-tier table present
- [x] 6.5 Cross-check README.md mentions the similarity tool alongside wiki.py with the
      correct commands

## 7. Bookkeeping

- [x] 7.1 Append the change entry to `log.md` (`## 2026-06-12 — Similarity engine`) noting
      the corrected links, the new workflow, and the trial-run result
- [x] 7.2 Remove or archive the now-integrated `reference/` files (owner's call — confirm
      before deleting) — owner chose **delete**; `reference/` removed
