from datetime import datetime, timezone
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.refresh_token import RefreshToken


def get_utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[int] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(String(15), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(15), nullable=False, index=True)
    user_email: Mapped[str] = mapped_column(
        String(40), nullable=False, unique=True, index=True
    )
    user_password: Mapped[str] = mapped_column(String(80), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(default=get_utc_now)
    edited_at: Mapped[datetime] = mapped_column(onupdate=get_utc_now, nullable=True)

    # Relationship with refresh tokens
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
