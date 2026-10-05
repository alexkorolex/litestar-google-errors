"""Google JSON style error payload models."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from msgspec import Struct

__all__ = ("GoogleError", "GoogleErrorItem", "GoogleErrorResponse", "LocationType")


class LocationType(str, Enum):
    FIELD = "field"
    PARAMETER = "parameter"
    PATH = "path"
    HEADER = "header"
    BODY = "body"
    QUERY = "query"
    COOKIE = "cookie"
    ENDPOINT = "endpoint"
    DOMAIN = "domain"


class GoogleErrorItem(Struct):
    domain: str
    reason: str
    message: str
    locationType: Optional[str] = None
    location: Optional[str] = None


class GoogleError(Struct):
    errors: list[GoogleErrorItem]
    code: int
    message: str


class GoogleErrorResponse(Struct):
    error: GoogleError
