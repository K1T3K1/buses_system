from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from base import Base
from typing import Optional


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    line_name: Mapped[str]
    course_loid: Mapped[int]
    day_course_loid: Mapped[int]
    vehicle_id: Mapped[int]
    delay_sec: Mapped[Optional[int]]
    longitude: Mapped[float]
    latitude: Mapped[float]
    angle: Mapped[int]
    reached_meters: Mapped[int]
    variant_loid: Mapped[int]
    last_ping_date: Mapped[int]
    distance_to_nearest_stop_point: Mapped[int]
    nearest_symbol: Mapped[str]
    operator: Mapped[int] = mapped_column(ForeignKey("operators.id"))
    on_stop_point: Mapped[Optional[str]]
    order_in_course: Mapped[int]
    optional_direction: Mapped[int] = mapped_column(ForeignKey("directions.id"))
