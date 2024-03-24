from pydantic import ConfigDict, Field, AliasGenerator
from pydantic.alias_generators import to_camel
from typing import Optional, Iterator
from .avro_model import AvroModel
from avro.io import BinaryEncoder, DatumWriter
import avro.schema
import io

_schema = avro.schema.parse(open("/avro/vehicle.avsc").read())

class Vehicle(AvroModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(validation_alias=to_camel, serialization_alias=to_camel),
        arbitrary_types_allowed=True,
        populate_by_name=True,
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

    def to_avro(self) -> bytes:
        buffer = io.BytesIO()
        encoder = BinaryEncoder(buffer)
        datum_writer = DatumWriter(_schema)
        datum_writer.write(self.model_dump(), encoder)
        return buffer.getvalue()
    
class RunningVehicles(AvroModel):
    vehicles: list[Vehicle]
    offline: bool = Field(exclude=True)

    def to_avro(self) -> Iterator[bytes]:
        for vehicle in self.vehicles:
            yield vehicle.to_avro()
    

