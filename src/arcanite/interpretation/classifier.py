"""
Arcanite Question Classifier

Uses an LLM to classify tarot questions into categories for context-aware interpretations.
"""

from arcanite.core.models import QuestionType
from arcanite.interpretation.llm.providers import LLMProvider, get_provider


CLASSIFICATION_PROMPT = """Classify this tarot question into exactly ONE of these categories:

- love (relationships, romance, partnership, dating, marriage, breakups, soulmates)
- career (work, profession, business, job, employment, promotion, colleagues)
- spiritual (growth, purpose, meaning, path, enlightenment, meditation, soul)
- financial (money, resources, material, wealth, investments, debt, abundance)
- health (physical, mental, wellness, healing, illness, energy, vitality)
- general (none of the above, or multiple categories equally)

Question: "{question}"

Respond with ONLY the category name, nothing else. Just one word."""


class QuestionClassifier:
    """
    Classifies tarot questions into categories using an LLM.

    This enables context-aware interpretations by selecting the appropriate
    question_context from card data.
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
        provider_name: str = "anthropic",
        model: str | None = None,
    ):
        """
        Initialize the classifier.

        Args:
            provider: An LLM provider instance (if None, creates one)
            provider_name: Which provider to create if none given
            model: Model to use (provider default if not specified)
        """
        if provider is not None:
            self._provider = provider
        else:
            kwargs = {}
            if model:
                kwargs["model"] = model
            # Use lower temperature for classification (more deterministic)
            kwargs["temperature"] = 0.1
            kwargs["max_tokens"] = 20  # We only need one word
            self._provider = get_provider(provider_name, **kwargs)

    @property
    def provider(self) -> LLMProvider:
        return self._provider

    async def classify(self, question: str) -> QuestionType:
        """
        Classify a question into a QuestionType.

        Args:
            question: The user's tarot question

        Returns:
            The classified QuestionType
        """
        if not question or not question.strip():
            return QuestionType.GENERAL

        prompt = CLASSIFICATION_PROMPT.format(question=question.strip())

        response = await self._provider.complete(
            prompt=prompt,
            temperature=0.1,  # Low temperature for consistent classification
            max_tokens=20,
        )

        # Parse the response
        category = response.content.strip().lower()

        # Map to QuestionType
        type_map = {
            "love": QuestionType.LOVE,
            "career": QuestionType.CAREER,
            "spiritual": QuestionType.SPIRITUAL,
            "financial": QuestionType.FINANCIAL,
            "health": QuestionType.HEALTH,
            "general": QuestionType.GENERAL,
        }

        return type_map.get(category, QuestionType.GENERAL)

    async def classify_with_confidence(
        self,
        question: str,
    ) -> tuple[QuestionType, str]:
        """
        Classify a question and return the raw LLM response for debugging.

        Args:
            question: The user's tarot question

        Returns:
            Tuple of (QuestionType, raw_response)
        """
        if not question or not question.strip():
            return QuestionType.GENERAL, ""

        prompt = CLASSIFICATION_PROMPT.format(question=question.strip())

        response = await self._provider.complete(
            prompt=prompt,
            temperature=0.1,
            max_tokens=20,
        )

        category = response.content.strip().lower()

        type_map = {
            "love": QuestionType.LOVE,
            "career": QuestionType.CAREER,
            "spiritual": QuestionType.SPIRITUAL,
            "financial": QuestionType.FINANCIAL,
            "health": QuestionType.HEALTH,
            "general": QuestionType.GENERAL,
        }

        return type_map.get(category, QuestionType.GENERAL), response.content


async def classify_question(
    question: str,
    provider: LLMProvider | None = None,
    provider_name: str = "anthropic",
) -> QuestionType:
    """
    Convenience function to classify a question.

    Args:
        question: The tarot question to classify
        provider: Optional LLM provider
        provider_name: Provider to use if none given

    Returns:
        The classified QuestionType
    """
    classifier = QuestionClassifier(provider=provider, provider_name=provider_name)
    return await classifier.classify(question)
