from typing import Optional, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.security import verify_password, create_access_token, decode_access_token
from backend.app.core.rate_limit import limiter
from backend.app.db.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.services.audit_service import AuditService

security_bearer = HTTPBearer(auto_error=False)


class AuthService:
    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
        client_ip: str
    ) -> User:
        """Authenticate user credentials with rate limiting and audit logging."""
        rate_key = f"login:{client_ip}"
        allowed, remaining = limiter.is_allowed(
            rate_key,
            max_attempts=settings.RATE_LIMIT_LOGIN_MAX_ATTEMPTS,
            window_seconds=settings.RATE_LIMIT_LOGIN_WINDOW_SECONDS
        )
        if not allowed:
            AuditService.log_event(
                db=db,
                action="AUTH_LOGIN_RATE_LIMITED",
                entity_type="AUTH",
                source_ip=client_ip,
                result="DENIED",
                metadata={"email": email}
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed login attempts. Please try again later."
            )

        user = db.query(User).filter(User.email == email.lower().strip()).first()
        if not user or not verify_password(password, user.password_hash):
            AuditService.log_event(
                db=db,
                action="AUTH_LOGIN_FAILED",
                entity_type="AUTH",
                actor_id=user.id if user else None,
                source_ip=client_ip,
                result="FAILURE",
                metadata={"attempted_email": email}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:
            AuditService.log_event(
                db=db,
                action="AUTH_LOGIN_INACTIVE_USER",
                entity_type="USER",
                actor_id=user.id,
                source_ip=client_ip,
                result="DENIED"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        # Successful login: reset rate limiter for this client IP
        limiter.reset(rate_key)
        AuditService.log_event(
            db=db,
            action="AUTH_LOGIN_SUCCESS",
            entity_type="AUTH",
            actor_id=user.id,
            source_ip=client_ip,
            result="SUCCESS"
        )
        return user


def get_token_from_request(request: Request, bearer: Optional[HTTPAuthorizationCredentials] = None) -> Optional[str]:
    """Extract token from HttpOnly cookie first, then Authorization Bearer header."""
    cookie_token = request.cookies.get(settings.COOKIE_NAME)
    if cookie_token:
        return cookie_token
    if bearer and bearer.credentials:
        return bearer.credentials
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    return None


def get_current_user(
    request: Request,
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    """Dependency that authenticates the user from JWT cookie or Authorization header."""
    token = get_token_from_request(request, bearer)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in."
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication session."
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token claims."
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account is deactivated."
        )

    return user


def get_optional_current_user(
    request: Request,
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Dependency allowing anonymous/guest access with optional user identification."""
    token = get_token_from_request(request, bearer)
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user and user.is_active:
        return user
    return None


def require_roles(allowed_roles: List[UserRole]):
    """Role-Based Access Control (RBAC) dependency factory."""
    def role_checker(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if current_user.role not in allowed_roles:
            AuditService.log_event(
                db=db,
                action="RBAC_ACCESS_DENIED",
                entity_type="ENDPOINT",
                actor_id=current_user.id,
                source_ip=request.client.host if request.client else None,
                result="DENIED",
                metadata={
                    "user_role": current_user.role,
                    "allowed_roles": [r.value for r in allowed_roles],
                    "path": request.url.path
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    return role_checker
