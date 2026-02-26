"""
Arcanite Core Module

Protocols, models, and deck/spread implementations.
"""

from arcanite.core.deck import TarotCard, TarotDeck, load_tarot_deck
from arcanite.core.models import (
    AssembledContext,
    CardInterpretation,
    CardRelationshipMatch,
    DeckConfig,
    DrawnCard,
    LLMConfig,
    Orientation,
    PDFConfig,
    QuestionType,
    Reading,
    ReadingConfig,
    RelationshipType,
    SpreadDefinition,
    SpreadLayout,
    SpreadPosition,
    SynthesizedReading,
)
from arcanite.core.protocols import (
    Card,
    Deck,
    InterpretationEngine,
    LLMProvider,
    PDFRenderer,
    SpreadLoader,
)
from arcanite.core.spread import (
    SpreadRegistry,
    get_spread_registry,
    list_spreads,
    load_spread,
)

__all__ = [
    # Protocols
    "Card",
    "Deck",
    "InterpretationEngine",
    "LLMProvider",
    "PDFRenderer",
    "SpreadLoader",
    # Implementations
    "TarotCard",
    "TarotDeck",
    "load_tarot_deck",
    "SpreadRegistry",
    "get_spread_registry",
    "load_spread",
    "list_spreads",
    # Models
    "AssembledContext",
    "CardInterpretation",
    "CardRelationshipMatch",
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
    "SpreadLayout",
    "SpreadPosition",
    "SynthesizedReading",
]
