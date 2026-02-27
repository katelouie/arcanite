"""
Arcanite Spread Loader

Loads spread definitions from JSON configuration.
"""

import json
from pathlib import Path
from typing import Any

from arcanite.core.models import (
    LayoutPosition,
    SpreadDefinition,
    SpreadLayout,
    SpreadPosition,
)


class SpreadRegistry:
    """
    Registry for loading and accessing spread definitions.

    Implements the SpreadLoader protocol.
    """

    def __init__(
        self,
        spreads: dict[str, SpreadDefinition],
        layouts: dict[str, SpreadLayout],
    ):
        self._spreads = spreads
        self._layouts = layouts

    @classmethod
    def from_config(
        cls,
        config_path: Path | str | None = None,
        package_root: Path | str | None = None,
        system: str = "tarot",
    ) -> "SpreadRegistry":
        """
        Load spreads from the configuration file.

        Args:
            config_path: Path to spreads config file
            package_root: Root path of the arcanite package
            system: Card system (default: 'tarot') - determines config file name

        Returns:
            SpreadRegistry instance
        """
        if package_root is None:
            package_root = Path(__file__).parent.parent

        if config_path is None:
            config_path = package_root / "spreads" / f"{system}-spreads.json"
        else:
            config_path = Path(config_path)

        with open(config_path) as f:
            data = json.load(f)

        # Parse layouts
        layouts = {}
        for layout_id, layout_data in data.get("layouts", {}).items():
            positions = [
                LayoutPosition(
                    x=pos["x"],
                    y=pos["y"],
                    rotation=pos.get("rotation", 0),
                    z_index=pos.get("zIndex", 0),
                )
                for pos in layout_data["positions"]
            ]
            layouts[layout_id] = SpreadLayout(
                name=layout_data["name"],
                positions=positions,
            )

        # Parse spreads
        spreads = {}
        for spread_data in data.get("spreads", []):
            spread_id = spread_data["id"]

            # Parse positions
            positions = []
            for pos_data in spread_data.get("positions", []):
                positions.append(
                    SpreadPosition(
                        name=pos_data["name"],
                        short_description=pos_data.get("short_description", ""),
                        detailed_description=pos_data.get("detailed_description", ""),
                        keywords=pos_data.get("keywords", []),
                        rag_mapping=pos_data.get("rag_mapping", "temporal_positions.present"),
                        question_adaptations=pos_data.get("question_adaptations", {}),
                    )
                )

            # Get the layout
            layout_id = spread_data.get("layout", "")
            layout = layouts.get(layout_id)

            spread = SpreadDefinition(
                id=spread_id,
                name=spread_data["name"],
                description=spread_data.get("description", ""),
                layout_id=layout_id,
                layout=layout,
                card_size=spread_data.get("cardSize", "medium"),
                aspect_ratio=spread_data.get("aspectRatio", 1.0),
                category=spread_data.get("category", "general"),
                difficulty=spread_data.get("difficulty", "beginner"),
                positions=positions,
            )
            spreads[spread_id] = spread

        return cls(spreads, layouts)

    def load_spread(self, spread_id: str) -> SpreadDefinition:
        """Load a spread definition by ID."""
        if spread_id not in self._spreads:
            available = ", ".join(sorted(self._spreads.keys()))
            raise KeyError(f"Spread not found: {spread_id}. Available: {available}")
        return self._spreads[spread_id]

    # Alias for protocol compatibility
    def get(self, spread_id: str) -> SpreadDefinition:
        """Load a spread definition by ID (protocol method)."""
        return self.load_spread(spread_id)

    def list_spreads(self) -> list[str]:
        """List all available spread IDs."""
        return sorted(self._spreads.keys())

    def get_spread_info(self) -> list[dict[str, Any]]:
        """Get summary info for all spreads."""
        return [
            {
                "id": spread.id,
                "name": spread.name,
                "description": spread.description,
                "positions": len(spread.positions),
                "category": spread.category,
                "difficulty": spread.difficulty,
            }
            for spread in self._spreads.values()
        ]

    def get_layout(self, layout_id: str) -> SpreadLayout:
        """Get a layout by ID."""
        if layout_id not in self._layouts:
            raise KeyError(f"Layout not found: {layout_id}")
        return self._layouts[layout_id]

    @property
    def spreads(self) -> dict[str, SpreadDefinition]:
        """All loaded spreads."""
        return self._spreads

    @property
    def layouts(self) -> dict[str, SpreadLayout]:
        """All loaded layouts."""
        return self._layouts

    def __len__(self) -> int:
        return len(self._spreads)

    def __repr__(self) -> str:
        return f"SpreadRegistry({len(self._spreads)} spreads, {len(self._layouts)} layouts)"


# Module-level singleton for convenience
_default_registry: SpreadRegistry | None = None


def get_spread_registry(
    config_path: Path | str | None = None,
    reload: bool = False,
    system: str = "tarot",
) -> SpreadRegistry:
    """
    Get the default spread registry (singleton).

    Args:
        config_path: Optional custom config path
        reload: Force reload even if already loaded
        system: Card system (default: 'tarot')

    Returns:
        SpreadRegistry instance
    """
    global _default_registry

    if _default_registry is None or reload:
        _default_registry = SpreadRegistry.from_config(config_path, system=system)

    return _default_registry


def load_spread(spread_id: str) -> SpreadDefinition:
    """
    Convenience function to load a spread by ID.

    Uses the default registry.
    """
    return get_spread_registry().load_spread(spread_id)


def list_spreads() -> list[str]:
    """List all available spread IDs."""
    return get_spread_registry().list_spreads()
