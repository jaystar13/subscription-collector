from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict

from app.models.content import ContentType, DomainType


class ContentBase(BaseModel):
    domain: DomainType
    content_type: ContentType
    title: str
    url: str
    thumbnail_url: Optional[str] = None
    published_at: datetime
    provider: str
    metadata_: Optional[Dict[str, Any]] = None

class ContentResponse(ContentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)