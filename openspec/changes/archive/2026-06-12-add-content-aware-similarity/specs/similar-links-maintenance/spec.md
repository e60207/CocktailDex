# similar-links-maintenance

## ADDED Requirements

### Requirement: Script computes, LLM selects and explains
CLAUDE.md §7 SHALL define the similar-cocktail workflow as: scores come exclusively from
`python scripts/similarity.py report` (never re-derived by hand); the LLM maintainer
selects the top 2–4 candidates marked as recommended (fused ≥ the owner-tunable `LINK_THRESHOLD`, currently 0.38) per card, writes a
brief why-note grounded in the report's rubric reasons and shared-ingredients breakdown,
and writes **TBD** when no candidate qualifies — weak matches MUST NOT be forced. The
fused score SHALL be authoritative; the legacy §7 discrete score remains reference and
tie-breaking input only.

#### Scenario: Ingest links from the report
- **WHEN** a new card is written to `wiki/` during ingest
- **THEN** the maintainer runs the similarity report and links only recommended candidates, top 2–4, or writes TBD if none qualify

#### Scenario: No hand-derived scores on cards
- **WHEN** a similar-links line is written or updated
- **THEN** any score it cites comes from the script's output for the current content

### Requirement: Mutual links and neighbor refresh
When a link A→B is written, B→A SHALL be written in the same operation, and the maintainer
SHALL re-run the similarity report after each ingest to refresh affected neighbors'
similar-links lines (dynamic re-evaluation), with the gaps drift check as the enforcement
backstop.

#### Scenario: New ingest refreshes neighbors
- **WHEN** a new card is ingested and the report shows it as a recommended candidate for an existing card
- **THEN** both the new card and the existing card link each other after the ingest completes

### Requirement: Consistent link annotation format
All `Other Similar Cocktails` entries SHALL use one consistent annotation format based on
the fused score and a brief LLM-written reason, e.g.
`[Mojito](./mojito.md) (fused 0.51 — same Rum base; shared lime, sugar)`. The legacy
hand-scored `(Score N: …)` format SHALL be retired; all existing cards' similar-links
lines SHALL be migrated to the new format in this change.

#### Scenario: Legacy annotations are migrated
- **WHEN** the change is implemented
- **THEN** no card's `Other Similar Cocktails` line contains a legacy `(Score N:` annotation

### Requirement: Audited link errors are corrected
The known-bad links found by the audit SHALL be corrected from the new report's output:
the Daiquiri ↔ Long Island Ice Tea rationale claiming a shared Rum base (LIIT's base is
Vodka) SHALL be removed or rewritten per the current scores, and the missing
Espresso Martini ↔ Long Island Ice Tea mutual link SHALL be added if the report recommends
it.

#### Scenario: Wrong-base rationale is gone
- **WHEN** the change is implemented
- **THEN** no card claims a shared Rum base between Daiquiri and Long Island Ice Tea

### Requirement: Tiered extension paths are documented
CLAUDE.md SHALL document the extension tiers for new similarity elements: new ingredient
variants → `ALIASES`; new sour/sweet agents → `SOUR_RE`/`SWEET_RE`; new tags →
`VOCABULARY` in `wiki.py` (automatically visible to scoring); new signal layers and
weight/threshold retuning → deliberate code changes. CLAUDE.md §1 SHALL gain a
**Similarity** operation row triggering `python scripts/similarity.py report`, and the
ingest workflow SHALL instruct extending the knowledge tables and re-running when the gaps
report flags coverage holes.

#### Scenario: Gap finding routes to the right extension point
- **WHEN** the gaps report flags an uncanonicalised ingredient variant cluster during ingest
- **THEN** the documented workflow directs the maintainer to add an `ALIASES` entry and re-run the report before linking
