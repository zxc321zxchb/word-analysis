"""Number extraction from Word XML."""
import re
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from docx import Document


@dataclass
class NumberInfo:
    """Information about a paragraph number."""

    num_id: int
    ilvl: int
    number_path: str


@dataclass
class LevelDef:
    """Numbering level definition from Word's numbering.xml."""

    ilvl: int
    start: int = 1
    fmt: str = "decimal"
    lvl_text: str = "%1."  # Template like "%1.%2."


class WordNumberingExtractor:
    """Extract actual numbering from Word's numbering.xml.

    This parses the numbering part of a Word document to get the actual
    numbering templates and generate display numbers like "1.2.3".
    """

    def __init__(self, document: Document):
        """Initialize the numbering extractor.

        Args:
            document: python-docx Document object
        """
        self.document = document
        self._abstract_nums: Dict[int, Dict[int, LevelDef]] = {}
        self._num_to_abstract: Dict[int, int] = {}
        self._counters: Dict[int, Dict[int, int]] = {}
        self._used_paths: Dict[str, int] = {}  # Track duplicate paths globally

        self._parse_numbering_part()

    def _parse_numbering_part(self) -> None:
        """Parse the numbering.xml part from the Word document."""
        try:
            numbering_part = self.document.part.numbering_part
            if numbering_part is None:
                return

            xml = numbering_part.element

            # Parse abstractNum definitions
            for abstract_num in xml.abstractNum:
                abstract_num_id = int(abstract_num.abstractNumId.val)

                self._abstract_nums[abstract_num_id] = {}

                for lvl in abstract_num.lvl:
                    ilvl = int(lvl.ilvl.val)

                    # Get start value
                    start = 1
                    if lvl.start is not None:
                        start = int(lvl.start.val)

                    # Get format
                    fmt = "decimal"
                    if lvl.numFmt is not None:
                        fmt = lvl.numFmt.val

                    # Get level text template
                    lvl_text = "%1."
                    if lvl.lvlText is not None:
                        lvl_text = lvl.lvlText.val

                    self._abstract_nums[abstract_num_id][ilvl] = LevelDef(
                        ilvl=ilvl, start=start, fmt=fmt, lvl_text=lvl_text
                    )

            # Parse num definitions (numId -> abstractNumId mapping)
            for num in xml.num:
                num_id = int(num.numId.val)
                abstract_num_id = int(num.abstractNumId.val)
                self._num_to_abstract[num_id] = abstract_num_id

        except (AttributeError, TypeError):
            # No numbering part or parsing error
            pass

    def _get_level_def(self, num_id: int, ilvl: int) -> Optional[LevelDef]:
        """Get the level definition for a given numId and level.

        Args:
            num_id: Numbering definition ID
            ilvl: Indent level (0-indexed)

        Returns:
            LevelDef if found, None otherwise
        """
        if num_id not in self._num_to_abstract:
            return None

        abstract_num_id = self._num_to_abstract[num_id]
        if abstract_num_id not in self._abstract_nums:
            return None

        return self._abstract_nums[abstract_num_id].get(ilvl)

    def _generate_from_template(self, template: str, counters: List[int]) -> str:
        """Generate numbering from a template.

        Args:
            template: Template like "%1.%2." or "%1)"
            counters: List of counter values [1, 2, 3]

        Returns:
            Generated number like "1.2" or "1)"
        """
        result = template

        # Find all %N patterns and replace them
        for match in list(re.finditer(r"%(\d+)", result)):
            idx = int(match.group(1)) - 1  # %1 -> index 0
            if idx < len(counters):
                result = result.replace(match.group(0), str(counters[idx]), 1)

        # Remove trailing dot if present
        return result.rstrip(".")

    def get_number_info(self, paragraph) -> Optional[NumberInfo]:
        """Get number information for a paragraph.

        Args:
            paragraph: python-docx Paragraph object

        Returns:
            NumberInfo with actual display number, or None
        """
        try:
            element = paragraph._element

            if element.pPr is None:
                return None

            numPr = element.pPr.numPr
            if numPr is None:
                return None

            ilvl = numPr.ilvl.val if numPr.ilvl is not None else 0
            numId = numPr.numId.val if numPr.numId is not None else 0

            # Initialize counters for this numId
            if numId not in self._counters:
                self._counters[numId] = {}

            # Reset counters for deeper levels
            for level in range(ilvl + 1, 9):
                if level in self._counters[numId]:
                    del self._counters[numId][level]

            # Get level definition for template
            level_def = self._get_level_def(numId, ilvl)
            if level_def is None:
                # Fallback to simple decimal numbering
                # Build the full path like "1.2.3" for all levels up to current
                if ilvl not in self._counters[numId]:
                    self._counters[numId][ilvl] = 0
                self._counters[numId][ilvl] += 1

                # Build path from all levels up to current
                parts = [
                    str(self._counters[numId][lvl])
                    for lvl in range(ilvl + 1)
                    if lvl in self._counters[numId]
                ]
                number_path = ".".join(parts)
            else:
                # Initialize counter if needed
                if ilvl not in self._counters[numId]:
                    self._counters[numId][ilvl] = level_def.start - 1
                self._counters[numId][ilvl] += 1

                # Build counter list for all levels up to current
                counters = []
                for lvl in range(ilvl + 1):
                    if lvl in self._counters[numId]:
                        counters.append(self._counters[numId][lvl])

                # Generate from template
                number_path = self._generate_from_template(
                    level_def.lvl_text, counters
                )

            # Handle duplicate paths by adding a suffix (using dot for hierarchy)
            # Keep trying until we find a unique path
            final_path = number_path
            suffix = 1
            while final_path in self._used_paths:
                final_path = f"{number_path}.{suffix}"
                suffix += 1
            self._used_paths[final_path] = 0
            number_path = final_path

            return NumberInfo(num_id=numId, ilvl=ilvl, number_path=number_path)

        except (AttributeError, TypeError):
            return None

    def reset(self) -> None:
        """Reset all counters."""
        self._counters.clear()
        self._used_paths.clear()


# Legacy NumberingTracker class - kept for backward compatibility
class NumberingTracker:
    """Track numbering state to build hierarchical paths."""

    def __init__(self):
        # Track separate counters for each numId (numbering definition)
        self.counters: dict[int, dict[int, int]] = {}
        # Track all used paths to ensure uniqueness across the document
        self.used_paths: dict[str, int] = {}
        # Track current path for each numId
        self.current_paths: dict[int, str] = {}

    def get_number_path(self, num_id: int, ilvl: int) -> str:
        """Get number path like '1.2.3' for a given numId and level."""
        if num_id not in self.counters:
            self.counters[num_id] = {}

        # Reset counters for deeper levels when we move to a shallower level
        for level in range(ilvl + 1, 9):
            if level in self.counters[num_id]:
                del self.counters[num_id][level]

        # Increment current level counter
        if ilvl not in self.counters[num_id]:
            self.counters[num_id][ilvl] = 0
        self.counters[num_id][ilvl] += 1

        # Build path from all levels up to current
        parts = [
            str(self.counters[num_id][lvl])
            for lvl in range(ilvl + 1)
            if lvl in self.counters[num_id]
        ]
        base_path = ".".join(parts)

        # Handle duplicate paths by adding a suffix
        if base_path in self.used_paths:
            self.used_paths[base_path] += 1
            unique_path = f"{base_path}-{self.used_paths[base_path]}"
        else:
            self.used_paths[base_path] = 0
            unique_path = base_path

        return unique_path

    def reset(self):
        """Reset all counters."""
        self.counters.clear()
        self.used_paths.clear()
        self.current_paths.clear()


def extract_number_from_paragraph(paragraph) -> Optional[NumberInfo]:
    """Extract number information from a paragraph element.

    Args:
        paragraph: python-docx Paragraph object

    Returns:
        NumberInfo if paragraph has numbering, None otherwise
    """
    try:
        # Access the paragraph's XML element
        element = paragraph._element

        # Check if paragraph has numbering properties
        if element.pPr is None:
            return None

        numPr = element.pPr.numPr
        if numPr is None:
            return None

        # Get numbering level and ID
        ilvl = numPr.ilvl.val if numPr.ilvl is not None else 0
        numId = numPr.numId.val if numPr.numId is not None else 0

        return NumberInfo(num_id=numId, ilvl=ilvl, number_path="")

    except (AttributeError, TypeError):
        return None


def get_display_number(paragraph) -> Optional[str]:
    """Get the display number text from a paragraph.

    This extracts the actual number that appears in the document,
    accounting for number formats.

    Args:
        paragraph: python-docx Paragraph object

    Returns:
        The display number as string, or None if not numbered
    """
    try:
        # The paragraph text often contains the number
        text = paragraph.text.strip()

        # Try to extract leading number pattern
        import re
        match = re.match(r"^(\d+(?:\.\d+)*\.?)\s+", text)
        if match:
            return match.group(1)

        return None
    except Exception:
        return None
