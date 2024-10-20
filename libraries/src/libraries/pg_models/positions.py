from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from base import Base
from typing import Optional


class Position(Base):
    __tablename__ = "positions"

    line_name: Mapped[int] = mapped_column(primary_key=True) # PKEY WILL BE DELETED BY MIGRATION SCRIPT
    course_loid: Mapped[int]
    day_course_loid: Mapped[int]
    vehicle_id: Mapped[int]
    delay_sec: Mapped[Optional[int]]
    longitude: Mapped[float]
    latitude: Mapped[float]
    angle: Mapped[int]
    reached_meters: Mapped[int]
    variant_loid: Mapped[int]
    last_ping_date: Mapped[int] = mapped_column(BigInteger)
    distance_to_nearest_stop_point: Mapped[int]
    nearest_symbol: Mapped[str]
    operator: Mapped[int]
    on_stop_point: Mapped[Optional[str]]
    order_in_course: Mapped[int]
    optional_direction: Mapped[int]
