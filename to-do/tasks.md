# 📋 CocktailDex — Project To-Do List

This list tracks planned improvements to the wiki schema, tag system, and similarity engine.

## 1. Taxonomy & Vocabulary
- [ ] **Review/update tag vocabulary**: Audit the current `VOCABULARY` in `scripts/wiki.py`.
- [ ] **Add tag category (Original vs Classic)**: Create a new dimension to distinguish between classic recipes and original creations.

## 2. Tag Selection Rules (Refinement)
- [ ] **Base Spirit Rule**: Only pick 1 main base spirit. If no dominant spirit exists (e.g., Long Island Ice Tea), do not use a base spirit tag.
- [ ] **Souring Agent Rule**: Do not use common souring agents (e.g., #Lemon, #Lime, #Orange) as tags. Reserve fruit tags for less common or themed/specialty fruits (e.g., #Peach, #Watermelon, #Mango).
- [ ] **Distribution Rule**: Ensure the majority of tags for any card come from the **Family / Style** and **Flavor / Profile** dimensions.

## 3. Similarity Engine & Scoring
- [ ] **Evaluate/update scoring system**: Adjust weights in `scripts/similarity.py` to give **Style/Family** and **Flavor Profile** significantly more weight than ingredient overlap.
- [ ] **Evaluate threshold for linking**: Review `LINK_THRESHOLD` and `REMOVE_THRESHOLD` after weight adjustments to ensure meaningful connections.

## 4. Documentation & Display
- [ ] **Update similarity justifications**: Refine the "why" notes in the `Other Similar Cocktails` field.
    - Focus on **Style/Family** and **Flavor** as the primary justifications.
    - Only cite ingredients as a reason if they are specialty/specialty items (e.g., #Peach, #Watermelon, #Falernum, #Campari).

---
*Created 2026-06-12*
