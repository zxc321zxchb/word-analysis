"""SQLAlchemy ORM models."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    BigInteger,
    TIMESTAMP,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

from src.doc_analysis.db.session import engine


Base = declarative_base()


class Document(Base):
    """Document model."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False, comment="Stored filename")
    original_filename = Column(String(255), nullable=False, comment="Original filename")
    file_hash = Column(String(64), unique=True, comment="File SHA256 hash for deduplication")
    file_size = Column(BigInteger, comment="File size in bytes")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    parsed_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    sections = relationship(
        "NumberedSection",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="NumberedSection.sort_order",
    )

    __table_args__ = (
        Index("idx_filename", "filename"),
        Index("idx_hash", "file_hash"),
        {"comment": "Document table"},
    )


class NumberedSection(Base):
    """Numbered section model (core table)."""

    __tablename__ = "numbered_sections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    number_path = Column(
        String(64),
        nullable=False,
        comment="Number path like 1, 1.1, 1.1.1",
    )
    level = Column(Integer, nullable=False, comment="Hierarchy level, 0 is top")
    parent_id = Column(
        Integer,
        ForeignKey("numbered_sections.id", ondelete="CASCADE"),
        nullable=True,
    )
    title = Column(String(512), comment="Section title")
    content_html = Column(Text, comment="HTML format content")
    content_json = Column(Text(length=4294967295), comment="JSON format content for rich text editor")
    sort_order = Column(Integer, nullable=False, comment="Sort order")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    # Relationships
    document = relationship("Document", back_populates="sections")
    parent = relationship("NumberedSection", remote_side=[id], backref="children")
    tables = relationship(
        "SectionTable",
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="SectionTable.sort_order",
    )
    images = relationship(
        "SectionImage",
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="SectionImage.sort_order",
    )

    __table_args__ = (
        Index("idx_document", "document_id"),
        Index("idx_parent", "parent_id"),
        Index("idx_sort", "sort_order"),
        Index("unique_doc_number", "document_id", "number_path", unique=True),
        {"comment": "Numbered section table"},
    )


class SectionTable(Base):
    """Tables associated with sections."""

    __tablename__ = "section_tables"

    id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(
        Integer,
        ForeignKey("numbered_sections.id", ondelete="CASCADE"),
        nullable=False,
    )
    table_index = Column(Integer, nullable=False, comment="Table order in section")
    row_count = Column(Integer, nullable=False, comment="Number of rows")
    col_count = Column(Integer, nullable=False, comment="Number of columns")
    html = Column(Text, comment="Table HTML")
    json_data = Column(Text(length=4294967295), comment="Table JSON data")
    sort_order = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    section = relationship("NumberedSection", back_populates="tables")

    __table_args__ = (
        Index("idx_section", "section_id"),
        {"comment": "Section table table"},
    )


class SectionImage(Base):
    """Images associated with sections."""

    __tablename__ = "section_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(
        Integer,
        ForeignKey("numbered_sections.id", ondelete="CASCADE"),
        nullable=False,
    )
    image_index = Column(Integer, nullable=False, comment="Image order in section")
    filename = Column(String(255), nullable=False, comment="Original filename")
    mime_type = Column(String(64), nullable=False, comment="MIME type")
    base64_data = Column(Text, nullable=False, comment="Base64 encoded image data")
    width = Column(Integer, comment="Width in pixels")
    height = Column(Integer, comment="Height in pixels")
    sort_order = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    section = relationship("NumberedSection", back_populates="images")

    __table_args__ = (
        Index("idx_section", "section_id"),
        {"comment": "Section image table"},
    )


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
