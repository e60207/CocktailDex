# similarity-gap-detection

## Purpose
Provide a deterministic `gaps` command in `scripts/similarity.py` that surfaces where the committed similarity knowledge tables fail to cover current `wiki/` content — uncanonicalised ingredient variants, sour/sweet double-misses, and link drift — and wire it into the CLAUDE.md Lint workflow as a gating check.

## Requirements

### Requirement: Gaps command surfaces uncovered knowledge deterministically
The system SHALL provide `python scripts/similarity.py gaps`, which deterministically
reports where the committed knowledge tables fail to cover the current `wiki/` content,
so extension is triggered by a machine check rather than ad-hoc noticing. The command
SHALL exit non-zero when it reports any warning-level finding, so it can gate the lint
workflow.

#### Scenario: Clean wiki yields a clean gaps run
- **WHEN** `python scripts/similarity.py gaps` runs and all ingredients canonicalise, no drift exists, and no double-misses exist
- **THEN** the command reports no findings and exits zero

### Requirement: Uncanonicalised ingredient variants are clustered and flagged
The gaps report SHALL list every ingredient token that fell through `ALIASES` (i.e.
canonicalised to its raw slug), grouped by word overlap into clusters. Clusters with two or
more distinct slugs SHALL be flagged at warning level as likely same-ingredient variants
needing an `ALIASES` entry; single-member fallthroughs SHALL be listed at info level only,
since a unique ingredient with no variants still matches itself across cards.

#### Scenario: Variant split is flagged
- **WHEN** one card's ingredients yield the fallthrough slug `passion-fruit-syrup` and another card's yield `passionfruit-puree`
- **THEN** the gaps report groups them into one cluster and flags it as a likely missing `ALIASES` entry

#### Scenario: Unique fallthrough is informational
- **WHEN** exactly one fallthrough slug exists with no word overlap with any other fallthrough
- **THEN** it is listed as info, not a warning, and does not affect the exit code

### Requirement: Sour/sweet double-misses are reported
The gaps report SHALL list, at info level, every card with a non-empty ingredient list
where neither `SOUR_RE` nor `SWEET_RE` matched any ingredient line, prompting review of
whether a new souring or sweetening agent needs to be added to the detection patterns.

#### Scenario: Card with undetected acid source is surfaced
- **WHEN** a card's only acid source is an ingredient not matched by `SOUR_RE` (e.g. verjus before it is added)
- **THEN** the card appears in the double-miss section of the gaps report

### Requirement: Link drift between written links and current scores is detected
The gaps report SHALL compare each card's written `Other Similar Cocktails` entries against
currently computed fused scores using hysteresis: a written link whose pair scores below
the removal threshold (`REMOVE_THRESHOLD`, currently 0.33) SHALL be flagged at warning level
as stale; written links scoring between the removal threshold and the link threshold
(`LINK_THRESHOLD`, currently 0.38) SHALL NOT be flagged. The report SHALL also flag, at
warning level, missing links — pairs scoring at or above the link threshold where neither
card links the other. Both thresholds SHALL be named, owner-tunable constants.

#### Scenario: Stale link is flagged
- **WHEN** a card links a cocktail whose current fused score with it is below the removal threshold
- **THEN** the gaps report flags that link as stale with both scores shown

#### Scenario: Hysteresis band suppresses churn
- **WHEN** a written link's pair currently scores within the removal–link band (e.g. 0.355)
- **THEN** the gaps report does not flag it

#### Scenario: Missing strong link is flagged
- **WHEN** two cards score at or above the link threshold and neither card's `Other Similar Cocktails` line links the other
- **THEN** the gaps report flags the pair as a missing link

### Requirement: Gap detection runs as part of the lint workflow
The CLAUDE.md Lint operation SHALL run both `python scripts/wiki.py lint` and
`python scripts/similarity.py gaps`, keeping `wiki.py` free of similarity knowledge
(no similarity imports in `wiki.py`).

#### Scenario: Lint workflow covers similarity gaps
- **WHEN** the documented Lint operation is performed
- **THEN** both commands are executed and their findings are reported together
