import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken, TokenStatus
import logging

logger = logging.getLogger(__name__)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not found in environment variables.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30


def cleanup_old_tokens(user_id: int, db: Session) -> None:
    """
    Clean up expired and revoked tokens for a user.
    This version ensures only ONE active token per user (single-device mode).
    """
    try:
        now = datetime.now(timezone.utc)

        # Mark expired tokens as EXPIRED (only if they're still ACTIVE)
        # Convert now to naive datetime to match database format
        now_naive = now.replace(tzinfo=None)
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.expires_at < now_naive,
            RefreshToken.status == TokenStatus.ACTIVE,
        ).update({"status": TokenStatus.EXPIRED})

        # LIMIT to maximum 5 active tokens per user (instead of 1)
        # This prevents issues with concurrent requests
        active_tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.status == TokenStatus.ACTIVE,
        ).order_by(RefreshToken.created_at.desc()).all()
        
        # Revoke old tokens if more than 5 active tokens
        if len(active_tokens) > 5:
            for token in active_tokens[5:]:
                token.status = TokenStatus.REVOKED

        # Delete old tokens that are either expired or revoked and older than 7 days
        cutoff_date = (now - timedelta(days=7)).replace(tzinfo=None)
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.status.in_([TokenStatus.EXPIRED, TokenStatus.REVOKED]),
            RefreshToken.created_at < cutoff_date,
        ).delete(synchronize_session=False)

        db.commit()
        logger.info(f"Cleaned up old tokens for user {user_id}")
    except Exception as e:
        logger.error(f"Error cleaning up old tokens for user {user_id}: {str(e)}")
        db.rollback()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: int, db: Session) -> str:
    try:
        cleanup_old_tokens(user_id, db)

        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        expires_at = datetime.now(timezone.utc) + expires_delta

        refresh_token = jwt.encode(
            {"sub": str(user_id), "exp": expires_at.timestamp()}, SECRET_KEY, algorithm=ALGORITHM
        )

        db_token = RefreshToken(
            token=refresh_token,
            expires_at=expires_at.replace(tzinfo=None),  # Store as naive datetime
            status=TokenStatus.ACTIVE,
            user_id=user_id,
        )
        db.add(db_token)
        db.commit()

        logger.info(
            f"Created new refresh token for user {user_id}, expires at {expires_at}"
        )
        return refresh_token
    except Exception as e:
        logger.error(f"Error creating refresh token for user {user_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating refresh token")


def verify_token(token: str, token_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning(f"{token_type.title()} token has expired")
        raise HTTPException(
            status_code=401, detail=f"{token_type.title()} token has expired"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid {token_type} token: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid {token_type} token")


def verify_and_get_refresh_token(token: str, db: Session) -> RefreshToken:
    verify_token(token, "refresh")

    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == token, RefreshToken.status == TokenStatus.ACTIVE)
        .first()
    )

    if not db_token:
        logger.warning("Refresh token not found or has been revoked")
        raise HTTPException(
            status_code=401, detail="Refresh token not found or has been revoked"
        )

    # Compare using naive datetimes since DB stores naive datetime
    if db_token.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        db_token.status = TokenStatus.EXPIRED
        db.commit()
        logger.warning("Refresh token has expired")
        raise HTTPException(status_code=401, detail="Refresh token has expired")

    return db_token


def revoke_refresh_token(token: str, db: Session) -> None:
    try:
        db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if db_token:
            db_token.status = TokenStatus.REVOKED
            db.commit()
            logger.info(f"Revoked refresh token for user {db_token.user_id}")
    except Exception as e:
        logger.error(f"Error revoking refresh token: {str(e)}")
        db.rollback()


def revoke_all_user_tokens(user_id: int, db: Session) -> int:
    """
    Revoke all active refresh tokens for a specific user.
    "logout from all devices" functionality
    """
    try:
        updated_count = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.user_id == user_id,
                RefreshToken.status == TokenStatus.ACTIVE,
            )
            .update({"status": TokenStatus.REVOKED})
        )

        db.commit()
        logger.info(f"Revoked {updated_count} active tokens for user {user_id}")
        return updated_count
    except Exception as e:
        logger.error(f"Error revoking all tokens for user {user_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error revoking tokens")
