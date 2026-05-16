from ssl import SSLContext
from typing import Any, TypedDict, Union

import jwt
from jwt import PyJWKClient
from typing_extensions import Unpack

CLIENT: Union[PyJWKClient, None] = None
BASE_URL: Union[str, None] = None


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
