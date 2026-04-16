from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_app_db
from app.models.user import User
from app.schemas.auth import AuthRequest, AuthResponse
from app.services.auth import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _session_for(user: User) -> AuthResponse:
    return AuthResponse(access_token=create_access_token(user), user=user)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: AuthRequest, app_db: Session = Depends(get_app_db)) -> AuthResponse:
    username = payload.username.strip().lower()
    user = User(username=username, password_hash=hash_password(payload.password))
    app_db.add(user)

    try:
        app_db.commit()
    except IntegrityError as exc:
        app_db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already registered.",
        ) from exc

    app_db.refresh(user)
    return _session_for(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: AuthRequest, app_db: Session = Depends(get_app_db)) -> AuthResponse:
    username = payload.username.strip().lower()
    user = app_db.query(User).filter(User.username == username).one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _session_for(user)
