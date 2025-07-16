from datetime import datetime
import uuid
from sqlalchemy import DateTime, String, func
from app.core.common.database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.association import USER_PERMISSION_PIVOT, USER_ROLE_PIVOT


class User(db.Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        unique=True, 
        index=True
    )
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(nullable=True, unique=True, index=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now()
    )
    
    # Relationship
    roles = relationship("Roles", secondary=USER_ROLE_PIVOT, back_populates="users")
    permissions = relationship("Permissions", secondary=USER_PERMISSION_PIVOT, back_populates="users")
    