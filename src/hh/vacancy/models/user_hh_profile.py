from sqlalchemy import ForeignKey, String, Integer, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from hh.libs.base_model import Base


class UserHHProfileModel(Base):
    """Stores HH OAuth tokens for a user."""
    __tablename__ = "user_hh_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    hh_id: Mapped[int] = mapped_column(Integer, unique=True)
    access_token: Mapped[str] = mapped_column(String)
    refresh_token: Mapped[str] = mapped_column(String)
    is_bot_active: Mapped[bool] = mapped_column(Boolean, default=False)
