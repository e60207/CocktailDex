# similarity-scoring

## Purpose
Provide a deterministic, Python-stdlib-only tool (`scripts/similarity.py`) that scores cocktail-card similarity by fusing the CLAUDE.md §7 discrete rubric, ingredient Jaccard overlap, and TF-IDF text cosine, with all similarity-specific knowledge committed as reviewed constants and CLI modes for reporting and machine consumption.

## Requirements

### Requirement: Deterministic three-layer fused similarity
The system SHALL provide `scripts/similarity.py`, a Python-stdlib-only tool that computes a
pairwise similarity score for every pair of cards in `wiki/` by fusing three signals:
the CLAUDE.md §7 discrete rubric re-derived deterministically (base spirit from frontmatter,
family/flavor/technique from tags, souring/sweetener roles from regex detection over
ingredient lines), Jaccard overlap of canonicalised ingredient tokens, and TF-IDF cosine
over the card's free text (Background, Profile, Instruction, Garnish, Glassware). The fused
score MUST be `0.45·(rubric/10) + 0.35·ingredient_jaccard + 0.20·text_cosine`, with weights
defined as named constants at the top of the file. Identical `wiki/` content MUST always
produce identical scores.

#### Scenario: Same input, same output
- **WHEN** `python scripts/similarity.py json` is run twice with no changes to `wiki/`
- **THEN** the two outputs are byte-identical

#### Scenario: Rubric derives sour/sweet from ingredient lines, not judgment
- **WHEN** two cards both list lime juice among their ingredients but neither carries a lime tag
- **THEN** the rubric layer still awards the shared-souring-agent point for that pair

### Requirement: Human-only fields and existing links are excluded from scoring
Scoring inputs SHALL exclude the Eric and Charlene rating blocks, Modified Variation, and
the existing `Other Similar Cocktails` line, so prior links cannot feed back into scores.

#### Scenario: Editing a similar-links line does not change scores
- **WHEN** a card's `Other Similar Cocktails` line is edited and the tool is re-run
- **THEN** every pair's fused score is unchanged

### Requirement: Tag-dimension knowledge is imported from wiki.py
`similarity.py` SHALL derive its flavor, technique, and family tag sets from `VOCABULARY`
imported from `scripts/wiki.py`, and MUST NOT define duplicate tag-dimension sets.
`wiki.py` SHALL remain self-contained (the dependency is one-way, similarity → wiki).

#### Scenario: New vocabulary tag is visible to scoring without touching similarity.py
- **WHEN** a new flavor tag is added to `VOCABULARY` in `scripts/wiki.py` and two cards carry it
- **THEN** `similarity.py` counts it as a shared flavor tag in the rubric layer with no change to `similarity.py`

### Requirement: Similarity-specific knowledge is committed data
The system SHALL keep all similarity-specific knowledge as named, version-controlled
top-of-file constants in `scripts/similarity.py` — ingredient canonicalisation (`ALIASES`,
ordered first-match-wins), souring/sweetener role detection (`SOUR_RE`, `SWEET_RE`), fusion
weights, and thresholds — so extension is a deliberate reviewed edit rather than runtime
inference.

#### Scenario: Brand and preparation noise canonicalises away
- **WHEN** one card lists "Gosling's Black Seal rum" and another lists "gold rum"
- **THEN** both canonicalise to the same token and count as a shared ingredient

### Requirement: CLI modes for reporting and machine consumption
The tool SHALL provide: `report` (per-card top-k neighbors with full per-layer breakdown,
rubric explanations, and shared ingredients; default `--top 4 --threshold 0.38`, both
overridable; the default threshold is the owner-tunable `LINK_THRESHOLD` constant), `pairs` (all pairs sorted by fused score), `matrix` (Markdown matrix),
`json` (machine-readable per-pair output including rubric points and reasons, shared
ingredients, layer scores, and legacy §7 eligibility), and `test` (self-test, exit non-zero
on failure). The report MUST mark candidates at or above the fused threshold as recommended
and MUST still print the legacy discrete §7 score (threshold ≥ 5) for reference.

#### Scenario: Report explains a recommendation
- **WHEN** `python scripts/similarity.py report` is run and a pair scores at or above the threshold
- **THEN** the pair is marked as a link candidate and its rubric reasons and shared ingredients are printed

#### Scenario: Self-test gates regressions
- **WHEN** `python scripts/similarity.py test` is run
- **THEN** it exercises canonicalisation, qty-stripping, rubric scoring, Jaccard, TF-IDF cosine, and the VOCABULARY import, and exits non-zero if any check fails
