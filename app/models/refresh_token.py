from sqlalchemy import Boolean, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

class RefreshToken(Base):
    """
    RefreshToken model for the database
    """
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    token = Column(String(1000), nullable=False)
    expires_at = Column(DateTime(timezone=True), index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship to User
    user = relationship("User", back_populates="refresh_tokens", lazy="select")

    def _repr_(self):
        return f"<RefreshToken id={self.id} user_id={self.user_id}>"