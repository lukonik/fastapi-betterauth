import asyncio

import jwt
import pytest
from fastapi import HTTPException, Request

from fastapi_betterauth import BetterAuth, TokenValidationError


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


def test_fetch_token_wraps_jwt_errors() -> None:
    auth = BetterAuth("http://localhost:3000")

    class JwkClient:
        def get_signing_key_from_jwt(self, token: str) -> object:
            raise jwt.DecodeError("invalid token")

    auth._BetterAuth__client = JwkClient()  # type: ignore[attr-defined]

    with pytest.raises(TokenValidationError):
        auth.fetch_token("invalid-token")


def test_token_validation_errors_are_returned_as_401() -> None:
    auth = BetterAuth("http://localhost:3000")

    def raise_token_error(token: str) -> object:
        raise TokenValidationError("Invalid bearer token")

    auth.fetch_token = raise_token_error  # type: ignore[method-assign]

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(auth(make_request({"Authorization": "Bearer invalid-token"})))

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
