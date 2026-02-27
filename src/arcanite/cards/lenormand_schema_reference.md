# Lenormand Card Schema Reference

## Overview

Each of the 36 Lenormand cards is stored as a single JSON file following the naming convention `l{number:02d}_{id}.json` (e.g., `l03_the_ship.json`, `l36_the_cross.json`).

## Card Categories

Every Lenormand card belongs to one primary category. These categories drive the stratified combination sampling:

| Category | Cards | Description |
|----------|-------|-------------|
| **person** | Gentleman (28), Lady (29), Child (13) | Cards that primarily represent people |
| **positive** | Clover (2), Bouquet (9), Sun (31), Star (16), Heart (24), Ring (25), Key (33), Anchor (35), Dog (18), Fish (34) | Cards with predominantly positive charge |
| **negative** | Clouds (6), Snake (7), Coffin (8), Scythe (10), Whip (11), Fox (14), Mountain (21), Mice (23), Cross (36) | Cards with predominantly negative or challenging charge |
| **neutral** | Rider (1), Ship (3), House (4), Tree (5), Book (26), Letter (27), Lily (30), Garden (20), Tower (19), Bear (15), Stork (17), Path (22), Birds (12) | Context-dependent cards |

> **Note:** Some cards straddle categories (Dog could be positive or neutral, Bear could be neutral or positive). The `core.charge` field captures the primary valence; the category assignment is for combination stratification purposes.

## Schema Fields

### Top-Level Identification

```json
{
  "id": "the_ship",           // snake_case, used as key in code
  "number": 3,                // 1-36, canonical Lenormand numbering
  "name": "The Ship",         // Display name
  "playing_card": "10 of Spades",  // Traditional playing card correspondence
  "system": "lenormand",      // Always "lenormand" for this deck
  "image_file": "03.png"      // Card image filename, zero-padded: {number:02d}.png
}
```

### `image`

Brief description of the card's traditional imagery. Used by LLM synthesis to reference visual symbolism.

```json
"image": "A large three-masted sailing ship on open water, moving away from shore toward a distant horizon."
```

### `core`

Essential card identity.

| Field | Type | Description |
|-------|------|-------------|
| `keywords` | `list[str]` | 7-10 core keywords, ordered by importance |
| `charge` | `str` | `"positive"`, `"negative"`, or `"neutral"` |
| `category` | `str` | `"person"`, `"object"`, `"nature"`, `"abstract"`, `"place"` |
| `topics` | `list[str]` | Life areas this card commonly speaks to |

### `timing`

For timing questions and pacing in readings.

| Field | Type | Description |
|-------|------|-------------|
| `thematic` | `str` | Qualitative timing feel (e.g., `"forward_movement"`, `"sudden"`, `"slow_growth"`) |
| `duration` | `str` | `"days"`, `"weeks"`, `"weeks_to_months"`, `"months"`, `"months_to_years"`, `"years"` |
| `season` | `str \| null` | Season association if any (`"spring"`, `"summer"`, `"autumn"`, `"winter"`) |
| `speed` | `str` | `"instant"`, `"fast"`, `"moderate"`, `"slow"`, `"glacial"` |
| `direction` | `str \| null` | Directional energy if relevant (`"toward"`, `"away"`, `"static"`, `"cyclical"`) |

### `as_person`

Who this card represents when read as a person (relevant in Grand Tableau and person-focused readings). All cards can potentially represent a person — this field captures the archetype.

### `modifier_behavior`

How this card modifies adjacent cards in a line.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `str` | `"descriptor"` (adds quality), `"negator"` (reverses/blocks), `"intensifier"` (amplifies), `"timer"` (adds timing), `"pivot"` (redirects) |
| `effect` | `str` | Human-readable description of the modification |

### `topic_contexts`

Topic-specific interpretive flavor, parallel to tarot's question_context system.

| Key | When to use |
|-----|-------------|
| `love` | Relationship and romance questions |
| `career` | Work, profession, ambition questions |
| `health` | Physical and mental health questions |
| `finances` | Money, investments, material security questions |
| `spiritual` | Inner growth, purpose, soul-path questions |

Each value is 1-3 sentences of interpretive guidance for that topic.

### `line_reading`

Positional interpretation for simple line spreads (3-card, 5-card, 7-card lines).

| Field | Description |
|-------|-------------|
| `as_first` | Card opens the line — sets the topic or context |
| `as_middle` | Card in a middle position — modifies, bridges, or complicates |
| `as_last` | Card closes the line — outcome, resolution, or advice |

### `directional_rules`

**The fallback system for unlisted combinations.** When a specific combination entry doesn't exist, the synthesis layer uses these rules to generate an interpretation.

| Field | Description |
|-------|-------------|
| `as_card_a` | How this card behaves when it appears LEFT of another card |
| `as_card_b` | How this card behaves when it appears RIGHT of another card |
| `summary` | One-line summary of the directional behavior |

**Design rationale:** Lenormand has 36 × 35 = 1,260 directional pairs. We curate ~15-17 representative combinations per card (stratified by category), and the directional rules cover the rest. The LLM synthesis layer can combine Card A's `as_card_a` rule with Card B's `as_card_b` rule to produce a reasonable interpretation for any unlisted pair.

### `combinations`

Curated combination interpretations, stratified by the partner card's category.

```json
"combinations": {
  "_stratification_note": "...",
  "person_cards": [...],
  "positive_cards": [...],
  "negative_cards": [...],
  "neutral_cards": [...]
}
```

Each combination entry:

```json
{
  "with": "the_heart",       // ID of the partner card
  "with_number": 24,         // Number for sorting/lookup
  "as_first": "...",         // This card LEFT, partner RIGHT
  "as_second": "..."         // Partner LEFT, this card RIGHT
}
```

**Stratification targets:**
- `person_cards`: All 3 person cards (Gentleman, Lady, Child) — always include all
- `positive_cards`: 4-5 representative positive cards
- `negative_cards`: 4-5 representative negative cards  
- `neutral_cards`: 4-5 representative neutral cards

This gives ~15-17 curated combos per card. Combined with directional rules, this covers all 1,260 pairs.

### `grand_tableau`

Interpretation guidance for the 36-card Grand Tableau spread.

| Field | Description |
|-------|-------------|
| `as_house` | What it means when OTHER cards land in this card's house position |
| `near_significator` | What it means when this card falls near the querent's significator |
| `far_from_significator` | What it means when this card is far from the significator |

## File Naming Convention

```
l01_the_rider.json
l02_the_clover.json
l03_the_ship.json
...
l36_the_cross.json
```

## Complete Card List

| # | ID | Name | Playing Card | Category |
|---|-----|------|-------------|----------|
| 1 | the_rider | The Rider | 9 of Hearts | neutral |
| 2 | the_clover | The Clover | 6 of Diamonds | positive |
| 3 | the_ship | The Ship | 10 of Spades | neutral |
| 4 | the_house | The House | King of Hearts | neutral |
| 5 | the_tree | The Tree | 7 of Hearts | neutral |
| 6 | the_clouds | The Clouds | King of Clubs | negative |
| 7 | the_snake | The Snake | Queen of Clubs | negative |
| 8 | the_coffin | The Coffin | 9 of Diamonds | negative |
| 9 | the_bouquet | The Bouquet | Queen of Spades | positive |
| 10 | the_scythe | The Scythe | Jack of Diamonds | negative |
| 11 | the_whip | The Whip | Jack of Clubs | negative |
| 12 | the_birds | The Birds | 7 of Diamonds | neutral |
| 13 | the_child | The Child | Jack of Spades | person |
| 14 | the_fox | The Fox | 9 of Clubs | negative |
| 15 | the_bear | The Bear | 10 of Clubs | neutral |
| 16 | the_star | The Star | 6 of Hearts | positive |
| 17 | the_stork | The Stork | Queen of Hearts | neutral |
| 18 | the_dog | The Dog | 10 of Hearts | positive |
| 19 | the_tower | The Tower | 6 of Spades | neutral |
| 20 | the_garden | The Garden | 8 of Spades | neutral |
| 21 | the_mountain | The Mountain | 8 of Clubs | negative |
| 22 | the_path | The Path | Queen of Diamonds | neutral |
| 23 | the_mice | The Mice | 7 of Clubs | negative |
| 24 | the_heart | The Heart | Jack of Hearts | positive |
| 25 | the_ring | The Ring | Ace of Clubs | positive |
| 26 | the_book | The Book | 10 of Diamonds | neutral |
| 27 | the_letter | The Letter | 7 of Spades | neutral |
| 28 | the_gentleman | The Gentleman | Ace of Hearts | person |
| 29 | the_lady | The Lady | Ace of Spades | person |
| 30 | the_lily | The Lily | King of Spades | neutral |
| 31 | the_sun | The Sun | Ace of Diamonds | positive |
| 32 | the_moon | The Moon | 8 of Hearts | positive |
| 33 | the_key | The Key | 8 of Diamonds | positive |
| 34 | the_fish | The Fish | King of Diamonds | positive |
| 35 | the_anchor | The Anchor | 9 of Spades | positive |
| 36 | the_cross | The Cross | 6 of Clubs | negative |

## Assembly Strategy for Arcanite

### Line Readings (3, 5, 7 cards)
1. For each card: pull `line_reading.as_first/middle/last` based on position
2. For each adjacent pair: look up `combinations` entry; if missing, combine `card_a.directional_rules.as_card_a` + `card_b.directional_rules.as_card_b`
3. Pull `topic_contexts[question_type]` if question type is known
4. Pass all assembled context to LLM synthesis

### Grand Tableau (36 cards)
1. For each card: note its house position and pull `grand_tableau.as_house`
2. Calculate distance from significator: pull `near_significator` or `far_from_significator`
3. For cards adjacent to significator: pull combinations
4. For cards in significant houses (Heart house, Ring house, etc.): pull house-specific interpretations
5. Pass assembled context to LLM synthesis
