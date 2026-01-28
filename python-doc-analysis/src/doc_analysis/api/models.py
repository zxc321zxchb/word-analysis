"""API请求和响应的Pydantic模型。"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


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
