from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=True, 
    connect_args={
        "server_settings": {
            "search_path": "collector"
        }
    }
)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Dependency로 사용할 함수
async def get_db():
    async with async_session() as session:
        yield session
