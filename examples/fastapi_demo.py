import os
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError, PyJWKClientError

from fastapi_betterauth import init_client, validate_token

bearer = HTTPBearer(auto_error=False)


def _cors_origins() -> list[str]:
    raw_origins = os.getenv("DEMO_CORS_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    base_url = os.getenv("BETTER_AUTH_BASE_URL")
    jwks_path = os.getenv("BETTER_AUTH_JWKS_PATH", "/api/auth/jwks")

    if base_url:
        init_client(base_url.rstrip("/"), auth_path=jwks_path)

    yield


app = FastAPI(title="fastapi-betterauth demo", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def current_claims(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return validate_token(credentials.credentials)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Better Auth client is not configured",
        ) from exc
    except (InvalidTokenError, PyJWKClientError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@app.get("/health")
def health() -> dict[str, bool]:
    return {"auth_configured": bool(os.getenv("BETTER_AUTH_BASE_URL"))}


@app.get("/public")
def public() -> dict[str, str]:
    return {"message": "This route does not require auth."}


@app.get("/me")
def me(claims: Annotated[dict[str, Any], Depends(current_claims)]) -> dict[str, Any]:
    return {"claims": claims}


@app.get("/protected")
def protected(
    claims: Annotated[dict[str, Any], Depends(current_claims)],
) -> dict[str, Any]:
    return {
        "message": "You reached a protected FastAPI route.",
        "subject": claims.get("sub"),
        "claims": claims,
    }
