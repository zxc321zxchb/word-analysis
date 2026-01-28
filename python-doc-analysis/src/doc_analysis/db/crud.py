"""Database CRUD operations."""
import hashlib
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from src.doc_analysis.db.models import (
    Document,
    NumberedSection,
    SectionTable,
    SectionImage,
)


def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA256 hash of file content."""
    return hashlib.sha256(file_content).hexdigest()


def create_document(
    db: Session,
    filename: str,
    original_filename: str,
    file_size: int,
    file_hash: str,
) -> Document:
    """Create a new document."""
    doc = Document(
        filename=filename,
        original_filename=original_filename,
        file_size=file_size,
        file_hash=file_hash,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document_by_id(db: Session, doc_id: int) -> Optional[Document]:
    """Get document by ID."""
    return db.query(Document).filter(Document.id == doc_id).first()


def get_document_by_hash(db: Session, file_hash: str) -> Optional[Document]:
    """Get document by file hash."""
    return db.query(Document).filter(Document.file_hash == file_hash).first()


def mark_document_parsed(db: Session, doc_id: int) -> None:
    """Mark document as parsed."""
    doc = get_document_by_id(db, doc_id)
    if doc:
        doc.parsed_at = datetime.utcnow()
        db.commit()


def create_section(
    db: Session,
    document_id: int,
    number_path: str,
    level: int,
    parent_id: Optional[int],
    title: Optional[str],
    content_html: Optional[str],
    content_json: Optional[str],
    sort_order: int,
) -> NumberedSection:
    """Create a new numbered section."""
    section = NumberedSection(
        document_id=document_id,
        number_path=number_path,
        level=level,
        parent_id=parent_id,
        title=title,
        content_html=content_html,
        content_json=content_json,
        sort_order=sort_order,
    )
    db.add(section)
    db.commit()
    db.refresh(section)
    return section


def get_sections_by_document(db: Session, document_id: int) -> List[NumberedSection]:
    """Get all sections for a document."""
    return (
        db.query(NumberedSection)
        .filter(NumberedSection.document_id == document_id)
        .order_by(NumberedSection.sort_order)
        .options(joinedload(NumberedSection.images), joinedload(NumberedSection.tables))
        .all()
    )


def get_section_by_path(
    db: Session, document_id: int, number_path: str
) -> Optional[NumberedSection]:
    """Get section by number path within a document."""
    return (
        db.query(NumberedSection)
        .filter(
            NumberedSection.document_id == document_id,
            NumberedSection.number_path == number_path,
        )
        .options(joinedload(NumberedSection.images), joinedload(NumberedSection.tables))
        .first()
    )


def create_table(
    db: Session,
    section_id: int,
    table_index: int,
    row_count: int,
    col_count: int,
    html: Optional[str],
    json_data: Optional[str],
    sort_order: int,
) -> SectionTable:
    """Create a new section table."""
    table = SectionTable(
        section_id=section_id,
        table_index=table_index,
        row_count=row_count,
        col_count=col_count,
        html=html,
        json_data=json_data,
        sort_order=sort_order,
    )
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def create_image(
    db: Session,
    section_id: int,
    image_index: int,
    filename: str,
    mime_type: str,
    base64_data: str,
    width: Optional[int],
    height: Optional[int],
    sort_order: int,
) -> SectionImage:
    """Create a new section image."""
    image = SectionImage(
        section_id=section_id,
        image_index=image_index,
        filename=filename,
        mime_type=mime_type,
        base64_data=base64_data,
        width=width,
        height=height,
        sort_order=sort_order,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


def build_section_tree(sections: List[NumberedSection]) -> List[Dict[str, Any]]:
    """Build hierarchical tree from flat section list."""

    def section_to_dict(s: NumberedSection) -> Dict[str, Any]:
        return {
            "id": s.id,
            "number_path": s.number_path,
            "level": s.level,
            "title": s.title,
            "children": [],
        }

    # Create id -> section mapping
    section_map = {s.id: section_to_dict(s) for s in sections}

    # Build tree structure
    root_sections = []
    for section in sections:
        node = section_map[section.id]
        if section.parent_id is None:
            root_sections.append(node)
        else:
            parent = section_map.get(section.parent_id)
            if parent:
                parent["children"].append(node)

    return root_sections


def get_documents_with_pagination(db: Session, page: int = 1, page_size: int = 10) -> Tuple[List[Document], int]:
    """Get documents with pagination.
    
    Args:
        db: Database session
        page: Page number (1-based)
        page_size: Number of items per page
        
    Returns:
        Tuple of (documents, total_count)
    """
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get total count
    total_count = db.query(Document).count()
    
    # Get documents with pagination
    documents = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    return documents, total_count


def get_section_count_by_document(db: Session, document_id: int) -> int:
    """Get number of sections for a document."""
    return db.query(NumberedSection).filter(NumberedSection.document_id == document_id).count()
