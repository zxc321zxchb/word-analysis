"""SQLAlchemy ORM models and Pydantic response models."""

from datetime import datetime
from typing import Optional, List, Dict, Any

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
from pydantic import BaseModel, Field


# =============================================================================
# SQLAlchemy ORM Models
# =============================================================================

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
    content_html = Column(Text(length=4294967295), comment="HTML format content")
    content_json = Column(Text(length=4294967295), comment="JSON format content for rich text editor")
    marked_content = Column(Text(length=4294967295), comment="带列表标记的文本内容，有序列表用<1>标识，无序列表用-标识")
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
    html = Column(Text(length=4294967295), comment="Table HTML")
    json_data = Column(Text(length=4294967295), comment="Table JSON data")
    sort_order = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    section = relationship("NumberedSection", back_populates="tables")

    __table_args__ = (
        Index("idx_section_table_section_id", "section_id"),
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
    base64_data = Column(Text(length=4294967295), nullable=False, comment="Base64 encoded image data")
    width = Column(Integer, comment="Width in pixels")
    height = Column(Integer, comment="Height in pixels")
    sort_order = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    section = relationship("NumberedSection", back_populates="images")

    __table_args__ = (
        Index("idx_section_image_section_id", "section_id"),
        {"comment": "Section image table"},
    )


# =============================================================================
# Pydantic Response Models
# =============================================================================

# 请求模型
class DocumentParseResponse(BaseModel):
    """文档解析响应。"""

    document_id: int
    filename: str
    sections_count: int
    sections: List["SectionResponse"]


class DocumentDetailResponse(BaseModel):
    """文档详情响应。"""

    id: int
    filename: str
    original_filename: str
    file_size: Optional[int]
    created_at: datetime
    parsed_at: Optional[datetime]
    sections: List["SectionResponse"]


class SectionResponse(BaseModel):
    """章节响应。"""

    id: int
    number_path: str
    level: int
    title: Optional[str]
    content_html: Optional[str]
    content_json: Optional[str]
    marked_content: Optional[str] = None  # 带列表标记的内容
    tables: List["TableResponse"] = []
    images: List["ImageResponse"] = []


class SectionDetailResponse(SectionResponse):
    """带父章节和子章节的详细章节响应。"""

    parent: Optional["SectionBriefResponse"]
    children: List["SectionBriefResponse"]


class SectionBriefResponse(BaseModel):
    """用于树结构的简要章节信息。"""

    id: int
    number_path: str
    level: int
    title: Optional[str]


class TableResponse(BaseModel):
    """表格响应。"""

    id: int
    table_index: int
    row_count: int
    col_count: int
    html: Optional[str]
    json_data: Optional[str]


class ImageResponse(BaseModel):
    """图片响应。"""

    id: int
    image_index: int
    filename: str
    mime_type: str
    base64_data: str
    width: Optional[int]
    height: Optional[int]


class SectionTreeResponse(BaseModel):
    """章节树响应。"""

    tree: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: str
    database: str


class ErrorResponse(BaseModel):
    """错误响应。"""

    detail: str


class DocumentBriefResponse(BaseModel):
    """列表视图的简要文档信息。"""

    id: int
    original_filename: str
    file_size: Optional[int]
    created_at: datetime
    parsed_at: Optional[datetime]
    sections_count: Optional[int] = Field(default=0, description="文档中的章节数量")


class DocumentListResponse(BaseModel):
    """分页文档列表响应。"""

    items: List[DocumentBriefResponse]
    total: int
    page: int
    page_size: int
    pages: int


# Update forward references
DocumentParseResponse.model_rebuild()
DocumentDetailResponse.model_rebuild()
SectionDetailResponse.model_rebuild()
DocumentBriefResponse.model_rebuild()
DocumentListResponse.model_rebuild()
