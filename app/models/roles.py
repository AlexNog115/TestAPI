from sqlalchemy import Boolean, Column, String, Integer, DateTime
from sqlalchemy.sql import func


from app.database import Base


class Role(Base):
    """
    Roles Management
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(80), unique=True, index=True, nullable=False)
    role_status = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Role {self.role_name}>"