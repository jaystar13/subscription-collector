import logging

from app.models.content import DomainType
from app.services.manager import ContentManager
from app.core.database import async_session


logger = logging.getLogger(__name__)

async def collect_all_domains_task():
    """
    정기적으로 실행될 수집 태스크
    """
    logger.info("Starting scheduled collection task...")

    # 도메인별 수집 대상 키워드 정의 (나중에 DB에서 관리하도록 확장 필요)
    targets = [
        {"domain": DomainType.HOUSING, "keyword": "공공분양"},
        {"domain": DomainType.HOUSING, "keyword": "3기신도시"},
        # 향후 추가될 프로야구 예시:
        # {"domain": DomainType.SPORTS, "keyword": "2026 프로야구"}
    ]

    async with async_session() as session:
        manager = ContentManager(session)
        for target in targets:
            try:
                logger.info(f"Collecting for {target['domain'].value}: {target['keyword']}")
                await manager.collect_and_save(target["domain"], target["keyword"])
            except Exception as e:
                logger.error(f"Error collecting {target['keyword']}: {e}")

    logger.info("Scheduled collection task completed.")