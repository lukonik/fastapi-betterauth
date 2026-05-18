# fastapi-betterauth

A simple FastAPI dependency to securely validate JSON Web Tokens (JWTs) issued by [Better Auth](https://better-auth.com/).

If your frontend logs users in with Better Auth and sends their tokens to your FastAPI backend, this library will verify those tokens and extract the user's details for you.

## Installation

```bash
pip install "fastapi-betterauth"
```

The package requires Python 3.10+

## Usage

Enable the Better Auth JWT plugin on your Better Auth server:

```ts
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [jwt()],
});
```

Enable the Better Auth JWT client plugin where your frontend requests tokens:

```ts
import { jwtClient } from "better-auth/client/plugins";
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  plugins: [jwtClient()],
});
```

Create a FastAPI dependency with your Better Auth base URL:

```py
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi_betterauth import BetterAuth, User

app = FastAPI()

better_auth = BetterAuth("http://localhost:3000")


@app.get("/me")
def me(user: Annotated[User, Depends(better_auth)]):
    return user
```

Send the JWT to FastAPI as a bearer token:

```ts
const { data } = await authClient.token();

const response = await fetch("http://127.0.0.1:8000/me", {
  headers: {
    Authorization: `Bearer ${data.token}`,
  },
});
```

If your Better Auth JWKS endpoint is not `/api/auth/jwks`, pass a custom path:

```py
better_auth = BetterAuth(
    "https://auth.example.com",
    auth_path="/custom/auth/jwks",
)
```

For optional authentication, set `auto_error=False`. Missing credentials return
`None` instead of raising a 401 response. Invalid bearer tokens still raise a
401 response:

```py
optional_better_auth = BetterAuth(
    "https://auth.example.com",
    auto_error=False,
)
```

## API Table

### `BetterAuth`

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `base_url` | `str` | Required | Public base URL of your Better Auth server. It is also used as the expected JWT issuer and audience. |
| `auth_path` | `str` | `"/api/auth/jwks"` | Path to the Better Auth JWKS endpoint. |
| `cache_keys` | `bool` | `False` | Passed to `jwt.PyJWKClient` to cache individual signing keys. |
| `max_cached_keys` | `int` | `16` | Maximum number of signing keys to cache when `cache_keys=True`. |
| `cache_jwk_set` | `bool` | `True` | Passed to `jwt.PyJWKClient` to cache the JWKS response. |
| `lifespan` | `float` | `300` | JWKS cache lifespan in seconds. |
| `headers` | `dict[str, Any] \| None` | `None` | Extra headers sent when fetching the JWKS. |
| `timeout` | `float` | `30` | Timeout in seconds for fetching the JWKS. |
| `ssl_context` | `SSLContext \| None` | `None` | Custom SSL context for the JWKS request. |
| `auto_error` | `bool` | `True` | When `True`, missing or invalid bearer tokens raise `401 Not authenticated`. When `False`, missing credentials return `None`; invalid bearer tokens still raise `401 Not authenticated`. |

### Methods and Types

| Name | Type | Description |
| --- | --- | --- |
| `BetterAuth.fetch_token(token)` | Method | Verifies a raw JWT string and returns decoded claims as `User`. Raises `TokenValidationError` when validation fails. |
| `BetterAuth.make_not_authenticated_error()` | Method | Builds the FastAPI `HTTPException` used for `401 Not authenticated` responses. |
| `User` | `TypedDict` | Common Better Auth JWT claims, including `id`, `sub`, `email`, `name`, `image`, `emailVerified`, `iat`, `exp`, `iss`, `aud`, `createdAt`, and `updatedAt`. Extra claims may still be present at runtime. |
| `TokenValidationError` | Exception | Raised by `fetch_token` when a token cannot be validated. |

## Guide

### What JWKS is

JWKS means JSON Web Key Set. It is a JSON document that contains public keys for
verifying JWT signatures.

JWT authentication usually has two sides:

1. Better Auth signs a token with a private key.
2. FastAPI verifies the token with the matching public key.

FastAPI does not need the private key. It only needs to know where to find the
public keys. Better Auth exposes those public keys through its JWKS endpoint,
which defaults to:

```text
<better-auth-base-url>/api/auth/jwks
```

For example, if Better Auth runs at `http://localhost:3000`, the JWKS endpoint is:

```text
http://localhost:3000/api/auth/jwks
```

### How it integrates with FastAPI

`fastapi-betterauth` wraps this verification flow in a FastAPI dependency:

1. The client signs in through Better Auth.
2. The frontend asks Better Auth for a JWT with `authClient.token()`.
3. The frontend sends that token to FastAPI in the `Authorization` header.
4. `BetterAuth` reads the bearer token from the request.
5. `BetterAuth` downloads the signing key from the JWKS endpoint when needed.
6. The JWT is verified with `EdDSA`.
7. The token `iss` and `aud` claims must match the `base_url` passed to
   `BetterAuth`.
8. Your route receives the decoded claims as a normal dependency value.

That means your FastAPI routes can stay small:

```py
@app.get("/private")
def private_route(user: Annotated[User, Depends(better_auth)]):
    return {"user_id": user["id"], "email": user["email"]}
```

If the request has no bearer token, or the token is expired, malformed, signed
with the wrong key, or issued for a different Better Auth base URL, the dependency
returns `401 Not authenticated`.
