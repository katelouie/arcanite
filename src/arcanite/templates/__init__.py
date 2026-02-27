"""
Arcanite Templates

Typst templates for PDF rendering.
"""

from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent

def get_template_path(name: str = "reading") -> Path:
    """Get the path to a template file."""
    return TEMPLATES_DIR / f"{name}.typ"
