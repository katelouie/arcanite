"""
Arcanite - A Tarot Reading Engine

A Python package for conducting tarot readings with deterministic
and LLM-powered interpretations.
"""

__version__ = "0.1.0"

from arcanite.core import (
    AssembledContext,
    Card,
    CardInterpretation,
    Deck,
    DeckConfig,
    DrawnCard,
    InterpretationEngine,
    LLMConfig,
    LLMProvider,
    Orientation,
    PDFConfig,
    PDFRenderer,
    QuestionType,
    Reading,
    ReadingConfig,
    RelationshipType,
    SpreadDefinition,
    SpreadLoader,
    SynthesizedReading,
)

__all__ = [
    "__version__",
    # Protocols
    "Card",
    "Deck",
    "InterpretationEngine",
    "LLMProvider",
    "PDFRenderer",
    "SpreadLoader",
    # Models
    "AssembledContext",
    "CardInterpretation",
    "DeckConfig",
    "DrawnCard",
    "LLMConfig",
    "Orientation",
    "PDFConfig",
    "QuestionType",
    "Reading",
    "ReadingConfig",
    "RelationshipType",
    "SpreadDefinition",
    "SynthesizedReading",
]
