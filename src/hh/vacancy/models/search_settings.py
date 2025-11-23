from typing import Optional

from sqlalchemy import ForeignKey, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from hh.libs.base_model import Base


class SearchSettingsModel(Base):
    """Stores user search configuration."""
    __tablename__ = "search_settings"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)

    resume_id: Mapped[str] = mapped_column(String)
    search_text: Mapped[str] = mapped_column(String)
    area_id: Mapped[str] = mapped_column(String)
    salary: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String)
    period: Mapped[int] = mapped_column(Integer)
    schedule: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    employment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    order_by: Mapped[str] = mapped_column(String)
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)