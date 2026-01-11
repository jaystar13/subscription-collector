import asyncio
from datetime import datetime
from typing import Any, List

import httpx
from app.models.content import Content, ContentType, DomainType
from app.services.collector.base import BaseCollector
from app.core.config import settings
from app.utils.scraper import get_og_image


class NaverNewsCollector(BaseCollector):
    def __init__(self):
        self.api_url = "https://openapi.naver.com/v1/search/news.json"
        self.headers = {
            "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
        }

    async def fetch(self, keyword) -> List[Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.api_url,
                headers=self.headers,
                params={"query": keyword, "display": 20, "sort": "sim"} # 유사도순
            )
            if response.status_code == 200:
                return response.json().get("items", [])
            return []

    async def process(self, raw_data: List[Any], domain: DomainType) -> List[Content]:

        tasks = [get_og_image(item["link"]) for item in raw_data]
        og_results = await asyncio.gather(*tasks)

        processed_data = []

        for item, og in zip(raw_data, og_results):
            pub_date = datetime.strptime(item["pubDate"], "%a, %d %b %Y %H:%M:%S +0900")

            # 기본 기사 정보 생성
            content = Content(
                domain=domain,
                content_type=ContentType.ARTICLE,
                provider="NAVER",
                title=item["title"].replace("<b>", "").replace("</b>", ""), # 태그제거
                url=item["link"],
                published_at=pub_date,
                thumbnail_url=og["thumbnail"],
                metadata_={
                    "publisher": og["publisher"] or "뉴스",
                    "subtitle": og["description"] or item["description"].replace("<b>", "").replace("</b>", "")
                }
            )
            processed_data.append(content)

        return processed_data
