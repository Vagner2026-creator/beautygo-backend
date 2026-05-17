from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base


class Professional(Base):
    __tablename__ = "professionals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    business_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cpf_cnpj = Column(String(20), nullable=True, unique=True, index=True)
    specialty = Column(String(255), nullable=True)
    experience_years = Column(Integer, default=0)
    rating = Column(Numeric(3, 2), default=0.00)
    rating_count = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    address = Column(Text, nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="professional_profile")
    city = relationship("City", backref="professionals")
