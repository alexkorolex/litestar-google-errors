# litestar-google-errors

Litestar plugin that documents `HTTPException` responses in the OpenAPI schema using the
[Google JSON style](https://google.github.io/styleguide/jsoncstyleguide.xml#error) error format
instead of Litestar's default `{"status_code", "detail", "extra"}` body.

```json
{
  "error": {
    "code": 404,
    "message": "Order not found",
    "errors": [
      {
        "domain": "global",
        "reason": "OrderNotFound",
        "message": "Order not found",
        "locationType": "endpoint",
        "location": "/example"
      }
    ]
  }
}
```

## Installation

```bash
uv add litestar-google-errors
# or straight from git
uv add "litestar-google-errors @ git+https://github.com/<owner>/litestar_google_errors.git"
```

## Usage

```python
from litestar import Litestar
from litestar_google_errors import GoogleErrorResponsesPlugin

app = Litestar(
    route_handlers=[...],
    plugins=[GoogleErrorResponsesPlugin()],
)
```

Every exception listed in a handler's `raises=[...]` appears in the schema in the Google format.
Exceptions sharing a status code are combined with `oneOf`.

The example values are configurable:

```python
GoogleErrorResponsesPlugin(domain="orders", location_type="path", example_location="/orders/1")
```

The plugin only changes the **documentation**. To return the same shape at runtime, use the bundled
`msgspec` models in your exception handlers:

```python
from litestar import MediaType, Request, Response
from litestar.exceptions import HTTPException
from litestar_google_errors import GoogleError, GoogleErrorItem, GoogleErrorResponse, LocationType


def http_exception_handler(request: Request, exc: HTTPException) -> Response[GoogleErrorResponse]:
    body = GoogleErrorResponse(
        error=GoogleError(
            code=exc.status_code,
            message=exc.detail,
            errors=[
                GoogleErrorItem(
                    domain="global",
                    reason=type(exc).__name__,
                    message=exc.detail,
                    locationType=LocationType.ENDPOINT,
                    location=request.url.path,
                )
            ],
        )
    )
    return Response(body, status_code=exc.status_code, media_type=MediaType.JSON)
```

## Caveat

Litestar has no public hook for error response schemas, so the plugin replaces the private
`litestar._openapi.responses.create_error_responses` function. The replacement is process-wide,
and the dependency is pinned to `litestar<3` because that internal may change.

## Development

```bash
uv sync
uv run pytest
uv build
```
