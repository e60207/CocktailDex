# GEMINI.md — CocktailDex (Gemini CLI entry point)

This file is the context Gemini CLI loads automatically for this project. It exists so the
wiki works identically whether the maintainer drives it with **Gemini CLI** or with
**Claude Code / Cowork**.

**Single source of truth.** All schema, workflows, and hard rules live in `CLAUDE.md`. This
file does not duplicate them — it *imports* them below, so there is exactly one place to
edit. When you (Gemini) act as the maintainer, treat every instruction in the imported file
as binding, reading "the LLM" / "the assistant" / "the AI" as **you**.

@./CLAUDE.md

---

## Gemini-specific operating notes

These don't override anything above — they just translate a few mechanics to the Gemini CLI
environment:

- **Shell tool.** Run the deterministic helpers with your shell tool, from the wiki folder:
  `python scripts/wiki.py compile` and `python scripts/wiki.py lint`. They are plain Python 3
  (no third-party packages) and are agent-agnostic. On Windows use `py scripts\wiki.py …` if
  `python` isn't found.
- **File edits.** Use your read/write/edit file tools for the `wiki/` cards and the `raw/`
  inbox↔archive moves. Never hand-edit the generated `index.md` / `tags.md` — recompile.
- **Web completion.** Use your web/search tooling to fill Background, recipe, etc., and cite
  a source URL exactly as the schema requires. Never guess history.
- **Defaults.** If the owner just drops files and says nothing, assume **Ingest** (§5 of the
  imported schema).

> If the `@./CLAUDE.md` import ever fails to resolve (e.g. the file was moved), the rulebook
> is still readable directly at `./CLAUDE.md` — open and follow it before doing any work.

*Last updated: 2026-06-20. Keep this shim thin; put real rules in `CLAUDE.md`.*
