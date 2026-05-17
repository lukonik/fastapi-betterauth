import os
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_betterauth import BetterAuth, User


def _better_auth_base_url() -> str:
    return os.getenv("BETTER_AUTH_BASE_URL", "http://localhost:3000")


def _cors_origins() -> list[str]:
    raw_origins = os.getenv("DEMO_CORS_ORIGINS")
    if raw_origins:
        origins = [origin.strip() for origin in raw_origins.split(",")]
    else:
        origins = [
            _better_auth_base_url(),
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    return list(dict.fromkeys(origin for origin in origins if origin))


better_auth = BetterAuth(
    _better_auth_base_url(),
    auth_path=os.getenv("BETTER_AUTH_JWKS_PATH", "/api/auth/jwks"),
)


app = FastAPI(title="fastapi-betterauth demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home(claims: Annotated[User, Depends(better_auth)]):
    return claims.email


@app.get("/me")
def me(claims=Depends(better_auth)):
    return claims
