from sqlalchemy.orm import Mapped, mapped_column
from base import Base


class Operator(Base):
    __tablename__ = "operators"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
