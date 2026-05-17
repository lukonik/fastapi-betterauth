# fastapi-betterauth

FastAPI helpers for Better Auth JWT verification.

The package verifies Better Auth JWTs with PyJWT and JWKS, then exposes the
verified claims either through a plain Python verifier or a FastAPI dependency.

## Installation

```bash
pip install fastapi-betterauth
```

For FastAPI dependency helpers:

```bash
pip install "fastapi-betterauth[fastapi]"
```

## Usage

```python
from fastapi_betterauth import BetterAuthVerifier

verifier = BetterAuthVerifier("https://your-app.example.com")

claims = verifier.validate_token(token)
```

By default, the verifier:

- reads keys from `/api/auth/jwks`
- verifies the `EdDSA` algorithm
- expects `iss` to match `base_url`
- expects `aud` to match `base_url`

## FastAPI

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi_betterauth import BetterAuthVerifier

app = FastAPI()
verifier = BetterAuthVerifier("https://your-app.example.com")
current_user = verifier.fastapi_dependency()


@app.get("/me")
def me(claims: Annotated[dict, Depends(current_user)]):
    return claims
```

Invalid tokens are converted to `401 Unauthorized` responses.

## Configuration

```python
from fastapi_betterauth import BetterAuthVerifier

verifier = BetterAuthVerifier(
    "https://your-app.example.com",
    jwks_path="/api/auth/jwks",
    issuer="https://your-app.example.com",
    audience="https://your-app.example.com",
    algorithms=("EdDSA",),
    cache_jwk_set=True,
    lifespan=300,
)
```

Set `issuer=None` or `audience=None` to disable that specific validation.

## Compatibility API

The older module-level style is still available:

```python
from fastapi_betterauth import init_client, validate_token

init_client("https://your-app.example.com")
claims = validate_token(token)
```

Prefer `BetterAuthVerifier` for new code because it avoids global state and
works better for tests, multiple apps, and multi-tenant services.

## FastAPI demo server

This repository includes a small FastAPI demo in `examples/fastapi_demo.py`.
Use it to test a real bearer token issued by your Better Auth application.

```bash
BETTER_AUTH_BASE_URL="http://localhost:3000" uv run python -m uvicorn examples.fastapi_demo:app --reload
```

The demo reads JWKS from `${BETTER_AUTH_BASE_URL}/api/auth/jwks` by default.
Override that path with `BETTER_AUTH_JWKS_PATH` if your Better Auth app uses a
different route.

Public route:

```bash
curl http://localhost:8000/public
```

Protected route:

```bash
curl \
  -H "Authorization: Bearer $BETTER_AUTH_TOKEN" \
  http://localhost:8000/me
```
