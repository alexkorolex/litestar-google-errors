# litestar-google-errors

[![PyPI](https://img.shields.io/pypi/v/litestar-google-errors.svg)](https://pypi.org/project/litestar-google-errors/)
[![Python versions](https://img.shields.io/pypi/pyversions/litestar-google-errors.svg)](https://pypi.org/project/litestar-google-errors/)
[![CI](https://github.com/alexkorolex/litestar-google-errors/actions/workflows/ci.yml/badge.svg)](https://github.com/alexkorolex/litestar-google-errors/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/alexkorolex/litestar-google-errors/blob/main/LICENSE)

**Google JSON style error responses for [Litestar](https://litestar.dev) OpenAPI.**

`litestar-google-errors` is a Litestar plugin that documents `HTTPException` error responses in
the OpenAPI (Swagger) schema using the
[Google JSON Style Guide](https://google.github.io/styleguide/jsoncstyleguide.xml#error) error
format, instead of Litestar's default `{"status_code", "detail", "extra"}` body. It also ships
typed `msgspec` models to return the same error shape from your API at runtime.

## Features

- Documents error responses in the OpenAPI schema using the Google JSON error format
- Covers every exception listed in a route handler's `raises=[...]`
- Combines exceptions that share an HTTP status code with `oneOf`
- Lets you configure the example `domain`, `locationType` and `location`
- Ships typed `msgspec` models (`GoogleErrorResponse`, `GoogleError`, `GoogleErrorItem`) for runtime error bodies
- Includes `py.typed` for type checkers
- Supports Python 3.10+ and Litestar 2.16+

## Litestar error format: before and after

Litestar's default error body:

```json
{
  "status_code": 404,
  "detail": "Order not found"
}
```

Google JSON style error body, as documented by this plugin:

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
pip install litestar-google-errors
# or
uv add litestar-google-errors
```

## Quick start

Register the plugin on your Litestar app:

```python
from litestar import Litestar
from litestar_google_errors import GoogleErrorResponsesPlugin

app = Litestar(
    route_handlers=[...],
    plugins=[GoogleErrorResponsesPlugin()],
)
```

Every exception listed in a handler's `raises=[...]` appears in the OpenAPI schema in the Google
format. Exceptions that share a status code are combined with `oneOf`.

### Configure the OpenAPI examples

```python
GoogleErrorResponsesPlugin(domain="orders", location_type="path", example_location="/orders/1")
```

### Return Google-style errors at runtime

The plugin only changes the **OpenAPI documentation**. To return the same JSON error shape from
your API, use the bundled `msgspec` models in a Litestar exception handler:

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


app = Litestar(
    route_handlers=[...],
    plugins=[GoogleErrorResponsesPlugin()],
    exception_handlers={HTTPException: http_exception_handler},
)
```

## Limitations

Litestar has no public hook for error response schemas, so the plugin replaces the private
`litestar._openapi.responses.create_error_responses` function. The replacement is process-wide,
and the dependency is pinned to `litestar<3` because that internal may change.

## Development

```bash
uv sync
uv run pytest
uv build
```

## License

[MIT](https://github.com/alexkorolex/litestar-google-errors/blob/main/LICENSE)
