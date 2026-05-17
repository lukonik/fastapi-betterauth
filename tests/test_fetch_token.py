from types import SimpleNamespace
from typing import Any
from unittest import TestCase
from unittest.mock import patch

from fastapi_betterauth import BetterAuth


class _SigningKeyClient:
    def get_signing_key_from_jwt(self, token: str) -> SimpleNamespace:
        assert token == "token"
        return SimpleNamespace(key="public-key")


class TestFetchToken(TestCase):
    def test_fetch_token_returns_decoded_claims_dict(self) -> None:
        payload = {
            "sub": "user_1",
            "email": "user@example.com",
            "customClaim": "custom-value",
        }

        def decode(
            token: str,
            key: str,
            *,
            algorithms: list[str],
            issuer: str,
            audience: str,
        ) -> dict[str, Any]:
            self.assertEqual(token, "token")
            self.assertEqual(key, "public-key")
            self.assertEqual(algorithms, ["EdDSA"])
            self.assertEqual(issuer, "https://auth.example.com")
            self.assertEqual(audience, "https://auth.example.com")
            return payload

        better_auth = BetterAuth("https://auth.example.com")
        better_auth._BetterAuth__client = _SigningKeyClient()

        with patch("fastapi_betterauth.jwt.decode", decode):
            claims = better_auth.fetch_token("token")

        self.assertIs(claims, payload)
        self.assertEqual(claims, payload)
        self.assertEqual(claims["email"], "user@example.com")
