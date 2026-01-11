from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.schemas.content import ContentResponse
from app.services.manager import ContentManager
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.content import ContentType, DomainType
from app.utils.pagination import CursorPage

router = APIRouter(prefix="/contents", tags=["contents"])

# 1. 수집 트리거 API (수동 수집 실행)
@router.post("/collect")
async def trigger_collection(
    domain: DomainType = DomainType.HOUSING,
    keyword: str = "공공분양",
    db: AsyncSession = Depends(get_db)
):
    manager = ContentManager(db)
    await manager.collect_and_save(domain, keyword)
    return {"message": f"Collection for '{keyword}' in {domain.value} started successfully."}

# 2. 수집된 콘텐츠 조회 API (커서 기반 페이지네이션)
@router.get("/", response_model=CursorPage[ContentResponse])
async def get_contents(
    domain: DomainType = Query(None),
    content_type: ContentType = Query(None),
    cursor: Optional[str] = None,
    size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    manager = ContentManager(db)
    items, next_cursor = await manager.get_list(
        size=size,
        cursor=cursor,
        domain=domain,
        content_type=content_type,
    )
    
    return CursorPage(
        items=items,
        next_cursor=next_cursor,
    )
