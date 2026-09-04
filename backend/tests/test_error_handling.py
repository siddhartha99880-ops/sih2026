from collections.abc import Callable

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from app.core.errors import AppValidationError, ResourceNotFoundError
from app.main import app


@pytest.fixture
def temporary_error_route() -> Callable[[str, type[Exception]], str]:
    route_paths: list[str] = []

    def add_route(path: str, error_type: type[Exception]) -> str:
        def raise_error(request: Request) -> None:
            raise error_type()

        app.add_api_route(path, raise_error, methods=["GET"])
        route_paths.append(path)
        return path

    yield add_route

    app.router.routes[:] = [
        route for route in app.router.routes if getattr(route, "path", None) not in route_paths
    ]


def test_resource_not_found_error_contract(temporary_error_route: Callable[[str, type[Exception]], str]) -> None:
    path = temporary_error_route("/test-error-resource-not-found", ResourceNotFoundError)

    response = TestClient(app).get(path)

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "RESOURCE_NOT_FOUND",
            "message": "resource not found",
        }
    }


def test_app_validation_error_contract(temporary_error_route: Callable[[str, type[Exception]], str]) -> None:
    path = temporary_error_route("/test-error-validation", AppValidationError)

    response = TestClient(app).get(path)

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "request validation failed",
        }
    }
