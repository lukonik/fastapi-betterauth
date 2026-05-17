# Better Auth SQLite Demo

TanStack Start example with Better Auth email/password registration and login.
User, session, account, verification, and JWKS records are stored in SQLite.

## Run

```bash
pnpm install
pnpm dev
```

Open `http://localhost:3000`, then use `/register` and `/login`.

## SQLite

The auth server uses `better-sqlite3` and writes to:

```text
data/auth.sqlite
```

Override the path with:

```bash
BETTER_AUTH_SQLITE_PATH="./data/custom-auth.sqlite" pnpm dev
```

Better Auth migrations run automatically before auth requests are handled. The
expected table layout is also checked in as `auth-schema.sql`.

## Environment

Set a stable secret outside local experiments:

```bash
BETTER_AUTH_SECRET="replace-with-a-long-random-value"
```

If the frontend runs on a different origin, set:

```bash
BETTER_AUTH_TRUSTED_ORIGIN="http://localhost:3000"
```

## Build

```bash
pnpm build
```
