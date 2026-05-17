import os
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError, PyJWKClientError

from fastapi_betterauth import BetterAuth, init_client, validate_token

bearer = HTTPBearer(auto_error=False)

better_auth = BetterAuth("http://localhost:3000")


def _cors_origins() -> list[str]:
    raw_origins = os.getenv("DEMO_CORS_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


app = FastAPI(title="fastapi-betterauth demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", dependencies=[Depends(better_auth)])
def home():
    return "Hello world"
