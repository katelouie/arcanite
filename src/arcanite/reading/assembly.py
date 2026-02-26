"""
Arcanite Deterministic Assembly

Layer 1: Assembles card interpretations using RAG mapping from spread positions.
"""

from arcanite.core.deck import TarotDeck
from arcanite.core.models import (
    AssembledContext,
    CardInterpretation,
    CardRelationshipMatch,
    Orientation,
    QuestionType,
    Reading,
    RelationshipType,
    SpreadDefinition,
)
from arcanite.core.spread import get_spread_registry


class DeterministicAssembler:
    """
    Assembles card interpretations using RAG mapping.

    This is Layer 1 - no LLM, just deterministic lookup of
    position-specific interpretations from card data.
    """

    def __init__(self, deck: TarotDeck):
        self._deck = deck
        self._spread_registry = get_spread_registry()

    def assemble(
        self,
        reading: Reading,
        question_type: QuestionType | str | None = None,
        include_relationships: bool = True,
    ) -> AssembledContext:
        """
        Assemble interpretations for all cards in a reading.

        Args:
            reading: The reading with drawn cards
            question_type: Optional question type for context
            include_relationships: Whether to detect card relationships

        Returns:
            AssembledContext with all interpretations assembled
        """
        # Get the spread definition
        spread = self._spread_registry.load_spread(reading.spread_id)

        # Normalize question_type
        if isinstance(question_type, str):
            question_type = QuestionType(question_type)
        elif question_type is None:
            question_type = reading.question_type

        # Assemble each card's interpretation
        card_interpretations = []
        raw_cards_data = []

        for drawn_card in reading.drawn_cards:
            # Get the card object
            card = self._deck.get_card(drawn_card.card_id)

            # Get the position definition
            position = spread.positions[drawn_card.position_index]

            # Get interpretation using RAG mapping
            is_reversed = drawn_card.orientation == Orientation.REVERSED
            interp_data = card.get_interpretation(position.rag_mapping, is_reversed)

            # Get question context if applicable
            question_context = None
            question_keywords = []
            if question_type and question_type != QuestionType.GENERAL:
                qc_data = card.get_question_context(question_type.value, is_reversed)
                question_context = qc_data.get("interpretation", "")
                question_keywords = qc_data.get("keywords", [])

            # Get core meaning for additional context
            core_meaning = card.get_core_meaning(is_reversed)

            card_interpretations.append(
                CardInterpretation(
                    card_id=drawn_card.card_id,
                    card_name=drawn_card.card_name,
                    position_index=drawn_card.position_index,
                    position_name=position.name,
                    position_description=position.detailed_description or position.short_description,
                    orientation=drawn_card.orientation,
                    position_interpretation=interp_data.get("interpretation", ""),
                    position_keywords=interp_data.get("keywords", []),
                    question_context=question_context,
                    question_keywords=question_keywords,
                    core_essence=core_meaning.get("essence", ""),
                    core_keywords=core_meaning.get("keywords", []),
                    image_path=drawn_card.image_path,
                )
            )

            # Store raw data for template rendering
            raw_cards_data.append({
                "card_id": drawn_card.card_id,
                "card_name": drawn_card.card_name,
                "position_index": drawn_card.position_index,
                "position_name": position.name,
                "position_description": position.detailed_description or position.short_description,
                "orientation": drawn_card.orientation.value,
                "position_interpretation": interp_data.get("interpretation", ""),
                "position_keywords": interp_data.get("keywords", []),
                "question_context": question_context,
                "question_keywords": question_keywords,
                "core_essence": core_meaning.get("essence", ""),
                "core_keywords": core_meaning.get("keywords", []),
                "image_path": str(drawn_card.image_path) if drawn_card.image_path else None,
                "raw_card_data": card.raw_data,
            })

        # Detect relationships between cards
        relationships = []
        if include_relationships:
            relationships = self._find_relationships(reading)

        return AssembledContext(
            reading_id=reading.id,
            spread_name=reading.spread_name,
            question=reading.question,
            question_type=question_type,
            card_interpretations=card_interpretations,
            relationships=relationships,
            raw_cards_data=raw_cards_data,
        )

    def _find_relationships(self, reading: Reading) -> list[CardRelationshipMatch]:
        """
        Find relationships between cards in the reading.

        Scans all pairs of drawn cards and checks for defined relationships.
        """
        relationships = []
        drawn_ids = {dc.card_id for dc in reading.drawn_cards}

        for drawn_card in reading.drawn_cards:
            card = self._deck.get_card(drawn_card.card_id)
            card_relationships = card.get_relationships()

            # Check each relationship type
            for rel_type_str, related_cards in card_relationships.items():
                try:
                    rel_type = RelationshipType(rel_type_str)
                except ValueError:
                    continue  # Skip unknown relationship types

                for other_card_id, rel_data in related_cards.items():
                    # Check if the other card is in our reading
                    if other_card_id in drawn_ids and other_card_id != drawn_card.card_id:
                        # Get the other card's name
                        other_card = self._deck.get_card(other_card_id)

                        # Avoid duplicates (A->B and B->A)
                        # Only add if card1 < card2 alphabetically
                        if drawn_card.card_id < other_card_id:
                            interpretation = rel_data.get("interpretation", "")
                            # Skip placeholder interpretations
                            if interpretation and not interpretation.startswith("[TO BE WRITTEN"):
                                relationships.append(
                                    CardRelationshipMatch(
                                        card1_id=drawn_card.card_id,
                                        card1_name=drawn_card.card_name,
                                        card2_id=other_card_id,
                                        card2_name=other_card.card_name,
                                        relationship_type=rel_type,
                                        interpretation=interpretation,
                                        keywords=rel_data.get("keywords", []),
                                    )
                                )

        return relationships


def assemble_context(
    reading: Reading,
    deck: TarotDeck,
    question_type: QuestionType | str | None = None,
    include_relationships: bool = True,
) -> AssembledContext:
    """
    Convenience function to assemble a reading's context.

    Args:
        reading: The reading to assemble
        deck: The tarot deck (for card lookups)
        question_type: Optional question type
        include_relationships: Whether to include card relationships

    Returns:
        AssembledContext with all interpretations
    """
    assembler = DeterministicAssembler(deck)
    return assembler.assemble(
        reading=reading,
        question_type=question_type,
        include_relationships=include_relationships,
    )
