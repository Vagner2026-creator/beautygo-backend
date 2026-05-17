import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


class MediaType(str, enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"


class ProfessionalMedia(Base):
    __tablename__ = "professional_media"

    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(SAEnum(MediaType), nullable=False)
    file_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    professional = relationship("Professional", backref="media")
