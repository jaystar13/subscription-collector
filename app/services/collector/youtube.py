from datetime import datetime
from typing import Any, List

import httpx
from app.models.content import Content, ContentType, DomainType
from app.services.collector.base import BaseCollector
from app.core.config import settings


class YoutubeCollector(BaseCollector):
    def __init__(self):
        self.api_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = settings.YOUTUBE_API_KEY

    async def fetch(self, keyword) -> List[Any]:
        async with httpx.AsyncClient() as client:

            search_res = await client.get(
                f"{self.api_url}/search",
                params={
                    "part": "snippet",
                    "q": keyword,
                    "type": "video",
                    "maxResults": 10,
                    "key": self.api_key,
                    "order": "relevance"
                }
            )

            items = search_res.json().get("items", [])
            if not items:
                return []
            
            video_ids = [item["id"]["videoId"] for item in items]

            stats_res = await client.get(
                f"{self.api_url}/videos",
                params={
                    "part": "statistics,snippet,contentDetails",
                    "id": ",".join(video_ids),
                    "key": self.api_key
                }
            )

            return stats_res.json().get("items", [])

    async def process(self, raw_data: List[Any], domain: DomainType) -> List[Content]:
        process_data = []
        for item in raw_data:
            snippet = item["snippet"]
            stats = item.get("statistics", {})

            view_count_raw = int(stats.get("viewCount", 0))
            view_count_str = self._format_view_count(view_count_raw)

            pub_date = datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))

            content = Content(
                domain=domain,
                content_type=ContentType.VIDEO,
                provider="YOUTUBE",
                title=snippet["title"],
                url=f"https://www.youtube.com/watch?v={item['id']}",
                thumbnail_url=snippet["thumbnails"]["high"]["url"],
                published_at=pub_date,
                metadata_={
                    "channel_name": snippet["channelTitle"],
                    "view_count": view_count_str,
                    "duration": item.get("contentDetails", {}).get("duration")
                }
            )
            process_data.append(content)
        return process_data

    def _format_view_count(self, count: int) -> str:
        if count >= 10_000:
            return f"조회수 {count // 10_000}만회"
        elif count >= 1_000:
            return f"조회수 {count // 1_000}천회"
        else:
            return f"조회수 {count}회"