from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...api.deps import get_db
from ...core.security import create_access_token, get_password_hash, verify_password
from ...models.user import User
from ...schemas.auth import Token, UserLogin, UserRegister, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)) -> User:
    """Đăng ký tài khoản người dùng mới."""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered",
        )

    hashed_pw = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_pw,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> dict[str, str]:
    """Đăng nhập bằng Email & Password, sinh mã JWT Access Token (HS256)."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}
