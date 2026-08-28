"""Authentication endpoints for account registration, login, and session lookup."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthSessionResponse,
    LoginRequest,
    SignUpRequest,
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/signup", response_model=AuthSessionResponse, status_code=status.HTTP_201_CREATED)
def sign_up(payload: SignUpRequest, db: Session = Depends(get_db)) -> AuthSessionResponse:
    try:
        return AuthService(db).sign_up(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)) -> UserResponse:
    try:
        signup_payload = SignUpRequest(
            email=user_in.email,
            password=user_in.password,
            full_name=user_in.full_name or "Traveler",
        )
        session = AuthService(db).sign_up(signup_payload)
        return session.user
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login")
def login(credentials: LoginRequest | UserLogin, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        req = LoginRequest(email=credentials.email, password=credentials.password)
        session = AuthService(db).login(req)
        return {
            "access_token": session.access_token,
            "token_type": "bearer",
            "user": session.user,
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user
