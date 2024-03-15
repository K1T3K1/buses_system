from pydantic import BaseModel, ConfigDict, Field, AliasGenerator
from pydantic.alias_generators import to_camel
from typing import Optional, ClassVar
from .parquet_model import ParquetModel
import pyarrow as pa

class Vehicle(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(validation_alias=to_camel, serialization_alias=to_camel),
        arbitrary_types_allowed=True
    )
    line_name: str
    course_loid: int
    day_course_loid: int
    vehicle_id: int
    delay_sec: Optional[int] = None
    longitude: float
    latitude: float
    angle: int
    reached_meters: int
    variant_loid: int
    last_ping_date: int
    distance_to_nearest_stop_point: int
    nearest_symbol: str
    operator: str
    on_stop_point: Optional[str] = None
    order_in_course: int
    optional_direction: str

    parquet_schema: ClassVar[pa.Schema] = pa.schema([
        pa.field("line_name", pa.string()),
        pa.field("course_loid", pa.int64()),
        pa.field("day_course_loid", pa.int64()),
        pa.field("vehicle_id", pa.int64()),
        pa.field("delay_sec", pa.int64()),
        pa.field("longitude", pa.float64()),
        pa.field("latitude", pa.float64()),
        pa.field("angle", pa.int64()),
        pa.field("reached_meters", pa.int64()),
        pa.field("variant_loid", pa.int64()),
        pa.field("last_ping_date", pa.int64()),
        pa.field("distance_to_nearest_stop_point", pa.int64()),
        pa.field("nearest_symbol", pa.string()),
        pa.field("operator", pa.string()),
        pa.field("on_stop_point", pa.string()),
        pa.field("order_in_course", pa.int64()),
        pa.field("optional_direction", pa.string())
    
    ])

class RunningVehicles(ParquetModel):
    vehicles: list[Vehicle]
    offline: bool = Field(exclude=True)

    def to_parquet(self) -> pa.Table:
        vehicles_dict_list = [vehicle.model_dump() for vehicle in self.vehicles]
        table = pa.Table.from_pylist(vehicles_dict_list, schema=Vehicle.parquet_schema)
        return table
