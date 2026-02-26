"""Common schemas for API responses."""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class BulkImportResult(BaseModel):
    total: int
    created: int
    updated: int
    errors: list[str]
