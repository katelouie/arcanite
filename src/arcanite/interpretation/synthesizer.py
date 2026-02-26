"""
Arcanite Reading Synthesizer

Layer 2: Uses LLM to synthesize assembled context into a cohesive reading.
"""

from pathlib import Path

import yaml
from jinja2 import Template

from arcanite.core.models import AssembledContext, Reading, SynthesizedReading
from arcanite.interpretation.llm.providers import LLMProvider, get_provider


class TraditionPrompt:
    """A tradition-specific prompt template."""

    def __init__(self, name: str, description: str, system: str, user: str):
        self.name = name
        self.description = description
        self.system_template = Template(system)
        self.user_template = Template(user)

    @classmethod
    def load(cls, tradition: str, prompts_path: Path | None = None) -> "TraditionPrompt":
        """Load a tradition prompt from YAML."""
        if prompts_path is None:
            prompts_path = Path(__file__).parent.parent / "prompts" / "traditions"

        yaml_path = prompts_path / f"{tradition}.yaml"
        if not yaml_path.exists():
            raise FileNotFoundError(f"Tradition not found: {tradition} (looked in {yaml_path})")

        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        return cls(
            name=data.get("name", tradition),
            description=data.get("description", ""),
            system=data.get("system", ""),
            user=data.get("user", ""),
        )

    def render(self, context: AssembledContext) -> tuple[str, str]:
        """Render the prompts with context data."""
        template_data = {
            "spread_name": context.spread_name,
            "question": context.question,
            "question_type": context.question_type.value if context.question_type else None,
            "cards": [
                {
                    "card_name": c.card_name,
                    "position_name": c.position_name,
                    "position_description": c.position_description,
                    "orientation": c.orientation.value,
                    "position_interpretation": c.position_interpretation,
                    "position_keywords": c.position_keywords,
                    "question_context": c.question_context,
                    "core_essence": c.core_essence,
                }
                for c in context.card_interpretations
            ],
            "relationships": [
                {
                    "card1_name": r.card1_name,
                    "card2_name": r.card2_name,
                    "relationship_type": r.relationship_type.value,
                    "interpretation": r.interpretation,
                }
                for r in context.relationships
            ],
        }

        system = self.system_template.render(**template_data)
        user = self.user_template.render(**template_data)

        return system.strip(), user.strip()


class ReadingSynthesizer:
    """Synthesizes readings using LLM and tradition prompts."""

    def __init__(
        self,
        provider: LLMProvider | None = None,
        provider_name: str = "anthropic",
        tradition: str = "intuitive",
        prompts_path: Path | None = None,
    ):
        if provider is not None:
            self._provider = provider
        else:
            self._provider = get_provider(provider_name, temperature=0.7, max_tokens=2000)

        self._tradition = TraditionPrompt.load(tradition, prompts_path)
        self._tradition_name = tradition

    async def synthesize(
        self,
        reading: Reading,
        context: AssembledContext,
    ) -> SynthesizedReading:
        """
        Synthesize a reading into a cohesive narrative.

        Args:
            reading: The original reading
            context: The assembled context from Layer 1

        Returns:
            SynthesizedReading with the LLM's narrative
        """
        system, user = self._tradition.render(context)

        response = await self._provider.complete(prompt=user, system=system)

        return SynthesizedReading(
            reading_id=reading.id,
            spread_name=reading.spread_name,
            question=reading.question,
            question_type=reading.question_type,
            tradition=self._tradition_name,
            synthesis=response.content,
            assembled_context=context,
            model_used=self._provider.model_name,
            tokens_used=response.total_tokens,
        )


async def synthesize_reading(
    reading: Reading,
    context: AssembledContext,
    tradition: str = "intuitive",
    provider_name: str = "anthropic",
) -> SynthesizedReading:
    """Convenience function to synthesize a reading."""
    synthesizer = ReadingSynthesizer(
        provider_name=provider_name,
        tradition=tradition,
    )
    return await synthesizer.synthesize(reading, context)
