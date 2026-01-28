"""Rich text renderer for HTML and JSON formats."""
import base64
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class RenderedImage:
    """Rendered image data."""

    filename: str
    mime_type: str
    base64_data: str
    width: Optional[int]
    height: Optional[int]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "filename": self.filename,
            "mime_type": self.mime_type,
            "base64_data": self.base64_data,
            "width": self.width,
            "height": self.height,
        }

    def get_data_uri(self) -> str:
        """Get data URI for embedding in HTML/JSON."""
        return f"data:{self.mime_type};base64,{self.base64_data}"


@dataclass
class RenderedTable:
    """Rendered table data."""

    rows: int
    cols: int
    html: str
    json_data: Optional[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "row_count": self.rows,
            "col_count": self.cols,
            "html": self.html,
            "json_data": self.json_data,
        }


class RichTextRenderer:
    """Renderer for converting parsed content to HTML and rich text JSON."""

    def __init__(self):
        self.content_blocks: List[Dict[str, Any]] = []

    def add_heading(self, text: str, level: int = 2) -> None:
        """Add a heading block."""
        self.content_blocks.append(
            {
                "type": "heading",
                "attrs": {"level": min(level, 6)},
                "content": [{"type": "text", "text": text}] if text else [],
            }
        )

    def add_paragraph(self, text: str) -> None:
        """Add a paragraph block."""
        if text.strip():
            self.content_blocks.append(
                {"type": "paragraph", "content": [{"type": "text", "text": text}]}
            )

    def add_image(
        self, image: RenderedImage, alt: Optional[str] = None
    ) -> None:
        """Add an image block."""
        self.content_blocks.append(
            {
                "type": "image",
                "attrs": {
                    "src": image.get_data_uri(),
                    "alt": alt,
                    "width": image.width,
                    "height": image.height,
                },
            }
        )

    def add_table(self, table: RenderedTable) -> None:
        """Add a table block."""
        if table.json_data:
            self.content_blocks.append(table.json_data)
        else:
            # Fallback to HTML content
            self.content_blocks.append(
                {"type": "html", "content": table.html}
            )

    def render_html(self) -> str:
        """Render content as HTML string."""
        html_parts = []

        for block in self.content_blocks:
            block_type = block.get("type")

            if block_type == "heading":
                level = block.get("attrs", {}).get("level", 2)
                text = self._extract_text(block.get("content", []))
                html_parts.append(f"<h{level}>{text}</h{level}>")

            elif block_type == "paragraph":
                text = self._extract_text(block.get("content", []))
                html_parts.append(f"<p>{text}</p>")

            elif block_type == "image":
                attrs = block.get("attrs", {})
                src = attrs.get("src", "")
                alt = attrs.get("alt", "")
                width = attrs.get("width")
                height = attrs.get("height")
                img_attrs = f' src="{src}" alt="{alt}"'
                if width:
                    img_attrs += f' width="{width}"'
                if height:
                    img_attrs += f' height="{height}"'
                html_parts.append(f"<img{img_attrs} />")

            elif block_type == "table":
                html_parts.append(block.get("html", ""))

            elif block_type == "html":
                html_parts.append(block.get("content", ""))

        return "".join(html_parts)

    def render_json(self) -> Dict[str, Any]:
        """Render content as TipTap-compatible JSON."""
        return {"type": "doc", "content": self.content_blocks}

    def clear(self) -> None:
        """Clear all content blocks."""
        self.content_blocks.clear()

    def _extract_text(self, content: List[Dict[str, Any]]) -> str:
        """Extract text from content array."""
        texts = []
        for item in content:
            if item.get("type") == "text":
                texts.append(item.get("text", ""))
        return "".join(texts)


def encode_image_to_base64(image_data: bytes, mime_type: str) -> str:
    """Encode image data to base64 string.

    Args:
        image_data: Raw image bytes
        mime_type: MIME type of the image

    Returns:
        Base64 encoded string
    """
    return base64.b64encode(image_data).decode("utf-8")


def table_to_html(rows: List[List[str]]) -> str:
    """Convert table data to HTML.

    Args:
        rows: List of rows, each row is a list of cell strings

    Returns:
        HTML table string
    """
    if not rows:
        return ""

    html_parts = ["<table>"]

    for i, row in enumerate(rows):
        html_parts.append("<tr>")
        for cell in row:
            tag = "th" if i == 0 else "td"
            html_parts.append(f"<{tag}>{cell}</{tag}>")
        html_parts.append("</tr>")

    html_parts.append("</table>")
    return "".join(html_parts)


def table_to_json(rows: List[List[str]]) -> Dict[str, Any]:
    """Convert table data to TipTap-compatible JSON.

    Args:
        rows: List of rows, each row is a list of cell strings

    Returns:
        TipTap table JSON
    """
    if not rows:
        return {}

    # Build table content
    table_rows = []
    for row_data in rows:
        cells = []
        for cell in row_data:
            cells.append(
                {
                    "type": "tableCell",
                    "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": cell}]}
                    ],
                }
            )
        table_rows.append({"type": "tableRow", "content": cells})

    return {"type": "table", "content": table_rows}
