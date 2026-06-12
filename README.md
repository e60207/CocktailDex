# How to Use & Maintain CocktailDex

A practical guide for **you, the owner**. It covers what to do, the exact steps, and the
prompts to copy-paste. (The assistant's internal rules and schema live in
[`CLAUDE.md`](./CLAUDE.md) — you rarely need to open it.)

> **Works with either AI agent.** This wiki is agent-agnostic: drive it with **Claude Code /
> Cowork** *or* **Gemini CLI**. Each tool auto-loads its own context file — Claude reads
> [`CLAUDE.md`](./CLAUDE.md), Gemini reads [`GEMINI.md`](./GEMINI.md) — but `GEMINI.md` just
> imports `CLAUDE.md`, so there is **one rulebook** and both agents behave the same. Every
> prompt below works verbatim in either tool.

---

## What this is

A personal cocktail knowledge base that gets smarter every time you add a drink. **You
curate and rate; the AI maintains.** When you add a cocktail, the assistant formats it,
fills in missing details from the web, tags it, links it to similar drinks you already own,
and keeps the navigation files in sync. It follows Andrej Karpathy's *LLM Wiki* pattern:
knowledge **accumulates** here instead of being re-derived from scratch each time you ask.

## The 30-second mental model

1. You drop cocktail notes into **`raw/inbox/`**.
2. You tell the AI to **"ingest"**.
3. The AI writes a clean, complete card to **`wiki/`**, moves your original into
   **`raw/archive/`** (frozen), and updates **`index.md`**, **`tags.md`**, **`log.md`**.
4. To find, compare, or decide what to make later, you just **ask** — the AI reads
   `index.md` first, then opens only the cards it needs.

> **Two fields are always yours alone.** The AI will never invent or overwrite the
> **Ratings** (Eric / Charlene) or the **Modified Variation**. It only records them when
> *you* dictate them.

## Folder map

| Path | What it's for |
|------|---------------|
| `raw/inbox/` | **Drop zone.** New cocktail files you haven't processed yet. |
| `raw/archive/` | Frozen originals, moved here after ingest. Never edited. |
| `wiki/` | The finished, living cocktail cards. |
| `index.md` | Master table — the AI's starting point and your at-a-glance view. |
| `tags.md` | 6-dimension tag index (tag → which cocktails). |
| `log.md` | Dated history of every ingest / lint. |
| `photos/` | Drink photos, named `<slug>.jpg`. |
| `CLAUDE.md` | The rulebook the AI follows — the single source of truth (Claude loads it automatically). |
| `GEMINI.md` | Gemini CLI's entry point. A thin shim that imports `CLAUDE.md`, so Gemini follows the same rulebook. |

## Getting started

Open this folder in whichever agent you prefer — the context file loads automatically, so the
assistant already knows the schema and workflows. You can talk to it in plain language; the
short prompts below are enough.

- **Claude Code / Cowork** — open this folder; `CLAUDE.md` loads automatically.
- **Gemini CLI** — run `gemini` from this folder; `GEMINI.md` loads automatically and imports
  `CLAUDE.md`, so Gemini follows the exact same rules.

Both agents share the same Python helpers (`scripts/wiki.py`), the same cards, and the same
indexes — so you can switch between them at any time, or use both on the same wiki, without
anything getting out of sync.

---

# The scripts: `wiki.py` (compile & lint) + `similarity.py`

Deterministic helpers keep the mechanical parts rock-solid, so they never depend on an
LLM remembering to update a table or eyeballing a similarity score. Run them from the wiki
folder:

```bash
python scripts/wiki.py compile        # rebuild index.md + tags.md from the wiki/ cards
python scripts/wiki.py lint           # health-check; lists problems, exits non-zero on errors
python scripts/similarity.py report   # ranked "similar cocktails" candidates per card
python scripts/similarity.py gaps     # similarity coverage + stale/missing-link check
```

- **compile** regenerates `index.md` and `tags.md` from the cards. The cards are the source
  of truth; those two files are *generated*, so **don't hand-edit them** — change a card and
  recompile. To add a brand-new canonical tag, add it to the `VOCABULARY` near the top of
  `scripts/wiki.py`, then compile.
- **lint** checks tag counts (3–7), frontmatter-vs-body tag agreement, that every tag is in
  the vocabulary, that "similar cocktails" links resolve and are mutual, that index/tags are
  in sync, and flags pending inbox files, blank ratings, and missing photos.
- **similarity.py** computes each pair's similarity deterministically by fusing three signals
  (the discrete rubric, canonicalised-ingredient overlap, and TF-IDF over the card text), so
  the "Other Similar Cocktails" links are reproducible instead of hand-scored. `report` lists
  the recommended `✅` candidates per card; `gaps` flags ingredients the engine can't yet
  canonicalise and links that have gone stale or are missing. It imports the tag vocabulary
  from `wiki.py` (one-way), so adding a tag there is automatically visible to scoring. Other
  modes: `pairs`, `matrix`, `json`, and `test` (self-test).

You don't have to run them by hand — just ask, and the assistant runs them for you:

```
Compile the wiki, then lint it and fix anything mechanical.
```

The assistant runs `compile` automatically at the end of every ingest (and `similarity.py
report` to (re)link similar drinks). `python scripts/compile.py` and `python scripts/lint.py`
work too — they're aliases for the `wiki.py` subcommands.

> Needs Python 3 (no third-party packages). On Windows, if `python` isn't found, use
> `py scripts\wiki.py compile`.

---

# Everyday tasks

Each task lists **when to use it**, the **steps**, and a **prompt** you can copy verbatim.

## 1. Add new cocktails  →  *Ingest*

**When:** you have one or more new drinks to file.

**Steps**
1. Create a `.md` file in `raw/inbox/`. One cocktail per file, **or** several in one file
   separated by `---`. Fill in whatever you know; leave the rest as `TBD`. A bare name plus
   a couple of ingredients is enough — see `raw/inbox/README.md` for the blank template.
2. Fill the **Rating** / **Modified Variation** lines yourself if you have them (optional).
3. Run the prompt below.

**Prompt (short)**
```
Ingest the new cocktails in raw/inbox/.
```

**Prompt (explicit, if you want to spell it out)**
```
Process every file in raw/inbox/: complete the missing fields from the web (cite a source
for Background), normalise the ingredients, assign 3–7 tags, link similar cocktails from
scripts/similarity.py report (link the recommended candidates, mutual), write the finished
cards to wiki/, update index.md / tags.md / log.md, and move the originals to raw/archive/.
Don't touch the Rating or Modified Variation fields.
```

**What you get back:** a summary of what was added, which fields were filled from the web
(with sources), and anything left as `TBD`. The assistant runs `compile` and `lint` at the
end, so the index and tags are already up to date.

---

## 2. Let the AI complete or fix missing data

**When:** a card has `TBD` gaps, or you want a recipe/background double-checked. (This
normally happens automatically during ingest — use this to redo or extend it.)

**Prompt**
```
Complete the TBD fields in wiki/<slug>.md from reliable sources, cite a source for any
history, and re-check the tags. Update index.md and tags.md if anything changes. Leave the
Rating and Modified Variation fields alone.
```

---

## 3. Ask questions / decide what to make  →  *Query*

**When:** any time you want to use the collection. The AI reads `index.md` first, narrows
with `tags.md` and search, then opens the relevant cards and answers **with citations**.

**Example prompts**
```
Using the wiki, what can I make if I have white rum, lime, and mint?
```
```
Show me every Tiki drink and how they differ.
```
```
Which cocktails did Eric rate 5/5?
```
```
I want something refreshing and not too boozy for a hot afternoon — suggest three with reasons.
```

**Tip:** if an answer is worth keeping (e.g. *"best summer rum drinks"*), say
`save that as a list page in wiki/ and note it in log.md` — that's how the wiki compounds.

---

## 4. Keep the index (first-layer table) current

**When:** rarely needed — ingest recompiles automatically. Use this after you hand-edit a card.

The index table holds each drink's **Glassware, Ingredients, Instruction, Profile, and both
Ratings**, with a link to the full card. It's generated, so rebuild it with one command:

```bash
python scripts/wiki.py compile
```

**Or just ask**
```
Rebuild index.md and tags.md from the wiki/ cards.
```

---

## 5. Work with tags

Tags span 6 dimensions — **base spirit, ingredient, flavour, technique, family, glassware**
— and each drink carries 3–7. `tags.md` is the reverse index (tag → cocktails).

**Find drinks by tag**
```
List all cocktails tagged #Refreshing, grouped by base spirit.
```

**Retag a drink (add/trim/fix)**
```
Review the tags on wiki/<slug>.md against tags.md and adjust to the 3–7 most salient ones.
Update the card's Tags line, its frontmatter, and tags.md so they all agree.
```

**Add a brand-new tag**
```
I want a "#LowABV" flavour-strength tag. Add it to tags.md under the right dimension and
apply it wherever it fits.
```

---

## 6. Manage "similar cocktails" links

Every card's **Other Similar Cocktails** is filled from `python scripts/similarity.py report`,
which scores each pair deterministically (rubric + ingredient overlap + card text — see
`CLAUDE.md` §7). The assistant links the recommended `✅` candidates (top 2–4, or TBD if none
qualify) and makes every link mutual. The link bar is the owner-tunable `LINK_THRESHOLD`
constant in `scripts/similarity.py`.

**Re-link everything (e.g. after adding several drinks)**
```
Run scripts/similarity.py report and re-link the "Other Similar Cocktails" across all wiki/
cards from the recommended candidates, keeping every link mutual.
```

**Re-link one drink**
```
Refresh the similar-cocktail links for wiki/<slug>.md from scripts/similarity.py report and
add the matching back-links.
```

### Inspect & calibrate similarity

**See the raw pairwise scores.** Three read-only views expose every pair's fused score and
the three "correlations" that compose it — the rubric, ingredient-overlap, and text layers:

```bash
python scripts/similarity.py pairs    # every pair, ranked by fused, with rub / ing / txt columns
python scripts/similarity.py matrix   # all-pairs grid (Markdown) of fused scores
python scripts/similarity.py json     # full per-pair detail (layer scores, rubric reasons, shared ingredients)
```

`fused = 0.45·(rubric/10) + 0.35·ingredient_jaccard + 0.20·text_cosine`. The `rub`/`ing`/`txt`
columns in `pairs` are exactly those three components, so you can see *why* any two drinks
score the way they do.

**Calibrate the thresholds.** The link bar isn't magic — it's the `LINK_THRESHOLD` constant
(with `REMOVE_THRESHOLD`, the stale-link floor, and the three `W_*` weights) near the top of
`scripts/similarity.py`. You set the baseline against your actual collection, and the
assistant edits the script for you. The loop:

1. **Look** at `python scripts/similarity.py pairs` — find the natural gap between the
   meaningful matches and the weak tail.
2. **Pick** a `LINK_THRESHOLD` in that gap (keep `REMOVE_THRESHOLD` ~0.05 below it so
   border-line links don't flap on every ingest).
3. **Apply** — the assistant edits the constant(s) in `scripts/similarity.py`, then re-runs
   `report` + `gaps` and re-links the cards so everything stays consistent.

**Prompt (calibrate)**
```
Show me scripts/similarity.py pairs, recommend a LINK_THRESHOLD for the current collection,
then set it in scripts/similarity.py, re-link all wiki/ cards from the report, and run gaps.
```

> Changing a threshold or weight changes which links qualify — always re-run `report` and
> re-link afterward (and `gaps` to confirm nothing went stale). The weights rarely need
> touching; the thresholds are the normal tuning knob as the collection grows.

---

# Maintenance

## Health check  →  *Lint*

**When:** every so often, or after a batch of edits. Catches broken links, bad tag counts,
orphan tags, index/card mismatches, one-way similar links, and files left in the inbox —
plus (via `similarity.py gaps`) stale/missing similar-links and ingredients the engine can't
yet canonicalise.

```bash
python scripts/wiki.py lint && python scripts/similarity.py gaps
```

**Or just ask**
```
Lint the wiki and fix anything mechanical; report what needs my decision.
```

## Add or change a rating (your words only)

Ratings are yours. Either edit the card directly, **or** dictate and have the AI transcribe
exactly what you say (it won't paraphrase or invent):

```
On wiki/daiquiri.md, set Eric — Rating to 4.5 / 5 with the comment: "the benchmark sour."
Record my words verbatim.
```

**Note:** Ratings use **0.5 increments** (e.g., 3.5, 4.0, 4.5). The website displays these
as stars (including half-stars). The `/ 5` denominator is hidden on the index page for a
cleaner look but should be kept in the wiki cards.

## Correct a cocktail (fix a recipe, etc.)

Because `raw/archive/` is frozen, you revise by **re-ingesting**:

1. Drop a corrected `.md` for that cocktail into `raw/inbox/`.
2. Run:
```
Re-ingest the corrected file in raw/inbox/ and overwrite its wiki card. Keep my existing
Rating and Modified Variation.
```

## Add a photo

Save an image as `photos/<slug>.jpg` (e.g. `photos/mojito.jpg`). The card already points to
it — it appears automatically. No prompt needed.

## Back up

The whole wiki is plain text + images. Use Git, or just copy the folder. (Git also gives you
a full history of every AI edit.)

---

# Prompt cheat-sheet

| You want to… | Say this |
|---|---|
| File new drinks | `Ingest the new cocktails in raw/inbox/.` |
| Fill gaps in a card | `Complete the TBD fields in wiki/<slug>.md and cite sources.` |
| Get a recommendation | `Using the wiki, what should I make with <ingredients>?` |
| Browse a style | `Show me every <#Tag> drink and how they differ.` |
| Find top-rated | `Which cocktails did Eric rate 4.5 or higher?` |
| Rebuild index & tags | `python scripts/wiki.py compile` — or *"rebuild the index"* |
| Fix tags | `Review and fix the tags on wiki/<slug>.md against the vocabulary.` |
| Refresh similar links | `Run scripts/similarity.py report and re-link from the ✅ candidates, mutual.` |
| Health check | `python scripts/wiki.py lint && python scripts/similarity.py gaps` — or *"lint the wiki"* |
| Record a rating | `Set <person> — Rating on wiki/<slug>.md to X.5/5, comment "…". My words verbatim.` |
| Fix a recipe | `Re-ingest the corrected file in raw/inbox/ and overwrite its card.` |

---

# Five rules worth remembering

1. **Drop in `raw/inbox/`, then say "ingest."** Empty inbox = everything's processed.
2. **Ratings & Modified Variation are yours.** The AI never invents or changes them.
3. **`raw/archive/` is frozen.** To fix a drink, re-ingest a corrected file.
4. **Tags come from `tags.md`.** New ones get added there deliberately, not ad-hoc.
5. **Every ingest keeps `index.md`, `tags.md`, and `log.md` in sync** — so the collection
   stays queryable as it grows.

*The four cocktails currently in the wiki are connected seed examples — keep, edit, or
delete them as you add your own.*
