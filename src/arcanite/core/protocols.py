"""
Arcanite Core Protocols

Abstract protocols defining contracts for extensibility across different
divination systems (Tarot, Lenormand, Kipper, etc.).
"""

from collections.abc import AsyncIterator, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from arcanite.core.models import (
        AssembledContext,
        DrawnCard,
        Reading,
        SpreadDefinition,
        SynthesizedReading,
    )


@runtime_checkable
class Card(Protocol):
    """Protocol for any card type (Tarot, Lenormand, Kipper, etc.)."""

    @property
    def card_id(self) -> str:
        """Unique identifier for the card (e.g., 'the_fool', 'ace_of_cups')."""
        ...

    @property
    def card_name(self) -> str:
        """Display name (e.g., 'The Fool', 'Ace of Cups')."""
        ...

    @property
    def image_filename(self) -> str:
        """Filename of the card image (e.g., 'm00.jpg')."""
        ...

    def get_interpretation(
        self,
        rag_mapping: str,
        reversed: bool = False,
    ) -> dict[str, Any]:
        """
        Get interpretation for a specific position mapping.

        Args:
            rag_mapping: Dot-notation path like 'temporal_positions.past'
            reversed: Whether the card is reversed

        Returns:
            Dict with interpretation text, keywords, etc.
        """
        ...

    def get_question_context(self, question_type: str, reversed: bool = False) -> dict[str, Any]:
        """
        Get question-specific interpretation.

        Args:
            question_type: One of 'love', 'career', 'spiritual', 'financial', 'health'
            reversed: Whether the card is reversed

        Returns:
            Dict with question-context interpretation
        """
        ...

    def get_relationships(self) -> dict[str, dict[str, Any]]:
        """
        Get card relationship data.

        Returns:
            Dict with keys like 'amplifies', 'challenges', 'clarifies',
            'similar_energy', 'opposite_energy', each containing card_id -> interpretation
        """
        ...

    @property
    def raw_data(self) -> dict[str, Any]:
        """Access to the complete raw card data."""
        ...


@runtime_checkable
class Deck(Protocol):
    """Protocol for any deck type."""

    @property
    def cards(self) -> Sequence[Card]:
        """All cards in the deck."""
        ...

    @property
    def image_path(self) -> Path:
        """Path to card images directory."""
        ...

    def get_card(self, card_id: str) -> Card:
        """Get a specific card by ID."""
        ...

    def get_image_path(self, card: Card) -> Path:
        """Get the full path to a card's image file."""
        ...

    def shuffle(self, seed: int | None = None) -> list[Card]:
        """
        Return a shuffled copy of the deck.

        Args:
            seed: Optional seed for reproducible shuffles

        Returns:
            New list with cards in shuffled order
        """
        ...

    def draw(
        self,
        count: int,
        seed: int | None = None,
        allow_reversals: bool = True,
    ) -> list["DrawnCard"]:
        """
        Draw cards from the deck.

        Args:
            count: Number of cards to draw
            seed: Optional seed for reproducibility
            allow_reversals: Whether cards can be reversed

        Returns:
            List of DrawnCard with card and orientation
        """
        ...


@runtime_checkable
class SpreadLoader(Protocol):
    """Protocol for loading spread definitions."""

    def load(self, spread_id: str) -> "SpreadDefinition":
        """Load a spread definition by ID."""
        ...

    def list_spreads(self) -> list[str]:
        """List all available spread IDs."""
        ...


@runtime_checkable
class InterpretationEngine(Protocol):
    """Protocol for interpretation engines (deterministic or LLM)."""

    def interpret(
        self,
        reading: "Reading",
        question_type: str | None = None,
    ) -> "AssembledContext | SynthesizedReading":
        """
        Generate interpretation for a reading.

        Args:
            reading: The reading with drawn cards
            question_type: Optional question type for context filtering

        Returns:
            AssembledContext (deterministic) or SynthesizedReading (LLM)
        """
        ...


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM providers (Anthropic, OpenAI, local)."""

    async def complete(self, prompt: str, system: str | None = None) -> str:
        """
        Get a completion from the LLM.

        Args:
            prompt: The user prompt
            system: Optional system prompt

        Returns:
            The LLM's response text
        """
        ...

    async def complete_stream(
        self,
        prompt: str,
        system: str | None = None,
    ) -> AsyncIterator[str]:
        """
        Get a streaming completion from the LLM.

        Args:
            prompt: The user prompt
            system: Optional system prompt

        Yields:
            Chunks of the response as they arrive
        """
        # Default implementation for providers that don't support streaming
        yield await self.complete(prompt, system)


@runtime_checkable
class PDFRenderer(Protocol):
    """Protocol for PDF rendering."""

    def render(
        self,
        reading: "Reading",
        interpretation: "AssembledContext | SynthesizedReading",
        include_spread_visual: bool = True,
        include_card_sections: bool = True,
        include_card_images: bool = True,
        include_relationships: bool = True,
    ) -> bytes:
        """
        Render a reading to PDF.

        Args:
            reading: The reading with drawn cards
            interpretation: The interpretation (deterministic or synthesized)
            include_spread_visual: Include x/y positioned card layout
            include_card_sections: Include card-by-card sections
            include_card_images: Embed actual card images
            include_relationships: Include card relationship section

        Returns:
            PDF file contents as bytes
        """
        ...
