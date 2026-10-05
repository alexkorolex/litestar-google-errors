"""OpenAPI schema generation for Google JSON style error responses."""

from __future__ import annotations

import contextlib
from http import HTTPStatus
from typing import Iterator

from litestar import MediaType
from litestar.exceptions import HTTPException
from litestar.openapi.spec import OpenAPIMediaType, OpenAPIResponse, OpenAPIType, Schema

__all__ = ("create_error_responses",)


def _status_phrase(status_code: int) -> str:
    with contextlib.suppress(ValueError):
        return HTTPStatus(status_code).phrase
    return ""


def _status_description(status_code: int) -> str:
    with contextlib.suppress(ValueError):
        return HTTPStatus(status_code).description
    return ""


def _error_schema(
    exc: type[HTTPException],
    status_code: int,
    detail: str,
    domain: str,
    location_type: str,
    location: str,
) -> Schema:
    return Schema(
        type=OpenAPIType.OBJECT,
        required=["error"],
        description=exc.__name__,
        properties={
            "error": Schema(
                type=OpenAPIType.OBJECT,
                required=["code", "message", "errors"],
                properties={
                    "code": Schema(type=OpenAPIType.INTEGER),
                    "message": Schema(type=OpenAPIType.STRING),
                    "errors": Schema(
                        type=OpenAPIType.ARRAY,
                        items=Schema(
                            type=OpenAPIType.OBJECT,
                            required=["domain", "reason", "message"],
                            properties={
                                "domain": Schema(type=OpenAPIType.STRING),
                                "reason": Schema(type=OpenAPIType.STRING),
                                "message": Schema(type=OpenAPIType.STRING),
                                "locationType": Schema(type=[OpenAPIType.STRING, OpenAPIType.NULL]),
                                "location": Schema(type=[OpenAPIType.STRING, OpenAPIType.NULL]),
                            },
                        ),
                    ),
                },
            )
        },
        examples=[
            {
                "error": {
                    "code": status_code,
                    "message": detail,
                    "errors": [
                        {
                            "domain": domain,
                            "reason": exc.__name__,
                            "message": detail,
                            "locationType": location_type,
                            "location": location,
                        }
                    ],
                }
            }
        ],
    )


def create_error_responses(
    exceptions: list[type[HTTPException]],
    *,
    domain: str = "global",
    location_type: str = "endpoint",
    location: str = "/example",
) -> Iterator[tuple[str, OpenAPIResponse]]:
    """Create OpenAPI responses for ``exceptions`` in the Google JSON error format.

    Exceptions sharing a status code are combined into a single response using ``oneOf``.
    """
    grouped: dict[int, list[type[HTTPException]]] = {}
    for exc in exceptions:
        grouped.setdefault(getattr(exc, "status_code", 500), []).append(exc)

    for status_code, group in grouped.items():
        description = ""
        schemas: list[Schema] = []
        for exc in group:
            detail = getattr(exc, "detail", None) or _status_phrase(status_code)
            description = description or getattr(exc, "detail", None) or ""
            schemas.append(_error_schema(exc, status_code, detail, domain, location_type, location))

        schema = schemas[0] if len(schemas) == 1 else Schema(one_of=schemas)
        yield (
            str(status_code),
            OpenAPIResponse(
                description=description or _status_description(status_code),
                content={MediaType.JSON: OpenAPIMediaType(schema=schema)},
            ),
        )
