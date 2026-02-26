"""
Arcanite Reading Engine

Orchestrates the creation of readings from deck + spread + configuration.
"""

from datetime import datetime

from arcanite.core.deck import TarotDeck
from arcanite.core.models import (
    DrawnCard,
    Orientation,
    QuestionType,
    Reading,
    ReadingConfig,
    SpreadDefinition,
)
from arcanite.core.spread import SpreadRegistry, get_spread_registry


class ReadingEngine:
    """
    Engine for creating tarot readings.

    Combines a deck, spread registry, and configuration to produce readings.
    """

    def __init__(
        self,
        deck: TarotDeck,
        spread_registry: SpreadRegistry | None = None,
    ):
        self._deck = deck
        self._spread_registry = spread_registry or get_spread_registry()

    @property
    def deck(self) -> TarotDeck:
        return self._deck

    @property
    def spread_registry(self) -> SpreadRegistry:
        return self._spread_registry

    def create_reading(
        self,
        spread_id: str,
        question: str | None = None,
        question_type: QuestionType | str | None = None,
        allow_reversals: bool = True,
        seed: int | None = None,
    ) -> Reading:
        """
        Create a new reading.

        Args:
            spread_id: ID of the spread to use
            question: Optional question for the reading
            question_type: Optional question type for context
            allow_reversals: Whether cards can appear reversed
            seed: Optional seed for reproducibility

        Returns:
            A Reading with drawn cards assigned to positions
        """
        # Load the spread
        spread = self._spread_registry.load_spread(spread_id)

        # Normalize question_type
        if isinstance(question_type, str):
            question_type = QuestionType(question_type)

        # Draw cards
        num_positions = len(spread.positions)
        drawn_cards = self._deck.draw(
            count=num_positions,
            seed=seed,
            allow_reversals=allow_reversals,
        )

        # Assign position names from spread
        for i, (card, position) in enumerate(zip(drawn_cards, spread.positions)):
            card.position_index = i
            card.position_name = position.name

        # Create the reading
        return Reading(
            id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            created_at=datetime.now(),
            spread_id=spread_id,
            spread_name=spread.name,
            question=question,
            question_type=question_type,
            drawn_cards=drawn_cards,
            allow_reversals=allow_reversals,
            seed=seed,
        )

    def create_reading_from_config(self, config: ReadingConfig) -> Reading:
        """Create a reading from a ReadingConfig."""
        return self.create_reading(
            spread_id=config.spread_id,
            question=config.question,
            question_type=config.question_type,
            allow_reversals=config.allow_reversals,
            seed=config.seed,
        )

    def list_spreads(self) -> list[str]:
        """List available spread IDs."""
        return self._spread_registry.list_spreads()


def create_reading(
    deck: TarotDeck,
    spread_id: str,
    question: str | None = None,
    question_type: QuestionType | str | None = None,
    allow_reversals: bool = True,
    seed: int | None = None,
) -> Reading:
    """
    Convenience function to create a reading.

    Args:
        deck: The tarot deck to use
        spread_id: ID of the spread
        question: Optional question
        question_type: Optional question type
        allow_reversals: Whether to allow reversed cards
        seed: Optional seed for reproducibility

    Returns:
        A Reading with drawn cards
    """
    engine = ReadingEngine(deck)
    return engine.create_reading(
        spread_id=spread_id,
        question=question,
        question_type=question_type,
        allow_reversals=allow_reversals,
        seed=seed,
    )
