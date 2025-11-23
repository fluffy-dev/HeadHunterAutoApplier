from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from hh.libs.base_model import Base


class ApplicationModel(Base):
    """History of applied vacancies."""
    __tablename__ = "applications"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    vacancy_id: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String)

    __table_args__ = (
        UniqueConstraint("user_id", "vacancy_id", name="_user_vacancy_uc"),
    )