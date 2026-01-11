from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON
from sqlalchemy.orm import DeclarativeBase
import enum

class Base(DeclarativeBase):
    pass

class DomainType(enum.Enum):
    HOUSING = "housing"
    SPORTS = "sports"

class ContentType(enum.Enum):
    ARTICLE = "article"
    VIDEO = "video"

class Content(Base):
    __tablename__ = 'contents'
    __table_args__ = {'schema': 'collector'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(Enum(DomainType), nullable=False, index=True)
    content_type = Column(Enum(ContentType), nullable=False)

    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    thumbnail_url = Column(String(1000), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False)

    provider = Column(String(50), nullable=False)

    metadata_ = Column(JSON, nullable=True)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))