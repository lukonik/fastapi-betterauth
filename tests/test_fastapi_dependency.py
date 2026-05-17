import asyncio

import pytest
from fastapi import HTTPException, Request

from fastapi_betterauth import BetterAuth


def make_request(headers: dict[str, str] | None = None) -> Request:
    return Request(
        {
            "type": "http",
            "headers": [
                (name.lower().encode(), value.encode())
                for name, value in (headers or {}).items()
            ],
        }
    )


def test_missing_authorization_raises_401() -> None:
    auth = BetterAuth("http://localhost:3000")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(auth(make_request()))

    assert exc_info.value.status_code == 401


def test_missing_authorization_can_be_optional() -> None:
    auth = BetterAuth("http://localhost:3000", auto_error=False)

    assert asyncio.run(auth(make_request())) is None


def test_bearer_authorization_validates_token() -> None:
    auth = BetterAuth("http://localhost:3000")
    auth.fetch_token = lambda token: {"token": token}  # type: ignore[method-assign]

    assert asyncio.run(auth(make_request({"Authorization": "Bearer test-token"}))) == {
        "token": "test-token"
    }


def test_invalid_bearer_authorization_raises_401() -> None:
    auth = BetterAuth("http://localhost:3000")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(auth(make_request({"Authorization": "Bearer invalid-token"})))

    assert exc_info.value.status_code == 401
