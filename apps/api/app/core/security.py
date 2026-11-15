from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import AuthenticationException
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)

# Cached PyJWKClient for asymmetric keys (RS256, ES256)
_jwks_client: Optional[jwt.PyJWKClient] = None


def get_jwks_client() -> Optional[jwt.PyJWKClient]:
    global _jwks_client
    if _jwks_client is None and settings.supabase_url:
        jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        try:
            _jwks_client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=3600)
        except Exception as exc:
            logger.warning(f"Could not initialize PyJWKClient for {jwks_url}: {exc}")
    return _jwks_client


def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a Supabase-issued JWT:
    - Verifies cryptographic signature (via JWKS for RS256/ES256 or JWT secret for HS256)
    - Verifies expiration (`exp`)
    - Verifies audience (`aud`)
    - Verifies issuer (`iss`) if configured
    """
    if not token or not token.strip():
        raise AuthenticationException("Empty bearer token provided.")

    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.DecodeError as exc:
        raise AuthenticationException(f"Malformed token header: {exc}")

    alg = unverified_header.get("alg", "HS256")
    kid = unverified_header.get("kid")

    # Determine key for verification
    key: Optional[str] = None
    if alg.startswith("RS") or alg.startswith("ES"):
        client = get_jwks_client()
        if client:
            try:
                signing_key = client.get_signing_key_from_jwt(token)
                key = signing_key.key
            except Exception as exc:
                raise AuthenticationException(f"Failed to fetch public key from JWKS: {exc}")
        if not key:
            raise AuthenticationException(f"No verification key found for algorithm '{alg}' and kid '{kid}'.")
    else:
        # Symmetric HS256
        key = settings.supabase_jwt_secret or settings.supabase_service_role_key or settings.supabase_anon_key
        if not key and settings.roamly_env in ("test", "development"):
            key = "roamly-default-development-jwt-secret-key-32-chars"

        if not key:
            raise AuthenticationException("No JWT signing secret configured on server.")

    # Validation options
    decode_options = {
        "verify_signature": True,
        "verify_exp": settings.jwt_verify_exp,
        "require": ["exp", "sub"],
    }

    expected_issuer = None
    if settings.jwt_verify_iss and settings.supabase_url:
        expected_issuer = f"{settings.supabase_url.rstrip('/')}/auth/v1"
        decode_options["verify_iss"] = True
    else:
        decode_options["verify_iss"] = False

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=settings.jwt_algorithms,
            audience=settings.jwt_audience if settings.jwt_audience else None,
            issuer=expected_issuer,
            options=decode_options,
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationException("Token has expired.")
    except jwt.InvalidAudienceError:
        raise AuthenticationException("Token audience is invalid.")
    except jwt.InvalidIssuerError:
        raise AuthenticationException("Token issuer is invalid.")
    except jwt.InvalidSignatureError:
        raise AuthenticationException("Invalid token signature.")
    except jwt.InvalidTokenError as exc:
        raise AuthenticationException(f"Invalid token: {exc}")


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency: Authenticates incoming request using Supabase JWT and resolves User.
    Auto-provisions user row if user is authentic in Supabase but not yet synced locally.
    """
    if not credentials or not credentials.credentials:
        raise AuthenticationException("Missing Bearer authorization token in request header.")

    token = credentials.credentials
    payload = verify_supabase_jwt(token)

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationException("JWT missing subject ('sub') claim.")

    # Resolve User in database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        email = payload.get("email") or f"{user_id}@roamly.user"
        user_metadata = payload.get("user_metadata") or {}
        full_name = user_metadata.get("full_name") or user_metadata.get("name")

        user = User(
            id=user_id,
            email=email,
            full_name=full_name,
            preferred_currency="USD",
            locale="en-US",
        )
        db.add(user)
        await db.flush()

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Optional authentication dependency: returns User if valid token is provided, None otherwise."""
    if not credentials or not credentials.credentials:
        return None
    try:
        return await get_current_user(credentials=credentials, db=db)
    except AuthenticationException:
        return None


def create_test_token(
    user_id: str,
    email: str = "traveler@example.com",
    role: str = "authenticated",
    expires_in_seconds: int = 3600,
    secret: Optional[str] = None,
    audience: str = "authenticated",
    issuer: Optional[str] = None,
) -> str:
    """Utility function to create valid test JWTs for automated test suites."""
    signing_secret = secret or settings.supabase_jwt_secret or settings.supabase_service_role_key or settings.supabase_anon_key or "roamly-default-development-jwt-secret-key-32-chars"
    now = datetime.now(timezone.utc)
    
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "aud": audience,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
    }
    if issuer:
        payload["iss"] = issuer

    return jwt.encode(payload, signing_secret, algorithm="HS256")
