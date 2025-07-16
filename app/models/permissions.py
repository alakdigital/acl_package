from datetime import datetime
import sqlalchemy
import uuid
from app.core.common.database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.association import ROLE_PERMISSION_PIVOT, USER_PERMISSION_PIVOT


class Permission(db.Base):
    __tablename__ = "permissions"
    
    id: Mapped[str] = mapped_column(
        sqlalchemy.String(36),
        primary_key=True, default=lambda: str(uuid.uuid4()),
        unique=True, index=True
    )
    codename: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    categorie: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    created_at = Mapped[datetime] = mapped_column(
        sqlalchemy.DateTime(True),
        server_default=sqlalchemy.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sqlalchemy.DateTime(timezone=True),
        onupdate=sqlalchemy.func.now()
    )
    
    roles = relationship("Role", secondary=ROLE_PERMISSION_PIVOT, back_populates="permissions")
    users = relationship("User", secondary=USER_PERMISSION_PIVOT, back_populates="permissions")