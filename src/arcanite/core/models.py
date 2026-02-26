"""
Arcanite Core Models

Pydantic models for cards, spreads, readings, and interpretations.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Enums
# =============================================================================


class Orientation(str, Enum):
    """Card orientation in a reading."""

    UPRIGHT = "upright"
    REVERSED = "reversed"


class QuestionType(str, Enum):
    """Types of questions for context-aware interpretations."""

    LOVE = "love"
    CAREER = "career"
    SPIRITUAL = "spiritual"
    FINANCIAL = "financial"
    HEALTH = "health"
    GENERAL = "general"


class RelationshipType(str, Enum):
    """Types of relationships between cards."""

    AMPLIFIES = "amplifies"
    CHALLENGES = "challenges"
    CLARIFIES = "clarifies"
    SIMILAR_ENERGY = "similar_energy"
    OPPOSITE_ENERGY = "opposite_energy"
    LEARNING_SEQUENCE = "learning_sequence"


# =============================================================================
# Card Models
# =============================================================================


class CoreMeaning(BaseModel):
    """Core meaning for upright or reversed orientation."""

    essence: str
    keywords: list[str]
    psychological: str
    spiritual: str
    practical: str
    shadow: str


class PositionInterpretation(BaseModel):
    """Interpretation for a specific position (upright + reversed)."""

    upright: str
    reversed: str
    keywords: list[str] = Field(default_factory=list)


class QuestionContext(BaseModel):
    """Question-specific interpretation."""

    upright: str
    reversed: str
    keywords: list[str] = Field(default_factory=list)


class CardRelationship(BaseModel):
    """Relationship between two cards."""

    interpretation: str
    keywords: list[str] = Field(default_factory=list)


class ElementalCorrespondences(BaseModel):
    """Elemental and astrological correspondences."""

    element: str | None = None
    zodiac: str | None = None
    hebrew_letter: str | None = None
    numerology: int | None = None
    planet: str | None = None
    season: str | None = None
    time_of_day: str | None = None
    colors: list[str] = Field(default_factory=list)
    crystals: list[str] = Field(default_factory=list)
    herbs: list[str] = Field(default_factory=list)


# =============================================================================
# Spread Models
# =============================================================================


class LayoutPosition(BaseModel):
    """Visual position in a spread layout."""

    x: float  # Percentage 0-100
    y: float  # Percentage 0-100
    rotation: float = 0  # Degrees
    z_index: int = Field(default=0, alias="zIndex")

    model_config = ConfigDict(populate_by_name=True)


class SpreadPosition(BaseModel):
    """Definition of a position in a spread."""

    name: str
    short_description: str
    detailed_description: str = ""
    keywords: list[str] = Field(default_factory=list)
    rag_mapping: str  # e.g., "temporal_positions.past"
    question_adaptations: dict[str, str] = Field(default_factory=dict)


class SpreadLayout(BaseModel):
    """Visual layout configuration for a spread."""

    name: str
    positions: list[LayoutPosition]


class SpreadDefinition(BaseModel):
    """Complete spread definition."""

    id: str
    name: str
    description: str
    layout_id: str  # Reference to layout in layouts dict
    layout: SpreadLayout | None = None  # Populated after loading
    card_size: str = Field(default="medium", alias="cardSize")
    aspect_ratio: float = Field(default=1.0, alias="aspectRatio")
    category: str = "general"
    difficulty: str = "beginner"
    positions: list[SpreadPosition]

    model_config = ConfigDict(populate_by_name=True)


# =============================================================================
# Reading Models
# =============================================================================


class DrawnCard(BaseModel):
    """A card drawn for a reading, with position and orientation."""

    card_id: str
    card_name: str
    position_index: int
    position_name: str
    orientation: Orientation = Orientation.UPRIGHT

    # These are populated during assembly
    image_path: Path | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Reading(BaseModel):
    """A complete reading with spread and drawn cards."""

    id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    created_at: datetime = Field(default_factory=datetime.now)
    spread_id: str
    spread_name: str
    question: str | None = None
    question_type: QuestionType | None = None
    drawn_cards: list[DrawnCard]
    allow_reversals: bool = True
    seed: int | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


# =============================================================================
# Interpretation Models
# =============================================================================


class CardInterpretation(BaseModel):
    """Assembled interpretation for a single card in context."""

    card_id: str
    card_name: str
    position_index: int
    position_name: str
    position_description: str
    orientation: Orientation

    # Core interpretation from RAG mapping
    position_interpretation: str
    position_keywords: list[str] = Field(default_factory=list)

    # Optional question context
    question_context: str | None = None
    question_keywords: list[str] = Field(default_factory=list)

    # Card metadata for display
    core_essence: str = ""
    core_keywords: list[str] = Field(default_factory=list)

    # Image path for rendering
    image_path: Path | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CardRelationshipMatch(BaseModel):
    """A matched relationship between two cards in the reading."""

    card1_id: str
    card1_name: str
    card2_id: str
    card2_name: str
    relationship_type: RelationshipType
    interpretation: str
    keywords: list[str] = Field(default_factory=list)


class AssembledContext(BaseModel):
    """
    Layer 1 output: Deterministic assembly of card interpretations.

    This can be used directly or fed to an LLM for synthesis.
    """

    reading_id: str
    spread_name: str
    question: str | None = None
    question_type: QuestionType | None = None

    # Card-by-card interpretations
    card_interpretations: list[CardInterpretation]

    # Relationships found between drawn cards
    relationships: list[CardRelationshipMatch] = Field(default_factory=list)

    # Raw data for template rendering
    raw_cards_data: list[dict[str, Any]] = Field(default_factory=list)

    def to_markdown(self) -> str:
        """Render the assembled context as markdown for LLM consumption."""
        lines = [
            f"# Tarot Reading: {self.spread_name}",
            "",
        ]

        if self.question:
            lines.append(f"**Question:** {self.question}")
            lines.append("")

        if self.question_type:
            lines.append(f"**Question Type:** {self.question_type.value}")
            lines.append("")

        lines.append("## Cards Drawn")
        lines.append("")

        for card in self.card_interpretations:
            lines.append(f"### Position {card.position_index + 1}: {card.position_name}")
            lines.append(f"**{card.card_name}** ({card.orientation.value})")
            lines.append("")
            lines.append(f"*Position meaning:* {card.position_description}")
            lines.append("")
            lines.append(f"**Interpretation:** {card.position_interpretation}")
            lines.append("")

            if card.position_keywords:
                lines.append(f"*Keywords:* {', '.join(card.position_keywords)}")
                lines.append("")

            if card.question_context:
                lines.append(f"**{self.question_type.value.title()} Context:** {card.question_context}")
                lines.append("")

            lines.append("---")
            lines.append("")

        if self.relationships:
            lines.append("## Card Relationships")
            lines.append("")
            for rel in self.relationships:
                lines.append(
                    f"- **{rel.card1_name}** {rel.relationship_type.value.replace('_', ' ')} "
                    f"**{rel.card2_name}**: {rel.interpretation}"
                )
            lines.append("")

        return "\n".join(lines)


class SynthesizedReading(BaseModel):
    """
    Layer 2 output: LLM-synthesized interpretation.
    """

    reading_id: str
    spread_name: str
    question: str | None = None
    question_type: QuestionType | None = None
    tradition: str

    # The synthesized narrative
    synthesis: str

    # Original assembled context (for reference/fallback)
    assembled_context: AssembledContext

    # Metadata
    model_used: str = ""
    tokens_used: int = 0


# =============================================================================
# Configuration Models
# =============================================================================


class DeckConfig(BaseModel):
    """Configuration for loading a deck."""

    card_data_path: Path = Path("cards/json")
    image_path: Path = Path("images/cards_github")
    image_format: str = "jpg"


class ReadingConfig(BaseModel):
    """Configuration for creating a reading."""

    spread_id: str
    question: str | None = None
    question_type: QuestionType | None = None
    auto_classify_question: bool = False
    allow_reversals: bool = True
    seed: int | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class LLMConfig(BaseModel):
    """Configuration for LLM providers."""

    provider: str = "anthropic"  # anthropic, openai, local
    model: str = "claude-sonnet-4-20250514"
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4000


class PDFConfig(BaseModel):
    """Configuration for PDF rendering."""

    include_spread_visual: bool = True
    include_card_sections: bool = True
    include_card_images: bool = True
    include_relationships: bool = True
    page_size: str = "letter"  # letter, a4

    model_config = ConfigDict(arbitrary_types_allowed=True)
