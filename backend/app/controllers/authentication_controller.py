import os
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_and_get_refresh_token,
    revoke_refresh_token,
    revoke_all_user_tokens
)
from app.db import get_db
from app.models.user import User
from app.schemas.user_schema import UserRegister, UserLogin, UserProfile
from app.schemas.token_schema import TokenResponse, TokenRefreshRequest, LogoutResponse

load_dotenv()

logger = logging.getLogger(__name__)
AUTH_CONTROLLER = APIRouter(prefix="/authentication")
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authentication/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


@AUTH_CONTROLLER.post("/register", response_model=TokenResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.user_email == user.user_email).first()
    if existing_user:
        logger.warning(f"User with email {user.user_email} already exists.")
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.user_password)
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        user_email=user.user_email,
        user_password=hashed_password,
        role=user.role,
        registered_at=datetime.now(timezone.utc),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": new_user.user_email})
    refresh_token = create_refresh_token(user_id=new_user.id, db=db)

    logger.info(f"User {user.user_email} registered successfully.")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@AUTH_CONTROLLER.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_email == user.user_email).first()
    if not db_user or not verify_password(user.user_password, db_user.user_password):
        logger.warning(f"Login failed for user '{user.user_email}'.")
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": db_user.user_email})
    refresh_token = create_refresh_token(user_id=db_user.id, db=db)

    logger.info(f"User '{user.user_email}' logged in successfully.")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@AUTH_CONTROLLER.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_request: TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        # Start transaction to prevent race conditions
        db_token = verify_and_get_refresh_token(refresh_request.refresh_token, db)
        user = db_token.user

        # Revoke the used token first
        revoke_refresh_token(refresh_request.refresh_token, db)

        # Create new tokens
        access_token = create_access_token(data={"sub": user.user_email})
        new_refresh_token = create_refresh_token(user_id=user.id, db=db)

        logger.info(f"Tokens refreshed for user '{user.user_email}'.")
        return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error during token refresh: {str(e)}")
        raise


@AUTH_CONTROLLER.post("/logout", response_model=LogoutResponse)
def logout(refresh_request: TokenRefreshRequest, db: Session = Depends(get_db)):
    """
    Logout endpoint that revokes the provided refresh token
    """
    try:
        revoke_refresh_token(refresh_request.refresh_token, db)
        logger.info("User logged out successfully")
    except Exception as e:
        logger.warning(f"Logout attempt with potentially invalid token: {str(e)}")
    
    return {"message": "Successfully logged out"}


@AUTH_CONTROLLER.post("/logout-all", response_model=LogoutResponse)
def logout_all(refresh_request: TokenRefreshRequest, db: Session = Depends(get_db)):
    """
    Logout endpoint that revokes all refresh tokens for the user
    Always returns success, even if tokens are already invalid
    """
    try:
        db_token = verify_and_get_refresh_token(refresh_request.refresh_token, db)
        user_id = db_token.user_id
        
        revoked_count = revoke_all_user_tokens(user_id, db)
        logger.info(f"User {user_id} logged out from all devices successfully, revoked {revoked_count} tokens")
    except Exception as e:
        logger.warning(f"Logout all attempt with potentially invalid token: {str(e)}")
    
    return {"message": "Successfully logged out from all devices"}


@AUTH_CONTROLLER.get("/me", response_model=UserProfile)
def get_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    user_email = payload.get("sub")
    user = db.query(User).filter(User.user_email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    return user
