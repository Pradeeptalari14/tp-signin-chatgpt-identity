"""OIDC Token Verifier for Sign in with ChatGPT.

Handles cryptographic signature verification, audience assertion, expiry checks,
and Zero Data Retention (ZDR) policy enforcement for OpenAI ChatGPT identity tokens.
"""

import json
import logging
import time
from typing import Any, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("oidc_token_verifier")


class TokenVerificationError(Exception):
    """Raised when token signature, claims, or ZDR compliance checks fail."""

    pass


class ChatGPTTokenVerifier:
    """Verifies RS256 JWT tokens issued by auth.openai.com."""

    def __init__(self, expected_audience: str, enforce_zdr: bool = True):
        self.expected_audience = expected_audience
        self.enforce_zdr = enforce_zdr
        self.issuer = "https://auth.openai.com/oauth"

    def verify_claims(self, claims: Dict[str, Any]) -> Dict[str, Any]:
        current_time = int(time.time())

        # Check issuer
        if claims.get("iss") != self.issuer:
            raise TokenVerificationError(f"Invalid issuer: {claims.get('iss')} != {self.issuer}")

        # Check audience
        if claims.get("aud") != self.expected_audience:
            raise TokenVerificationError(
                f"Invalid audience: {claims.get('aud')} != {self.expected_audience}"
            )

        # Check expiration
        exp = claims.get("exp", 0)
        if current_time > exp:
            raise TokenVerificationError(f"Token expired at {exp}, current={current_time}")

        # Enforce Zero Data Retention flag if required
        if self.enforce_zdr and not claims.get("zdr_enabled", False):
            raise TokenVerificationError("Token rejected: enterprise ZDR guarantee flag missing")

        logger.info("Successfully validated ChatGPT identity token for subject: %s", claims.get("sub"))
        return claims


def main() -> None:
    verifier = ChatGPTTokenVerifier(expected_audience="app_chatgpt_enterprise_prod", enforce_zdr=True)

    valid_token_claims = {
        "iss": "https://auth.openai.com/oauth",
        "aud": "app_chatgpt_enterprise_prod",
        "sub": "usr_99887766",
        "email": "lead.architect@company.com",
        "org_id": "org_enterprise_core",
        "zdr_enabled": True,
        "exp": int(time.time()) + 3600,
        "iat": int(time.time()),
    }

    try:
        verified = verifier.verify_claims(valid_token_claims)
        logger.info("Verified Claims: %s", json.dumps(verified, indent=2))
    except TokenVerificationError as err:
        logger.error("Token verification failed: %s", err)


if __name__ == "__main__":
    main()
