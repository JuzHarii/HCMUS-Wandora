"""Account registration and login business logic."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import AuthSessionResponse, LoginRequest, SignUpRequest


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def sign_up(self, payload: SignUpRequest) -> AuthSessionResponse:
        email = payload.email.lower()
        existing_user = self.db.scalar(select(User).where(User.email == email))
        if existing_user is not None:
            raise ValueError("Email này đã được đăng ký.")
        user = User(full_name=payload.full_name, email=email, password_hash=hash_password(payload.password))
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError as exc:
            # The pre-check offers a helpful response in the common case; the
            # unique database constraint covers two simultaneous requests.
            self.db.rollback()
            raise ValueError("Email này đã được đăng ký.") from exc
        self.db.refresh(user)
        return self._session_for(user)

    def login(self, payload: LoginRequest) -> AuthSessionResponse:
        user = self.db.scalar(select(User).where(User.email == payload.email.lower()))
        if user is None or not verify_password(payload.password, user.password_hash):
            raise ValueError("Email hoặc mật khẩu không đúng.")
        return self._session_for(user)

    def _session_for(self, user: User) -> AuthSessionResponse:
        return AuthSessionResponse(access_token=create_access_token(user.id), user=user)
