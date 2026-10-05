from litestar import Litestar, get
from litestar.exceptions import NotAuthorizedException, NotFoundException, PermissionDeniedException
from litestar.testing import TestClient

from litestar_google_errors import GoogleErrorResponsesPlugin


class OrderNotFound(NotFoundException):
    detail = "Order not found"


class UserNotFound(NotFoundException):
    detail = "User not found"


@get("/orders", raises=[OrderNotFound, UserNotFound, NotAuthorizedException, PermissionDeniedException])
async def get_order() -> dict:
    return {}


def _openapi(plugin: GoogleErrorResponsesPlugin) -> dict:
    app = Litestar(route_handlers=[get_order], plugins=[plugin])
    with TestClient(app) as client:
        return client.get("/schema/openapi.json").json()


def test_error_responses_use_google_format() -> None:
    responses = _openapi(GoogleErrorResponsesPlugin())["paths"]["/orders"]["get"]["responses"]

    schema = responses["401"]["content"]["application/json"]["schema"]
    assert schema["required"] == ["error"]
    assert set(schema["properties"]["error"]["properties"]) == {"code", "message", "errors"}
    example = schema["examples"][0]["error"]
    assert example["code"] == 401
    assert example["errors"][0]["reason"] == "NotAuthorizedException"


def test_same_status_exceptions_are_combined() -> None:
    responses = _openapi(GoogleErrorResponsesPlugin())["paths"]["/orders"]["get"]["responses"]

    variants = responses["404"]["content"]["application/json"]["schema"]["oneOf"]
    assert [v["examples"][0]["error"]["message"] for v in variants] == ["Order not found", "User not found"]
    assert responses["404"]["description"] == "Order not found"


def test_example_values_are_configurable() -> None:
    plugin = GoogleErrorResponsesPlugin(domain="orders", location_type="path", example_location="/orders/1")
    responses = _openapi(plugin)["paths"]["/orders"]["get"]["responses"]

    item = responses["403"]["content"]["application/json"]["schema"]["examples"][0]["error"]["errors"][0]
    assert (item["domain"], item["locationType"], item["location"]) == ("orders", "path", "/orders/1")
