import uuid
from sqlalchemy import Column, ForeignKey, String, Table
from app.core.common.database import db

USER_ROLE_PIVOT = Table(
    'user_role_association',
    db.Base.metadata,
    Column('id_user_role_association', String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True),
    Column('id_role', String(36), ForeignKey('role.id'), nullable=False),
    Column('id_user', String(36), ForeignKey('user.id'), nullable=False)
)

ROLE_PERMISSION_PIVOT = Table(
    'permission_role_association',
    db.Base.metadata,
    Column('id_permission_role_association', String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True),
    Column('id_role', String(36), ForeignKey('role.id'), nullable=False),
    Column('id_permission', String(36), ForeignKey('permission.id'), nullable=False)
)


USER_PERMISSION_PIVOT = Table(
    'user_permission_association',
    db.Base.metadata,
    Column('id_user_permission_association', String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True),
    Column('id_user', String(36), ForeignKey('user.id'), nullable=False),
    Column('id_permission', String(36), ForeignKey('permission.id'), nullable=False)
)