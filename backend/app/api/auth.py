from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.security import create_access_token
from backend.app.db.session import get_db
from backend.app.schemas.user import UserLogin, TokenResponse, UserOut
from backend.app.services.auth_service import AuthService, get_current_user
from backend.app.services.audit_service import AuditService
from backend.app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with credentials.
    Sets secure HttpOnly cookie and returns JWT payload.
    Enforces brute-force rate limiting.
    """
    client_ip = request.client.host if request.client else "unknown"
    user = AuthService.authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
        client_ip=client_ip
    )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value, "email": user.email}
    )

    # Set secure HttpOnly cookie
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=access_token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user)
    )


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Terminates authenticated session and clears HttpOnly cookie.
    """
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        path="/"
    )
    AuditService.log_event(
        db=db,
        action="AUTH_LOGOUT",
        entity_type="AUTH",
        actor_id=current_user.id,
        source_ip=request.client.host if request.client else None,
        result="SUCCESS"
    )
    return {"message": "Successfully logged out."}


@router.get("/me", response_model=UserOut)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get authenticated user's profile. Passwords are never serialized.
    """
    return UserOut.model_validate(current_user)
