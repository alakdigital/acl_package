from datetime import datetime
import sqlalchemy
import uuid
from app.core.common.database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.association import USER_ROLE_PIVOT


class Role(db.Base):
    __tablename__ = "roles"
    
    id: Mapped[str] = mapped_column(
        sqlalchemy.String(36),
        primary_key=True, default=lambda: str(uuid.uuid4()),
        unique=True, index=True
    )
    libelle: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    
    created_at = Mapped[datetime] = mapped_column(
        sqlalchemy.DateTime(True),
        server_default=sqlalchemy.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sqlalchemy.DateTime(timezone=True),
        onupdate=sqlalchemy.func.now()
    )
    
    
    # Relationship
    users = relationship("User", secondary=USER_ROLE_PIVOT, back_populates="roles")
    permissions = relationship("Permission", secondary=USER_ROLE_PIVOT, back_populates="roles")