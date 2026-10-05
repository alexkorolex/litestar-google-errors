"""Litestar plugin wiring the Google error schema into OpenAPI generation."""

from __future__ import annotations

from functools import partial

import litestar._openapi.responses as response_factory
from litestar.config.app import AppConfig
from litestar.plugins import InitPlugin

from litestar_google_errors.openapi import create_error_responses

__all__ = ("GoogleErrorResponsesPlugin",)


class GoogleErrorResponsesPlugin(InitPlugin):
    """Render ``HTTPException`` responses in the OpenAPI schema using the Google JSON error format.

    Litestar has no public hook for error response schemas, so the plugin replaces
    ``litestar._openapi.responses.create_error_responses``. The replacement is process-wide.
    """

    def __init__(
        self,
        *,
        domain: str = "global",
        location_type: str = "endpoint",
        example_location: str = "/example",
    ) -> None:
        self.domain = domain
        self.location_type = location_type
        self.example_location = example_location

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        response_factory.create_error_responses = partial(  # type: ignore[assignment]
            create_error_responses,
            domain=self.domain,
            location_type=self.location_type,
            location=self.example_location,
        )
        return app_config
