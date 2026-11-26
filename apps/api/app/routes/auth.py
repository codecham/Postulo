"""Account creation and login."""

from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserRead
from app.services import users
from app.services.auth_throttle import AuthThrottle, TooManyAttemptsError

router = APIRouter(prefix="/auth", tags=["auth"])

TOO_MANY_ATTEMPTS: dict[int | str, dict[str, Any]] = {
    status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too many attempts, retry later"}
}


@lru_cache
def get_auth_throttle() -> AuthThrottle:
    """Dependency: one throttle for the whole process, so the counts are shared."""
    return AuthThrottle.from_settings(get_settings())


Throttle = Annotated[AuthThrottle, Depends(get_auth_throttle)]


def client_ip(request: Request) -> str:
    # Behind the reverse proxy, Uvicorn's --proxy-headers puts the real client IP here
    return request.client.host if request.client else "unknown"


def too_many_attempts(error: TooManyAttemptsError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many attempts, try again later",
        headers={"Retry-After": str(error.retry_after_seconds)},
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Registration is closed on this server"},
        status.HTTP_409_CONFLICT: {"description": "Email already registered"},
        **TOO_MANY_ATTEMPTS,
    },
)
def register(
    data: UserCreate,
    request: Request,
    throttle: Throttle,
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    if not get_settings().registration_open:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is closed on this server",
        )
    try:
        throttle.check_registration(client_ip(request))
        user = users.create_user(db, data)
    except TooManyAttemptsError as error:
        raise too_many_attempts(error) from None
    except users.EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None
    return UserRead.model_validate(user)


@router.post(
    "/login",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Incorrect email or password"},
        **TOO_MANY_ATTEMPTS,
    },
)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    throttle: Throttle,
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    # OAuth2 calls the field "username": we use it for the email
    try:
        throttle.check_login(client_ip(request), form.username)
    except TooManyAttemptsError as error:
        raise too_many_attempts(error) from None
    user = users.authenticate_user(db, form.username, form.password)
    if user is None:
        throttle.record_failed_login(form.username)
        # Same message whether the email or the password is wrong:
        # never tell an attacker which emails have an account
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(
        access_token=create_access_token(str(user.id)),
        expires_in=get_settings().access_token_expire_minutes * 60,
    )
