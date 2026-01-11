from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Tuple, List

from app.models.content import Content, ContentType, DomainType
from app.services.collector.naver import NaverNewsCollector
from app.services.collector.youtube import YoutubeCollector
from app.utils.pagination import decode_cursor, encode_cursor

class ContentManager:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.collectors = {
            "naver": NaverNewsCollector(),
            "youtube": YoutubeCollector()
        }

    async def get_list(
        self,
        size: int,
        cursor: Optional[str] = None,
        domain: Optional[DomainType] = None,
        content_type: Optional[ContentType] = None,
    ) -> Tuple[List[Content], Optional[str]]:
        query = select(Content)

        if domain:
            query = query.where(Content.domain == domain)
        if content_type:
            query = query.where(Content.content_type == content_type)
        
        if cursor:
            last_published_at, last_id = decode_cursor(cursor)
            query = query.where(
                (Content.published_at < last_published_at) |
                ((Content.published_at == last_published_at) & (Content.id < last_id))
            )

        # 다음 페이지 존재 여부를 확인하기 위해 size + 1개를 요청
        query = query.order_by(Content.published_at.desc(), Content.id.desc()).limit(size + 1)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        next_cursor = None
        if len(items) > size:
            # 마지막 아이템은 다음 커서용으로 사용하고, 결과에서는 제외
            last_item = items[size]
            next_cursor = encode_cursor(last_item.published_at, last_item.id)
            items = items[:size]
            
        return items, next_cursor

    async def collect_and_save(self, domain: DomainType, keyword: str):
        # 1. 수집
        all_contents = []
        for name, collector in self.collectors.items():
            raw = await collector.fetch(keyword)
            processed = await collector.process(raw, domain)
            all_contents.extend(processed)

        # 2. 저장
        for content in all_contents:
            # URL 기준으로 중복 확인
            stmt = select(Content).where(Content.url == content.url)
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                continue  # 중복된 콘텐츠는 저장하지 않음

            self.db.add(content)
            
        await self.db.commit()