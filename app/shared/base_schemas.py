"""Schémas Pydantic de base partagés."""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Generic, Optional, TypeVar


T = TypeVar("T")

class BaseSchema(BaseModel):
    """Schéma de base avec configuration commune."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        str_strip_whitespace=True
    )


class TimestampSchema(BaseSchema):
    """Schéma avec timestamps."""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ResponseSchema(BaseSchema):
    """Schéma de réponse générique."""

    success: bool = True
    message: str
    data: Optional[dict] = None


class PaginationParams(BaseSchema):
    """Paramètres de pagination."""

    page: int = Field(default=1, ge=1, description="Numéro de page")
    limit: int = Field(default=20, ge=1, le=100, description="Taille de la page")

    @property
    def skip(self) -> int:
        """Calcule le nombre d'éléments à sauter."""
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseSchema, Generic[T]):
    """Réponse paginée."""

    items: list[T]
    total: int
    page: int
    limit: int
    total_pages: int

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        limit: int
    ) -> "PaginatedResponse[T]":
        """Crée une réponse paginée."""
        total_pages = (total + limit - 1) // limit

        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
