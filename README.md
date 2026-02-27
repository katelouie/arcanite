# Arcanite

A Python tarot reading engine with two-layer interpretation: deterministic assembly of curated card meanings, plus optional LLM synthesis for cohesive narrative readings.

## Features

- **78 richly-detailed tarot cards** with position-specific interpretations, question contexts, and card relationships
- **11 spread layouts** from simple 3-card to Celtic Cross, with semantic position meanings
- **Two-layer interpretation system:**
  - **Layer 1 (Deterministic):** Assembles pre-written interpretations using RAG mapping - no hallucination, just curated content matched to spread positions
  - **Layer 2 (LLM Synthesis):** Weaves assembled context into flowing narrative using tradition-specific prompts
- **Multiple LLM providers:** Anthropic (Claude), OpenAI, or local models via Ollama
- **Question classification:** Auto-detect question type (love, career, spiritual, etc.) for context-aware interpretations
- **PDF report generation:** Beautiful reading reports via Typst with spread visualization and card-by-card sections
- **Extensible design:** Protocol-based architecture ready for Lenormand, Kipper, and other oracle systems

## Installation

```bash
pip install arcanite

# For LLM features:
pip install arcanite[llm]

# For PDF generation:
pip install arcanite[pdf]

# Everything:
pip install arcanite[all]
```

## Quick Start

```python
import asyncio
from arcanite.core import TarotDeck
from arcanite.reading import create_reading, assemble_context
from arcanite.interpretation import synthesize_reading

async def main():
    # Load the deck
    deck = TarotDeck.load()

    # Create a reading
    reading = create_reading(
        deck=deck,
        spread_id="past-present-future",
        question="What do I need to know about my creative projects?",
        question_type="career",
        allow_reversals=True,
    )

    # Layer 1: Deterministic assembly
    context = assemble_context(reading, deck)

    # Layer 2: LLM synthesis (optional)
    result = await synthesize_reading(reading, context, tradition="intuitive")

    print(result.synthesis)

asyncio.run(main())
```

## How It Works

### The RAG Mapping System

Each spread position has a `rag_mapping` that points directly into the card's interpretation structure:

```txt
Position: "Past"
rag_mapping: "temporal_positions.past"

Card: The Fool
→ card["position_interpretations"]["temporal_positions"]["past"]["upright"]
→ "A pivotal leap of faith in the past has shaped your journey..."
```

This means the LLM doesn't generate interpretations from scratch—it synthesizes pre-curated, position-aware content.

### Available Spreads

| Spread | Cards | Description |
| ------ | ---- | ----------- |
| `single-focus` | 1 | Daily guidance |
| `past-present-future` | 3 | Classic timeline |
| `mind-body-spirit` | 3 | Holistic wellness |
| `situation-action-outcome` | 3 | Decision making |
| `four-card-decision` | 4 | Weighing options |
| `five-card-cross` | 5 | Comprehensive overview |
| `relationship-spread` | 6 | Relationship dynamics |
| `horseshoe-traditional` | 7 | Classic fortune-telling |
| `horseshoe-apex` | 7 | Apex-focused variant |
| `celtic-cross` | 10 | The classic deep dive |
| `year-ahead` | 12 | Monthly forecast |

### Tradition Prompts

Customize the LLM's interpretive style with tradition prompts:

- `intuitive` - Warm, accessible, practical guidance (default)
- `kate-signature` - Psychologically rich, analytical, "compassionate scalpel" style with macro-analysis of elemental shifts and empowerment through accountability
- More traditions coming soon (Jungian, Golden Dawn, etc.)

## Deterministic-Only Mode

Don't want LLM synthesis? Use Layer 1 directly:

```python
context = assemble_context(reading, deck)

# Get markdown for display
print(context.to_markdown())

# Or access structured data
for card in context.card_interpretations:
    print(f"{card.position_name}: {card.card_name}")
    print(f"  {card.position_interpretation}")
```

## Question Classification

Auto-detect question type for context-aware interpretations:

```python
from arcanite.interpretation import classify_question

question_type = await classify_question("Will I find love this year?")
# → QuestionType.LOVE
```

## Using Local LLMs

Use Ollama or any OpenAI-compatible local server:

```python
from arcanite.interpretation import LocalProvider, ReadingSynthesizer

provider = LocalProvider(
    model="llama3.2",
    base_url="http://localhost:11434/v1",
)

synthesizer = ReadingSynthesizer(provider=provider, tradition="intuitive")
result = await synthesizer.synthesize(reading, context)
```

## PDF Generation

Generate beautiful PDF reports with spread visualization:

```python
from arcanite.render import render_reading_to_pdf

# Get layout positions from spread
layout_positions = [
    (pos.x, pos.y, pos.rotation)
    for pos in spread.layout.positions
]

# Render deterministic-only PDF
render_reading_to_pdf(
    reading=context,  # AssembledContext
    output_path="reading.pdf",
    title="Your Reading",
    layout_positions=layout_positions,
)

# Or render with LLM synthesis
render_reading_to_pdf(
    reading=synthesized,  # SynthesizedReading
    output_path="reading_full.pdf",
    title="Your Reading",
    layout_positions=layout_positions,
)
```

The PDF includes:
- Spread visualization with positioned cards
- Card-by-card interpretations with keywords
- Card relationships (if present)
- Synthesized reading narrative (if LLM-generated)

## Card Data Structure

Each card includes:

- Core meanings (upright/reversed) with essence, keywords, psychological, spiritual, practical, shadow aspects
- Position-specific interpretations for 30+ position types
- Question context variations (love, career, spiritual, financial, health)
- Elemental correspondences (element, zodiac, planet, colors, crystals, herbs)
- Card relationships (amplifies, challenges, clarifies, similar/opposite energy)
- Affirmations, journaling prompts, meditation focus

## Examples

See `examples/cookbook.ipynb` for a complete walkthrough of the pipeline, including:
- Loading decks and spreads
- Creating readings
- Layer 1 deterministic assembly
- Layer 2 LLM synthesis with different traditions
- PDF generation
- Question classification
- Using local LLMs (Ollama)

## Roadmap

- [x] PDF report generation with Typst
- [x] Lenormand support foundation (schema + spreads)
- [ ] More tradition prompts (Jungian, Golden Dawn, Marseille)
- [ ] Complete Lenormand deck (36 cards)
- [ ] Web interface

## License

MIT
