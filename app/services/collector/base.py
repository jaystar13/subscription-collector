from abc import ABC, abstractmethod
from typing import Any, List

from app.models.content import Content, DomainType


class BaseCollector(ABC):
    @abstractmethod
    async def fetch(self, keyword: str) -> List[Any]:
        """외부 API로부터 원본 데이터를 가져오는 로직을 구현합니다."""
        pass

    @abstractmethod
    async def process(self, raw_data: List[Any], domain: DomainType) -> List[Content]:
        """원본 데이터를 DB 모델(Content)로 변환하는 로직을 구현합니다."""
        pass