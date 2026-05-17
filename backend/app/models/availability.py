from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Time, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id", ondelete="CASCADE"), nullable=False, index=True)
    weekday = Column(Integer, nullable=False)  # 0=segunda ... 6=domingo
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    professional = relationship("Professional", backref="availabilities")
