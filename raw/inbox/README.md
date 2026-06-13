# 📥 Inbox — Drop new cocktails here

This is the **drop zone**. Anything in this folder is **pending** (not yet processed).

## How to add a cocktail

1. Drop a `.md` file here — one cocktail per file, or several in one file separated by `---`.
   Fill in what you know; leave the rest as `TBD` (the AI will complete it from the web).
   You can use the **blank template** below.
2. Tell agent-agnostic: **"ingest my new cocktails"** (or just "ingest").
3. The AI will: complete missing fields, add 3–7 tags, link similar cocktails, write the
   finished card to `wiki/`, update `index.md` / `tags.md` / `log.md`, and **move your
   original file to `raw/archive/`** (frozen, never edited).

When this folder is empty, everything has been processed.

> **Never filled by the AI:** the two Rating fields and Modified Variation are yours alone.
> Write them by hand whenever you like — the AI carries them across and never overwrites them.

---

## Blank template (copy this)

```markdown
## {Name}

**Background:** TBD

- **Glassware:** TBD
- **Ingredients:**
  - {qty} {ingredient}
  - {qty} {ingredient}
- **Instruction:** TBD
- **Garnish:** TBD
- **Profile:** TBD

**Eric — Rating:** _ / 5  (0.5 increments, e.g. 4.5 / 5)
> N/A

**Charlene — Rating:** _ / 5  (0.5 increments, e.g. 4.5 / 5)
> N/A

**Modified Variation:** N/A

**!!Tips:** N/A
```

Even a bare name plus a couple of ingredients is enough — the AI fills the rest. (See the
already-ingested examples in [`../archive/`](../archive/) for how sparse a raw drop can be.)
