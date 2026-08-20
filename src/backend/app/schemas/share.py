from datetime import datetime

from pydantic import BaseModel, Field


class ShareLinkResponse(BaseModel):
    share_url: str
    token: str
    expires_at: datetime | None = None


class TripExportResponse(BaseModel):
    workspace_id: int
    title: str
    format: str = Field(description="json hoặc markdown")
    content: str = Field(description="Nội dung chuỗi JSON hoặc Markdown được định dạng")
