"""
Arcanite Render Module

PDF rendering for tarot readings using Typst.
"""

from arcanite.render.typst_renderer import (
    TypstRenderer,
    render_reading_to_pdf,
)

__all__ = [
    "TypstRenderer",
    "render_reading_to_pdf",
]


def get_default_renderer() -> TypstRenderer:
    """Get a default TypstRenderer instance."""
    return TypstRenderer()
