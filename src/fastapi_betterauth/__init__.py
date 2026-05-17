from ssl import SSLContext
from typing import Any, TypedDict, cast

import jwt
from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2
from jwt import PyJWKClient


def _get_authorization_scheme_param(
    authorization_header_value: str | None,
) -> tuple[str, str]:
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param.strip()


class User(TypedDict, total=False):
    aud: str
    createdAt: str
    email: str
    emailVerified: bool
    exp: int
    iat: int
    id: str
    image: str
    iss: str
    name: str
    sub: str
    updatedAt: str


class TokenValidationError(Exception):
    """Raised when a bearer token cannot be validated."""


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

    def fetch_token(self, token: str) -> User:
        try:
            signing_key = self.__client.get_signing_key_from_jwt(token)
            response = jwt.decode(
                token,
                signing_key.key,
                algorithms=["EdDSA"],
                issuer=self.base_url,
                audience=self.base_url,
            )
            return cast(User, response)
        except (jwt.PyJWTError, TypeError) as exc:
            raise TokenValidationError("Invalid bearer token") from exc

    def make_not_authenticated_error(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async def __call__(self, request: Request) -> User | None:
        authorization = request.headers.get("Authorization")
        scheme, param = _get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise self.make_not_authenticated_error()
            return None

        try:
            return self.fetch_token(param)
        except TokenValidationError as exc:
            raise self.make_not_authenticated_error() from exc
