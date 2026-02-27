"""
Arcanite Deck Implementations

Concrete implementations of the Deck protocol for different card systems.
"""

import json
import random
from pathlib import Path
from typing import Any

from arcanite.core.models import DeckConfig, DrawnCard, Orientation


class TarotCard:
    """
    A tarot card loaded from JSON.

    Implements the Card protocol with full access to position interpretations,
    question contexts, and card relationships.
    """

    def __init__(self, data: dict[str, Any], image_filename: str):
        self._data = data
        self._image_filename = image_filename

    @property
    def card_id(self) -> str:
        return self._data["card_id"]

    @property
    def card_name(self) -> str:
        return self._data["card_name"]

    @property
    def card_number(self) -> int:
        return self._data.get("card_number", 0)

    @property
    def suit(self) -> str:
        return self._data.get("suit", "major_arcana")

    @property
    def archetype(self) -> str:
        return self._data.get("archetype", "")

    @property
    def image_filename(self) -> str:
        return self._image_filename

    def get_interpretation(
        self,
        rag_mapping: str,
        reversed: bool = False,
    ) -> dict[str, Any]:
        """
        Navigate to the interpretation using the RAG mapping path.

        Args:
            rag_mapping: Dot-notation path like 'temporal_positions.past'
            reversed: Whether to get reversed interpretation

        Returns:
            Dict with interpretation data including text, keywords, etc.
        """
        # Navigate the path
        position_interps = self._data.get("position_interpretations", {})
        current = position_interps

        parts = rag_mapping.split(".")
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                # Fallback to core meanings if path not found
                return self._get_core_meaning_fallback(reversed)

        # current should now be a dict with 'upright', 'reversed', 'keywords'
        if isinstance(current, dict):
            orientation_key = "reversed" if reversed else "upright"
            return {
                "interpretation": current.get(orientation_key, ""),
                "keywords": current.get("keywords", []),
                "raw": current,
            }

        return self._get_core_meaning_fallback(reversed)

    def _get_core_meaning_fallback(self, reversed: bool) -> dict[str, Any]:
        """Fallback to core meanings if RAG path not found."""
        core = self._data.get("core_meanings", {})
        orientation_key = "reversed" if reversed else "upright"
        meaning = core.get(orientation_key, {})
        return {
            "interpretation": meaning.get("essence", ""),
            "keywords": meaning.get("keywords", []),
            "raw": meaning,
        }

    def get_question_context(
        self,
        question_type: str,
        reversed: bool = False,
    ) -> dict[str, Any]:
        """Get question-specific interpretation."""
        contexts = self._data.get("question_contexts", {})
        context = contexts.get(question_type, {})

        orientation_key = "reversed" if reversed else "upright"
        return {
            "interpretation": context.get(orientation_key, ""),
            "keywords": context.get("keywords", []),
            "raw": context,
        }

    def get_core_meaning(self, reversed: bool = False) -> dict[str, Any]:
        """Get the core meaning (essence, keywords, etc.)."""
        core = self._data.get("core_meanings", {})
        orientation_key = "reversed" if reversed else "upright"
        return core.get(orientation_key, {})

    def get_relationships(self) -> dict[str, dict[str, Any]]:
        """Get card relationship data."""
        return self._data.get("card_relationships", {})

    def get_elemental_correspondences(self) -> dict[str, Any]:
        """Get elemental and astrological correspondences."""
        return self._data.get("elemental_correspondences", {})

    def get_symbols(self) -> dict[str, str]:
        """Get symbol interpretations."""
        return self._data.get("symbols", {})

    def get_affirmations(self) -> list[str]:
        """Get card affirmations."""
        return self._data.get("affirmations", [])

    def get_journaling_prompts(self) -> list[str]:
        """Get journaling prompts."""
        return self._data.get("journaling_prompts", [])

    @property
    def raw_data(self) -> dict[str, Any]:
        return self._data

    def __repr__(self) -> str:
        return f"TarotCard({self.card_name!r})"


class TarotDeck:
    """
    A complete tarot deck loaded from JSON files.

    Implements the Deck protocol with shuffling and drawing capabilities.
    """

    def __init__(
        self,
        cards: list[TarotCard],
        image_path: Path,
        image_format: str = "jpg",
    ):
        self._cards = cards
        self._image_path = image_path
        self._image_format = image_format
        self._card_by_id = {card.card_id: card for card in cards}

    @classmethod
    def load(
        cls,
        card_data_path: Path | str | None = None,
        image_path: Path | str | None = None,
        image_format: str = "jpg",
        package_root: Path | str | None = None,
        system: str = "tarot",
    ) -> "TarotDeck":
        """
        Load a tarot deck from JSON files.

        Args:
            card_data_path: Path to directory containing card JSON files
            image_path: Path to directory containing card images
            image_format: Image file extension (default: 'jpg')
            package_root: Root path of the arcanite package (for finding bundled data)
            system: Card system subdirectory (default: 'tarot')

        Returns:
            A loaded TarotDeck instance
        """
        # Determine paths
        if package_root is None:
            # Default to the package's own data
            package_root = Path(__file__).parent.parent

        if card_data_path is None:
            card_data_path = package_root / "cards" / "json" / system
        else:
            card_data_path = Path(card_data_path)

        if image_path is None:
            image_path = package_root / "images" / "cards_github"
        else:
            image_path = Path(image_path)

        # Load all card JSON files
        cards = []
        for json_file in sorted(card_data_path.glob("*.json")):
            with open(json_file) as f:
                data = json.load(f)

            # Derive image filename from JSON filename
            image_filename = f"{json_file.stem}.{image_format}"
            cards.append(TarotCard(data, image_filename))

        return cls(cards, image_path, image_format)

    @classmethod
    def from_config(cls, config: DeckConfig, package_root: Path | str | None = None) -> "TarotDeck":
        """Load a deck from a DeckConfig."""
        return cls.load(
            card_data_path=config.card_data_path,
            image_path=config.image_path,
            image_format=config.image_format,
            package_root=package_root,
        )

    @property
    def cards(self) -> list[TarotCard]:
        return self._cards

    @property
    def image_path(self) -> Path:
        return self._image_path

    def get_card(self, card_id: str) -> TarotCard:
        """Get a card by its ID."""
        if card_id not in self._card_by_id:
            raise KeyError(f"Card not found: {card_id}")
        return self._card_by_id[card_id]

    def get_image_path(self, card: TarotCard) -> Path:
        """Get the full path to a card's image file."""
        return self._image_path / card.image_filename

    def shuffle(self, seed: int | None = None) -> list[TarotCard]:
        """
        Return a shuffled copy of the deck.

        Args:
            seed: Optional seed for reproducible shuffles

        Returns:
            New list with cards in shuffled order
        """
        cards = list(self._cards)
        rng = random.Random(seed)
        rng.shuffle(cards)
        return cards

    def draw(
        self,
        count: int,
        seed: int | None = None,
        allow_reversals: bool = True,
    ) -> list[DrawnCard]:
        """
        Draw cards from the deck.

        Args:
            count: Number of cards to draw
            seed: Optional seed for reproducibility
            allow_reversals: Whether cards can be reversed

        Returns:
            List of DrawnCard with card info and orientation
        """
        if count > len(self._cards):
            raise ValueError(f"Cannot draw {count} cards from a {len(self._cards)}-card deck")

        rng = random.Random(seed)
        shuffled = list(self._cards)
        rng.shuffle(shuffled)

        drawn = []
        for i, card in enumerate(shuffled[:count]):
            # Determine orientation
            if allow_reversals:
                is_reversed = rng.random() < 0.5
                orientation = Orientation.REVERSED if is_reversed else Orientation.UPRIGHT
            else:
                orientation = Orientation.UPRIGHT

            drawn.append(
                DrawnCard(
                    card_id=card.card_id,
                    card_name=card.card_name,
                    position_index=i,
                    position_name="",  # Will be filled when assigned to spread
                    orientation=orientation,
                    image_path=self.get_image_path(card),
                )
            )

        return drawn

    def __len__(self) -> int:
        return len(self._cards)

    def __repr__(self) -> str:
        return f"TarotDeck({len(self._cards)} cards)"


# Convenience function
def load_tarot_deck(
    card_data_path: Path | str | None = None,
    image_path: Path | str | None = None,
    image_format: str = "jpg",
    system: str = "tarot",
) -> TarotDeck:
    """
    Convenience function to load a tarot deck.

    Args:
        card_data_path: Path to card JSON files
        image_path: Path to card images
        image_format: Image file extension
        system: Card system subdirectory (default: 'tarot')

    Returns:
        Loaded TarotDeck
    """
    return TarotDeck.load(card_data_path, image_path, image_format, system=system)
