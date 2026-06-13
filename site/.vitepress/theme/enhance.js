// CocktailDex — client-side, READ-ONLY DOM enhancement.
//
// Two transforms run after each page renders:
//   1. enhanceTags    — the card "**Tags:** #Rum #Lime …" line → dimension-coloured chips.
//   2. enhanceRatings — the "**Eric — Rating:** 4 / 5" line → ★ glyphs (display only).
//
// INVARIANTS (see design.md D3/D4, Risks):
//   - Never throws on unexpected markup — every transform is wrapped so a parse miss
//     leaves the original text in place. The page must stay readable if a card differs.
//   - Read-only: ratings are derived purely from the number already in the markup. No
//     value is written, defaulted, or inferred. Blank (`_ / 5`) → explicit "not yet rated".
//   - Idempotent: a `data-cdx-*` marker prevents re-processing on re-runs.

// --- Dimension lookup: MIRROR of the 6-dimension VOCABULARY in scripts/wiki.py ---------
// KEEP IN SYNC with scripts/wiki.py. A tag not found here falls back to a neutral chip
// (data-dimension="unknown") — it never errors. This duplication is the documented
// trade-off of D3; the Python VOCABULARY remains the source of truth.
const VOCABULARY = {
  base: ['Rum', 'Gin', 'Vodka', 'Whiskey', 'Tequila', 'Mezcal',
    'Brandy', 'Cognac', 'Aquavit', 'Liqueur', 'FortifiedWine', 'Wine'],
  ingredient: ['Lime', 'Mint', 'Falernum', 'Pineapple', 'Mango', 'Lemon', 'Orange',
    'Sugar', 'Demerara', 'Angostura', 'Soda', 'Campari',
    'Vermouth', 'Egg', 'Cream', 'Ginger', 'Coffee'],
  flavor: ['Refreshing', 'Spiced', 'Fruity', 'Citrusy', 'Tart', 'Sweet',
    'Bitter', 'Herbal', 'Boozy', 'Complex', 'Light', 'Creamy', 'Smoky', 'Dry'],
  technique: ['Shaken', 'Muddled', 'Swizzle', 'Stirred', 'Built',
    'Blended', 'Thrown', 'Layered', 'DryShake'],
  family: ['Tiki', 'Highball', 'Sour', 'OldFashioned', 'Martini',
    'Fizz', 'Punch', 'Spritz', 'Daisy', 'Flip', 'Julep'],
  glassware: ['Collins', 'Coupe', 'Rocks', 'NickAndNora',
    'TikiMug', 'Hurricane', 'WineGlass', 'Flute', 'Shot', 'Margarita', 'Pint'],
}

// Reverse map { tag -> dimension } built once.
const TAG_TO_DIM = {}
for (const [dim, tags] of Object.entries(VOCABULARY)) {
  for (const t of tags) TAG_TO_DIM[t] = dim
}

function dimensionOf(tag) {
  return TAG_TO_DIM[tag] || 'unknown'
}

// Collect every node after `strong` within its parent, returning the combined text and
// the nodes (so the caller can remove them once it has built a replacement).
function trailingNodes(strong) {
  const nodes = []
  let text = ''
  let node = strong.nextSibling
  while (node) {
    text += node.textContent
    nodes.push(node)
    node = node.nextSibling
  }
  return { nodes, text }
}

function enhanceTags(root) {
  // The Tags line is the only place a `**Tags:**` label appears (cards only — tags.md uses
  // `**#Rum**` / code spans, which never match "Tags:").
  root.querySelectorAll('li > strong, p > strong').forEach((strong) => {
    if (strong.textContent.trim() !== 'Tags:') return
    const parent = strong.parentNode
    if (parent.dataset.cdxTags) return // idempotent

    const { nodes, text } = trailingNodes(strong)
    const tokens = text.match(/#\w+/g)
    if (!tokens || !tokens.length) return // unexpected markup → leave as-is

    const list = document.createElement('span')
    list.className = 'cdx-tags'
    tokens.forEach((tok) => {
      const name = tok.slice(1)
      const chip = document.createElement('span')
      chip.className = 'cdx-tag'
      chip.dataset.dimension = dimensionOf(name)
      chip.textContent = name
      list.appendChild(chip)
    })

    nodes.forEach((n) => n.remove())
    parent.appendChild(list)
    parent.dataset.cdxTags = '1'
  })
}

function enhanceRatings(root) {
  root.querySelectorAll('p > strong, li > strong').forEach((strong) => {
    if (!/Rating:\s*$/.test(strong.textContent)) return
    const parent = strong.parentNode
    if (parent.dataset.cdxRating) return // idempotent

    const { nodes, text } = trailingNodes(strong)
    // Read the value ALREADY in the markup. Supports decimals like 4.5.
    const m = text.match(/([\d.]+|_)\s*\/\s*(\d+)/)
    if (!m) return // unexpected markup → leave as-is
    const max = parseInt(m[2], 10)
    if (!Number.isFinite(max) || max < 1 || max > 10) return

    const wrap = document.createElement('span')
    wrap.className = 'cdx-rating'

    if (m[1] === '_') {
      // Blank rating → explicit not-yet-rated state. No value written.
      wrap.classList.add('cdx-rating--empty')
      for (let i = 0; i < max; i++) {
        const s = document.createElement('span')
        s.className = 'cdx-star'
        s.textContent = '☆'
        wrap.appendChild(s)
      }
      const note = document.createElement('span')
      note.className = 'cdx-rating-note'
      note.textContent = 'not yet rated'
      wrap.appendChild(note)
    } else {
      const value = parseFloat(m[1])
      const filled = Math.max(0, Math.min(max, value))
      for (let i = 1; i <= max; i++) {
        const s = document.createElement('span')
        if (i <= filled) {
          s.className = 'cdx-star cdx-star--on'
          s.textContent = '★'
        } else if (i - 0.5 <= filled) {
          s.className = 'cdx-star cdx-star--half'
          s.textContent = '☆'
        } else {
          s.className = 'cdx-star'
          s.textContent = '☆'
        }
        wrap.appendChild(s)
      }
      const note = document.createElement('span')
      note.className = 'cdx-rating-note'
      note.textContent = `${filled} / ${max}`
      wrap.appendChild(note)
    }

    nodes.forEach((n) => n.remove())
    parent.appendChild(wrap)
    parent.dataset.cdxRating = '1'
  })
}

function enhanceHumanFields(root) {
  root.querySelectorAll('p > strong, li > strong').forEach((strong) => {
    const label = strong.textContent.trim()
    const parent = strong.parentNode

    if (label === 'Modified Variation:') {
      if (parent.dataset.cdxModified) return
      const { text } = trailingNodes(strong)
      if (text.trim() === 'N/A') {
        parent.style.display = 'none'
      }
      parent.dataset.cdxModified = '1'
    } else if (label === '!!Tips:') {
      if (parent.dataset.cdxTips) return
      const { text } = trailingNodes(strong)
      const content = text.trim()
      if (content === 'N/A') {
        parent.style.display = 'none'
      } else {
        // Style the parent as a box and rebuild content
        parent.className = 'cdx-tips-box'
        parent.innerHTML = ''

        const symbol = document.createElement('span')
        symbol.className = 'cdx-tips-symbol'
        symbol.textContent = '!!'

        const tipLabel = document.createElement('strong')
        tipLabel.textContent = 'Tips: '

        parent.appendChild(symbol)
        parent.appendChild(tipLabel)
        parent.appendChild(document.createTextNode(content))
      }
      parent.dataset.cdxTips = '1'
    }
  })
}

// Entry point — run both transforms over the rendered doc. Wrapped so a failure in one
// never breaks the page (graceful degradation to plain markdown).
export function enhanceContent() {
  if (typeof document === 'undefined') return
  const root = document.querySelector('.vp-doc')
  if (!root) return
  try { enhanceTags(root) } catch (e) { /* leave tags as plain text */ }
  try { enhanceRatings(root) } catch (e) { /* leave ratings as plain text */ }
  try { enhanceHumanFields(root) } catch (e) { /* leave human fields as plain text */ }
}
