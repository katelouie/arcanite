"""
Arcanite Typst Renderer

Renders tarot readings to PDF using Typst templates.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import typst
except ImportError:
    typst = None  # type: ignore

from arcanite.core.models import (
    AssembledContext,
    PDFConfig,
    Reading,
    SpreadDefinition,
    SynthesizedReading,
)


class TypstRenderer:
    """
    Renders tarot readings to PDF using Typst.

    Takes a SynthesizedReading (or AssembledContext) and generates a
    professionally formatted PDF report.
    """

    def __init__(
        self,
        template_path: Path | str | None = None,
        config: PDFConfig | None = None,
    ):
        """
        Initialize the renderer.

        Args:
            template_path: Path to custom Typst template. If None, uses built-in template.
            config: PDF rendering configuration.
        """
        if template_path is None:
            # Use the bundled template
            template_path = Path(__file__).parent.parent / "templates" / "reading.typ"
        self._template_path = Path(template_path)
        self._config = config or PDFConfig()

    def render(
        self,
        reading: SynthesizedReading | AssembledContext,
        output_path: Path | str,
        title: str | None = None,
        layout_positions: list[tuple[float, float, float]] | None = None,
    ) -> Path:
        """
        Render a reading to PDF.

        Args:
            reading: The reading to render (SynthesizedReading or AssembledContext)
            output_path: Where to save the PDF
            title: Custom title for the reading (default: "Tarot Reading")
            layout_positions: List of (x, y, rotation) tuples for spread visualization

        Returns:
            Path to the generated PDF
        """
        output_path = Path(output_path)

        # Generate the Typst source
        typst_source = self._generate_typst_source(reading, title, layout_positions)

        # Write to temp file and compile
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".typ",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(typst_source)
            temp_path = Path(f.name)

        try:
            self._compile_typst(temp_path, output_path)
        finally:
            temp_path.unlink(missing_ok=True)

        return output_path

    def _generate_typst_source(
        self,
        reading: SynthesizedReading | AssembledContext,
        title: str | None,
        layout_positions: list[tuple[float, float, float]] | None,
    ) -> str:
        """Generate Typst source code from reading data."""

        # Determine if we have a synthesized reading or just assembled context
        is_synthesized = isinstance(reading, SynthesizedReading)
        if is_synthesized:
            context = reading.assembled_context
            synthesis = reading.synthesis
        else:
            context = reading
            synthesis = ""  # No synthesis for deterministic-only

        # Build cards array
        cards_typst = self._build_cards_array(context)

        # Build relationships array
        relationships_typst = self._build_relationships_array(context)

        # Build layout positions
        layout_typst = self._build_layout_array(layout_positions)

        # Build the variable definitions
        variables = f'''
// Variables populated by Python renderer
#let reading_title = "{self._escape(title or "Tarot Reading")}"
#let spread_name = "{self._escape(context.spread_name)}"
#let reading_date = "{datetime.now().strftime("%B %d, %Y")}"
#let question = {self._typst_string(context.question)}
#let question_type = {self._typst_string(context.question_type.value if context.question_type else None)}

#let cards = {cards_typst}

#let relationships = {relationships_typst}

#let synthesis = {self._typst_content_block(synthesis)}

#let layout_positions = {layout_typst}

#let show_spread_visual = {str(self._config.include_spread_visual and layout_positions is not None).lower()}
#let show_card_images = {str(self._config.include_card_images).lower()}
#let show_relationships = {str(self._config.include_relationships).lower()}
#let show_synthesis = {str(is_synthesized).lower()}
'''

        # Read the template and inject variables
        template = self._template_path.read_text(encoding="utf-8")

        # Find where variables should be inserted (after the "Variables" section marker)
        marker = "// Variables (populated by Python)"
        if marker in template:
            # Replace the placeholder variables section
            before_vars = template.split(marker)[0]
            after_vars_marker = "// =============================================================================\n// Colors"
            if after_vars_marker in template:
                after_vars = after_vars_marker + template.split(after_vars_marker)[1]
                return before_vars + marker + "\n" + variables + "\n" + after_vars

        # Fallback: prepend variables
        return variables + "\n" + template


    def _build_cards_array(self, context: AssembledContext) -> str:
        """Build Typst array of card data."""
        cards = []
        for card in context.card_interpretations:
            # Get image path as string or none
            image_path = f'"{card.image_path}"' if card.image_path else "none"

            # Build keywords array (no limit)
            keywords = ", ".join(f'"{self._escape(k)}"' for k in card.position_keywords)

            # No truncation - include full text
            cards.append(
                f'("{self._escape(card.card_name)}", '
                f'"{self._escape(card.position_name)}", '
                f'"{card.orientation.value}", '
                f'{image_path}, '
                f'"{self._escape(card.position_interpretation)}", '
                f'({keywords}), '
                f'"{self._escape(card.position_description)}")'
            )

        return "(\n  " + ",\n  ".join(cards) + "\n)"

    def _build_relationships_array(self, context: AssembledContext) -> str:
        """Build Typst array of relationship data."""
        if not context.relationships:
            return "()"

        rels = []
        for rel in context.relationships:
            rel_type = rel.relationship_type.value.replace("_", " ")
            rels.append(
                f'("{self._escape(rel.card1_name)}", '
                f'"{self._escape(rel.card2_name)}", '
                f'" {self._escape(rel_type)} ", '
                f'"{self._escape(rel.interpretation[:300])}")'
            )

        return "(\n  " + ",\n  ".join(rels) + "\n)"

    def _build_layout_array(
        self, positions: list[tuple[float, float, float]] | None
    ) -> str:
        """Build Typst array of layout positions."""
        if not positions:
            return "()"

        pos_strs = [f"({x}, {y}, {r})" for x, y, r in positions]
        return "(" + ", ".join(pos_strs) + ")"

    def _escape(self, text: str) -> str:
        """Escape text for Typst strings."""
        if not text:
            return ""
        return (
            text.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "")
        )

    def _typst_string(self, value: str | None) -> str:
        """Convert Python string to Typst string or none."""
        if value is None or value == "":
            return "none"
        return f'"{self._escape(value)}"'

    def _typst_content_block(self, text: str) -> str:
        """Convert text to Typst content block with proper escaping."""
        if not text:
            return '[]'

        import re

        # Convert markdown to Typst markup
        lines = []
        for line in text.split("\n"):
            # Convert markdown headers to Typst
            if line.startswith("### "):
                line = f"=== {line[4:]}"
            elif line.startswith("## "):
                line = f"== {line[3:]}"
            elif line.startswith("# "):
                line = f"= {line[2:]}"
            else:
                # Convert **bold** to *bold* (Typst syntax)
                line = re.sub(r'\*\*(.+?)\*\*', r'*\1*', line)
                # Convert _italic_ stays the same in Typst

            lines.append(line)

        return '[\n' + '\n\n'.join(lines) + '\n]'

    def _compile_typst(self, input_path: Path, output_path: Path) -> None:
        """Compile Typst source to PDF."""
        if typst is None:
            raise RuntimeError(
                "typst package not found. Install it with: pip install typst"
            )

        try:
            # Use the Python typst package to compile
            pdf_bytes = typst.compile(input_path)
            output_path.write_bytes(pdf_bytes)
        except Exception as e:
            raise RuntimeError(f"Typst compilation failed:\n{e}")

    def render_to_bytes(
        self,
        reading: SynthesizedReading | AssembledContext,
        spread: SpreadDefinition | None = None,
        title: str | None = None,
    ) -> bytes:
        """
        Render a reading to PDF and return as bytes.

        This method aligns with the PDFRenderer protocol.

        Args:
            reading: The reading to render
            spread: Optional spread definition (for layout positions)
            title: Custom title for the reading

        Returns:
            PDF file contents as bytes
        """
        # Extract layout positions from spread if available
        layout_positions = None
        if spread and spread.layout:
            layout_positions = [
                (pos.x, pos.y, pos.rotation)
                for pos in spread.layout.positions
            ]

        # Render to a temp file and read the bytes
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_pdf = Path(f.name)

        try:
            self.render(reading, temp_pdf, title, layout_positions)
            return temp_pdf.read_bytes()
        finally:
            temp_pdf.unlink(missing_ok=True)


def render_reading_to_pdf(
    reading: SynthesizedReading | AssembledContext,
    output_path: Path | str,
    title: str | None = None,
    layout_positions: list[tuple[float, float, float]] | None = None,
    config: PDFConfig | None = None,
) -> Path:
    """
    Convenience function to render a reading to PDF.

    Args:
        reading: The reading to render
        output_path: Where to save the PDF
        title: Custom title (default: "Tarot Reading")
        layout_positions: (x, y, rotation) tuples for spread visualization
        config: PDF rendering options

    Returns:
        Path to the generated PDF
    """
    renderer = TypstRenderer(config=config)
    return renderer.render(reading, output_path, title, layout_positions)
