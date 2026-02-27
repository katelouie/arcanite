# Changelog

All notable changes to Arcanite will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Lenormand support foundation**: New directory structure and loaders for multi-system oracle support
  - Cards now organized by system: `cards/json/tarot/`, `cards/json/lenormand/`
  - Spreads now organized by system: `tarot-spreads.json`, `lenormand-spreads.json`
  - Deck and spread loaders accept `system` parameter (defaults to `"tarot"`)
- **Lenormand card schema**: Template card (`l03_the_ship.json`) with Lenormand-specific structure
  - Directional combinations (`as_first` / `as_second`) for reading cards in sequence
  - Few-shot combination examples by category (person, positive, negative, object)
  - Line reading positions (`as_first`, `as_middle`, `as_last`)
  - Grand Tableau house meanings
- **Lenormand spreads config**: Initial spread definitions
  - 3-card and 5-card line spreads with positional roles
  - Full 36-card house definitions for Grand Tableau
  - Layouts for horizontal line readings
- **New tradition prompts**:
  - `kate-signature.yaml`: Psychologically rich, analytical, "compassionate scalpel" style (based off of an LLM evaluation of my own sample reading style)
- **PDF report generation**: Full Typst-based PDF rendering system
  - `TypstRenderer` class for generating reading reports
  - `render_reading_to_pdf()` convenience function
  - Spread visualization with positioned cards
  - Card-by-card sections with interpretations and keywords
  - Conditional synthesis section (only shown for LLM-generated readings)
  - Card relationship display
  - Uses Python `typst` package (no CLI required)
- **Cookbook example**: `examples/cookbook.ipynb` demonstrating the full pipeline
  - Loading decks and spreads
  - Creating readings and assembling context
  - Deterministic and LLM-synthesized PDFs
  - Question classification
  - Multiple tradition prompts
  - Local LLM usage (Ollama)

### Changed

- `TarotDeck.load()` now accepts `system` parameter for loading different card systems
- `SpreadRegistry.from_config()` now accepts `system` parameter for loading system-specific spreads
- Tarot cards moved from `cards/json/` to `cards/json/tarot/`
- Spreads config renamed from `spreads-config.json` to `tarot-spreads.json`

## [0.1.0] - 2026-02-26

### Added

- **Core architecture**: Protocol-based design for extensible oracle systems
  - `Card`, `Deck`, `Spread`, `LLMProvider`, `InterpretationEngine` protocols
  - Pydantic models for `Reading`, `DrawnCard`, `AssembledContext`, `SynthesizedReading`
- **Tarot deck**: Full 78-card Rider-Waite-Smith deck
  - Rich card data with position-specific interpretations
  - Question context variations (love, career, spiritual, financial, health, general)
  - Card relationships (amplifies, challenges, clarifies, similar/opposite energy)
  - Elemental correspondences, symbols, affirmations, journaling prompts
- **Spread system**: 11 spread layouts from single-card to Celtic Cross
  - RAG mapping system for position-aware interpretations
  - Visual layouts with x/y positioning for PDF rendering
- **Two-layer interpretation system**:
  - **Layer 1 (Deterministic)**: `DeterministicAssembler` navigates card JSON using RAG mappings
  - **Layer 2 (LLM Synthesis)**: `ReadingSynthesizer` weaves context into cohesive narrative
- **LLM providers**: Support for multiple backends
  - `AnthropicProvider` for Claude models
  - `OpenAIProvider` for GPT models
  - `LocalProvider` for Ollama and OpenAI-compatible local servers
- **Question classifier**: Auto-detect question type for context-aware interpretations
- **Tradition prompts**: YAML-based prompt templates with Jinja2
  - `intuitive.yaml`: Warm, accessible, practical guidance
  - `kate-signature.yaml`: Psychologically rich, analytical, "compassionate scalpel" style
- **Reading engine**: Card drawing with reversals toggle, spread assignment
- **Documentation**: Comprehensive README with usage examples

### Technical Notes

- Lazy imports for optional LLM dependencies (`anthropic`, `openai`, `httpx`)
- Package published to PyPI: `pip install arcanite`
- Requires Python 3.11+
