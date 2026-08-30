"""Firebase token verification and security utilities."""

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = structlog.get_logger()

# HTTP Bearer scheme for Swagger UI integration
bearer_scheme = HTTPBearer(auto_error=True)


class FirebaseUser:
    """Represents a verified Firebase user."""

    def __init__(self, uid: str, email: str | None = None, name: str | None = None) -> None:
        self.uid = uid
        self.email = email
        self.name = name

    def __repr__(self) -> str:
        return f"FirebaseUser(uid={self.uid!r}, email={self.email!r})"


async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> FirebaseUser:
    """Verify a Firebase ID token from the Authorization header.

    Returns a FirebaseUser with the decoded token claims.
    Raises 401 if the token is invalid or expired.
    """
    token = credentials.credentials

    try:
        from firebase_admin import auth

        decoded_token = auth.verify_id_token(token)
        return FirebaseUser(
            uid=decoded_token["uid"],
            email=decoded_token.get("email"),
            name=decoded_token.get("name"),
        )
    except ImportError:
        logger.warning("firebase_admin_not_configured", hint="Using dev bypass")
        # Development fallback: accept any token and extract uid
        # This should NEVER be used in production
        from app.config import settings

        if not settings.is_production:
            return FirebaseUser(uid=token, email="dev@localhost", name="Dev User")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase Admin SDK not configured",
        )
    except Exception as e:
        logger.warning("firebase_token_invalid", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Alias for convenience
get_current_user = verify_firebase_token
