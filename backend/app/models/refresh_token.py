from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class TokenStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


def get_utc_now():
    return datetime.now(timezone.utc)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TokenStatus.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(default=get_utc_now)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationship using string reference
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
