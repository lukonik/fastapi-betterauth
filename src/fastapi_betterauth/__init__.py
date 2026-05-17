import dataclasses
import time
from dataclasses import dataclass
from ssl import SSLContext
from typing import Any, TypedDict, Union

import jwt
from fastapi import Request
from fastapi.security import OAuth2
from jwt import PyJWKClient
from typing_extensions import Unpack

CLIENT: Union[PyJWKClient, None] = None
BASE_URL: Union[str, None] = None


def _get_authorization_scheme_param(
    authorization_header_value: str | None,
) -> tuple[str, str]:
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param.strip()


@dataclass
class User:
    aud: str
    createdAt: str
    email: str
    emailVerified: str
    exp: str
    iat: str
    id: str
    image: str
    iss: str
    name: str
    sub: str
    updatedAt: str


class BetterAuth(OAuth2):
    def __init__(
        self,
        base_url: str,
        *,
        auth_path: str = "/api/auth/jwks",
        cache_keys: bool = False,
        max_cached_keys: int = 16,
        cache_jwk_set: bool = True,
        lifespan: float = 300,
        headers: dict[str, Any] | None = None,
        timeout: float = 30,
        ssl_context: SSLContext | None = None,
        auto_error: bool = True,
    ):
        super().__init__(auto_error=auto_error)
        self.base_url = base_url
        full_url = f"{base_url}{auth_path}"
        self.__client = PyJWKClient(
            full_url,
            cache_keys=cache_keys,
            max_cached_keys=max_cached_keys,
            cache_jwk_set=cache_jwk_set,
            lifespan=lifespan,
            headers=headers,
            timeout=timeout,
            ssl_context=ssl_context,
        )

    def fetch_token(self, token: str):
        signing_key = self.__client.get_signing_key_from_jwt(token)
        response = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA"],
            issuer=self.base_url,
            audience=self.base_url,
        )
        user = User(**response)
        return user

    async def __call__(self, request: Request) -> Any | None:
        authorization = request.headers.get("Authorization")
        scheme, param = _get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise self.make_not_authenticated_error()
            return None

        try:
            return self.fetch_token(param)
        except jwt.PyJWTError as exc:
            raise self.make_not_authenticated_error() from exc
