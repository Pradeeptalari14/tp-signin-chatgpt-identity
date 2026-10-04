"""FastAPI / ASGI Authentication Middleware for Sign in with ChatGPT.

Intercepts inbound HTTP requests, extracts Authorization Bearer headers,
and binds the authenticated ChatGPT enterprise identity to the request state.
"""

import logging
from typing import Any, Callable, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("chatgpt_auth_middleware")


class ChatGPTAuthMiddleware:
    """Authentication gateway for microservices consuming ChatGPT enterprise tokens."""

    def __init__(self, verifier_fn: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.verifier_fn = verifier_fn

    def handle_request(self, headers: Dict[str, str], payload_claims: Dict[str, Any]) -> Dict[str, Any]:
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return {"status": 401, "error": "Missing or malformed Authorization header"}

        try:
            verified_identity = self.verifier_fn(payload_claims)
            return {
                "status": 200,
                "user_id": verified_identity["sub"],
                "org_id": verified_identity.get("org_id"),
                "zdr_verified": verified_identity.get("zdr_enabled", False),
            }
        except Exception as exc:
            return {"status": 403, "error": str(exc)}


def run_middleware_demo() -> None:
    def mock_verifier(claims: Dict[str, Any]) -> Dict[str, Any]:
        if not claims.get("zdr_enabled"):
            raise PermissionError("Policy requires zdr_enabled=True")
        return claims

    middleware = ChatGPTAuthMiddleware(mock_verifier)

    headers = {"Authorization": "Bearer mock-token-value"}
    claims = {"sub": "usr_dev_42", "org_id": "org_cyber_sec", "zdr_enabled": True}

    response = middleware.handle_request(headers, claims)
    logger.info("Middleware Response: %s", response)


if __name__ == "__main__":
    run_middleware_demo()
