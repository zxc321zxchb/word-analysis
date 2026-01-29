"""文档分析API路由。"""
import io
import uuid
import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.doc_analysis.config import settings
from src.doc_analysis.logger import get_logger
from src.doc_analysis.db.session import get_db
from src.doc_analysis.db.models import (
    Base,
    Document,
    NumberedSection,
    DocumentParseResponse,
    DocumentDetailResponse,
    DocumentBriefResponse,
    DocumentListResponse,
    SectionResponse,
    SectionDetailResponse,
    SectionBriefResponse,
    SectionTreeResponse,
    TableResponse,
    ImageResponse,
    HealthResponse,
)
from src.doc_analysis.db import crud
from src.doc_analysis.parser.docx import parse_docx_file, DocxParser, ParsedDocument, ParsedSection
from src.doc_analysis.parser.renderer import RichTextRenderer, RenderedImage

router = APIRouter(prefix=settings.api_prefix, tags=["documents"])
logger = get_logger(__name__)


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """健康检查端点。"""
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return HealthResponse(status="healthy", database="connected")
    except Exception as e:
        logger.debug(f"Health check database connection failed: {e}")
        return HealthResponse(status="unhealthy", database="disconnected")


@router.post(
    "/documents/parse",
    response_model=DocumentParseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def parse_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """上传并解析Word (.docx)文档。

    提取编号章节、文本内容、表格和图片。
    使用标题样式（h1, h2, h3, h4, h5）进行解析。
    存储到数据库并返回解析结果。
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .docx files are supported",
        )

    # Read file content
    file_content = await file.read()

    # Validate file size
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB",
        )

    # Validate MIME type
    if file.content_type and file.content_type not in settings.allowed_mime_types:
        logger.warning(
            f"File {file.filename} has unexpected MIME type: {file.content_type}"
        )

    # Parse document using heading styles
    try:
        parser = DocxParser()
        parsed = parser.parse_by_heading(file_content, file.filename)
    except OSError as e:
        logger.error(f"File I/O error while parsing document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to read document file",
        )
    except Exception as e:
        logger.error(f"Failed to parse document {file.filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse document",
        )

    # Check for duplicate (by hash)
    existing = crud.get_document_by_hash(db, parsed.file_hash)
    if existing:
        # Return existing document
        sections = crud.get_sections_by_document(db, existing.id)
        section_responses = [_section_to_response(s, db) for s in sections]

        return DocumentParseResponse(
            document_id=existing.id,
            filename=existing.filename,
            sections_count=len(section_responses),
            sections=section_responses,
        )

    # Create new document record
    stored_filename = f"{uuid.uuid4()}_{file.filename}"
    doc = crud.create_document(
        db=db,
        filename=stored_filename,
        original_filename=file.filename,
        file_size=parsed.file_size,
        file_hash=parsed.file_hash,
    )

    # Build section path map for parent lookups
    path_to_id: Dict[str, int] = {}
    sort_order = 0

    # First pass: create sections
    for parsed_section in parsed.sections:
        sort_order += 1

        # Get parent ID from parent info
        parent_id = None
        if parsed_section.parent and parsed_section.parent.get("number_path"):
            parent_id = path_to_id.get(parsed_section.parent["number_path"])

        # Generate content with title
        renderer = RichTextRenderer()

        # Add heading with number and title
        heading_text = f"{parsed_section.number_path}"
        if parsed_section.title:
            heading_text += f" {parsed_section.title}"
        renderer.add_heading(heading_text, level=min(parsed_section.level + 1, 6))

        # Add paragraphs
        for p in parsed_section.paragraphs:
            renderer.add_paragraph(p)

        # Add tables
        for table in parsed_section.tables:
            renderer.add_table(table)

        # Add images
        for image in parsed_section.images:
            renderer.add_image(image)

        content_html = renderer.render_html()
        content_json = renderer.render_json()

        section = crud.create_section(
            db=db,
            document_id=doc.id,
            number_path=parsed_section.number_path,
            level=parsed_section.level,
            parent_id=parent_id,
            title=parsed_section.title,
            content_html=content_html,
            content_json=str(content_json),
            sort_order=sort_order,
        )

        path_to_id[parsed_section.number_path] = section.id

        # Store tables
        for idx, table in enumerate(parsed_section.tables):
            crud.create_table(
                db=db,
                section_id=section.id,
                table_index=idx,
                row_count=table.rows,
                col_count=table.cols,
                html=table.html,
                json_data=str(table.json_data) if table.json_data else None,
                sort_order=idx,
            )

        # Store images
        for idx, image in enumerate(parsed_section.images):
            try:
                crud.create_image(
                    db=db,
                    section_id=section.id,
                    image_index=idx,
                    filename=image.filename,
                    mime_type=image.mime_type,
                    base64_data=image.base64_data,
                    width=image.width,
                    height=image.height,
                    sort_order=idx,
                )
            except Exception as e:
                # Log error but continue processing other images
                logger.warning(
                    f"Failed to store image {image.filename} in section {section.number_path}: {e}",
                    exc_info=True,
                )

    # Mark document as parsed
    crud.mark_document_parsed(db, doc.id)

    # Get all sections for response
    sections = crud.get_sections_by_document(db, doc.id)
    section_responses = [_section_to_response(s, db) for s in sections]

    return DocumentParseResponse(
        document_id=doc.id,
        filename=stored_filename,
        sections_count=len(section_responses),
        sections=section_responses,
    )


@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    """获取文档详情，包含所有章节。"""
    doc = crud.get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在",
        )

    sections = crud.get_sections_by_document(db, document_id)
    section_responses = [_section_to_response(s, db) for s in sections]

    return DocumentDetailResponse(
        id=doc.id,
        filename=doc.filename,
        original_filename=doc.original_filename,
        file_size=doc.file_size,
        created_at=doc.created_at,
        parsed_at=doc.parsed_at,
        sections=section_responses,
    )


@router.get(
    "/documents/{document_id}/sections/{number_path}",
    response_model=SectionDetailResponse,
)
def get_section_by_path(
    document_id: int,
    number_path: str,
    db: Session = Depends(get_db),
):
    """根据章节编号路径获取特定章节。"""
    section = crud.get_section_by_path(db, document_id, number_path)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在",
        )

    response = _section_to_detail_response(section, db)
    return response


@router.get(
    "/documents/{document_id}/sections",
    response_model=SectionTreeResponse,
)
def get_sections_tree(
    document_id: int,
    db: Session = Depends(get_db),
):
    """获取所有章节的层次结构树。"""
    sections = crud.get_sections_by_document(db, document_id)
    tree = crud.build_section_tree(sections)

    return SectionTreeResponse(tree=tree)


@router.get(
    "/documents",
    response_model=DocumentListResponse,
)
def get_documents(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    """获取带分页的文档列表，包含基本信息。

    返回按创建时间排序的文档（最新的在前）。
    每个文档包含基本信息和章节数量。
    """
    # Validate pagination parameters
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = settings.default_page_size
    elif page_size > settings.max_page_size:
        page_size = settings.max_page_size

    # Get documents with section counts (optimized single query)
    documents, total_count, section_counts = crud.get_documents_with_section_counts(
        db, page, page_size
    )

    # Build response items with section counts
    items = []
    for doc in documents:
        items.append(
            DocumentBriefResponse(
                id=doc.id,
                original_filename=doc.original_filename,
                file_size=doc.file_size,
                created_at=doc.created_at,
                parsed_at=doc.parsed_at,
                sections_count=section_counts.get(doc.id, 0),
            )
        )

    # Calculate total pages
    total_pages = (total_count + page_size - 1) // page_size

    return DocumentListResponse(
        items=items,
        total=total_count,
        page=page,
        page_size=page_size,
        pages=total_pages,
    )


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    """根据文档ID删除文档及其所有关联的章节、表格和图片。

    由于数据库外键设置了 CASCADE，删除文档会自动删除：
    - 所有关联的章节 (numbered_sections)
    - 所有章节的表格 (section_tables)
    - 所有章节的图片 (section_images)

    Args:
        document_id: 要删除的文档ID

    Returns:
        HTTP 204 No Content 如果删除成功
        HTTP 404 Not Found 如果文档不存在
    """
    success = crud.delete_document(db, document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在",
        )
    # Return None for 204 No Content
    return None


def _section_to_response(
    section: NumberedSection, db: Session
) -> SectionResponse:
    """将数据库章节转换为API响应。"""
    # 根据配置决定是否返回 content_html 和 content_json
    content_html = None
    content_json = None

    if settings.content_format == "html":
        content_html = section.content_html
    elif settings.content_format == "json":
        content_json = section.content_json
    else:  # "both" or any other value
        content_html = section.content_html
        content_json = section.content_json

    return SectionResponse(
        id=section.id,
        number_path=section.number_path,
        level=section.level,
        title=section.title,
        content_html=content_html,
        content_json=content_json,
        tables=[_table_to_response(t) for t in section.tables],
        images=[_image_to_response(i) for i in section.images],
    )


def _section_to_detail_response(
    section: NumberedSection, db: Session
) -> SectionDetailResponse:
    """将数据库章节转换为详细的API响应。"""
    # 根据配置决定是否返回 content_html 和 content_json
    content_html = None
    content_json = None

    if settings.content_format == "html":
        content_html = section.content_html
    elif settings.content_format == "json":
        content_json = section.content_json
    else:  # "both" or any other value
        content_html = section.content_html
        content_json = section.content_json

    parent = None
    if section.parent_id:
        parent_section = (
            db.query(NumberedSection)
            .filter(NumberedSection.id == section.parent_id)
            .first()
        )
        if parent_section:
            parent = SectionBriefResponse(
                id=parent_section.id,
                number_path=parent_section.number_path,
                level=parent_section.level,
                title=parent_section.title,
            )

    children = [
        SectionBriefResponse(
            id=c.id,
            number_path=c.number_path,
            level=c.level,
            title=c.title,
        )
        for c in section.children
    ]

    return SectionDetailResponse(
        id=section.id,
        number_path=section.number_path,
        level=section.level,
        title=section.title,
        content_html=content_html,
        content_json=content_json,
        tables=[_table_to_response(t) for t in section.tables],
        images=[_image_to_response(i) for i in section.images],
        parent=parent,
        children=children,
    )


def _table_to_response(table) -> TableResponse:
    """将数据库表格转换为API响应。"""

    return TableResponse(
        id=table.id,
        table_index=table.table_index,
        row_count=table.row_count,
        col_count=table.col_count,
        html=table.html,
        json_data=table.json_data,
    )


def _image_to_response(image) -> ImageResponse:
    """将数据库图片转换为API响应。"""

    return ImageResponse(
        id=image.id,
        image_index=image.image_index,
        filename=image.filename,
        mime_type=image.mime_type,
        base64_data=image.base64_data,
        width=image.width,
        height=image.height,
    )
