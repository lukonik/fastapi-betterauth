import time
from ssl import SSLContext
from typing import Any, TypedDict, Union

import jwt
from fastapi.security import OAuth2
from jwt import PyJWKClient
from typing_extensions import Unpack

CLIENT: Union[PyJWKClient, None] = None
BASE_URL: Union[str, None] = None

#  self,
#         uri: str,
#         cache_keys: bool = False,
#         max_cached_keys: int = 16,
#         cache_jwk_set: bool = True,
#         lifespan: float = 300,
#         headers: dict[str, Any] | None = None,
#         timeout: float = 30,
#         ssl_context: SSLContext | None = None,


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
    ):
        super().__init__()
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

    def is_authorized(self):
        signing_key = self.__client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA"],
            issuer=BASE_URL,
            audience=BASE_URL,
        )


class PyJWKClientKwargs(TypedDict, total=False):
    cache_keys: bool
    max_cached_keys: int
    cache_jwk_set: bool
    lifespan: float
    headers: Union[dict[str, Any], None]
    timeout: float
    ssl_context: Union[SSLContext, None]


def init_client(
    base_url: str,
    auth_path: str = "/api/auth/jwks",
    **kwargs: Unpack[PyJWKClientKwargs],
):
    full_url = f"{base_url}{auth_path}"
    global BASE_URL, CLIENT
    BASE_URL = base_url
    base_url = base_url
    CLIENT = PyJWKClient(
        **kwargs,
        uri=full_url,
    )


def _assert_client() -> PyJWKClient:
    if CLIENT is None:
        raise RuntimeError("Client is not initialized call init_client first")
    return CLIENT


def validate_token(token: str):
    client = _assert_client()
    signing_key = client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["EdDSA"],
        issuer=BASE_URL,
        audience=BASE_URL,
    )
